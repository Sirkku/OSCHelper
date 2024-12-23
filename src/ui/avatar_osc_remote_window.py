from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QAction

from src.vrc_osc.avatar import Avatar
from src.vrc_osc.vrc_osc import OscMessage, VrcOscService

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


class AvatarOSCRemoteWindow(src.ui.base_window.BaseWindow):
    """
    The window that contains the OSC remote controls and views.
    """
    translate_all_chinese: QAction
    central_widget: AvatarWidget | None

    def __init__(self, app, avatar: Avatar):
        super().__init__(app.translator)
        self.app = app
        self.setWindowTitle("Vrchat OSC Tool")
        self.central_widget: Optional[AvatarWidget] = None
        menu_bar = self.menuBar()
        self.tool_menu = menu_bar.addMenu("Tools")
        self.filter_menu = menu_bar.addMenu("Filter")
        self.filter_actions = list()

        self.translate_all_chinese = QAction("Translate all chinese")
        self.translate_all_chinese.triggered.connect(self.translate_all_chinese_action)
        self.tool_menu.addAction(self.translate_all_chinese)

        self.set_avatar(avatar)

    def closeEvent(self, event):
        super().closeEvent(event)

    def translate_all_chinese_action(self):
        if self.central_widget:
            self.central_widget.translate_all_chinese()

    def set_avatar(self, avatar: Avatar):
        if self.central_widget is not None:
            for tfqa in self.filter_actions:
                self.filter_menu.removeAction(tfqa)

        self.central_widget = AvatarWidget(self.app.translator, avatar)

        for f in self.central_widget.filters:
            f: _Filter
            new_tfqa = ToggleFilterQAction(self.central_widget, f)
            new_tfqa.setChecked(f.default_state())
            self.filter_actions.append(new_tfqa)
            self.filter_menu.addAction(new_tfqa)

        self.setCentralWidget(self.central_widget)
        return True
