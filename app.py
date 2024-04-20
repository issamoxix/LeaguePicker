from LeagueClient import LeagueClient


# TODO Add logs
# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO accept Q & Lock Champion
# TODO conntect to ws wss://riot:<remote_toke>@127.0.0.1:51061/ wss://riot:remote_token@host:port/
# TODO remove Cache file Mechanism (if the lockfile exists then we check (_get_cmd_args) proccess)

with LeagueClient() as lcu:
    summoner = lcu.summoner
    login_succ = lcu.get("/lol-login/v1/session", "raw")
    print(login_succ.url)
    print(lcu.league_auth)
    print(lcu.passowrd)
    print(login_succ.json())
    print(lcu.remote_token)