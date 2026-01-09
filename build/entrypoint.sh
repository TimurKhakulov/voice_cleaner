#!/usr/bin/env bash

set -e

echo "Voice Cleaner - Starting..."

# Проверяем наличие ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Error: ffmpeg is not installed!"
    exit 1
fi

# Проверяем наличие ffprobe
if ! command -v ffprobe &> /dev/null; then
    echo "Error: ffprobe is not installed!"
    exit 1
fi

# Запускаем основной скрипт
exec python /app/source/main.py "$@"