from fastapi import status
from fastapi.testclient import TestClient
from api.api import app
from db.models import *
from pony.orm import get, db_session, commit

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

def test_robo_exitoso():
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()

        response = client.put(f'/jugadores/{jugador.id}/robar')
        assert count(jugador.cartas) == 1

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Robo exitoso!"}

def test_mano_llena():
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()
    
        for i in range(5):
            response = client.put(f'/jugadores/{jugador.id}/robar')

        assert count(jugador.cartas) == 5
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Mano llena!"}


def test_mazo_vacio():
    with db_session:
        partida = Partida[1]
        jugador = select(j for j in partida.jugadores).first()
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