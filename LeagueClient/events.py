import json
from time import sleep
from typing import Optional


from .utils.log import logger


class HandleEvents:
    state: Optional[str] = None

    def __init__(self):
        logger.debug("Handle Events Initialize")

    def handle_message(self, uri):
        if "/lol-champ-select/v1/session" == uri:
            self._event_champ_select()

    def set_state(self, value: str):
        if self.state == value:
            return self.state
        logger.debug("Status: " + value)
        self.state = value

        match value:
            case "ReadyCheck":
                self._event_ready_check()
            case "ChampSelect":
                self._event_champ_select()
        return self.state

    def _get_action(self) -> dict:
        json_response = self.get("/lol-champ-select/v1/session", response_type="json")

        no_action = {"id": 0, "type": None}

        actions = json_response.get("actions", None)

        if not actions:
            return no_action
        
        for action_list in actions:
            for action in action_list:
                if action.get("completed"):
                    continue

                if action.get("actorCellId") != json_response.get("localPlayerCellId"):
                    continue

                return action
        return no_action

    def _event_ready_check(self):
        logger.debug("[Event][ReadyCheck]")
        if not self.auto_accept:
            return
        sleep(self.auto_accept_timeout)
        self.post("/lol-matchmaking/v1/ready-check/accept")

    def _event_champ_select(self):
        logger.debug("[Event][ChampSelect]")
        if len(self.champions_pool) <= 0 or not self.auto_pick:
            return

        sleep(self.auto_champ_select_timeout)

        action = self._get_action()
        action_id = action.get("id")
        action_type = action.get("type")

        if action == action_id:
            return

        if action_type == "pick":
            data = {"championId": self.champions_pool[0]}
        elif action_type == "ban":
            data = {"championId": self.champions_ban_pool[0]}
        else:
            return 
        self.patch(
            f"/lol-champ-select/v1/session/actions/{action_id}",
            payload=json.dumps(data),
        )
        sleep(self.auto_hover_champ_timeout)
        self.post(
            f"/lol-champ-select/v1/session/actions/{action_id}/complete",
            payload=json.dumps(data),
        )
