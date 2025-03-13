run:
	python msk/main.py
	
makemigration:
	alembic revision --autogenerate -m "$(name)"

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

initdb:
	python database/db_main.py

save-requirements:
	pip freeze > requirements.txt
	conda list --explicit > conda-requirement.txt

docker-up:
	docker-compose up -d

run-api:
	python celonis_api/main.py

start-all:
	make docker-up && make run && make run-api
