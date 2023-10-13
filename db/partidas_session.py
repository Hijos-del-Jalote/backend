from api.router.schemas import *
from db.models import Partida, Jugador
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

def fin_partida_respond(idPartida: int, winners: list, winning_team: str) -> FinPartidaResponse:
    with db_session:
        
        # por las dudas que haya problema con la db, los vuelvo a obtener
        ganadores = []
        for jugador in winners:    
            ganadores.append(jugador)
        
        if winning_team == "cosos":
            return FinPartidaResponse(isHumanoTeamWinner=False,
                                      winners=sorted(ganadores))
            
        else:
            if winning_team == "humanos":
                
                return FinPartidaResponse(isHumanoTeamWinner=True,
                                      winners=sorted(ganadores))
                
            else:
                raise Exception

