import os
from fastapi import APIRouter, WebSocket,  Request, Depends, HTTPException, WebSocketDisconnect
from fastapi.responses import FileResponse
import uuid
from rejson import Path
import json

from ..socket.connection import ConnectionManager
from ..socket.utils import get_token

from ..redis.producer import Producer
from ..redis.config import Redis
from ..redis.cache import Cache

from ..schema.chat import Chat

from ..redis.stream import StreamConsumer

chat = APIRouter()
manager = ConnectionManager()
redis = Redis()


# @route   /
# @desc    home
# @access  Public
@chat.get("/")
def homepage():
    return FileResponse('../client/index.html', media_type='text/html')


# @route   POSjs jquery hide and unhide divT /token
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
    json_client = redis.create_rejson_connection()
    consumer = StreamConsumer(redis_client)

    try:
        while True:
            data = await websocket.receive_text()
            print("Websocket data:",data)
            stream_data = {}
            stream_data[str(token)] = str(data)
            await producer.add_to_stream(stream_data, "message_channel")
            response = await consumer.consume_stream(stream_channel="response_channel", count=1, block=0)
            print("stream_data:", stream_data)

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]
                    print("toen:", token)
                    print("resp token:", response_token)
                    if token == response_token:
                        response_message = [v.decode('utf-8')
                                            for k, v in message[1].items()][0]
                        print("Message1 Items:",message[1].items())
                        print("Response Msg:",response_message)
                        response_message = json.dumps(response_message)
                        # response_message = json.loads(response_message)
                        # response_message3 = json.dumps(response_message2)
                        # print(message[0].decode('utf-8'))
                        print("json msg:",response_message )
                        print("str msg:", str(response_message))
                        # print("Json Msg1:", response_message1)
                        # print("Json Msg2:", response_message2)
                        # print("Json Msg3:", response_message3)

                        await manager.send_personal_message(response_message, websocket)

                    await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))

            # await manager.send_personal_message(f"GPT Bot response placeholder", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
