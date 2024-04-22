from LeagueClient import LeagueClient

# TODO Support MAC
# ref https://hextechdocs.dev/getting-started-with-the-lcu-api/
# TODO add logic for the ChampSelect actions

with LeagueClient() as client:
    client.auto_accept = True
    client.champions_pool = [
        98,  # Sheen
    ]
    summoner = client.summoner
    print(summoner)
    print(client.port, client.remote_token, client.headers, client.headers)
