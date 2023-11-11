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


def populate_db():
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
        return partida, jugador, lacosa, carta1, carta2, carta3
        
def test_descartar_carta(cleanup_db_after_test):
    with db_session:
        partida, jugador, lacosa, carta1, carta2, carta3 = populate_db()
        
        descartar_4_cartas(carta1, jugador)
        
        descartar_infectado(jugador, partida)
        
        descartar_la_cosa(lacosa, jugador)
        

    with db_session:                                   
        descartar_random(carta1, jugador)
        
        
    with db_session:                        
        infectado2 = descartar_infectado_mas_1(jugador, partida)
    with db_session:                       
        jugador = Jugador.get(id=jugador.id)
        infectado2 = Carta.get(id=infectado2.id)
        assert len(jugador.cartas) == 4  ##verifico que se descarte la carta
        assert infectado2.descartada == True

def descartar_infectado_mas_1(jugador, partida):
    #descarto una carta infectado si tengo mas de 1
    jugador = Jugador.get(id=jugador.id)
    partida = Partida.get(id=partida.id)
    infectado2 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
    commit()
    response= client.put(f'cartas/descartar_carta/{infectado2.id}')
    assert response.status_code == 200
    return infectado2 
    
def descartar_random(carta1, jugador):
        #descarto una carta cualquiera
    response= client.put(f'cartas/descartar_carta/{carta1.id}')
    assert response.status_code == 200
    jugador = Jugador.get(id=jugador.id)
    carta1 = Carta.get(id=carta1.id)
    assert len(jugador.cartas) == 4  ##verifico que se descarte la carta
    assert carta1.descartada == True 

def descartar_la_cosa(lacosa, jugador):
    #trato de descartar la cosa
    response= client.put(f'cartas/descartar_carta/{lacosa.id}')
    assert response.status_code == 400
    assert len(jugador.cartas) == 5
    assert lacosa.descartada == False

def descartar_infectado(jugador, partida):
    ## trato de descartar la carta infectado si solo tengo 1 carta infectado
    infectado1 = Carta(template_carta="Infectado", jugador=jugador, partida=partida)
    commit()
    assert len(jugador.cartas) == 5   
    response= client.put(f'cartas/descartar_carta/{infectado1.id}') 
    assert response.status_code == 400
    assert len(jugador.cartas) == 5
    assert infectado1.descartada == False  ## verifico que no se descarte la carta infectado
   
def descartar_4_cartas(carta1, jugador):
    ## trato de descartar con 4 cartas
    response= client.put(f'cartas/descartar_carta/{carta1.id}')
    assert response.status_code == 400  ##verifico que no se descarte la carta con 4 cartas en la mano
    assert len(jugador.cartas) == 4
    assert carta1.descartada == False
