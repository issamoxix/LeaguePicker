import wmi
import os
import base64
import requests
from time import sleep
from typing import Union
import threading
import pythoncom
from functools import lru_cache

from .utils.log import with_try_except, logger
from .constants import PROCESS_NAME

class LeagueClient:
    league_dir: str = None
    league_auth: str = None
    lcu_url: str = "https://127.0.0.1"
    port: int = None
    linked: bool = False
    protocol: str = "https"
    password: str
    cache_file: str = "cache.txt"
    timeout: int = 8
    trials: int = 1  # in seconds "1s"
    state: str = "Offline"
    _remote_token: str = None
    options: list[str] = [
        "--app-port",
        "--install-directory",
        "--remoting-auth-token",
    ]

    def __init__(self, league_dir: Union[None, str]= None, log_level: str = "INFO"):
        logger.setLevel(log_level)
        logger.debug("Initializing LeagueClient")
        if league_dir:
            self.league_dir = league_dir
            self.cmd_args_thread = self._get_cmd_args_thread()
        else:
            self.league_dir, self.port = self._get_cmd_args()

        self.passowrd = self._get_password()

        self.league_auth = self._handle_password()
        self.headers = {
            "Authorization": f"Basic {self.league_auth}",
            "Accept": "application/json",
        }
        self.linked = self.ClientIsOpen()

    def __enter__(self):
        return self
    
    @lru_cache
    def _get_cmd_args(self):
        logger.debug("Getting command line arguments")
        pythoncom.CoInitialize()  # Initialize pythoncom

        c = wmi.WMI()
        for process in c.Win32_Process():
            if process.name == PROCESS_NAME:
                cmd = process.CommandLine
                for segment in cmd.split('" "'):
                    if "--app-port" in segment:
                        self.port = int(segment.split("=")[1])
                    if "--install-directory" in segment:
                        self.league_dir = segment.split("=")[1]
                    if "--remoting-auth-token" in segment:
                        self._remote_token = segment.split("=")[1]
                break
        else:
            raise Exception("The League client must be running!")
        return True

    def _get_cmd_args_thread(self):
        thread = threading.Thread(target=self._get_cmd_args)
        thread.start()
        return thread

    def _read_lockfile(self):
        logger.debug("Reading lockfile")
        if not self.league_dir:
            raise Exception("The League client must be running !")
        lockfile_path = os.path.join(self.league_dir, "lockfile")

        if not os.path.exists(lockfile_path):
            raise Exception("The League client must be running !")

        with open(lockfile_path, "r") as lockfile:
            content = lockfile.read()

        return content.split(":")

    def _get_password(self):
        logger.debug("Getting password from lockfile")
        process, PID, port, password, protocol = self._read_lockfile()
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
    
    @property
    def remote_token(self):
        if self.cmd_args_thread.is_alive():
            self.cmd_args_thread.join()
        return self._remote_token
    

    @with_try_except
    def get(self, path, response_type: str = "json"):
        logger.debug(f"GET request to {path}")
        response = requests.get(
            f"{self.lcu_url}:{self.port}{path}",
            timeout=self.timeout,
            headers=self.headers,
            verify=False,
        )

        match response_type:
            case "json":
                return response.json()
            case "json":
                return response.text
            case _:
                return response

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
        logger.info("Program is Closed")
