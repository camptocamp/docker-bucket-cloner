init:
	virtualenv -p /usr/bin/python3 venv

deps:
	pip3 install -r requirements.txt

dev-deps: deps
	pip3 install -r requirements-dev.txt

lint:
	pylint bucketcloner

test:
	pytest -v tests

install:
	python3 setup.py install
