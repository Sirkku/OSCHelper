from __future__ import annotations

import json

from PyQt6.QtGui import QAction

import src.ui.base_window
from src.ui.avatar_widget import AvatarWidget, _Filter


class ToggleFilterQAction(QAction):
    def __init__(self, parent, _filter: _Filter):
        super(QAction, self).__init__()
        self.filter: _Filter = _filter
        self.setText(self.filter.get_text())
        self.setCheckable(True)
        self.toggled.connect(self.on_toggled)

    def on_toggled(self):
        self.filter.active = self.isChecked()
        self.filter.filter_toggled.emit()




class AvatarOSCRemote(src.ui.base_window.BaseWindow):
    translate_all_chinese: QAction
    central_widget: AvatarWidget | None

    def __init__(self, app):
        super(AvatarOSCRemote, self).__init__(app)
        self.setWindowTitle("Vrchat OSC Tool")
        self.osc_client = app.osc_client
        self.central_widget = None
        menu_bar = self.menuBar()
        self.tool_menu = menu_bar.addMenu("Tools")
        self.filter_menu = menu_bar.addMenu("Filter")
        self.filter_actions = list()

        self.translate_all_chinese = QAction("Translate all chinese")
        self.translate_all_chinese.triggered.connect(self.translate_all_chinese_action)
        self.tool_menu.addAction(self.translate_all_chinese)

    def translate_all_chinese_action(self):
        if self.central_widget:
            self.central_widget.translate_all_chinese()

    def send_osc_message(self, address, value):
        self.osc_client.send_message(address, value)

    def load_file(self, filename):
        with open(filename, 'r', encoding='utf-8-sig') as file:
            j = json.load(file)

            if self.central_widget is not None:
                for tfqa in self.filter_actions:
                    self.filter_menu.removeAction(tfqa)
            self.central_widget = AvatarWidget(self.app, j)

            for f in self.central_widget.filters:
                f: _Filter
                new_tfqa = ToggleFilterQAction(self.central_widget, f)
                self.filter_actions.append(new_tfqa)
                self.filter_menu.addAction(new_tfqa)

            self.setCentralWidget(self.central_widget)
            return True
