from __future__ import annotations

import re

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout

from src import utils
from src.data.avatar_param import AvatarParam
from src.ui.avatar_param_widget import AvatarParamWidget


class _Filter(QObject):
    filter_toggled = pyqtSignal()

    def __init__(self):
        super(QObject, self).__init__()
        self.active = False

    def filter(self, avatar_params: set[AvatarParam]) -> set[AvatarParam]:
        raise NotImplementedError()

    def get_text(self):
        return "Unnamed?"


class SelectionFilter(_Filter):
    def filter(self, avatar_params: set[AvatarParam]) -> set[AvatarParam]:
        filtered_params = set()
        for param in avatar_params:
            if param.selected:
                filtered_params.add(param)
        return filtered_params

    def get_text(self):
        return "Selected"


class GoGoLocoFilter(_Filter):
    def filter(self, avatar_params: set[AvatarParam]) -> set[AvatarParam]:
        filtered_params = set()
        for param in avatar_params:
            if not re.match("^Go/", param.name):
                filtered_params.add(param)
        return filtered_params

    def get_text(self):
        return "Exclude GoGoLoco"

class AvatarWidget(QWidget):
    def __init__(self, app, avatar_json):
        super().__init__()
        self.app = app
        self.params: set[AvatarParam] = set()
        """
        Represents all osc-related parameters of an avatar
        
        -> *.param_selection* contains the currently displayed parameters
        """
        self.param_selection: list[AvatarParam] = []
        """
        contains the currently displayed osc-related parameters. basically a 
          1. sorted 
          2. filtered 
        selection of .params
        """
        self.param_widgets: list[AvatarParamWidget] = []
        """
        list of widgets for every item in .param_selection
        """
        self.filters: set[_Filter] = set()
        """
        list of subclasses of _Filter. These are toggleable filters
        """
        self.selection_filter = SelectionFilter()
        self.gogoloco_filter = GoGoLocoFilter()
        self.filters.add(self.selection_filter)
        self.filters.add(self.gogoloco_filter)
        for f in self.filters:
            f.filter_toggled.connect(self.update_widgets)

        # centerpiece
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(0)

        for j_param in avatar_json["parameters"]:
            if "input" not in j_param:
                continue
            param = AvatarParam()
            param.load_from_json(j_param)
            self.params.add(param)
            self.param_selection.append(param)

        # Add Scroll Bar
        self.dummy_widget = QWidget()
        self.dummy_widget.setLayout(self.vbox)

        scrollview = QScrollArea(self)
        scrollview.setWidget(self.dummy_widget)
        scrollview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollview.setWidgetResizable(True)

        hbox = QHBoxLayout()
        hbox.addWidget(scrollview)
        self.setLayout(hbox)

        self.odd_row_palette = QPalette()
        self.odd_row_palette.setColor(QPalette.ColorRole.Window, QColor(0xFF, 0xFF, 0xFF))
        self.even_row_palette = QPalette()
        self.even_row_palette.setColor(QPalette.ColorRole.Window, QColor(0xDD, 0xDD, 0xDD))

        self.update_widgets()

    def update_widgets(self) -> None:
        """
        Recreate the ui based on self.param_selection
        """
        selection = self.params
        for f in [f for f in self.filters if f.active]:
            selection = f.filter(selection)
        self.param_selection = list(selection)
        self.param_selection.sort(key=lambda ap: ap.name)

        for widget in self.param_widgets:
            self.vbox.removeWidget(widget)

        every_other = False
        for param in self.param_selection:
            # create
            new_param_widget = AvatarParamWidget(
                param, self.on_value_changed, self.translate
            )

            # stylize
            new_param_widget.setAutoFillBackground(True)
            if every_other:
                new_param_widget.setPalette(self.odd_row_palette)
            else:
                new_param_widget.setPalette(self.even_row_palette)
            every_other = not every_other

            # store
            self.param_widgets.append(new_param_widget)
            self.vbox.addWidget(new_param_widget)
        return

    def on_value_changed(self, address, value):
        self.app.osc_client.send_message(address, value)

    def translate(self, text, callback):
        return self.app.translator.translate(text, callback)

    def translate_all_chinese(self):
        for widget in self.param_widgets:
            if utils.contains_chinese(widget.ap.name):
                widget.translate_name()
