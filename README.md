# backend

Información para compilación, datos por ahora de lo que vamos aprendiendo, etc.
Para esta primera parte, se uso el codigo de Chun (https://github.com/matiaslee/testing_talk/tree/main), 
(https://www.youtube.com/watch?v=GN6ICac3OXY) y este video. Capaz que algo de lo puesto aca esta mal asi que por las dudas se recomienda mirar ese material.


Instalar uvicorn y fastapi
```
    - sudo apt install uvicorn
    - pip3 install fastapi
```
Luego, en juego.py va a estar la logica principal.


## juego.py
```
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"Hello": "World"}
```
Esto define la app principal y los metodos de HTTP (?). El primer metodo definido es bastante simple, es un GET que simplemente imprimer Hello World. 

IMPORTANTE: Para usar la aplicacion:
```
    uvicorn juego:app --reload
// juego es el nombre del modulo, app no se (quiza la variable?, o es algo de fastapi)
    localhost:8000
// en el browser como si fuera una URL
```

## models.py
models.py supongo que va a tener definidas las clases. A continuacion un ejemplo que usa Listas, algo opcional, tipo Enum, tipo referenciando a clase, etc. Hay muchos imports.

```
class Ocupation(str, Enum):
    student = "student"
    worker = "worker"

class User(BaseModel):
    id: Optional[UUID] = uuid4()
    first_name: str
    ocupation: Ocupation
    roles: List[Role]
```

Luego, en juego.py despues de app = FastAPI():
```
db: List[User] = [
    User(
        id=uuid4(),
        first_name = "Pedro",
        ocupation = Ocupation.student),
    User(
        id=uuid4(),
        first_name = "Laura",
        ocupation = Ocupation.student),
]
```
Basicamente, crea instancias de esa clase.

Aqui otro get pero que obtiene los usuarios y los imprime.
```
@app.get("/api/v1/users")
async def fetch_users():
    return db;
```
```
localhost:8000/api/v1/users en el browser
```
Uno para agregar usuarios:
```
@app.post("/api/v1/users")
async def register_user(user: User):
    db.append(user)
    return {"id": user.id}
```
Y uno para borrarlos:
```
@app.delete("/api/v1/users/{user_id}")
async def delete_user(user_id: UUID):
    for user in db
        if user.id == user_id
            db.remove(user)
    return {"id": user.id}
```

Para toda esta parte de HTTP es importante ver los metodos (GET,POST, etc.) y los codigos de errores. Ademas usar excepciones, try, catch, etc.

Estan los dos archivos (juego.py y models.py) con todo lo detallado aca + los imports.
