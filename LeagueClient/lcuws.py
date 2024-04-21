from typing import Union
from websockets.sync.client import connect
from websockets import exceptions

import ssl
from .constants import WEBSOCKET_MESSAGE
import json
from .utils.log import logger


class LcuWebsocket:

    remote_token: Union[str, None] = None
    host: str = "127.0.0.1"
    port: Union[int, None] = None
    username: str = "riot"
    headers: Union[dict, None] = None

    def __init__(self, port, remote_token, headers) -> None:
        self.port = port
        self.remote_token = remote_token
        self.headers = headers
        self.url = f"wss://{self.username}:{self.remote_token}@{self.host}:{self.port}"


    def ws_connect(self, set_state):
      
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        with connect(
            self.url,
            additional_headers=self.headers,
            ssl_context=ssl_context,
            max_size=2**30
        ) as websocket:
            websocket.send(WEBSOCKET_MESSAGE)
            while True:
                try:
                    message = websocket.recv()
                    s = self.check_status(message)
                    if s:
                        logger.debug(f"Received: {s}")
                        set_state(s)

                except Exception as e:
                    logger.error("Error; ",e)
                    if isinstance(e, exceptions.ConnectionClosed):
                        raise e

    def check_status(self, message):
        if "/lol-gameflow/v1/gameflow-phase" in message:
            message = json.loads(message)
            message = message[2]
            if "ReadyCheck" == message.get("data"):
                return "ReadyCheck"
            elif "Matchmaking" == message.get("data"):
                return "Matchmaking"
            else:
                return message.get("data")
            
        elif "/lol-chat/v1/" in message:
            message = json.loads(message)
            message = message[2]
            if message.get("data", None):
                if message.get("data").get("lol", None):
                    return message.get("data").get("lol").get("gameStatus", None) 
        return False
