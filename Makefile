run_obtener_partida_test:
	ENVIRONMENT=test
	python3 tests/populate_db.py
	py.test -s tests/test_obtener_partida.py
	rm db/database_test.sqlite
	unset ENVIRONMENT