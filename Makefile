.PHONY: help build run stop logs shell test lint format clean docker-build docker-push deploy

PYTHON := python3.11
VENV := venv
DOCKER_IMAGE := minirack-management:latest
DOCKER_REGISTRY ?= docker.io
REGISTRY_URL ?= $(DOCKER_REGISTRY)/yourusername

help: ## Show this help message
	@echo "MiniRack Management Portal - Build & Development Commands"
	@echo "==========================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development

install: ## Install development dependencies
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip setuptools wheel
	. $(VENV)/bin/activate && pip install -e ".[dev]"

dev: ## Run development server with auto-reload
	. $(VENV)/bin/activate && python -m uvicorn minirack_ai_lab_management.main:app --reload --host 0.0.0.0 --port 8080

lint: ## Run code linters
	. $(VENV)/bin/activate && black --check minirack_ai_lab_management/
	. $(VENV)/bin/activate && isort --check-only minirack_ai_lab_management/
	. $(VENV)/bin/activate && flake8 minirack_ai_lab_management/
	. $(VENV)/bin/activate && mypy minirack_ai_lab_management/

format: ## Format code with black and isort
	. $(VENV)/bin/activate && black minirack_ai_lab_management/
	. $(VENV)/bin/activate && isort minirack_ai_lab_management/

test: ## Run test suite
	. $(VENV)/bin/activate && pytest tests/ -v --cov=minirack_ai_lab_management

test-watch: ## Run tests in watch mode
	. $(VENV)/bin/activate && pytest-watch tests/

clean: ## Clean up build artifacts and cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/

# Docker

docker-build: ## Build Docker image
	docker build -t $(DOCKER_IMAGE) .
	@echo "✅ Built $(DOCKER_IMAGE)"

docker-build-no-cache: ## Build Docker image without cache
	docker build --no-cache -t $(DOCKER_IMAGE) .
	@echo "✅ Built $(DOCKER_IMAGE) (no cache)"

docker-run: ## Run Docker container
	docker run -d -p 8080:8080 --name minirack-management $(DOCKER_IMAGE)
	@echo "✅ Container started on http://localhost:8080"

docker-stop: ## Stop Docker container
	docker stop minirack-management || true
	docker rm minirack-management || true
	@echo "✅ Container stopped"

docker-logs: ## View Docker container logs
	docker logs -f minirack-management

docker-shell: ## Open shell in running container
	docker exec -it minirack-management /bin/bash

docker-push: ## Push Docker image to registry
	docker tag $(DOCKER_IMAGE) $(REGISTRY_URL)/$(DOCKER_IMAGE)
	docker push $(REGISTRY_URL)/$(DOCKER_IMAGE)
	@echo "✅ Pushed to $(REGISTRY_URL)/$(DOCKER_IMAGE)"

# Docker Compose

up: ## Start services with docker-compose
	docker-compose up -d
	@echo "✅ Services started"
	@echo "🌐 Portal: http://localhost:8080"
	@echo "📚 API Docs: http://localhost:8080/api/docs"

down: ## Stop services with docker-compose
	docker-compose down
	@echo "✅ Services stopped"

logs: ## View docker-compose logs
	docker-compose logs -f

logs-portal: ## View portal service logs
	docker-compose logs -f management-portal

compose-build: ## Build with docker-compose
	docker-compose build

compose-rebuild: ## Rebuild with docker-compose (no cache)
	docker-compose build --no-cache

compose-restart: ## Restart services
	docker-compose restart

# Deployment

deploy-docker: docker-build up ## Build and deploy with Docker Compose
	@echo "✅ Deployment complete!"

deploy-ansible: ## Deploy with Ansible
	ansible-playbook -i ../minirack-ai-lab/inventory/servers.ini \
		tasks/deploy-management.yaml -u localadmin -k -K

deploy-kubernetes: ## Deploy to Kubernetes
	kubectl apply -f k8s/

# System

health: ## Check system health
	curl -s http://localhost:8080/health | python -m json.tool

api-docs: ## Open API documentation in browser
	@command -v xdg-open >/dev/null && xdg-open http://localhost:8080/api/docs || \
	command -v open >/dev/null && open http://localhost:8080/api/docs || \
	echo "Open http://localhost:8080/api/docs in your browser"

check-ports: ## Check if required ports are available
	@echo "Checking ports..."
	@netstat -tuln | grep -E ':8080|:9100' || echo "✅ Ports available"

dependencies: ## Show Python dependencies
	. $(VENV)/bin/activate && pip list

requirements: ## Export requirements to requirements.txt
	. $(VENV)/bin/activate && pip freeze > requirements.txt

# Documentation

docs: ## Build documentation
	@echo "Documentation available at:"
	@echo "  - README.md - Project overview"
	@echo "  - DEPLOYMENT.md - Deployment guide"
	@echo "  - API Docs: http://localhost:8080/api/docs"

# System integration

install-systemd: ## Install systemd service (bare metal)
	@echo "Installing systemd service..."
	@sudo cp systemd/minirack-management.service /etc/systemd/system/
	@sudo systemctl daemon-reload
	@sudo systemctl enable minirack-management
	@echo "✅ Service installed. Start with: sudo systemctl start minirack-management"

uninstall-systemd: ## Uninstall systemd service
	@sudo systemctl stop minirack-management || true
	@sudo systemctl disable minirack-management || true
	@sudo rm /etc/systemd/system/minirack-management.service || true
	@sudo systemctl daemon-reload
	@echo "✅ Service uninstalled"

service-status: ## Check service status
	sudo systemctl status minirack-management

service-logs: ## View service logs
	sudo journalctl -u minirack-management -f

service-restart: ## Restart service
	sudo systemctl restart minirack-management
	@echo "✅ Service restarted"

# Utility

version: ## Show version information
	@grep -E '"version":|version = ' pyproject.toml | head -1

info: ## Show project information
	@echo "MiniRack AI Lab Management Portal"
	@echo "=================================="
	@echo "Project: $(shell grep 'name' pyproject.toml | head -1)"
	@echo "Python: $(PYTHON)"
	@echo "Docker: $(DOCKER_IMAGE)"
	@echo ""
	@echo "Directories:"
	@echo "  - Source: minirack_ai_lab_management/"
	@echo "  - Tests: tests/"
	@echo "  - Frontend: minirack_ai_lab_management/static/"
	@echo ""
	@echo "Commands:"
	@echo "  Development: make install && make dev"
	@echo "  Production: make docker-build && make up"
	@echo "  Deployment: make deploy-docker or make deploy-ansible"
