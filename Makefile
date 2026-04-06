lint:
	@python -m flake8 . --count --show-source --statistics

test:
	@pytest tests/ -v

