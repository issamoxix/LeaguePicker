from LeagueClient import LeagueClient


# TODO Add logs
# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO accept Q & Lock Champion

with LeagueClient() as lcu:
    summoner = lcu.summoner