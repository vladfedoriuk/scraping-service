.PHONY: services

# docker

services: ### bring up all the dependency services.
	docker compose --profile services up -d

down: ### bring down all the services
	docker compose down --remove-orphans