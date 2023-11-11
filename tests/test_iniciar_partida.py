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

    # creo partida
    response = client.post(f'partidas/?nombrePartida={partida}&idHost={host.id}') 

    with db_session:
        partida = Partida.get(id = response.json()["idPartida"])
    
    
    # uno jugadores a partida
    for i in range(1,4):
        client.post(f"partidas/unir?idPartida={partida.id}&idJugador={jugadores[i].id}")

    iniciar_partida_correcta(partida, host)

 
def iniciar_partida_correcta(partida, host):   
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

@db_session    
def test_partida_ya_iniciada(setup_db_before_test, cleanup_db_after_test):
    # cantidad incorrecta de jugadores
    response = client.put(f"partidas/iniciar/{Partida[1].id}?idJugador={Jugador[1].id}")  
    assert (response.status_code == status.HTTP_400_BAD_REQUEST) & (response.text == '{"detail":"Partida ya iniciada"}')    

@db_session    
def test_cantidad_incorrecta_jugadores(setup_db_before_test, cleanup_db_after_test):
    # cantidad incorrecta de jugadores
    response = client.put(f"partidas/iniciar/{Partida[2].id}?idJugador={Jugador[5].id}")  
    assert (response.status_code == status.HTTP_400_BAD_REQUEST) & (response.text == '{"detail":"Partida no respeta limites jugadores"}')    
    
@db_session
def test_no_host_inicia_partida(setup_db_before_test, cleanup_db_after_test):
    # host no es host
    response = client.put(f"partidas/iniciar/{Partida[1].id}?idJugador={Jugador[2].id}")
    assert (response.status_code == status.HTTP_400_BAD_REQUEST) & (response.text == '{"detail":"El jugador no es el host"}')    

@db_session
def test_iniciar_partida_inextistente(setup_db_before_test, cleanup_db_after_test):  
    response = client.put(f"partidas/iniciar/{2121}?idJugador={Jugador[1].id}")  
    assert (response.status_code == status.HTTP_404_NOT_FOUND) & (response.text == '{"detail":"No existe partida con ese id"}')
