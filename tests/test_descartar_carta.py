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


def test_descartar_carta(cleanup_db_after_test):
    with db_session:
        crear_templates_cartas()
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
        
        ## trato de descartar con 4 cartas
        response= client.put(f'cartas/descartar_carta/{carta1.id}')
        assert response.status_code == 400  ##verifico que no se descarte la carta con 4 cartas en la mano
        assert len(jugador.cartas) == 4
        assert carta1.descartada == False
        
        ## trato de descartar la carta infectado si solo tengo 1 carta infectado
        infectado1 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
        commit()
        assert len(jugador.cartas) == 5   
        response= client.put(f'cartas/descartar_carta/{infectado1.id}') 
        assert response.status_code == 400
        assert len(jugador.cartas) == 5
        assert infectado1.descartada == False  ## verifico que no se descarte la carta infectado
        
        #trato de descartar la cosa
        response= client.put(f'cartas/descartar_carta/{lacosa.id}')
        assert response.status_code == 400
        assert len(jugador.cartas) == 5
        assert lacosa.descartada == False
        
        #descarto una carta cualquiera
    with db_session:                                   
        response= client.put(f'cartas/descartar_carta/{carta1.id}')
        assert response.status_code == 200
        jugador = Jugador.get(id=jugador.id)
        carta1 = Carta.get(id=carta1.id)
        assert len(jugador.cartas) == 4  ##verifico que se descarte la carta
        assert carta1.descartada == True 
        
        #descarto una carta infectado si tengo mas de 1
    with db_session:                        
        jugador = Jugador.get(id=jugador.id)
        partida = Partida.get(id=partida.id)
        infectado2 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
        commit()
        response= client.put(f'cartas/descartar_carta/{infectado2.id}')
        assert response.status_code == 200
    with db_session:                       
        jugador = Jugador.get(id=jugador.id)
        infectado2 = Carta.get(id=infectado2.id)
        assert len(jugador.cartas) == 4  ##verifico que se descarte la carta
        assert infectado2.descartada == True
