runserver:
	uv run manage.py runserver
	
makemigrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

showmigrations:
	uv run manage.py showmigrations

shell:
	uv run manage.py shell

dbshell:
	uv run manage.py dbshell

pytest:
	uv run pytest -v --tb=short --maxfail=5 --disable-warnings

docker-dev:
	docker compose -f ../docker-compose.dev.yml up --build -d

docker-prod:
	docker compose -f ../docker-compose.prod.yml up --build -d