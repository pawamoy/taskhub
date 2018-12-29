.PHONY: build-docs clean load-fixtures help build no-deps
.DEFAULT_GOAL := help

SELF := $(abspath $(lastword $(MAKEFILE_LIST)))
PWD := $(patsubst %/,%,$(dir $(SELF)))
CWD := /opt/srv/taskhub/src

# Conditional variables ---------------------------------------------------------------------------
COMPOSE_FILE := docker-compose.yml

DOCKER := docker
DOCKER_COMPOSE := docker-compose
ifndef HOSTNAME
HOSTNAME := $(shell hostname)
endif
DJANGO_SETTINGS_MODULE := core.settings
COMPOSE_FILE := compose-development.yml

DOCKER_COMPOSE += -f docker/$(COMPOSE_FILE) --project-directory .

CONTAINER = taskhub
RUN = $(DOCKER_COMPOSE) run $(RUN_OPTS) --rm $(CONTAINER)
MAKE_IN = $(RUN) make -f Makefile.in-container

DOCKER0_ADDRESS := $(shell ifconfig | grep docker0 -A 1 | grep -Eo 'inet add?r:[^ ]*' | cut -d: -f2)

export DJANGO_SETTINGS_MODULE
export DOCKER0_ADDRESS

# Information -------------------------------------------------------------------------------------
#$(info ----------------------------------------------------)
#$(info HOSTNAME                = ${HOSTNAME})
#$(info COMPOSE_FILE            = ${COMPOSE_FILE})
#$(info DOCKER0_ADDRESS         = ${DOCKER0_ADDRESS})
#$(info DJANGO_SETTINGS_MODULE  = ${DJANGO_SETTINGS_MODULE})
#$(info ----------------------------------------------------)
#$(info )

# Context rules -----------------------------------------------------------------------------------
no-deps:
	$(eval RUN_OPTS = --no-deps)

in-db-container:
	$(eval CONTAINER = taskhub_db)

in-djangoapp-container:
	$(eval CONTAINER = taskhub)

# Building rules ----------------------------------------------------------------------------------
all: build up-no-start build-database build-superuser up ## Build images, create tables, insert fixtures, create super user and start application.

build: ## Build the Docker images.
	$(DOCKER_COMPOSE) build

build-django: ## Build the image for Django.
	$(DOCKER_COMPOSE) build taskhub

build-database: ## Migrate the application database (create or alter tables).
	@$(MAKE_IN) build-database

build-initial-migrations: ## Create the initial database migrations.
	@$(MAKE_IN) build-initial-migrations

build-superuser: ## Create a super user in the application database.
	@$(MAKE_IN) build-superuser

build-docs: ## Build the documentation.
	@$(MAKE_IN) build-docs

# Running rules -----------------------------------------------------------------------------------
up: ## Start the application.
	$(DOCKER_COMPOSE) up

up-no-start: ## Create the containers without starting the application.
	$(DOCKER_COMPOSE) up --no-start

up-daemon: ## Start the application in background.
	$(DOCKER_COMPOSE) up -d

down: ## Stop the application.
	$(DOCKER_COMPOSE) down

shell: ## Launch a shell in the djangoapp container.
	@$(RUN) bash

python: ## Launch a Python shell in the djangoapp container.
	@$(MAKE_IN) python

# Updating rules ----------------------------------------------------------------------------------
load-static-files: delete-django-image delete-static-volume build-django ## Collect static files.

update-migrations: ## Update the database migrations.
	@$(MAKE_IN) update-migrations

create-data-migration: ## Create a new, empty data migration for app APP.
	@$(MAKE_IN) create-data-migration APP=$(APP)

reset-migrations: delete-migrations build-initial-migrations ## Delete all migrations and re-create the initial migrations.

# Testing / Linting rules -------------------------------------------------------------------------
check: check-safety check-bandit check-pylint check-isort check-docs-links check-docs-spelling ## Run all the check jobs.

test: up-daemon pytest down ## Run the test jobs within the whole container infrastructure.

pytest: ## Run the test suite.
	@$(MAKE_IN) pytest

check-safety: no-deps ## Run safety on the dependencies.
	@$(MAKE_IN) check-safety

check-bandit: no-deps ## Run bandit on the code.
	@$(MAKE_IN) check-bandit

check-pylint: no-deps ## Run pylint on the code.
	@$(MAKE_IN) check-pylint

isort: no-deps ## Run isort (write files) on the code.
	@$(MAKE_IN) isort

check-isort: no-deps ## Run isort check on the code.
	@$(MAKE_IN) check-isort

check-docs-links: no-deps ## Check the documentation (spelling, URLs).
	@$(MAKE_IN) check-docs-links

check-docs-spelling: no-deps ## Check the documentation (spelling, URLs).
	@$(MAKE_IN) check-docs-spelling

# Cleaning rules ----------------------------------------------------------------------------------
delete-database-volume: down ## Delete the database volume. Don't do this in production!!
	$(DOCKER) volume rm -f taskhub_data

delete-django-image: down ## Delete the Docker image for the djangoapp service.
	$(DOCKER) image rm taskhub_taskhub || true

delete-static-volume: down ## Delete the Docker volume storing static assets.
	$(DOCKER) volume rm taskhub_static || true

delete-migrations: ## Delete the migrations.
	@$(MAKE_IN) delete-migrations

clean: ## Remove artifacts (build/docs dirs, coverage files, etc.)
	rm -rf build/* 2>/dev/null
	rm -rf .cache 2>/dev/null
	rm -rf .pytest_cache 2>/dev/null
	find . -type f -name "*.pyc" -delete 2>/dev/null
	find . -type d -name __pycache__ -delete 2>/dev/null

clean-docker: down ## Stop and remove containers, volumes and networks.
	$(DOCKER) system prune -f || true

# Usage rules -------------------------------------------------------------------------------------
help: ## Print this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
