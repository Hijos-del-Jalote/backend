from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from db.models import Partida

client = TestClient(app)


def test_get_partida_valid():
    response = client.get('partidas/1')
    with db_session:
        expected_response = {
            'nombre': Partida[1].nombre,
            'maxJugadores': Partida[1].maxJug,
            'minJugadores': Partida[1].minJug,
            'iniciada': Partida[1].iniciada,
            'turnoActual': Partida[1].turnoActual,
            'sentido': Partida[1].sentido,
            'jugadores': [{'id': j.id, 'nombre': j.nombre} for j in Partida[1].jugadores]
        }
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


def test_get_partida_invalid():
    response = client.get('partidas/154589')
    assert response.status_code == status.HTTP_404_NOT_FOUND