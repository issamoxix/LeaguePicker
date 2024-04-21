from typing import List

class Options:
    auto_accept: bool = False
    auto_pick: bool = False
    auto_accept_timeout: int = 0
    pick_champions: List[str] = []

    def __init__(self):
        return self


