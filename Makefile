.PHONY: services

# docker

services: ### bring up all the dependency services.
	docker compose --profile services up -d

down: ### bring down all the services
	docker compose down --remove-orphans


# celery

celery-worker: ### spin up a celery worker process
	celery -A scrapping worker -l info