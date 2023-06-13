import os
from fastapi import APIRouter, WebSocket,  Request, Depends, HTTPException, WebSocketDisconnect
from fastapi.responses import FileResponse
import uuid
from rejson import Path
import asyncio

from ..socket.connection import ConnectionManager
from ..socket.utils import get_token

from ..redis.producer import Producer
from ..redis.config import Redis
from ..redis.cache import Cache
from ..redis.stream import StreamConsumer

from ..schema.chat import Chat

from . import utils


chat = APIRouter()
manager = ConnectionManager()
redis = Redis()


# @route   /
# @desc    home
# @access  Public
@chat.get("/")
async def homepage():
    return FileResponse('../client/index.html', media_type='text/html')


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

    # Create new chat session
    json_client = redis.create_rejson_connection()

    chat_session = Chat(
        token=token,
        messages=[],
        name=name )

    # Store chat session in redis JSON with the token as key
    json_client.jsonset(str(token), Path.rootPath(), chat_session.dict())

    # Set a timeout for redis data
    redis_client = await redis.create_connection()
    await redis_client.expire(str(token), 3600)

    return chat_session.dict()


# @route   POST /refresh_token
# @desc    Route to refresh token
# @access  Public

@chat.post("/refresh_token")
async def refresh_token(request: Request, token: str):
    json_client = redis.create_rejson_connection()
    cache = Cache(json_client)
    data = await cache.get_chat_history(token)

    if data == None:
        raise HTTPException(
            status_code=400, detail="Session expired or does not exist")
    else:
        return data

# @route   Websocket /chat
# @desc    Socket for chatbot
# @access  Public

@chat.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(get_token)):
    await manager.connect(websocket)
    redis_client = await redis.create_connection()
    producer = Producer(redis_client)
    # json_client = redis.create_rejson_connection()
    consumer = StreamConsumer(redis_client)

    try:
        # Run two coroutines concurrently. One awaits for user messages on websocket. Other awaits for bot responses on resonse channel.
        await asyncio.gather(utils.message_await(websocket, token, producer), 
                             utils.response_await(websocket, token, consumer, manager))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


