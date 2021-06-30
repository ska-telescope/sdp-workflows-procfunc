FROM python:3.9-slim

RUN apt-get update && apt-get -y install gcc

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY test_batch.py ./
ENTRYPOINT ["python", "test_batch.py"]
