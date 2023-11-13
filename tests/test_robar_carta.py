from fastapi import status
from fastapi.testclient import TestClient
from api.api import app
from db.models import *
from pony.orm import get, db_session, commit
from unittest.mock import AsyncMock, patch
import json
import datetime

client=TestClient(app)

def vaciar_manos(partida: Partida):
    for j in partida.jugadores:
        j.cartas.clear()

def descartar_todo(partida: Partida):
    for c in partida.cartas:
        c.set(descartada=True)


def mazo_is_available(mazo: Set(Carta)) -> bool:
    with db_session:
        mazo_cant = count(mazo.select())
        mazo_discarded_cant = count(mazo.select(lambda carta: carta.descartada == False))
    return mazo_cant == mazo_discarded_cant


def rm_panico_cards(mazo: Set(Carta)):
    with db_session:
        for c in mazo.select():
            if c.template_carta.tipo == Tipo_Carta.panico:
                c.delete()

def test_robo_exitoso(setup_db_before_test):
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()
        
        rm_panico_cards(partida.cartas)
        commit()

        with client.websocket_connect(f"ws://localhost:8000/partidas/{partida.id}/ws/chat?idJugador={jugador.id}") as wschat:
            with patch("db.utils.obtener_tiempo_actual") as mock_time:
                mock_time.return_value = "00:00"
                response = client.put(f'/jugadores/{jugador.id}/robar')

            logmsg = wschat.receive_json()
            assert logmsg == {'event':"chat_msg",'data':{'isLog':True,'player': None,'msg':f'{jugador.nombre} robó una carta','time':"00:00"}}
        
        assert count(jugador.cartas) == 1

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Robo exitoso!"}

def test_mano_llena():
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()
        
        rm_panico_cards(partida.cartas)
        commit()
        
        for i in range(5):
            response = client.put(f'/jugadores/{jugador.id}/robar')

        assert count(jugador.cartas) == 5
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Mano llena!"}


def test_mazo_vacio():
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()
        rm_panico_cards(partida.cartas)
        commit()

        vaciar_manos(partida)
        descartar_todo(partida)
        commit()
        
    with db_session:
        response = client.put(f'/jugadores/{jugador.id}/robar')
        commit()
        jugador = Jugador.get(id=jugador.id)
        assert count(jugador.cartas) == 1

    assert mazo_is_available(partida.cartas)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Robo exitoso!"}