from src.controller import Controller
from src.vrc_osc.avatar import Avatar


class ExBController(Controller):
    @staticmethod
    def get_avatar_id() -> str:
        return "usr_03f3f5e6-d527-4b46-85bf-d3526ca88735"

    def __init__(self, avatar: Avatar, parent=None):
        super().__init__(avatar, parent)
