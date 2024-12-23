from __future__ import annotations

import argparse
import os
import sys
import typing
from typing import Callable, Type

from PyQt6.QtCore import QFile, QDir, QSettings, Qt, QCoreApplication
from PyQt6.QtNetwork import QNetworkAccessManager, QHostAddress
from PyQt6.QtWidgets import QWidget
from pythonosc import udp_client

from src.controller import Controller, ControllerRegistry
from src.vrc_osc.avatar import Avatar
from src.my_translator import MyTranslator
from src.ui.main_window import MainWindow
from src.vrc_api import VRCApiService
from src.ui.avatar_osc_remote_window import AvatarOSCRemoteWindow
from src.vrc_osc.vrc_osc import VrcOscService, OscMessage

from src.ui.avatar_controller_window import AvatarControllerWindow

import logging

class App:
    """
    Holds all singletons and a list of all windows. Responsible for wiring the dependencies.

    In this project ...Service most likely means a singleton single purpose class that is independent and
    needs to be passed to app logic components
    """
    def __init__(self):
        self.avatar_controller: list[AvatarControllerWindow] = []
        self.avatar_windows: list[AvatarOSCRemoteWindow] = []

        QCoreApplication.setOrganizationName("Usagi Corp.")
        QCoreApplication.setApplicationName("OSC Sniffer")

        # parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--recv-ip", default="127.0.0.1",
                            help="IP from where to receive messages VRC osc messages from.", dest="ip_in")
        parser.add_argument("--send-ip", default="127.0.0.1",
                            help="IP of the VRChat client.", dest="ip_out")
        parser.add_argument("--send-port", type=int, default=9000,
                            help="Port to send osc messages to VRC", dest="port_out")
        parser.add_argument("--recv-port", type=int, default=9001,
                            help="Port to receive osc messages from VRC", dest="port_in")
        parser.add_argument("--verbose", action="store_true", help="Enable debug mode")
        args = parser.parse_args()

        # setup logger
        log_level = logging.DEBUG if args.verbose else logging.ERROR
        logging.basicConfig(level=log_level)
        logging.debug("verbose mode enabled")

        # setup services
        self.network_manager: QNetworkAccessManager = QNetworkAccessManager()
        self.osc_client: udp_client.SimpleUDPClient = udp_client.SimpleUDPClient(args.ip_out, args.port_out)
        self.translator: MyTranslator = MyTranslator()
        self.vrca: VRCApiService = VRCApiService(self.network_manager)

        self.osc_service: VrcOscService = VrcOscService()
        self.osc_subscriber: set[Callable[[OscMessage], None]] = set()
        self.osc_service.set_handler(self._osc_handler)
        self.osc_service.connect(QHostAddress(args.ip_in), args.port_in, QHostAddress(args.ip_out), args.port_out)

        self.controller_registry = ControllerRegistry()
        self.controller_registry.load_all_plugins(self.controller_registry.get_standard_plugins_location())

        # setup ui
        self.mw: MainWindow = MainWindow(self)
        self.vrca.logged_in.connect(self.mw.on_login)
        self.vrca.fast_login()

        self.mw.show()

    def spawn_avatar_window(self, filename: str, parent: Callable[[QWidget], None] | None = None) -> None:
        if filename and QFile(filename).exists():
            new_avatar = Avatar(self.osc_service)
            new_avatar.load_vrchat_osc_file(filename)
            new_window = AvatarOSCRemoteWindow(self, new_avatar)
            self.avatar_windows.append(new_window)
            if parent is None:
                new_window.show()
            else:
                parent(new_window)

    def spawn_controller_window(self, filename: str, controller: Type[Controller], parent: Callable[[QWidget], None]):
        if filename and QFile(filename).exists():
            new_avatar = Avatar(self.osc_service)
            new_avatar.load_vrchat_osc_file(filename)
            new_window = AvatarControllerWindow(self, new_avatar, controller)
            self.avatar_controller.append(new_window)
            new_window.show()


    def subscribe_osc(self, handler: Callable[[OscMessage], None]):
        self.osc_subscriber.add(handler)

    def unsubscribe_osc(self, handler: Callable[[OscMessage], None]):
        self.osc_subscriber.remove(handler)

    def _osc_handler(self, msg: OscMessage) -> None:
        for handler in self.osc_subscriber:
            try:
                handler(msg)
            except Exception as e:
                print("Error while dispatching OSC Message")
                print(e)

    @staticmethod
    def get_osc_directory() -> str:
        # TODO: Consider making it multiplatform
        osc_dir = QDir(os.environ["APPDATA"] + "\\..\\LocalLow\\VRChat\\VRChat\\OSC\\")
        return osc_dir.absolutePath()
