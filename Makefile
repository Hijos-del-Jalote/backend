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

run_obtener_jugador_test:
	ENVIRONMENT=test
	python3 tests/populate_db.py
	py.test -s tests/test_obtener_jugador.py
	rm db/database_test.sqlite
	unset ENVIRONMENT

run_all_tests:
	pytest tests/test_newplayer.py
	rm db/database_test.sqlite
	pytest tests/test_crear_partida.py
	rm db/database_test.sqlite
	pytest tests/test_unir_jugador.py
	rm db/database_test.sqlite
	pytest tests/test_iniciar_partida.py
	rm db/database_test.sqlite
	pytest tests/test_crear_mazo.py
	rm db/database_test.sqlite
	pytest tests/test_repartir_cartas.py
	rm db/database_test.sqlite
	pytest tests/test_jugar_carta.py
	rm db/database_test.sqlite
	pytest tests/test_efecto_lanzallamas.py
	rm db/database_test.sqlite
	pytest tests/test_efecto_infeccion.py
	rm db/database_test.sqlite
	pytest tests/test_finalizar_partida.py
	rm db/database_test.sqlite
	pytest tests/test_efecto_vigila_tus_espaldas.py
	rm db/database_test.sqlite
	pytest tests/test_efecto_cambio_de_lugar.py
  rm db/database_test.sqlite
	pytest tests/test_cartas_accion.py
	rm db/database_test.sqlite
	pytest tests/test_cartas_defensa.py
	rm db/database_test.sqlite
	make run_obtener_partida_test
	make run_robar_carta_test
	make run_obtener_jugador_test
	pytest tests/test_ws.py
	rm db/database_test.sqlite
