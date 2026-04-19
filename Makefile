# Alvos úteis para avaliação local.
# Predefinição: interpretador do venv do projeto (reprodutível com README).
# Sobrescrever se necessário: make test PYTHON=python3

PYTHON ?= .venv/bin/python

.PHONY: docker-up docker-down test e2e venv

venv:
	@echo "Crie o ambiente com: python3 -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt"

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

test:
	$(PYTHON) run_tests.py

e2e:
	bash scripts/e2e_demo.sh
