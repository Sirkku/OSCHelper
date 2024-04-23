from __future__ import annotations

import argparse
import os

from PyQt6.QtCore import QFile, QDir
from PyQt6.QtNetwork import QNetworkAccessManager
from pythonosc import udp_client

import src.my_translator
import src.ui.main_window
from src import vrc_api
from src.ui import avatar_osc_remote


class App:
    def __init__(self):
        self.osc_client: udp_client.SimpleUDPClient | None = None
        self.translator: src.my_translator.MyTranslator | None = None
        self.vrca: vrc_api.VRCApiService | None = None
        self.mw: src.ui.main_window.MainWindow | None = None
        self.network_manager: QNetworkAccessManager | None = None
        self.avatar_windows = []

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
                            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=9000,
                            help="The port the OSC server is listening on")
        args = parser.parse_args()

        self.network_manager = QNetworkAccessManager()

        self.osc_client = udp_client.SimpleUDPClient(args.ip, args.port)
        self.translator = src.my_translator.MyTranslator()
        self.vrca = vrc_api.VRCApiService(self.network_manager)

        self.mw = src.ui.main_window.MainWindow(self)

        self.vrca.logged_in.connect(self.mw.on_login)
        self.vrca.interactive_login_user()

        # client.send_message("/avatar/parameters/fluff/dps/penetrator", True)
        # %Appdata%\..\LocalLow\VRCHat\vrchat\OSC\

        self.mw.show()

    def spawn_avatar_window(self, filename: str) -> None:
        new_window = avatar_osc_remote.AvatarOSCRemote(self)
        if filename and QFile(filename).exists():
            new_window.load_file(filename)
        new_window.show()
        self.avatar_windows.append(new_window)

    # noinspection PyMethodMayBeStatic
    def get_osc_directory(self) -> str:
        osc_dir = QDir(os.environ["APPDATA"] + "\\..\\LocalLow\\VRChat\\VRChat\\OSC\\")
        return osc_dir.absolutePath()
