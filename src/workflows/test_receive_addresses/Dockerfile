FROM python:3.8

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY test_receive_addresses.py ./
ENTRYPOINT ["python", "test_receive_addresses.py"]
