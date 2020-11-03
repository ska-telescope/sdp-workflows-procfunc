#
# Makefile for building and publishing the `sdp_vis_receive` image.
#

# ----------------------------------------------------------------------------
# Variables
# ----------------------------------------------------------------------------
IMAGE_NAME:=vis-receive
VERSION:=$(shell awk -F= '/.*/{print $$1}' VERSION)
IMAGE:=$(DOCKER_REGISTRY_HOST)/$(DOCKER_REGISTRY_USER)/$(IMAGE_NAME)

# ----------------------------------------------------------------------------
# Docker helper targets
# ----------------------------------------------------------------------------

.PHONY: build
build:  ## Build the docker image
	docker build -t $(IMAGE):$(VERSION) .

.PHONY: ls
ls:  ## List docker images
	docker image ls --filter=reference="$(IMAGE)"

.PHONY: push
push:   ## Push the image to the remote repository
	docker push "$(IMAGE):$(VERSION)"

# ----------------------------------------------------------------------------
# Help target
# ----------------------------------------------------------------------------


.DEFAULT_GOAL := help
.PHONY: help
help:  ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' ./Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
