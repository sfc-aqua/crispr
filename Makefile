.PHONY: format build all clean
format:
	poetry run black ./crispr/*.py ./crispr/**/*.py 

build:
	poetry build

all:
	poetry install
	pip install -e .

clean:
	rm -rf dist crispr/__pycache__ __pycache__
