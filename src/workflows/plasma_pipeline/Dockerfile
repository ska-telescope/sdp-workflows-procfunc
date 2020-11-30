FROM python:3.8

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY  cbf_sdp.py ./
ENTRYPOINT ["python", "cbf_sdp.py"]
