import json
from time import sleep
from typing import Optional

from .utils.log import logger


class HandleEvents:
    state: Optional[str] = None

    def __init__(self):
        logger.debug("Handle Events Initialize")

    def handle_message(self, uri):
        if self.routes.champ_select.session == uri:
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

    def _get_action(self):
        json_response = self.get(self.routes.champ_select.session, r_type="json")
        unavailable_champs = self._handle_unavailable_champs(json_response)
        no_action = {"id": 0, "type": None}

        actions = json_response.get("actions", None)

        if not actions:
            return no_action, unavailable_champs

        local_cell_id = json_response.get("localPlayerCellId")
        for action_list in actions:
            for action in action_list:
                if action.get("completed"):
                    continue

                if action.get("actorCellId") != local_cell_id:
                    continue

                return action, unavailable_champs
        return no_action, unavailable_champs

    def _event_ready_check(self):
        logger.debug("[Event][ReadyCheck]")
        if not self.auto_accept:
            return
        sleep(self.auto_accept_timeout)
        self.post(self.routes.matchmaking.ready_check_accept)

    def _event_champ_select(self):
        logger.debug("[Event][ChampSelect]")
        if len(self.champions_pool) <= 0 or not self.auto_pick:
            return

        action, unavailable_champs = self._get_action()
        action_id = action.get("id")
        action_type = action.get("type")

        if action == action_id:
            return

        if action_type == "pick":
            champions_list = list(self.champions_pool)
        elif action_type == "ban":
            champions_list = list(self.champions_ban_pool)
        else:
            return

        unpickable_champs = []
        for champion in champions_list:
            if champion not in unavailable_champs:
                break
            unpickable_champs.append(champion)
        if champions_list == unpickable_champs:
            return

        data = {"championId": champion}
        sleep(self.auto_champ_select_timeout)

        self.patch(
            self.routes.champ_select.session_actions_by_id % action_id,
            payload=json.dumps(data),
        )

        sleep(self.auto_hover_champ_timeout)

        self.post(
            self.routes.champ_select.session_actions_complete % action_id,
            payload=json.dumps(data),
        )

    def _handle_unavailable_champs(self, json_response: dict) -> list:
        champ_list = []
        bans = json_response.get("bans", None)
        my_team = json_response.get("myTeam", [])
        their_team = json_response.get("theirTeam", [])

        if bans:
            my_team_bans = bans.get("myTeamBans", [])
            their_team_bans = bans.get("theirTeamBans", [])
            champ_list += my_team_bans + their_team_bans

        if len(my_team) > 0:
            for team in my_team:
                champ_list.append(team.get("championId", 0))
        if len(their_team) > 0:
            for team in their_team:
                champ_list.append(team.get("championId", 0))

        return champ_list
