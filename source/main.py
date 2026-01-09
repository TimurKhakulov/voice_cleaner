#!/usr/bin/env python3
"""
Voice Cleaner - Утилита для очистки речи в видео
"""

import os
import sys
import argparse
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict

from .paths import *
from .ffmpeg_client import FFmpegClient


class VoiceCleaner:
    """Основной класс для очистки речи в видео"""

    def __init__(self):
        self.ffmpeg_client = FFmpegClient()
        self.temp_dir = tempfile.mkdtemp(prefix="voice_cleaner_")
        print(f"Created temp directory: {self.temp_dir}")

    def cleanup(self):
        """Очистка временных файлов"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def process_video(self, input_path: str, output_path: str) -> bool:
        """Обработка одного видео файла"""
        try:
            print(f"\n{'=' * 60}")
            print(f"Processing: {os.path.basename(input_path)}")
            print(f"{'=' * 60}")

            # Проверка существования файла
            if not os.path.exists(input_path):
                print(f"Error: Input file not found: {input_path}")
                return False

            # Шаг 1: Получение информации о видео
            print("1. Analyzing video...")
            video_info = self.ffmpeg_client.probe_video(input_path)
            if not video_info:
                print("Error: Could not probe video")
                return False

            # Шаг 2: Извлечение аудио
            print("2. Extracting audio...")
            temp_audio = os.path.join(self.temp_dir, "original_audio.wav")
            if not self.ffmpeg_client.extract_audio(input_path, temp_audio):
                return False

            # Шаг 3: Анализ спектра
            print("3. Analyzing audio spectrum...")
            audio_analysis = self.ffmpeg_client.analyze_audio_spectrum(temp_audio)
            print(f"   Audio analysis: {audio_analysis}")

            # Шаг 4: Обнаружение участков речи
            print("4. Detecting speech regions...")
            speech_regions = self.ffmpeg_client.detect_speech_regions(temp_audio)
            print(f"   Found {len(speech_regions)} speech regions")

            # Шаг 5: Создание спектрограммы (опционально)
            if False:  # Можно включить для отладки
                spectrogram = os.path.join(self.temp_dir, "spectrogram.png")
                self.ffmpeg_client.create_spectrogram(temp_audio, spectrogram)
                print(f"   Spectrogram saved to: {spectrogram}")

            # Шаг 6: Очистка аудио
            print("5. Cleaning audio (noise reduction)...")
            cleaned_audio = os.path.join(self.temp_dir, "cleaned_audio.wav")
            if not self.ffmpeg_client.apply_noise_reduction(temp_audio, cleaned_audio):
                return False

            # Шаг 7: Нормализация аудио
            print("6. Normalizing audio levels...")
            normalized_audio = os.path.join(self.temp_dir, "normalized_audio.wav")
            if not self.ffmpeg_client.normalize_audio_levels(cleaned_audio, normalized_audio):
                # Если не удалось нормализовать, используем очищенное аудио
                normalized_audio = cleaned_audio

            # Шаг 8: Объединение с видео
            print("7. Merging cleaned audio with video...")
            if not self.ffmpeg_client.merge_audio_video(input_path, normalized_audio, output_path):
                return False

            # Шаг 9: Проверка результата
            print("8. Verifying output...")
            output_info = self.ffmpeg_client.probe_video(output_path)
            if output_info:
                duration = float(output_info['format']['duration'])
                print(f"   Success! Output duration: {duration:.2f} seconds")
                print(f"   Output saved to: {output_path}")
                return True
            else:
                print("Error: Could not verify output video")
                return False

        except Exception as e:
            print(f"Error processing video: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_directory(self, input_dir: str, output_dir: str,
                          extensions: List[str] = None) -> int:
        """Обработка всех видео в директории"""
        if extensions is None:
            extensions = VIDEO_EXTENSIONS

        # Создание выходной директории
        os.makedirs(output_dir, exist_ok=True)

        # Поиск видео файлов
        video_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    video_files.append(os.path.join(root, file))

        print(f"Found {len(video_files)} video file(s) to process")

        # Обработка каждого файла
        success_count = 0
        for i, video_file in enumerate(video_files, 1):
            print(f"\nProcessing file {i}/{len(video_files)}")

            # Создание имени выходного файла
            filename = os.path.basename(video_file)
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_cleaned{ext}"
            output_path = os.path.join(output_dir, output_filename)

            # Обработка видео
            if self.process_video(video_file, output_path):
                success_count += 1

        return success_count

    def run_from_fixtures(self, output_dir: str) -> int:
        """Запуск обработки тестовых файлов из fixtures"""
        print("Running from fixtures...")

        if not os.path.exists(FIXTURES_DIR):
            print(f"Fixtures directory not found: {FIXTURES_DIR}")
            return 0

        return self.process_directory(FIXTURES_DIR, output_dir)

    def auto_analyze(self, input_path: str) -> Dict:
        """Автоматический анализ видео файла"""
        print(f"\nAuto-analyzing: {input_path}")

        if not os.path.exists(input_path):
            print(f"Error: File not found: {input_path}")
            return {}

        # Извлекаем аудио для анализа
        temp_audio = os.path.join(self.temp_dir, "analysis_audio.wav")
        if not self.ffmpeg_client.extract_audio(input_path, temp_audio):
            return {}

        # Получаем информацию о видео
        video_info = self.ffmpeg_client.probe_video(input_path)

        # Анализируем аудио
        audio_analysis = self.ffmpeg_client.analyze_audio_spectrum(temp_audio)

        # Обнаруживаем участки речи
        speech_regions = self.ffmpeg_client.detect_speech_regions(temp_audio)

        # Создаем спектрограмму
        spectrogram = os.path.join(self.temp_dir, "analysis_spectrogram.png")
        self.ffmpeg_client.create_spectrogram(temp_audio, spectrogram)

        # Формируем отчет
        analysis_report = {
            'filename': os.path.basename(input_path),
            'video_info': video_info,
            'audio_analysis': audio_analysis,
            'speech_regions_count': len(speech_regions),
            'speech_regions': speech_regions[:5],  # Первые 5 регионов
            'spectrogram': spectrogram if os.path.exists(spectrogram) else None,
            'analysis_time': datetime.now().isoformat()
        }

        # Вывод отчета
        print("\n" + "=" * 60)
        print("ANALYSIS REPORT")
        print("=" * 60)
        print(f"File: {analysis_report['filename']}")
        print(f"Duration: {analysis_report['audio_analysis'].get('duration', 0):.2f}s")
        print(f"Speech regions detected: {analysis_report['speech_regions_count']}")
        print(f"Sample rate: {analysis_report['audio_analysis'].get('sample_rate', 0)} Hz")
        print("=" * 60)

        return analysis_report


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description='Voice Cleaner - Remove music and noise from videos, keep speech clear',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input input.mp4 --output output.mp4
  %(prog)s --auto-analyze input.mp4
  %(prog)s --process-dir ./videos --output-dir ./cleaned
  %(prog)s --fixtures
        """
    )

    # Основные аргументы
    parser.add_argument('--input', '-i', type=str,
                        help='Input video file')
    parser.add_argument('--output', '-o', type=str,
                        help='Output video file')

    # Дополнительные аргументы
    parser.add_argument('--auto-analyze', '-a', action='store_true',
                        help='Auto-analyze video without processing')
    parser.add_argument('--process-dir', '-d', type=str,
                        help='Process all videos in directory')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                        help=f'Output directory (default: {OUTPUT_DIR})')
    parser.add_argument('--fixtures', '-f', action='store_true',
                        help='Process fixture files')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    # Создание экземпляра VoiceCleaner
    cleaner = VoiceCleaner()

    try:
        # Выбор режима работы
        if args.auto_analyze and args.input:
            # Режим анализа
            cleaner.auto_analyze(args.input)

        elif args.input and args.output:
            # Обработка одного файла
            success = cleaner.process_video(args.input, args.output)
            if success:
                print(f"\n✓ Successfully processed: {args.input}")
                print(f"  Output: {args.output}")
                sys.exit(0)
            else:
                print(f"\n✗ Failed to process: {args.input}")
                sys.exit(1)

        elif args.process_dir:
            # Обработка директории
            success_count = cleaner.process_directory(
                args.process_dir,
                args.output_dir
            )
            print(f"\n✓ Processed {success_count} file(s)")
            sys.exit(0)

        elif args.fixtures:
            # Обработка тестовых файлов
            success_count = cleaner.run_from_fixtures(args.output_dir)
            print(f"\n✓ Processed {success_count} fixture file(s)")
            sys.exit(0)

        else:
            # Вывод справки
            parser.print_help()
            print("\n\nAvailable fixtures:")
            if os.path.exists(FIXTURES_DIR):
                for file in os.listdir(FIXTURES_DIR):
                    if any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                        print(f"  - {file}")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
    finally:
        # Очистка временных файлов
        cleaner.cleanup()


if __name__ == "__main__":
    main()
