from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *
from db.models import *
from tests.test_newplayer import random_user
from db.mazo_session import *
from db.cartas_session import *

client = TestClient(app)

def test_cartas_defensa(cleanup_db_after_test):
        jugadores = []
        for j in range(4):
            username = random_user()
            response = client.post(f'jugadores?nombre={username}')
            with db_session:
                jugadores.append(Jugador.get(id = response.json()["id"]))
        partida = random_user()
        host = jugadores[0]
        # creo partida
        response = client.post(f'partidas/?nombrePartida={partida}&idHost={host.id}') 
        with db_session:
            partida = Partida.get(id = response.json()["idPartida"])
        # uno jugadores a partida
        for i in range(1,4):
            client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")
        # inicio  partida
        response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")  
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            templates = list(TemplateCarta.select())
            assert templates[12].nombre == "Aterrador" and templates[12].tipo == Tipo_Carta.defensa and templates[12].descripcion == "Niegate a un ofrecimiento de cambio de carta , mira la carta que te has negado a recibir y roba una carta 'alejate"
            assert templates[13].nombre == "Aqui estoy bien" and templates[13].tipo == Tipo_Carta.defensa and templates[13].descripcion == "cancela una carta 'cambio de lugar' o 'mas vale que corras y roba una carta 'alejate"
            assert templates[14].nombre == "No, gracias" and templates[14].tipo == Tipo_Carta.defensa and templates[14].descripcion == "Niegate a un ofrecimiento de cambio de carta y roba una carta 'alejate"
            assert templates[15].nombre == "Fallaste" and templates[15].tipo == Tipo_Carta.defensa and templates[15].descripcion == """el siguiente jugador despues de ti realiza el intercambio de cartas en tu lugar ,
                             no queda infectado si recibe una carta infectado roba una carta 'alejate'"""
            assert templates[16].nombre == "Nada de barbacoas" and templates[16].tipo == Tipo_Carta.defensa and templates[16].descripcion == "cancela una carta 'lanzallamas' que te tenga como objetivo y roba una carta 'alejate"
            