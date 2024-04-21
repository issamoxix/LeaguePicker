from LeagueClient import LeagueClient

# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO Lock Champion

league_path = r"C:\Riot Games\League of Legends"
with LeagueClient(league_dir=league_path) as client:
    client.auto_accept = True
    client.auto_accept_timeout = 2
    summoner = client.summoner
    print(summoner)
    print(client.port, client.remote_token, client.headers, client.headers)