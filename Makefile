setup:
	poetry install --with dev --extras all
	poetry run pre-commit install

generate-badges:
	poetry run pytest --cov --local-badge-output-dir badges/
