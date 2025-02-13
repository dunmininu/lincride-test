init:
	pip install -r requirements.txt
	pre-commit install

test:
	python manage.py test

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

docker-build:
	docker-compose build

docker-up:
	docker-compose up

lint:
	ruff check --fix .