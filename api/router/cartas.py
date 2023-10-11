from fastapi import APIRouter, HTTPException
from pony.orm import db_session
from db.models import *
from . import efectos_cartas




cartas_router = APIRouter()

@cartas_router.post("/jugar", status_code=200)
async def jugar_carta(id_carta:int, id_objetivo:int | None = None):
    with db_session:
        carta = Carta.get(id=id_carta)
        if carta and carta.jugador:
            if carta.partida.turnoActual != carta.jugador.Posicion : raise HTTPException(status_code=400, detail="No es el turno del jugador que tiene esta carta") 

            partida = carta.partida
            
            match carta.template_carta.nombre: 
            
                case "Lanzallamas":
                    efectos_cartas.efecto_lanzallamas(id_objetivo)
                case "Vigila tus espaldas":
                    efectos_cartas.vigila_tus_espaldas(partida)
                case "Cambio de lugar":
                    efectos_cartas.cambio_de_lugar(carta.jugador, Jugador[id_objetivo])
                case "Mas vale que corras":
                    efectos_cartas.mas_vale_que_corras(carta.jugador, Jugador[id_objetivo])
                    
            carta.jugador.cartas.remove(carta)
            carta.descartada=True
                
            if partida.sentido:
                for i in range(1, len(partida.jugadores)):
                    pos = (partida.turnoActual+i) % len(partida.jugadores)
                    if Jugador.get(Posicion=pos, partida=partida).isAlive:
                        partida.turnoActual = pos
                        break
            else:
                for i in range(1, len(partida.jugadores)):
                    pos = (partida.turnoActual-i) % len(partida.jugadores)
                    if Jugador.get(Posicion=pos, partida=partida).isAlive:
                        partida.turnoActual = pos
                        break

        else:
            raise HTTPException(status_code=400, detail="No existe el id de la carta ó jugador que la tenga")

