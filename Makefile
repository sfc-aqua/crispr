.PHONY: format build all clean
format:
	poetry run black ./quisp_run/*.py ./quisp_run/**/*.py -v

build:
	poetry build

all:
	poetry install
	pip install -e .

clean:
	rm -rf dist quisp_run/__pycache__ __pycache__
