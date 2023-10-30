from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import PartidaIn, PartidaOut

from db.models import Partida, db, Jugador, Rol

from tests.test_newplayer import random_user

client = TestClient(app)


def test_iniciar_partida(cleanup_db_after_test):
    # parte parecida a test_newplayer pero necesito el idHost

    jugadores = []
    for i in range(4):
        username = random_user()
        response = client.post(f'jugadores?nombre={username}')
        with db_session:
            jugadores.append(Jugador.get(id = response.json()["id"]))
    partida = random_user()
    host = jugadores[0]
    db.commit()
    
    response = client.put(f"partidas/iniciar/{2121}?idJugador={host.id}")  
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # creo partida
    response = client.post(f'partidas/?nombrePartida={partida}&idHost={host.id}') 

    with db_session:
        partida = Partida.get(id = response.json()["idPartida"])
    # host no es host
    response = client.put(f"partidas/iniciar/{partida.id}?idJugador={jugadores[1].id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    # cantidad incorrecta de jugadores
    response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")  
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # uno jugadores a partida
    for i in range(1,4):
        client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")
    
    # partida correcta
    response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")  
    assert response.status_code == status.HTTP_200_OK
    
    # verifico que se haya iniciado
    with db_session:
        partida = Partida.get(id = partida.id)
        jugadores = list(partida.jugadores)
    assert partida.iniciada == True

    # verifico que tengan posicion , rol por defecto y el resto de atributos en default
    posiciones = set()
    cant_cosas = 0
    for jugador in jugadores:
        assert jugador.Posicion not in posiciones
        posiciones.add(jugador.Posicion)
        assert jugador.Rol == "Humano" or jugador.Rol == "La cosa"
        assert jugador.isAlive == True
        assert jugador.blockDer == False
        assert jugador.blockIzq == False
        assert jugador.cuarentena == False
        if jugador.Rol == "La cosa":
            cant_cosas += 1

    assert cant_cosas == 1
    
    # partida ya iniciada
    response = client.put(f"partidas/iniciar/{partida.id}?idJugador={host.id}")  
    assert response.status_code == status.HTTP_400_BAD_REQUEST

