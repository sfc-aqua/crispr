.PHONY: format build all clean
format:
	poetry run black ./*.py

build:
	poetry build

all:
	poetry install

clean:
	rm -rf dist quisp_run/__pycache__ __pycache__
	