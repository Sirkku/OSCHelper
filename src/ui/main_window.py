from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTabWidget

from src.controller import Controller
from src.ui.base_window import BaseWindow
from src.vrc_api import AvatarData

import logging

log = logging.getLogger(__name__)


class MainWindow(BaseWindow):
    """

    """
    def __init__(self, app):
        super().__init__(app.translator)
        self.vrca = app.vrca
        self.app = app
        self.setWindowTitle("Vrchat OSC Tool")

        self.tabwidget = QTabWidget()

        self.tabwidget.setTabsClosable(True)
        self.tabwidget.tabCloseRequested.connect(self.tab_close_handler)

        self.setCentralWidget(self.tabwidget)

        self.move(10, 10)
        self.resize(800, 800)
        self.cw = QWidget()
        self.tabwidget.addTab(self.cw, "Main")

        self.outer_layout = QVBoxLayout()
        self.cw.setLayout(self.outer_layout)

        self.avi_lbl = QLabel(self)
        self.img_lbl = QLabel(self)
        self.img_lbl.setMinimumSize(256, 192)
        self.img_lbl.setMaximumSize(256, 192)

        self.outer_layout.addWidget(self.avi_lbl)

        self.inner_layout = QHBoxLayout()
        self.outer_layout.addLayout(self.inner_layout)
        self.outer_layout.addStretch(1)

        self.inner_btn_layout = QVBoxLayout()
        self.inner_layout.addWidget(self.img_lbl)
        self.inner_layout.addLayout(self.inner_btn_layout)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.pressed.connect(self.refresh_action)
        self.inner_btn_layout.addWidget(self.refresh_btn)

        self.launch_remote_btn = QPushButton("Start Remote")
        self.launch_remote_btn.pressed.connect(self.launch_remote_action)
        self.inner_btn_layout.addWidget(self.launch_remote_btn)

        self.refresh_launch_btn = QPushButton("Refresh & Launch")
        self.refresh_launch_btn.pressed.connect(self.refresh_launch_action)
        self.inner_btn_layout.addWidget(self.refresh_launch_btn)

        self.launch_controller_btn = QPushButton("Launch Controller")
        self.launch_controller_btn.setEnabled(False)
        self.launch_controller_btn.pressed.connect(self.launch_controller)
        self.inner_btn_layout.addWidget(self.launch_controller_btn)

        self.avatarData: Optional[AvatarData] = None

    def on_login(self, success: bool):
        self.refresh_action()

    def tab_close_handler(self, index):
        if index == 0:
            return
        self.tabwidget.removeTab(index)

    def reload_finished(self, res: AvatarData):
        self.avi_lbl.setText("Avatar: " + res.name + " (" + str(res.id) + ")")
        self.img_lbl.setPixmap(QPixmap.fromImage(res.img))
        self.avatarData = res


    def refresh_action(self):
        self.app.vrca.get_avatar_stuff(self.vrca.get_current_user(cached=False).current_avatar,
                                       lambda res: self.reload_finished(res))

    def reload_finished_launch(self, res: AvatarData):
        self.reload_finished(res)
        self.launch_remote_action()

    def refresh_launch_action(self):
        self.vrca.get_avatar_stuff(self.vrca.get_current_user(cached=False).current_avatar,
                                       lambda res: self.reload_finished_launch(res))

    def launch_remote_action(self):
        log.debug("Launching remote")
        if self.avatarData is None:
            log.debug("Couldn't launch remote, avatarData is None")
            return
        log.debug(f"remote is for {self.avatarData.name} ({self.avatarData.id})")
        clean_path = self._get_avatar_osc_file()
        self.app.spawn_avatar_window(clean_path, lambda x: self.add_avatar_window_tab(x, self.avatarData.name))

    def launch_controller_action(self):
        if self.avatarData is None:
            log.warning("Trying to load controller for none-selected avatar")



    def add_avatar_window_tab(self, avatar_window: QWidget, avatar_name: str):
        new_tab_index = self.tabwidget.addTab(avatar_window, avatar_name)
        self.tabwidget.setCurrentIndex(new_tab_index)


    def _get_avatar_osc_file(self) -> str:
        osc_base_dir = self.app.get_osc_directory()
        entire_path = osc_base_dir + "/" + self.avatarData.user + "/Avatars/" + self.avatarData.id + ".json"
        return QDir(entire_path).absolutePath()

    def update_controller_button(self, avatar_id: str) -> None:
        c = Controller.registry.get(avatar_id, None)
        if c is None:
            self.launch_controller_btn.setEnabled(False)
        else:
            self.launch_controller_btn.setEnabled(True)

    def launch_controller(self):
        if self.avatarData is None:
            return
        controller = Controller.registry.get(self.avatarData.id, None)
        if controller is None:
            return
        json_path = self._get_avatar_osc_file()
        self.app.spawn_controller_window(json_path, controller)
