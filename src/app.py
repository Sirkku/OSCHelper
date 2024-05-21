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
        parser.add_argument("--recv-ip", default="127.0.0.1",
                            help="IP from where to receive messages VRC osc messages from.", dest="ip_in")
        parser.add_argument("--send-ip", default="127.0.0.1",
                            help="IP of the VRChat client.", dest="ip_in")
        parser.add_argument("--send-port", type=int, default=9000,
                            help="Port to send osc messages to VRC", dest="port_out")
        parser.add_argument("--recv-port", type=int, default=9001,
                            help="Port to receive osc messages from VRC", dest="port_in")
        args = parser.parse_args()

        self.network_manager = QNetworkAccessManager()

        self.osc_client = udp_client.SimpleUDPClient(args.ip_out, args.port_out)
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
