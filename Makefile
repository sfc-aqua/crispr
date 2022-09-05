.PHONY: format build all clean check
format:
	poetry run black ./crispr/*.py ./crispr/**/*.py  ./templates/*.py ./templates/*.ipynb

build:
	poetry build

all:
	poetry install
	pip install -e .

clean:
	rm -rf dist crispr/__pycache__ __pycache__

check:
	poetry run pytest -s
