.PHONY: services down selery-worker dev

# docker

services:  ### bring up all the dependency services.
	docker compose --profile services up -d

observability:  ### bring up all the observability related services.
	docker compose --profile observability up -d

examples-integrations:  ### bring up the example integrations.
	docker compose --profile examples-integrations up -d

dev: services observability  ### spin up development server and the worker processes.
	docker compose --profile dev up -d

down:  ### bring down all the services.
	docker compose down --remove-orphans

