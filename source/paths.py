import os

# Базовые пути
BASE_DIR = "/app"
INPUT_DIR = os.getenv("INPUT_DIR", os.path.join(BASE_DIR, "input_video"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", os.path.join(BASE_DIR, "output_video"))
FIXTURES_DIR = os.getenv("FIXTURES_DIR", os.path.join(BASE_DIR, "fixtures"))

# Расширения видео файлов
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']

# Параметры обработки
SAMPLE_RATE = 16000
SPEECH_BAND = (300, 3400)  # Полоса речи
NOISE_REDUCTION_LEVEL = 0.3
COMPRESSION_RATIO = 1.5
