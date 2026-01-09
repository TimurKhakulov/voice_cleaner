FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY source/ ./source/
COPY build/entrypoint.sh /entrypoint.sh
COPY build/run_decoder_process.sh /run_decoder_process.sh
RUN chmod +x /entrypoint.sh /run_decoder_process.sh

RUN mkdir -p /app/input_video /app/output_video /app/fixtures

ENTRYPOINT ["/entrypoint.sh"]