install:
	@poetry install
activate:
	@eval $(poetry env activate)
run:
	@poetry run python3 workout_updater/lambda_function.py
all: install activate run
