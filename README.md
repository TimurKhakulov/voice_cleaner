**Инструкция по использованию**

**Запуск через Docker Compose:**
**1. Соберка проекта:**

bash
cd voice-cleaner
docker-compose -f build/docker-compose.yml build

2. Поместите видео файлы в папку input_video

3. Запустите обработку:

bash
# Обработка одного файла
docker-compose -f build/docker-compose.yml run voice-cleaner \
  --input /app/input_video/video.mp4 \
  --output /app/output_video/cleaned.mp4

# Обработка всех файлов в директории
docker-compose -f build/docker-compose.yml run voice-cleaner \
  --process-dir /app/input_video \
  --output-dir /app/output_video

# Авто-анализ файла
docker-compose -f build/docker-compose.yml run voice-cleaner \
  --auto-analyze /app/input_video/video.mp4

# Обработка тестовых файлов
docker-compose -f build/docker-compose.yml run voice-cleaner --fixtures


**Ключевые особенности реализации:**
1. Только ffmpeg и стандартная библиотека Python - не используются внешние модели или нейросети

2. Auto-анализ спектра - автоматическое определение характеристик аудио

3. Комплексная обработка:

  Бандпас фильтр (300-3400 Гц) для выделения речи

  Динамическая компрессия для улучшения разборчивости

  Подавление шумов с помощью FFT-фильтра

  Нормализация уровней для предотвращения клиппинга

4. Сохранение синхронизации - использование shortest=None для сохранения оригинальной длительности

5. Поддержка различных форматов - все основные видео форматы

6. CLI интерфейс - гибкие параметры командной строки