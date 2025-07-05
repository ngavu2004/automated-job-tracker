lint:
	flake8 .
	isort . --skip-glob "*env/*"
	black . --exclude ".*env([\\/])|migrations"
	bandit -r .

format:
	isort . --skip-glob "*env/*"
	black . --exclude ".*env([\\/])|migrations"