import os
import json
import subprocess

workflow_file = "workflows.json"
prefix_old = "nexus.engageska-portugal.pt/sdp-prototype/workflow"
prefix_new = "artefact.skao.int/ska-sdp-wflow"

# Environment variables to use for labels

label_envars = [
    "CI_COMMIT_AUTHOR",
    "CI_COMMIT_REF_NAME",
    "CI_COMMIT_REF_SLUG",
    "CI_COMMIT_SHA",
    "CI_COMMIT_SHORT_SHA",
    "CI_COMMIT_TIMESTAMP",
    "CI_JOB_ID",
    "CI_JOB_URL",
    "CI_PIPELINE_ID",
    "CI_PIPELINE_IID",
    "CI_PIPELINE_URL",
    "CI_PROJECT_ID",
    "CI_PROJECT_PATH_SLUG",
    "CI_PROJECT_URL",
    "CI_REPOSITORY_URL",
    "CI_RUNNER_ID",
    "CI_RUNNER_REVISION",
    "CI_RUNNER_TAGS",
    "GITLAB_USER_EMAIL",
    "GITLAB_USER_ID",
    "GITLAB_USER_LOGIN",
    "GITLAB_USER_NAME",
]

# Read old workflow image names

with open(workflow_file, "r") as file:
    definitions = json.load(file)

repositories = {repo["name"]: repo["path"] for repo in definitions["repositories"]}
images = [
    repositories[w["repository"]] + "/" + w["image"] + ":" + v
    for w in definitions["workflows"]
    for v in w["versions"]
]

# Construct --label flags

labels = []
for name in label_envars:
    value = os.environ.get(name, "")
    labels += ["--label", f"{name}={value}"]

# For each image, build a new one using the old one as a base and add the
# metadata, then push to CAR.

for image_old in images:
    print(image_old)
    image_new = image_old.replace(prefix_old, prefix_new)
    print("Building new image")
    with open("Dockerfile", "w") as file:
        file.write(f"FROM {image_old}\n")
    command = ["docker", "build", ".", "--pull", "-t", image_new] + labels
    print(" ".join(command))
    subprocess.run(command)
    print("Pushing new image")
    command = ["docker", "push", image_new]
    print(" ".join(command))
    subprocess.run(command)
