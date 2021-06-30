FROM python:3.9-slim

# TODO: remove 'make' from install once this is ported to workflow lib
#   test that build works then too; probably other parts also need updating
RUN apt-get update && apt-get -y install gcc make

COPY requirements.txt ./
RUN pip install -r requirements.txt

WORKDIR /app
COPY daliuge ./daliuge
ENTRYPOINT ["python", "-m", "daliuge.main"]
