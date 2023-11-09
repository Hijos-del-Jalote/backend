from api.api import app
from fastapi.testclient import TestClient
from pony.orm import db_session
from db.models import Jugador,Partida
from api.ws import manager_chat
from .conftest import *
from db.partidas_session import get_jugadores_partida
import time
from unittest.mock import AsyncMock, patch
import datetime
import json
import asyncio


#{'isLog': isLog,'player': nombre,'msg': msg,'time': tiempo}

async def test_chat(setup_db_before_test):
    client = TestClient(app)
    with db_session:
        Jugador[5].nombre = 'j1'
        Jugador[6].nombre = 'j2'
        Jugador[7].nombre = 'j3'        

            
    datetime_fijo = datetime.datetime(180,3,17,0,0,0,000000)

    with client.websocket_connect("ws://localhost:8000/partidas/2/ws/chat?idJugador=5") as ws1:
        with client.websocket_connect("ws://localhost:8000/partidas/2/ws/chat?idJugador=6") as ws2:
            with client.websocket_connect("ws://localhost:8000/partidas/2/ws/chat?idJugador=7") as ws3: 
                while len(manager_chat.active_connections.get(2,{})) != 3:   
                    time.sleep(0.1)
                with patch("datetime.datetime") as mock_datetime:
                    mock_datetime.now.return_value = datetime_fijo                                
                


                    ws1.send_text("hola")
                    resp = ws2.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j1",'msg':"hola",'time':"00:00"}}
                    resp = ws3.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j1",'msg':"hola",'time':"00:00"}}
                    resp = ws1.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j1",'msg':"hola",'time':"00:00"}}

                    ws2.send_text("Temer se debe sólo a aquellas cosas que pueden causar algún tipo de daño; mas a las otras no, pues mal no hacen.")
                    resp = ws2.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j2",'msg':"Temer se debe sólo a aquellas cosas que pueden causar algún tipo de daño; mas a las otras no, pues mal no hacen.",'time':"00:00"}}
                    resp = ws3.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j2",'msg':"Temer se debe sólo a aquellas cosas que pueden causar algún tipo de daño; mas a las otras no, pues mal no hacen.",'time':"00:00"}}
                    resp = ws1.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j2",'msg':"Temer se debe sólo a aquellas cosas que pueden causar algún tipo de daño; mas a las otras no, pues mal no hacen.",'time':"00:00"}}

                    ws3.send_text("que dice xd")
                    resp = ws2.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j3",'msg':"que dice xd",'time':"00:00"}}
                    resp = ws3.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j3",'msg':"que dice xd",'time':"00:00"}}
                    resp = ws1.receive_text()
                    assert json.loads(resp) == {'event':"chat_msg",'data':{'isLog':False,'player':"j3",'msg':"que dice xd",'time':"00:00"}}

                    ws1.send_text("")
                   
async def test_chat_ep(cleanup_db_after_test):
    client = TestClient(app)

    response = client.get("partidas/2/chat")
    print(response.json())
    assert response.json() == [{'isLog':False,'player':"j1",'msg':"hola",'time':"00:00"},
                               {'isLog':False,'player':"j2",'msg':"Temer se debe sólo a aquellas cosas que pueden causar algún tipo de daño; mas a las otras no, pues mal no hacen.",'time':"00:00"},
                               {'isLog':False,'player':"j3",'msg':"que dice xd",'time':"00:00"}
                               ]