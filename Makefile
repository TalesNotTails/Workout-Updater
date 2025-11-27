install:
	@poetry install
run:
	@poetry run python3 workout_updater/lambda_function.py
all: install run
