install:
	@pip install -r requirements.txt
init:
	@python -m flask initdb
	@python -m flask createsu >> access.txt
server:
	@python -m flask run --debug
format:
	@python -m black -l 79 .
	@python -m isort .
lint:
	@python -m black -l 79 --check .
	@python -m isort --check .
test:
	# @pytest tests/units/test_hash_generator.py -v
	# @pytest tests/units/test_password_generator.py -v
sec:
	@pip-audit