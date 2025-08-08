setup:
	poetry install --with dev --extras all
	poetry run pre-commit install

generate-badges:
	poetry run pytest --cov=src/ --local-badge-output-dir badges/
