import json
from fastapi import WebSocket
from ..socket.connection import ConnectionManager
from ..redis.producer import Producer
from ..redis.stream import StreamConsumer

async def message_await(websocket: WebSocket, token: str, producer: Producer):
    while True:
            data = await websocket.receive_text()
            stream_data = {}
            stream_data[str(token)] = str(data)
            await producer.add_to_stream(stream_data, "message_channel")


async def response_await(websocket: WebSocket, token: str, consumer: StreamConsumer, manager: ConnectionManager):
    while True:
            response = await consumer.consume_stream(stream_channel="response_channel", block=0)

            for stream, messages in response:
                for message in messages:
                    response_token = [k.decode('utf-8')
                                      for k, v in message[1].items()][0]

                    if token == response_token:
                        response_message = [v.decode('utf-8')
                                            for k, v in message[1].items()][0]

                        response_message = json.dumps(response_message)

                        await manager.send_personal_message(response_message, websocket)

                    await consumer.delete_message(stream_channel="response_channel", message_id=message[0].decode('utf-8'))
