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
	conda list --explicit > conda-requirements.txt

docker-up:
	docker-compose up -d

run-api:
	uvicorn celonis_api.main:app --host 0.0.0.0 --port 8000 --reload


start-all:
	make docker-up && make run && make run-api
