#from pony.orm import Database, Required

#from settings import DATABASE_FILENAME

# Configuración de la base de datos
# db = Database()

from enum import Enum
from pydantic import BaseModel
from uuid import UUID,uuid4
from typing import Optional
# Define la entidad Product
class Ocupation(str, Enum):
    student = "student"
    worker = "worker"

class User(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    ocupation: Ocupation
    #roles: List[Role]

class Jugador(BaseModel):
    


# Conecta a la base de datos SQLite en el archivo 'database.sqlite'
# db.bind(provider='sqlite', filename=DATABASE_FILENAME, create_db=True)

# Genera las tablas en la base de datos
# db.generate_mapping(create_tables=True)