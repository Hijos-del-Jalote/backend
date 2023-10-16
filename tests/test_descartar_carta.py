from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from db.models import *
from tests.test_newplayer import random_user
from db.cartas_session import *
from api.router.cartas import *



client = TestClient(app)

crear_templates_cartas()


def test_descartar_carta():
    with db_session:
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4)
        commit()
        jugador = Jugador(nombre="Jugador", Posicion=0, Rol="Infectado", isAlive=True, partida=partida)
        commit()
        lacosa=  Carta(template_carta="La cosa", jugador=jugador, partida=partida)
        carta1 = Carta(template_carta="Lanzallamas", jugador=jugador, partida=partida)
        carta2 = Carta(template_carta="Lanzallamas", jugador=jugador, partida=partida)
        carta3 = Carta(template_carta="Lanzallamas", jugador=jugador, partida=partida)
        commit()
        assert len(jugador.cartas) == 4
        try:
            descartar_carta(carta1.id)  ## tratando de descartar la carta con 4 cartas en la mano
        except HTTPException as e:      ## verifico que no se pueda descartar con 4 cartas en la mano
            assert e.status_code == 400
            assert e.detail == "No se puede descartar con 4 cartas en la mano"
        assert len(jugador.cartas) == 4
        carta4 = Carta(template_carta="Lanzallamas", jugador=jugador, partida=partida)
        infectado1 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
        commit()
        assert len(jugador.cartas) == 6 ##verifico que se creen las cartas
        descartar_carta(carta1.id)
        assert len(jugador.cartas) == 5  ##verifico que se descarte la carta
        assert carta1.descartada == True 
        # Caso carta La Cosa
        try:
            descartar_carta(lacosa.id)  ## tratando de descartar la carta La Cosa
        except HTTPException as e:      ## verifico que no se pueda descartar
            assert e.status_code == 400
            assert e.detail == "No se puede descartar la carta La cosa"
        assert len(jugador.cartas) == 5
        assert lacosa.descartada == False
        try :
            descartar_carta(infectado1.id) ## tratando de descartar la carta Infectado
        except HTTPException as e:        ## verifico que no se pueda descartar
            assert e.status_code == 400
            assert e.detail == "No se puede descartar la carta Infectado"
        infectado2 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
        commit()
        assert len(jugador.cartas) == 6
        descartar_carta(infectado2.id)   ## descarto la carta Infectado una vez que hay mas de 1 carta de infectado
        assert len(jugador.cartas) == 5
        assert infectado2.descartada == True



