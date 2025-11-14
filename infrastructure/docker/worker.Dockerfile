FROM python:3.11-slim
WORKDIR /code
RUN apt-get update && apt-get install -y build-essential
COPY . /code
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH="/code"
CMD ["python", "app/workers/sentiment_worker.py"]