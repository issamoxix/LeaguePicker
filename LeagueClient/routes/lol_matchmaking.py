VERSION = "v1/"


class MatchMaking:
    route = "/lol-matchmaking/" + VERSION
    ready_check_accept: str = route + "ready-check/accept"


class ChampSelect:
    route = "/lol-champ-select/" + VERSION
    session_actions_by_id = "session/actions/%s"


class Endpoints(MatchMaking, ChampSelect):
    ...
