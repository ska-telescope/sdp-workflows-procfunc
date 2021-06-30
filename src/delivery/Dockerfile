FROM python:3.9-slim

RUN apt-get update && apt-get -y install gcc

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY delivery.py ./
ENTRYPOINT ["python", "delivery.py"]
