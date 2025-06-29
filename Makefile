.PHONY: migrate app test

migrate: 
	@echo "Running migration"
	docker compose up -d

app:
	@echo "Running main application"
	python main.py

test:
	@echo "Running tests"
	python -m pytest tests

report:
	@echo "Generating test report"
	python -m pytest tests -v --cov --cov-report=html