import wmi
import os
import base64
import requests
from time import sleep
from typing import Optional
import threading
import pythoncom

from .options import Options
from .lcuws import LcuWebsocket
from .utils.log import with_try_except, logger
from .utils.functions import handle_request
from .constants import PROCESS_NAME
from .exceptions import LeagueClientClosed
from .routes.lol_matchmaking import Endpoints


class LeagueClient(Options, LcuWebsocket):
    league_dir: Optional[str]
    league_auth: Optional[str]
    lcu_url: str = "https://127.0.0.1"
    port: Optional[int]
    linked: bool = False
    protocol: str = "https"
    password: str
    _remote_token: Optional[str] = None
    wait_client: bool = True

    def __init__(
        self,
        league_dir: Optional[str] = None,
        log_level: str = "INFO",
        live: bool = True,
    ):
        logger.setLevel(log_level)
        logger.debug("Initializing LeagueClient")

        self.routes = Endpoints()
        self.league_dir = league_dir
        while not self.is_client_open():
            logger.info("Waiting for Client")
            if not self.wait_client:
                raise LeagueClientClosed
            sleep(self.client_checker_sleep)

        self.passowrd = self._get_password()
        self.league_auth = self._handle_password()

        self.full_url = f"{self.lcu_url}:{self.port}"
        self.headers = {
            "Authorization": f"Basic {self.league_auth}",
            "Accept": "application/json",
        }

        self.linked = self.ClientIsOpen()
        self.live = live

    def __enter__(self):
        if self.live:
            LcuWebsocket.__init__(self)
            self.ws_thread = threading.Thread(target=self.ws_connect)
            self.ws_thread.start()
        return self

    def is_client_open(self):
        if self.league_dir:
            lockfile_path = os.path.join(self.league_dir, "lockfile")
            lockfile_exists = os.path.exists(lockfile_path)
            if lockfile_exists:
                self.cmd_args_thread = self._get_cmd_args_thread()
            return lockfile_exists
        else:
            return self._get_cmd_args()

    def _get_cmd_args(self):
        logger.debug("Getting command line arguments")
        pythoncom.CoInitialize()

        c = wmi.WMI()
        for process in c.Win32_Process():
            if process.name == PROCESS_NAME:
                cmd = process.CommandLine
                segments = cmd.split('" "')
                self._parse_segments(segments)
                break
        else:
            return False
        return True

    def _parse_segments(self, segments):
        for segment in segments:
            if "--app-port" in segment:
                self.port = int(segment.split("=")[1])
            if "--install-directory" in segment:
                self.league_dir = segment.split("=")[1]
            if "--remoting-auth-token" in segment:
                self._remote_token = segment.split("=")[1]

    def _get_cmd_args_thread(self):
        thread = threading.Thread(target=self._get_cmd_args)
        thread.start()
        return thread

    def _read_lockfile(self):
        logger.debug("Reading lockfile")
        if not self.league_dir:
            raise LeagueClientClosed
        lockfile_path = os.path.join(self.league_dir, "lockfile")

        if not os.path.exists(lockfile_path):
            raise LeagueClientClosed

        with open(lockfile_path, "r") as lockfile:
            content = lockfile.read()

        return content.split(":")

    def _get_password(self):
        logger.debug("Getting password from lockfile")
        _, _, port, password, protocol = self._read_lockfile()
        self.protocol = protocol
        self.password = password
        self.port = port
        return password

    def _handle_password(self):
        logger.debug("Handling password")
        return base64.b64encode(f"riot:{self.password}".encode()).decode()

    @property
    def summoner(self):
        current_summoner = self.routes.summoner.current_summoner
        return self.get(current_summoner, r_type="json")

    @property
    def remote_token(self):
        if self._remote_token:
            return self._remote_token
        if self.cmd_args_thread.is_alive():
            self.cmd_args_thread.join()
        return self._remote_token

    @with_try_except
    def post(self, path, r_type=None, payload: str = "{}"):
        logger.debug(f"POST request to {path}")
        return handle_request(
            "POST", self.full_url, path, self.headers, r_type, payload
        )

    @with_try_except
    def patch(self, path, r_type: Optional[str] = None, payload: str = "{}"):
        logger.debug(f"PATCH request to {path}")
        return handle_request(
            "PATCH", self.full_url, path, self.headers, r_type, payload
        )

    @with_try_except
    def get(self, path, r_type: Optional[str] = None):
        logger.debug(f"GET request to {path}")
        return handle_request("GET", self.full_url, path, self.headers, r_type)

    def ClientIsOpen(self):
        logger.debug("Checking if the client is open")
        seconds = 0
        connection_error = requests.exceptions.ConnectionError
        session_path = self.routes.login.login_session
        while True:
            connection_response = self.get(session_path, r_type="raw")

            if isinstance(connection_response, connection_error):
                continue

            if connection_response.status_code != 200:
                continue

            connection_json = connection_response.json()
            state = connection_json.get("state", "Offline")

            if state == "SUCCEEDED":
                return True

            sleep(1)
            seconds += 1

            if seconds > 200:
                return False

    def __exit__(self, exc_type, exc_value, traceback):
        self.linked = False
        if self.live and self.ws_thread.is_alive():
            self.ws_thread.join()
        logger.debug("Program is Closed")
