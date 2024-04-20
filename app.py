from LeagueClient import LeagueClient
from LeagueClient.lcuws import LcuWebsocket

# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO accept Q & Lock Champion
# TODO add the websocket connection to the Main Client
league_path = r"C:\Riot Games\League of Legends"
with LeagueClient(league_dir=league_path) as lcu:
    summoner = lcu.summoner
    print(summoner)
    wss_connection = LcuWebsocket(
        port=lcu.port, remote_token=lcu.remote_token, headers=lcu.headers
    )
