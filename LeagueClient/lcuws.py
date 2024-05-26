from typing import Union
from websockets.sync.client import connect
from websockets import exceptions
import ssl
import json
import threading

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
        network_addr = f"{self.host}:{self.port}"
        self.url = f"wss://{self.username}:{self.remote_token}@{network_addr}"
        super().__init__()
        self.stop_event = threading.Event()

    def _handle_message(self, message):
        status = self.check_status(message)
        if status:
            logger.debug(f"Received: {status}")
            self.set_state(status)

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
            try:
                while not self.stop_event.is_set():
                    try:
                        message = websocket.recv()
                        self._handle_message(message)
                    except exceptions.ConnectionClosed as e:
                        logger.error("Connection closed: %s", e)
                        raise e
                    except Exception as e:
                        logger.error("Error: %s", e)
            except KeyboardInterrupt:
                logger.debug("Process interrupted by user")

    def check_status(self, message):
        if message:
            message = json.loads(message)
            message = message[2]
            uri = message.get("uri")
            match uri:
                case self.routes.game_flow.session:
                    return message.get("data").get("phase")
                case self.routes.game_flow.phase:
                    return message.get("data")
                case _:
                    if "/lol-chat/v1/" in message:
                        data = message.get("data", {})
                        if "lol" in data:
                            return data.get("lol").get("gameStatus", None)

                    self.handle_message(uri)
        return False
