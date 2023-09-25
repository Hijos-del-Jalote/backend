from pydantic import BaseModel
from typing import List, Optional

class PlayerResponse(BaseModel):
    id: int

class PartidaResponse(BaseModel):
    nombre: str
    maxJugadores: int
    minJugadores: int
    inciada: bool
    turnoActual: Optional[int]
    sentido: bool