.PHONY: prep-db compose-local-up dvc-ready compose-local-down clean

prep-db:
	@cd scripts && python prep_db_ingestion.py

compose-local-up:
	@docker compose -f compose.local.yaml up

dvc-ready:
	@dvc import-db --table "customer_churn" --conn pgsql --output-format csv --verbose -o data/processed/churn_data.csv --force

compose-local-down:
	@docker compose -f compose.local.yaml down


clean:
	@find . -type d \( -name "__pycache__"  -o -name ".ruff_cache" \) -print
	@find . -type d \( -name "__pycache__" -o -name "outputs" -o -name ".ruff_cache" -o -name "multirun"  -o -name "logs" -o -name "logs" -o -name "mlruns" \) -exec rm -rf {} +