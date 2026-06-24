.PHONY: prep-db compose-local-up dvc-ready compose-local-down clean lint
.DEFAULT_GOAL := help


SHELL := /bin/bash
.ONESHELL:
.SILENT:

# -----------------------------
# Project config
# -----------------------------
SRC := src


# -----------------------------
# Help on Makefile
# -----------------------------
help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "; printf "\nAvailable targets:\n"} /^[a-zA-Z0-9_-]+:.*## / { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)



# -----------------------------
# Preparation on DB Ingestion
# -----------------------------
prep-db:  ## Prepare database ingestion data
	@cd scripts && python prep_db_ingestion.py


# -----------------------------
#  DVC File to improve the Data
# -----------------------------
dvc-ready: ## Import customer churn table with DVC
	@dvc import-db --table "customer_churn" --conn pgsql --output-format csv --verbose -o data/processed/churn_data.csv --force


# -----------------------------
#  Install dependencies
# -----------------------------
install: ## Install dependencies
	@uv sync --all-groups


# -----------------------------
# Up and Run the Containers
# -----------------------------
compose-local-up:  ## Start local Docker Compose stack
	@docker compose -f compose.local.yaml up -d


# -----------------------------
# Clean the Containers
# -----------------------------
compose-local-down: ## Stop services and remove volumes
	@docker compose -f compose.local.yaml down
	@docker volume rm mlchurn_minio_data mlchurn_postgres_data mlchurn_grafana_data


# -----------------------------
#  Clean the Local files
# -----------------------------
clean: ## Remove caches and generated artifacts
	@find . -type d \( -name "__pycache__" -o -name "outputs" -o -name ".ruff_cache" -o -name "multirun"  -o -name "logs" -o -name "logs" -o -name "mlruns" \) -exec rm -rf {} +
	@rm train.log hparam.log test.log || true


# -----------------------------
# Quality gates (production pattern)
# -----------------------------
lint: ## Format code with black and ruff
	@ruff check $(SRC) --fix