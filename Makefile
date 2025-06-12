lint:
	flake8 .
	isort . --skip-glob "*env/*"
	black . --exclude ".*env([\\/]|$)"
	bandit -r .

format:
	isort . --skip-glob "*env/*"
	black . --exclude ".*env([\\/]|$)"