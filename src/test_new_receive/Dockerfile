FROM python:3.9-slim

RUN apt-get update && apt-get -y install gcc

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY  cbf_sdp.py ./
ENTRYPOINT ["python", "cbf_sdp.py"]
