.PHONY: help build push
.DEFAULT_GOAL := help

PREFIX ?=
RELEASE ?=
GITHASH ?= $(shell git rev-parse --verify --short=8 HEAD)

ifeq ($(RELEASE),)
	TAG := $(NAME):$(VERSION)-$(GITHASH)
else
	TAG := $(NAME):$(VERSION)
endif

ifneq ($(PREFIX),)
	TAG := $(PREFIX)/$(TAG)
endif

# Environment variables to use as labels when building

LABEL_ENVVARS := \
	CI_COMMIT_AUTHOR \
	CI_COMMIT_REF_NAME \
	CI_COMMIT_REF_SLUG \
	CI_COMMIT_SHA \
	CI_COMMIT_SHORT_SHA \
	CI_COMMIT_TIMESTAMP \
	CI_JOB_ID \
	CI_JOB_URL \
	CI_PIPELINE_ID \
	CI_PIPELINE_IID \
	CI_PIPELINE_URL \
	CI_PROJECT_ID \
	CI_PROJECT_PATH_SLUG \
	CI_PROJECT_URL \
	CI_REPOSITORY_URL \
	CI_RUNNER_ID \
	CI_RUNNER_REVISION \
	CI_RUNNER_TAGS \
	GITLAB_USER_EMAIL \
	GITLAB_USER_ID \
	GITLAB_USER_LOGIN \
	GITLAB_USER_NAME

# Construct --label flags

LABELS := $(foreach var,$(LABEL_ENVVARS),--label $(var)="$${$(var)}")

help: ## Show this help
	@echo
	@echo "Targets:"
	@echo
	@for m in $(MAKEFILE_LIST); do \
		grep -E '^[a-zA-Z_-]+:.*?## .*$$' $$m | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2}'; \
	done
	@echo

build: ## Build the Docker image
	docker build --pull $(LABELS) -t $(TAG) .

push: ## Push the Docker image
	docker push $(TAG)
