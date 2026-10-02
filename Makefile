.PHONY: install format lint fix check clean

# Install dependencies
install:
	pip install -r requirements.txt


# Format code using Ruff
format:
	ruff format .


# Lint code
lint:
	ruff check .


# Auto-fix lint issues
fix:
	ruff check . --fix


# Run formatting + lint fixes
check: fix format


# Run individual schema components
schema:
	python -m app.schema.device


# Run individual prompts components
prompts:
	python -m app.prompts.templates	

# Run individual data components
data:
	python -m app.data.devices
	

# Run individual services components
services:
	python -m app.services.extraction
	python -m app.services.search

# Run individual utils components
services:
	python -m app.utils.extraction
	python -m app.utils.search

backend:
	uvicorn app.main:app --reload
	




# Remove Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete