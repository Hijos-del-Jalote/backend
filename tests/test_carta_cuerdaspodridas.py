from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from api.router.cartas import *
from db.models import *
from api.ws import *
import asyncio


async def test_jugar_cuerdas_podridas(cleanup_db_after_test):
    client = TestClient(app)
    crear_datos_partida()
    with db_session:
        assert Jugador[2].cuarentena == True          ####Chequeo que esten en cuarentena
        assert Jugador[3].cuarentena == True
    response = client.post(f'cartas/jugar?id_carta=1') 
    assert response.status_code == 200
    with db_session:
        partida=Partida[1]
        for jugador in partida.jugadores:
            assert jugador.cuarentena == False   ####Chequeo que ya no esten en cuarentena
            



def crear_datos_partida():
    with db_session:
        crear_templates_cartas()
        partida = Partida(nombre="partida", iniciada=True, finalizada=False , maxJug=5, minJug=4, turnoActual=1)
        db.commit()
        jugador = Jugador(nombre="Jugador", Rol="Humano", isHost=True, isAlive=True, blockIzq=False, blockDer=False, Posicion=0 , partida=partida)
        jugador2= Jugador(nombre="Jugador2", Rol="Humano", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=1 , 
                          partida=partida , cuarentena=True)
        jugador3= Jugador(nombre="Jugador3", Rol="Humano", isHost=False, isAlive=True, blockIzq=False, blockDer=False, 
                          Posicion=2 , partida=partida , cuarentena=True)
        jugador4= Jugador(nombre="Jugador4", Rol="Humano", isHost=False, isAlive=True, blockIzq=False, blockDer=False, Posicion=3 , partida=partida)
        db.commit()
        Carta(descartada=False, template_carta="Cuerdas podridas", partida=partida, jugador=jugador)
        for i in range(4):
            Carta(descartada=False, template_carta="Lanzallamas" , partida=partida, jugador=jugador)
        db.commit()