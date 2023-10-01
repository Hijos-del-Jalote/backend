from fastapi.testclient import TestClient
from fastapi import status
from pony.orm import db_session
from api.api import app
from api.router.partidas import *


client = TestClient(app)


def test_unir_jugador():
    with db_session:
        p = db.Partida(nombre="Partida", maxJug=5, minJug=1, sentido=0, iniciada=True)
        j = db.Jugador(nombre="Diego", isHost=True, isAlive=True, blockIzq=False, blockDer=True)
        db.commit()
        partidas = list(Partida.select().order_by(lambda p: desc(p.id)))
        jugadores = list(Jugador.select().order_by(lambda p: desc(p.id)))
        db.commit()
        ultima_id_partida = partidas[0].id
        ultima_id_jugador = jugadores[0].id

        ambos_existen_response = client.post(f"partidas/unir?idPartida={ultima_id_partida}&idJugador={ultima_id_jugador}")

        assert ambos_existen_response.status_code == 200
        
        no_existe_jugador_response = client.post(f"partidas/unir?idPartida={ultima_id_partida}&idJugador={ultima_id_jugador+1}")

        assert no_existe_jugador_response.status_code == 400

        no_existe_partida_response = client.post(f"partidas/unir?idPartida={ultima_id_partida+1}&idJugador={ultima_id_jugador}")

        assert no_existe_partida_response.status_code == 400
        
        j.partida = p
        db.commit()
        
        jugador_en_partida = client.post(f"partidas/unir?idPartida={p.id}&idJugador={j.id}")
       
        assert jugador_en_partida.status_code == 400
