FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc libffi-dev libssl-dev ffmpeg aria2 \
    && pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]
