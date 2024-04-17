from LeagueClient import LeagueClient


# TODO Add logs
# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO accept Q & Lock Champion

with LeagueClient() as lcu:
    summoner = lcu.summoner
    login_succ = lcu.get("/lol-gameflow/v1/gameflow-phase", "raw")
    print(login_succ.url)
    print(lcu.league_auth)