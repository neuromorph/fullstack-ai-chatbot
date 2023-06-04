import os
from fastapi import APIRouter, WebSocket,  Request, Depends, HTTPException, WebSocketDisconnect
import uuid
from ..socket.connection import ConnectionManager
from ..socket.utils import get_token

chat = APIRouter()

manager = ConnectionManager()

# @route   POST /token
# @desc    Route to generate chat token
# @access  Public

@chat.post("/token")
async def token_generator(name: str, request: Request):
    if name == "":
        raise HTTPException(status_code=400, detail={
            "loc": "name", "msg": "Enter a valid name"
        })
    token = str(uuid.uuid4())
    data = {"name": name, "token": token}

    return data

# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public

@chat.post("/refresh_token")
async def refresh_token(request: Request):
    return None

# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            await manager.send_personal_message(f"GPT Bot response placeholder", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
