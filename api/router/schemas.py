from pydantic import BaseModel
from typing import List, Optional, Dict, Union

class PlayerResponse(BaseModel):
    id: int

class PartidaResponse(BaseModel):
    nombre: str
    maxJugadores: int
    minJugadores: int
    inciada: bool
    turnoActual: Optional[int]
    sentido: bool
    jugadores: List[Dict[str, Union[str,int]]]