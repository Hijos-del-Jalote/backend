import pytest
from pony.orm import count, db_session
from ..db.session import Session
from ..db.models import Partida,Jugador,Carta

@pytest.fixture
def session():
    return Session()

@pytest.mark.integration_test
def test_crear_partida(session: Session):
    with db_session:
        cant_partidas = count(Partida.select())

    session.crear_partida(50, "partida_prueba", "secreto",
                        12, 4)
    
    with db_session:
        assert count(Partida.select()) == cant_partidas + 1

@pytest.mark.integration_test
@db_session
def test_get_partidas(session: Session):
    partidas = session.get_partidas()
    assert len(partidas) == count(Partida.select())

def test_get_partida(session: Session):
    session.crear_partida(51, "partida_prueba", "secreto",
                        12, 4)
    partida = session.get_partida(51)
    partida_esperada = {
        "id": 51,
        "nombre": "partida_prueba",
        "password": "secreto",
        "maxJug": 12,
        "minJug": 4,
        "sentido": True,
        "iniciada": False,
        "jugadors": {},
        "cartas": {} 
    }
    assert partida == partida_esperada