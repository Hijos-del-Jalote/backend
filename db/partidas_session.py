from api.router.schemas import *
from db.models import Partida
from pony.orm import db_session

@db_session
def get_jugadores_partida(idPartida: int):
    with db_session:
        partida = Partida.get(id=idPartida)

        jugadores_list = sorted([{"id": j.id,
                                  "nombre": j.nombre,
                                  "posicion": j.Posicion,
                                  "isAlive": j.isAlive} for j in partida.jugadores], key=lambda j: j['id'])
    return jugadores_list

@db_session
def get_partida(id: int) -> PartidaResponse:
    with db_session:
        partida = Partida.get(id=id)

        jugadores_list = get_jugadores_partida(id)
        
        partidaResp = PartidaResponse(nombre=partida.nombre,
                                      maxJugadores=partida.maxJug,
                                      minJugadores=partida.minJug,
                                      iniciada=partida.iniciada,
                                      turnoActual=partida.turnoActual,
                                      sentido=partida.sentido,
                                      jugadores=jugadores_list)

    return partidaResp