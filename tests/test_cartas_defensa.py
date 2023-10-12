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

def test_cartas_defensa():
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
        response = client.put(f"partidas/iniciar?idPartida={partida.id}")
        # verifico que haya la cant de cartas correcta
        with db_session:
            partida = Partida.get(id = partida.id)
            templates = list(TemplateCarta.select())
            assert templates[12].nombre == "Aterrador" and templates[12].tipo == Tipo_Carta.defensa and templates[12].descripcion == "Niegate a un ofrecimiento de cambio de carta , mira la carta que te has negado a recibir y roba una carta 'alejate"
            assert templates[13].nombre == "Aqui estoy bien" and templates[13].tipo == Tipo_Carta.defensa and templates[13].descripcion == "cancela una carta 'cambio de lugar' o 'mas vale que corras y roba una carta 'alejate"
            assert templates[14].nombre == "No, gracias" and templates[14].tipo == Tipo_Carta.defensa and templates[14].descripcion == "Niegate a un ofrecimiento de cambio de carta y roba una carta 'alejate"
            assert templates[15].nombre == "Fallaste" and templates[15].tipo == Tipo_Carta.defensa and templates[15].descripcion == "el siguiente jugador despues de ti realiza el intercambio de cartas en tu lugar , no queda infectado si recibe una carta infectado roba una carta 'alejate'"
            assert templates[16].nombre == "Nada de barbacoas" and templates[16].tipo == Tipo_Carta.defensa and templates[16].descripcion == "cancela una carta 'lanzallamas' que te tenga como objetivo y roba una carta 'alejate"
            assert templates[17].nombre == "Puerta atrancada" and templates[17].tipo == Tipo_Carta.obstaculo and templates[17].descripcion == "Coloca esta carta entre un jugador adyacente y tu , no se permiten acciones entre este jugador y tu"
            assert templates[18].nombre == "Cuarentena" and templates[18].tipo == Tipo_Carta.obstaculo and templates[18].descripcion == "C"
            assert templates[19].nombre == "Revelaciones" and templates[19].tipo == Tipo_Carta.panico and templates[19].descripcion == "o"
            assert templates[20].nombre == "Sal de aqui" and templates[20].tipo == Tipo_Carta.panico and templates[20].descripcion == "o"
            assert templates[21].nombre == "Olvidadizo" and templates[21].tipo == Tipo_Carta.panico and templates[21].descripcion == "o"
            assert templates[22].nombre == "Cuerdas podridas" and templates[22].tipo == Tipo_Carta.panico and templates[22].descripcion == "o"
            assert templates[23].nombre == "Uno, dos" and templates[23].tipo == Tipo_Carta.panico and templates[23].descripcion == "o"
            assert templates[24].nombre == "Tres, cuatro" and templates[24].tipo == Tipo_Carta.panico and templates[24].descripcion == "o"
            assert templates[25].nombre == "Es aqui la fiesta?" and templates[25].tipo == Tipo_Carta.panico and templates[25].descripcion == "o"
            assert templates[26].nombre == "Que quede entre nosotros" and templates[26].tipo == Tipo_Carta.panico and templates[26].descripcion == "o"
            assert templates[27].nombre == "Vuelta y vuelta" and templates[27].tipo == Tipo_Carta.panico and templates[27].descripcion == "o"
            assert templates[28].nombre == "No podemos ser amigos?" and templates[28].tipo == Tipo_Carta.panico and templates[28].descripcion == "o"
            assert templates[29].nombre == "Cita a ciegas" and templates[29].tipo == Tipo_Carta.panico and templates[29].descripcion == "o"
            assert templates[30].nombre == "Ups" and templates[30].tipo == Tipo_Carta.panico and templates[30].descripcion == "o"