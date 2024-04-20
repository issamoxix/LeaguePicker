from typing import Union
from websockets.sync.client import connect
import ssl
from .constants import WEBSOCKET_MESSAGE


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
                    print(f"Received: {message.split('"gameStatus":')[1].split(',')[0]}")
                except Exception as e:
                    pass
                    print("Error: ", e)
