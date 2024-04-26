from LeagueClient import LeagueClient


with LeagueClient(log_level="DEBUG") as client:
    # Setting Options
    client.auto_accept = True
    client.auto_pick = True
    client.champions_pool = [
        222, # Jinx
        98,  # Sheen
    ]
    client.champions_ban_pool = [
        412,  # thresh
    ]
    summoner = client.summoner
    print(summoner)
    print(f"wss://riot:{client.remote_token}@127.0.0.1:{client.port}")
    print(
        client.port,
        client.remote_token,
        client.headers,
        client.headers,
        client.league_auth,
    )
