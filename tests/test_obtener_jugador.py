from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session, count
from api.api import app
from db.models import Jugador

client = TestClient(app)

def cargar_mano(jugador: Jugador):
    with db_session:
        partida = jugador.partida
        cartas = partida.cartas
        for c in cartas:
            if(count(jugador.cartas) < 4):
                jugador.cartas.add(c)
            else:
                break


def test_get_jugador_valido():
    with db_session:
        cargar_mano(Jugador[1])

    response = client.get('jugadores/1')
    with db_session:
        lista_cartas = sorted([{
                "id": carta.id,
                "nombre": carta.template_carta.nombre,
                "descripcion": carta.template_carta.descripcion,
                "tipo": carta.template_carta.tipo
            } for carta in Jugador[1].cartas], key=lambda c: c['id'])

        expected_response = {
            'nombre': Jugador[1].nombre,
            'isHost': Jugador[1].isHost,
            'posicion': Jugador[1].Posicion,
            'isAlive': Jugador[1].isAlive,
            'cartas': lista_cartas
        }

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


def test_get_partida_no_valido():
    response = client.get('jugador/1234')
    assert response.status_code == status.HTTP_404_NOT_FOUND