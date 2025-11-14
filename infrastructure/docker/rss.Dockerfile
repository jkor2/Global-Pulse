FROM python:3.11-slim
WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
 && update-ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY . /code
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH="/code"

CMD ["python", "app/workers/rss_worker.py"]