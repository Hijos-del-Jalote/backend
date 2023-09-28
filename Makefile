run_get_partidaid_test:
	ENVIRONMENT=test
	python3 tests/populate_db.py
	pytest tests/test_get_partidaid.py -vv
	rm db/database_test.sqlite
	unset ENVIRONMENT