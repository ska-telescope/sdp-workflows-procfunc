FROM python:3.9-slim

RUN apt-get update && apt-get -y install gcc

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY pss_receive.py ./
ENTRYPOINT ["python", "pss_receive.py"]
