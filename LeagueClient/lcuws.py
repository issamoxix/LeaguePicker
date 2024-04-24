from typing import Union
from websockets.sync.client import connect
from websockets import exceptions
import ssl
import json

from LeagueClient.events import HandleEvents
from .constants import WEBSOCKET_MESSAGE
from .utils.log import logger


class LcuWebsocket(HandleEvents):

    remote_token: Union[str, None] = None
    host: str = "127.0.0.1"
    port: Union[int, None] = None
    username: str = "riot"
    headers: Union[dict, None] = None

    def __init__(self) -> None:
        self.url = f"wss://{self.username}:{self.remote_token}@{self.host}:{self.port}"
        super().__init__()

    def ws_connect(self):
        ssl_context = ssl.SSLContext()
        ssl_context.verify_mode = ssl.CERT_NONE
        with connect(
            self.url,
            additional_headers=self.headers,
            ssl_context=ssl_context,
            max_size=2**30,
        ) as websocket:
            websocket.send(WEBSOCKET_MESSAGE)
            while True:
                try:
                    message = websocket.recv()
                    status = self.check_status(message)
                    if status:
                        logger.debug(f"Received: {status}")
                        self.set_state(status)

                except Exception as e:
                    logger.error("Error; ", e)
                    if isinstance(e, exceptions.ConnectionClosed):
                        raise e

    def check_status(self, message):
        if message:
            message = json.loads(message)
            message = message[2]
            uri = message.get("uri")
            match uri:
                case "/lol-gameflow/v1/session":
                    return message.get("data").get("phase")
                case "/lol-gameflow/v1/gameflow-phase":
                    return message.get("data")
                case _:
                    if "/lol-chat/v1/" in message:
                        if message.get("data", None) and message.get("data", {}).get("lol"):
                            return message.get("data").get("lol").get("gameStatus", None)
                    
                    self.handle_message(uri)
        return False
