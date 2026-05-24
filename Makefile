.PHONY: 


compose-local-up:
	@docker compose -f compose.local.yaml up

compose-local-down:
	@docker compose -f compose.local.yaml down


clean:
	@find . -type d \( -name "__pycache__"  -o -name ".ruff_cache" \) -print
	@find . -type d \( -name "__pycache__"  -o -name ".ruff_cache" \) -exec rm -rf {} +