from __future__ import annotations

from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
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

        self.inner_layout = QHBoxLayout()
        self.outer_layout.addLayout(self.inner_layout)

        self.img_lbl = QLabel(self)
        self.avi_lbl = QLabel(self)
        self.outer_layout.addWidget(self.img_lbl)
        self.outer_layout.addWidget(self.avi_lbl)

    def on_login(self):
        self.app.vrca.get_avatar_stuff('avtr_d26f8bc5-0a0c-41fe-977c-c1dfbc5c8c96',
                                       lambda res: self.reload_finished(res))

    def reload_finished(self, res: AvatarData):
        self.avi_lbl.setText("Avatar: " + res.name + " (" + str(res.id) + ")")
        self.img_lbl.setPixmap(QPixmap.fromImage(res.img))
