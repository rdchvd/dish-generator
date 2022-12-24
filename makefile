cnf ?= .env
include $(cnf)
export $(shell sed 's/=.*//' $(cnf))

.PHONY: help build up start down destroy stop restart logs ps
# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)


TARGET_MAX_CHAR_NUM=20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

## Build or rebuild services
build:
	docker-compose -f docker-compose.yml build $(c)

## Create and start containers
up:
	 docker-compose -f docker-compose.yml up -d $(c)
## Start services
start:
	docker-compose -f docker-compose.yml start $(c)
## Stop and remove containers, networks
down:
	docker-compose -f docker-compose.yml down $(c)
## Remove named volumes declared in the volumes section of the Compose file and anonymous volumes attached to containers
destroy:
	docker-compose -f docker-compose.yml down -v $(c)
## Stop services
stop:
	docker-compose -f docker-compose.yml stop $(c)
## Restart containers
restart:
	docker-compose -f docker-compose.yml restart $(c)
## View output from containers
logs:
	docker-compose -f docker-compose.yml logs --tail=100 -f $(c)
## List containers
ps:
	docker-compose -f docker-compose.yml ps

## Run FastAPI server
run_server:
	uvicorn handler:app --reload

## Run migrations
migrations:
	alembic revision --autogenerate -m "init"
	alembic upgrade head

## Run tests in docker container
run_tests:
	docker-compose build --build-arg TARGET=test; \
	export TARGET=test; \
	docker-compose up --abort-on-container-exit; \
  	unset TARGET
