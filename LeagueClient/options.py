from typing import List

class Options:
    auto_accept: bool = False
    auto_pick: bool = False
    champions_pool: List[str] = []
    auto_accept_timeout: int = 0
    auto_champ_select_timeout: int = 0
    auto_hover_champ_timeout: int = 0

    def __init__(self):
        return self

