PYLINT = pylint
PYLINTFLAGS = -rn

PYTHONFILES := $(wildcard *.py)

pylint: $(patsubst %.py,%.pylint,$(PYTHONFILES))



.PHONY: black
black:
	poetry run black ./src --config ./pyproject.toml

.PHONY: isort
isort:
	poetry run isort ./src --settings-path ./pyproject.toml

.PHONY: format
format:
	make black && make isort

.PHONY: pycheck
pycheck:
	poetry run pylint --rcfile ./pyproject.toml src

.PHONY: py!
py!:
	 make format && make pycheck

