SOURCE_FOLDER=./src
TESTS_FOLDER=./tests
SERVICE_NAME=gateway-service

COMPOSE_CMD := $(shell (command -v "docker" >/dev/null 2>&1 && docker compose version >/dev/null 2>&1 && echo "docker compose") || echo "docker-compose")


build:
	$(COMPOSE_CMD) -f docker-compose.yml build

run:
	$(COMPOSE_CMD) -f docker-compose.yml up

bash:
	docker exec -it $(SERVICE_NAME) bash

attach:
	docker attach $(SERVICE_NAME)

run-tests:
	docker exec -it $(SERVICE_NAME) bash -c "pytest --asyncio-mode=auto -x"

check-code-quality:
	docker exec -it $(SERVICE_NAME) bash -c "isort $(SOURCE_FOLDER) $(TESTS_FOLDER) --diff --check-only"
	docker exec -it $(SERVICE_NAME) bash -c "flake8 $(SOURCE_FOLDER) $(TESTS_FOLDER)"
	docker exec -it $(SERVICE_NAME) bash -c "black --check $(SOURCE_FOLDER)"

check-yaml-standards:
	docker exec -it $(SERVICE_NAME) bash -c "yamllint ."

format:
	docker exec -it $(SERVICE_NAME) bash -c "isort --jobs 4 $(SOURCE_FOLDER) $(TESTS_FOLDER)"
	docker exec -it $(SERVICE_NAME) bash -c "autoflake --jobs 4 --recursive --in-place --remove-unused-variables --remove-all-unused-imports $(SOURCE_FOLDER) $(TESTS_FOLDER)"
	docker exec -it $(SERVICE_NAME) bash -c "autopep8 --jobs 4 --exclude migrations --recursive --in-place -a -a $(SOURCE_FOLDER) $(TESTS_FOLDER)"
	docker exec -it $(SERVICE_NAME) bash -c "black $(SOURCE_FOLDER) $(TESTS_FOLDER)"
