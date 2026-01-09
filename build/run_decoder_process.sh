#!/bin/bash
# Скрипт для запуска дополнительных процессов обработки (резервный)

echo "Starting decoder process..."
python /app/source/main.py "$@"