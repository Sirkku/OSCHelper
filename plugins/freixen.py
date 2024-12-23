from src.controller import Controller


class FreixenCtrl(Controller):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @staticmethod
    def get_avatar_id() -> str:
        return "aavtr_f456bddf-1bfa-4da8-8918-e3ca56bf47ed"