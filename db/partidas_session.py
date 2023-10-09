from api.router.schemas import *
from db.models import Partida
from pony.orm import db_session

def get_partida(id: int) -> PartidaResponse:
    with db_session:
        partida = Partida.get(id=id)

        jugadores_list = sorted([{"id": j.id,
                                  "nombre": j.nombre,
                                  "posicion": j.Posicion,
                                  "isAlive": j.isAlive} for j in partida.jugadores], key=lambda j: j['id'])
        
        partidaResp = PartidaResponse(nombre=partida.nombre,
                                      maxJugadores=partida.maxJug,
                                      minJugadores=partida.minJug,
                                      iniciada=partida.iniciada,
                                      turnoActual=partida.turnoActual,
                                      sentido=partida.sentido,
                                      jugadores=jugadores_list)

    return partidaResp

def fin_partida_respond(idPartida: int) -> FinPartidaResponse:
    with db_session:
        jugadores = partida.jugadores
        humanos = []
        cosos = []
        isLacosaAlive = false
        for jugador in jugadores:
            if jugador.Rol == "humano":
                humanos.append(jugador.id)
            if jugador.Rol == "lacosa" and jugador.isAlive:
                isLacosaAlive = True
            if jugador.Rol == "lacosa" or jugador.Rol == "infectado":
                cosos.append(jugador.id)

    if len(humanos) == 0 and isLacosaAlive: # gana la cosa y su team
        return FinPartidaResponse(finalizada=True,
                                  isHumanoTeamWinner=False,
                                  winners=sorted(cosos))
    else:
        if (not isLacosaAlive) and len(humanos) > 0: # ganan los humanos
            return FinPartidaResponse(finalizada=True,
                                      isHumanoTeamWinner=False,
                                      winners=sorted(humanos))
        else: # no termino la partida
            return FinPartidaResponse(finalizada=False)
