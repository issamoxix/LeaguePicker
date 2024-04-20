from LeagueClient import LeagueClient


# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO accept Q & Lock Champion
# TODO conntect to ws wss://riot:<remote_toke>@127.0.0.1:51061/ wss://riot:remote_token@host:port/

league_path = r"C:\Riot Games\League of Legends"
with LeagueClient(league_dir=league_path, log_level="DEBUG") as lcu:
    summoner = lcu.summoner
    print(summoner)
    print(lcu.remote_token)