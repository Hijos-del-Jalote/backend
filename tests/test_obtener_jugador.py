from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from db.models import Jugador

client = TestClient(app)


def test_get_jugador_valido():
    response = client.get('jugadores/1')
    with db_session:

        lista_cartas = []
        for carta in Jugador[1].cartas:
            dict_carta = {
                "id": carta.id,
                "nombre": carta.template_carta.nombre,
                "descripcion": carta.template_carta.descripcion,
                "tipo": carta.template_carta.tipo
            }
            lista_cartas.append(dict_carta)

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