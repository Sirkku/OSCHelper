from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import QSize, QDir
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.uic.properties import QtWidgets

import base_window
from vrc_api import AvatarData


class MainWindow(base_window.BaseWindow):
    def __init__(self, app):
        super(MainWindow, self).__init__(app)
        self.setWindowTitle("Vrchat OSC Tool")

        self.cw = QWidget(self)
        self.setCentralWidget(self.cw)

        self.outer_layout = QVBoxLayout()
        self.cw.setLayout(self.outer_layout)

        self.avi_lbl = QLabel(self)
        self.img_lbl = QLabel(self)
        self.img_lbl.setMinimumSize(256, 192)
        self.img_lbl.setMaximumSize(256, 192)

        self.outer_layout.addWidget(self.avi_lbl)

        self.inner_layout = QHBoxLayout()
        self.outer_layout.addLayout(self.inner_layout)

        self.inner_btn_layout = QVBoxLayout()
        self.inner_layout.addWidget(self.img_lbl)
        self.inner_layout.addLayout(self.inner_btn_layout)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.pressed.connect(self.refresh_action)
        self.inner_btn_layout.addWidget(self.refresh_btn)
        self.launch_remote_btn = QPushButton("Start Remote")
        self.launch_remote_btn.pressed.connect(self.launch_remote_action)
        self.inner_btn_layout.addWidget(self.launch_remote_btn)

        self.avatarData: Optional[AvatarData] = None

    def on_login(self, success: bool):
        self.refresh_action()

    def reload_finished(self, res: AvatarData):
        self.avi_lbl.setText("Avatar: " + res.name + " (" + str(res.id) + ")")
        self.img_lbl.setPixmap(QPixmap.fromImage(res.img))
        self.avatarData = res

    def refresh_action(self):
        self.app.vrca.get_avatar_stuff(self.app.vrca.get_current_user(cached=False).current_avatar,
                                       lambda res: self.reload_finished(res))

    def launch_remote_action(self):
        if self.avatarData is None:
            return
        osc_base_dir = self.app.get_osc_directory()
        entire_path = osc_base_dir + "/" + self.avatarData.user + "/Avatars/" + self.avatarData.id + ".json"
        clean_path = QDir(entire_path).absolutePath()
        self.app.spawn_avatar_window(clean_path)
