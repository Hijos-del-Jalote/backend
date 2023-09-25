run_get_partidaid_test:
	ENVIRONMENT=test
	pytest tests/test_get_partidaid.py -vv
	rm db/database_test.sqlite
	unset ENVIRONMENT