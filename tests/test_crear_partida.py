from fastapi.testclient import TestClient
from fastapi import status

from ..api.api import app
from ..api.router.partidas import PartidaIn, PartidaOut


client = TestClient(app)


def test_crear_partida():

    partidaCorrecta = {"nombrePartida": "partidaDePrueba"}

    response = client.post("/partidas/", json=partidaCorrecta)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() != {
        'id': None
        }
    
    partidaSinNombre = {"nombrePartida": ""}

    response = client.post("/partidas/", json=partidaIncorrecta)

    assert response.status_code == status.HTTP_400_BAD_REQUEST