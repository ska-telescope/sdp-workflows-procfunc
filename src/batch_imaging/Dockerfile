FROM nexus.engageska-portugal.pt/rascil-docker/rascil-full

WORKDIR /rascil

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY batch_imaging.py rascil_workflows.py ./
ENTRYPOINT ["python3", "batch_imaging.py"]
