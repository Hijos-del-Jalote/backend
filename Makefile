run_obtener_partida_test:
	ENVIRONMENT=test
	python3 tests/populate_db.py
	py.test -s tests/test_obtener_partida.py
	rm db/database_test.sqlite
	unset ENVIRONMENT

run_robar_carta_test:
	ENVIRONMENT=test
	python3 tests/populate_db.py
	py.test -s tests/test_robar_carta.py
	rm db/database_test.sqlite
	unset ENVIRONMENT