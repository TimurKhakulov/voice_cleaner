import subprocess
from typing import Dict, List, Tuple
import ffmpeg

from .paths import *


class FFmpegClient:
    """Клиент для работы с FFmpeg"""

    @staticmethod
    def probe_video(filepath: str) -> Dict:
        """Получение информации о видео файле"""
        try:
            probe = ffmpeg.probe(filepath)
            return probe
        except ffmpeg.Error as e:
            print(f"Error probing video: {e}")
            return {}

    @staticmethod
    def extract_audio(video_path: str, audio_path: str) -> bool:
        """Извлечение аудио из видео"""
        try:
            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='pcm_s16le', ac=1, ar=SAMPLE_RATE)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error extracting audio: {e}")
            return False

    @staticmethod
    def analyze_audio_spectrum(audio_path: str) -> Dict:
        """Анализ спектра аудио для определения характеристик"""
        try:
            # Используем ffmpeg для анализа спектра
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'astats=metadata=1:reset=1',
                '-f', 'null',
                '-'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Парсим вывод для получения информации об аудио
            analysis = {
                'sample_rate': SAMPLE_RATE,
                'channels': 1,
                'duration': 0,
                'rms_level': -30,  # по умолчанию
                'peak_level': -6,  # по умолчанию
            }

            # Получаем длительность
            probe = FFmpegClient.probe_video(audio_path)
            if probe and 'format' in probe:
                analysis['duration'] = float(probe['format'].get('duration', 0))

            return analysis

        except Exception as e:
            print(f"Error analyzing audio spectrum: {e}")
            return {}

    @staticmethod
    def apply_noise_reduction(input_audio: str, output_audio: str,
                              reduction_level: float = NOISE_REDUCTION_LEVEL) -> bool:
        """Применение шумоподавления"""
        try:
            # Комплексный фильтр для подавления шумов и музыки
            # 1. Бандпас фильтр для выделения полосы речи
            # 2. Динамическая компрессия
            # 3. Подавление шума
            # 4. Нормализация

            filter_chain = [
                # Бандпас фильтр для выделения полосы речи
                f"highpass=f={SPEECH_BAND[0]}",
                f"lowpass=f={SPEECH_BAND[1]}",

                # Динамическая компрессия для улучшения речи
                f"acompressor=threshold=-30dB:ratio={COMPRESSION_RATIO}:attack=50:release=500",

                # Подавление шумов
                f"afftdn=nf={reduction_level}:nt=w",

                # Нормализация
                "loudnorm=I=-16:LRA=11:TP=-1.5",
            ]

            filter_str = ",".join(filter_chain)

            (
                ffmpeg
                .input(input_audio)
                .output(output_audio, af=filter_str, acodec='pcm_s16le', ar=SAMPLE_RATE)
                .overwrite_output()
                .run(quiet=True)
            )
            return True

        except ffmpeg.Error as e:
            print(f"Error applying noise reduction: {e}")
            return False

    @staticmethod
    def merge_audio_video(original_video: str, cleaned_audio: str,
                          output_video: str) -> bool:
        """Объединение очищенного аудио с оригинальным видео"""
        try:
            # Сохраняем оригинальное видео без аудио
            video_stream = ffmpeg.input(original_video).video

            # Добавляем очищенное аудио
            audio_stream = ffmpeg.input(cleaned_audio).audio

            # Объединяем
            (
                ffmpeg
                .output(video_stream, audio_stream, output_video,
                        vcodec='copy', acodec='aac', audio_bitrate='128k',
                        shortest=None)  # Используем длительность видео
                .overwrite_output()
                .run(quiet=True)
            )
            return True

        except ffmpeg.Error as e:
            print(f"Error merging audio with video: {e}")
            return False

    @staticmethod
    def normalize_audio_levels(audio_path: str, output_path: str) -> bool:
        """Нормализация уровней аудио для предотвращения клиппинга"""
        try:
            (
                ffmpeg
                .input(audio_path)
                .output(output_path,
                        af="loudnorm=I=-16:LRA=11:TP=-1.5",
                        acodec='pcm_s16le',
                        ar=SAMPLE_RATE)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error normalizing audio: {e}")
            return False

    @staticmethod
    def detect_speech_regions(audio_path: str) -> List[Tuple[float, float]]:
        """Обнаружение участков с речью"""
        try:
            # Используем простой детектор активности
            cmd = [
                'ffmpeg',
                '-i', audio_path,
                '-af', 'silencedetect=noise=-30dB:d=0.5',
                '-f', 'null',
                '-'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Парсим результаты silencedetect
            regions = []
            lines = result.stderr.split('\n')
            silence_start = None

            for line in lines:
                if 'silence_start' in line:
                    parts = line.split(' ')
                    for i, part in enumerate(parts):
                        if part == 'silence_start:':
                            silence_start = float(parts[i + 1])
                            break
                elif 'silence_end' in line and silence_start is not None:
                    parts = line.split(' ')
                    for i, part in enumerate(parts):
                        if part == 'silence_end:':
                            silence_end = float(parts[i + 1].split('|')[0])
                            # Речь - это интервалы между тишиной
                            if silence_start > 0:  # Начало не с нуля
                                regions.append((0, silence_start))
                            # Добавляем region после тишины
                            regions.append((silence_end, None))
                            silence_start = None
                            break

            # Если последний region не закрыт
            if silence_start is not None:
                regions.append((silence_start, None))

            return regions

        except Exception as e:
            print(f"Error detecting speech regions: {e}")
            return []

    @staticmethod
    def create_spectrogram(audio_path: str, output_image: str) -> bool:
        """Создание спектрограммы для анализа"""
        try:
            (
                ffmpeg
                .input(audio_path)
                .output(output_image,
                        filter_complex="showspectrumpic=s=1024x512:mode=combined",
                        frames=1)
                .overwrite_output()
                .run(quiet=True)
            )
            return True
        except ffmpeg.Error as e:
            print(f"Error creating spectrogram: {e}")
            return False
