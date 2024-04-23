import wmi
import os
import base64
import requests
from time import sleep
from typing import Union, Optional
import threading
import pythoncom
from functools import lru_cache
import json

from .options import Options
from .lcuws import LcuWebsocket
from .utils.log import with_try_except, logger
from .utils.functions import handle_request
from .constants import PROCESS_NAME
from .exceptions import LeagueClientClosed


class LeagueClient(Options):
    league_dir: Optional[str]
    league_auth: Optional[str]
    lcu_url: str = "https://127.0.0.1"
    port: Optional[int]
    linked: bool = False
    protocol: str = "https"
    password: str
    trials: int = 1  # in seconds "1s"
    state: str = "Offline"
    _remote_token: Optional[str] = None
    options: dict = {"auto_accept": False}

    def __init__(
        self,
        league_dir: Optional[str] = None,
        log_level: str = "INFO",
        live: bool = True,
    ):
        logger.setLevel(log_level)
        logger.debug("Initializing LeagueClient")
        if league_dir:
            self.league_dir = league_dir
            self.cmd_args_thread = self._get_cmd_args_thread()
        else:
            self._get_cmd_args()

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
            self.ws_thread = threading.Thread(target=self._connect_to_websocket)
            self.ws_thread.start()
        return self

    def _connect_to_websocket(self):
        self.LcuWebsocket = LcuWebsocket(
            port=self.port, remote_token=self.remote_token, headers=self.headers
        )
        self.LcuWebsocket.ws_connect(self.set_state)

    @lru_cache
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
            raise LeagueClientClosed
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
        # have all the endpoints in a Dict "constants.py"
        return self.get("/lol-summoner/v1/current-summoner")

    def set_state(self, value: str) -> str:
        if self.state == value:
            return self.state
        logger.info("Status: " + value)
        self.state = value
        if "ReadyCheck" == value and self.auto_accept:
            sleep(self.auto_accept_timeout)
            self.post("/lol-matchmaking/v1/ready-check/accept", response_type="text")
        if value in ["ChampSelect", "championSelect"]  and len(self.champions_pool) > 0:
            sleep(self.auto_champ_select_timeout)
            # get actions from 
            # GET: /lol-champ-select/v1/session
            # whenever an action been fulfiled the next action
            # will be added to the list 
            # actions += 1 by aciotn: id 
            action = 1
            data = {"championId": self.champions_pool[0]}
            self.patch(
                f"/lol-champ-select/v1/session/actions/{action}",
                payload=json.dumps(data),
            )
            sleep(self.auto_hover_champ_timeout)
            self.post(
                f"/lol-champ-select/v1/session/actions/{action}/complete",
                payload=json.dumps(data),
            )


        return self.state

    @property
    def remote_token(self):
        if self._remote_token:
            return self._remote_token
        if self.cmd_args_thread.is_alive():
            self.cmd_args_thread.join()
        return self._remote_token

    @with_try_except
    def post(self, path, response_type: str = "json", payload: str = "{}"):
        logger.debug(f"POST request to {path}")
        return handle_request(
            "POST", self.full_url, path, self.headers, response_type, payload
        )
    
    @with_try_except
    def patch(self, path, response_type: str = "json", payload: str = "{}"):
        logger.debug(f"POST request to {path}")
        return handle_request(
            "PATCH", self.full_url, path, self.headers, response_type, payload
        )

    @with_try_except
    def get(self, path, response_type: str = "json"):
        logger.debug(f"GET request to {path}")
        return handle_request("GET", self.full_url, path, self.headers, response_type)

    def ClientIsOpen(self):
        logger.debug("Checking if the client is open")
        seconds = 0
        while True:
            connection_response = self.get("/lol-login/v1/session", response_type="raw")

            if isinstance(connection_response, requests.exceptions.ConnectionError):
                continue

            if connection_response.status_code != 200:
                continue

            connection_json = connection_response.json()
            self.state = connection_json.get("state", "Offline")

            if self.state == "SUCCEEDED":
                return True

            sleep(1)
            seconds += 1

            if seconds > 200:
                return False

    def __exit__(self, exc_type, exc_value, traceback):
        self.linked = False
        if self.live and self.ws_thread.is_alive():
            self.ws_thread.join()
        logger.info("Program is Closed")
