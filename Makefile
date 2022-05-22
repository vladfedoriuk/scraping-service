.PHONY: services down selery-worker dev

# docker

services:  ### bring up all the dependency services.
	docker compose --profile services up -d

observability:  ### bring up all the observability related services.
	docker compose --profile observability up -d

examples-integrations:  ### bring up the example integrations.
	docker compose --profile examples-integrations up -d

down:  ### bring down all the services.
	docker compose down --remove-orphans


# celery

celery-worker:  ### spin up a celery worker process.
	celery -A scraping worker -l info

dev: services observability  ### spin up development server.
	python manage.py runserver