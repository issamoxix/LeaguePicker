import wmi
import os
import base64
import requests
from time import sleep
from .utils import with_try_except


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

    def __init__(self):
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

    def _check_cache(self):
        """
        cache.txt
        will contain the league dir path
        """

        if not os.path.exists(self.cache_file):
            return False
        with open(self.cache_file, "r") as file:
            self.league_dir = file.read().strip()
        return True

    def _save_to_cache(self, value: str):
        with open(self.cache_file, "w") as file:
            file.write(value)

    def _get_cmd_args(self):
        if self._check_cache():
            return self.league_dir, self.port
        c = wmi.WMI()
        for process in c.Win32_Process():
            if process.name == "LeagueClientUx.exe":
                cmd = process.CommandLine
                for segment in cmd.split('" "'):
                    if "--app-port" in segment:
                        port = int(segment.split("=")[1])
                    if "--install-directory" in segment:
                        install_directory = segment.split("=")[1]
                break
        else:
            raise Exception("The League client must be running!")
        self._save_to_cache(install_directory)
        return install_directory, port

    def _read_lockfile(self):
        if not self.league_dir:
            raise Exception("The League client must be running !")
        lockfile_path = os.path.join(self.league_dir, "lockfile")

        count = 0
        while not os.path.exists(lockfile_path):
            print("Waiting for Client to Open")
            sleep(self.trials)
            count += 1
            if count > 1500:
                if os.path.exists(self.cache_file):
                    os.remove(self.cache_file)
                break

        if not os.path.exists(lockfile_path):
            raise Exception("The League client must be running !")

        with open(lockfile_path, "r") as lockfile:
            content = lockfile.read()

        return content.split(":")

    def _get_password(self):
        process, PID, port, password, protocol = self._read_lockfile()
        self.protocol = protocol
        self.password = password
        self.port = port
        return password

    def _handle_password(self):
        return base64.b64encode(f"riot:{self.password}".encode()).decode()

    @property
    def summoner(self):
        summoner_path = "/lol-summoner/v1/current-summoner"  # have all the endpoints in a Dict "constants.py"
        return self.get(summoner_path)

    @with_try_except
    def get(self, path, response_type: str = "json"):

        response = requests.get(
            f"{self.lcu_url}:{self.port}{path}",
            timeout=self.timeout,
            headers=self.headers,
            verify=False,
        )

        match response_type:
            case "json":
                return response.json()
            case "text":
                return response.text
            case _:
                return response

    def ClientIsOpen(self):
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
        print("Program is Closed")
