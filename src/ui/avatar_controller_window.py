import typing
from typing import Type

from src.my_translator import MyTranslator
from src.ui.base_window import BaseWindow
from src.vrc_osc.avatar import Avatar
import src.app
import src.controller


class AvatarControllerWindow(BaseWindow):
    def __init__(self, my_translator: MyTranslator, avatar: Avatar, controller: Type[src.controller.Controller]):
        super().__init__(my_translator)

        self.avatar = avatar
        self.setWindowTitle(avatar.avatar_name + " Controller")

        self.controller = controller(avatar, parent=self)
        self.central_widget = self.controller

