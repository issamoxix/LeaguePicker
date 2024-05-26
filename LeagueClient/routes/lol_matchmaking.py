VERSION = "v1/"
BASE_ROUTE = "/lol-"


class Endpoint:
    def __init__(self, service):
        self.route = f"{BASE_ROUTE}{service}/{VERSION}"


class Login(Endpoint):
    def __init__(self):
        super().__init__("login")
        self.login_session = f"{self.route}session"


class MatchMaking(Endpoint):
    def __init__(self):
        super().__init__("matchmaking")
        self.ready_check_accept = f"{self.route}ready-check/accept"


class Summoner(Endpoint):
    def __init__(self):
        super().__init__("summoner")
        self.current_summoner = f"{self.route}current-summoner"


class ChampSelect(Endpoint):
    def __init__(self):
        super().__init__("champ-select")
        self.session = f"{self.route}session"
        self.session_actions_by_id = f"{self.route}session/actions/%s"
        self.session_actions_complete = f"{self.route}session/actions/%s/complete"


class GameFlow(Endpoint):
    def __init__(self):
        super().__init__("gameflow")
        self.session = f"{self.route}session"
        self.phase = f"{self.route}gameflow-phase"


class Endpoints(MatchMaking, ChampSelect, Summoner, Login):
    def __init__(self):
        self.matchmaking = MatchMaking()
        self.summoner = Summoner()
        self.champ_select = ChampSelect()
        self.login = Login()
        self.game_flow = GameFlow()
