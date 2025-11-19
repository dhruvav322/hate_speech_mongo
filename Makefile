.PHONY: help install dev backend frontend test lint format clean docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev: ## Start both backend and frontend in development mode
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8001"
	@echo "Frontend: http://localhost:3000"
	@make -j2 backend frontend

backend: ## Start backend server
	uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

frontend: ## Start frontend server
	cd frontend && npm run dev

test: ## Run all tests
	@echo "Running backend tests..."
	pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test

lint: ## Lint code
	@echo "Linting backend..."
	ruff check src/ tests/
	@echo "Linting frontend..."
	cd frontend && npm run lint

format: ## Format code
	@echo "Formatting backend..."
	black src/ tests/
	ruff check --fix src/ tests/
	@echo "Formatting frontend..."
	cd frontend && npm run format || npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css}"

clean: ## Clean build artifacts
	@echo "Cleaning..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -r {} + 2>/dev/null || true
	rm -rf frontend/.next
	rm -rf frontend/out
	rm -rf frontend/dist
	rm -rf frontend/build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Initial setup (install deps, copy env files)
	@echo "Setting up project..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env from .env.example - please update with your values"; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		cp frontend/.env.example frontend/.env.local; \
		echo "Created frontend/.env.local from .env.example"; \
	fi
	@make install

