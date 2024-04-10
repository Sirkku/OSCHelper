from __future__ import annotations

import json
import os

from PyQt6.QtCore import Qt, QDir, QFile
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QScrollArea

import base_window
import my_translator
import utils


class OSCValueType:
    FLOAT: str = "Float"
    BOOL: str = "Bool"
    INT: str = "Int"
    UNDEFINED: str = "Undefined"

    single_letter = {
        FLOAT: "F",
        BOOL: "B",
        INT: "I",
        UNDEFINED: "?"
    }


class AvatarParamWidget(QWidget):
    def btn_set1_pressed(self):
        new_value = None
        match self.osc_type:
            case OSCValueType.FLOAT:
                new_value = 1.0
            case OSCValueType.BOOL:
                new_value = True
            case OSCValueType.INT:
                try:
                    # reduce number by one if in range
                    new_value = int(self.value)
                    if new_value == 255:
                        new_value = 0
                    else:
                        new_value += 1
                except ValueError:
                    new_value = int(0)
        self.update_value(new_value)

    def btn_set0_pressed(self):
        new_value = None
        match self.osc_type:
            case OSCValueType.FLOAT:
                new_value = 0.0
            case OSCValueType.BOOL:
                new_value = False
            case OSCValueType.INT:
                try:
                    # reduce number by one if in range
                    new_value = int(self.value)
                    if new_value == 0:
                        new_value = 255
                    else:
                        new_value -= 1
                except ValueError:
                    new_value = int(0)
        self.update_value(new_value)

    def lineeditupdate(self) -> None:
        new_value = None
        match self.osc_type:
            case OSCValueType.FLOAT:
                try:
                    new_value = float(self.value_line_edit.text())
                except ValueError:
                    new_value = 0.0
            case OSCValueType.BOOL:
                try:
                    new_value = bool(self.value_line_edit.text())
                except ValueError:
                    new_value = False
            case OSCValueType.INT:
                try:
                    new_value = int(self.value_line_edit.text())
                except ValueError:
                    new_value = 0
        if new_value is not None:
            self.update_value(new_value)
        else:
            print("LineEdit for " + self.name + " wasn't converted to anything?" + self.osc_type)

    def update_value(self, new_value: int | bool | float) -> None:
        self.value = new_value
        self.value_line_edit.setText(str(new_value))
        self.callback(self.input_address, new_value)

    def translate_name(self) -> None:
        translation = self.translator(self.name)
        if translation == my_translator.MyTranslator.TRANSLATION_ERROR_SAME_LANGUAGE:
            translation = "already eng?"
        self.translation = translation
        self.label.setText(self.name + " (" + self.translation + ")")

    def __init__(self, json_data, call_back, translator):
        super().__init__()
        self.callback = call_back
        self.translator = translator
        # default values for json data
        self.name = ""
        self.translation = ""
        self.input_address = ""
        self.output_address = ""
        self.osc_type = OSCValueType.UNDEFINED

        # try to load values from the json
        if j_name := json_data.get('name'):
            self.name = j_name
        if j_input := json_data.get('input'):
            if j_in_add := j_input.get('address'):
                self.input_address = j_in_add
            if j_in_type := j_input.get('type'):
                self.osc_type = j_in_type
        if j_output := json_data.get('output'):
            if j_out_addr := j_output.get('address'):
                self.output_address = j_out_addr
            if j_out_type := j_output.get('type'):
                self.osc_type = j_out_type

        # calculate values
        self.value = {
            OSCValueType.INT: int(0),
            OSCValueType.FLOAT: 0.0,
            OSCValueType.BOOL: False
        }.get(self.osc_type, 0.0)

        # UI
        self.hbox = QHBoxLayout()

        self.translate_btn = QPushButton("Translate")
        self.translate_btn.clicked.connect(self.translate_name)

        self.hbox.addWidget(self.translate_btn)
        self.label = QLabel(self.name)
        self.hbox.addWidget(self.label)

        self.hbox.addStretch()

        self.osc_type_label = QLabel(OSCValueType.single_letter.get(self.osc_type, "?"))
        self.osc_type_label.setMinimumSize(12, 24)
        self.osc_type_label.setMaximumSize(12, 24)
        self.hbox.addWidget(self.osc_type_label)

        self.value_line_edit = QLineEdit()
        self.value_line_edit.setText(str(self.value))
        self.value_line_edit.setMaximumSize(72, 24)
        self.value_line_edit.editingFinished.connect(self.lineeditupdate)
        self.hbox.addWidget(self.value_line_edit)

        self.set0_btn = QPushButton('0')
        self.set0_btn.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.set0_btn.setMinimumSize(24, 24)
        self.set0_btn.setMaximumSize(24, 24)
        self.set0_btn.pressed.connect(self.btn_set0_pressed)
        self.hbox.addWidget(self.set0_btn)

        self.set1_btn = QPushButton('1')
        self.set1_btn.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.set1_btn.setMinimumSize(24, 24)
        self.set1_btn.setMaximumSize(24, 24)
        self.set1_btn.pressed.connect(self.btn_set1_pressed)
        self.hbox.addWidget(self.set1_btn)

        self.hbox.setContentsMargins(4, 4, 4, 4)
        self.setLayout(self.hbox)


class AvatarWidget(QWidget):
    def __init__(self, app, avatar_json):
        super().__init__()
        self.app = app
        self.param_widgets = []

        # Center Piece
        vbox = QVBoxLayout()
        vbox.setSpacing(0)

        for param in avatar_json["parameters"]:
            if "input" not in param:
                continue
            new_param_widget = AvatarParamWidget(
                param, self.on_value_changed, self.translate
            )
            self.param_widgets.append(new_param_widget)

        pal1 = QPalette()
        pal2 = QPalette()
        pal1.setColor(QPalette.ColorRole.Window, QColor(0xFF, 0xFF, 0xFF))
        pal2.setColor(QPalette.ColorRole.Window, QColor(0xDD, 0xDD, 0xDD))

        every_other = False
        for widget in self.param_widgets:
            if every_other:
                widget.setPalette(pal1)
            else:
                widget.setPalette(pal2)
            every_other = not every_other
            widget.setAutoFillBackground(True)
            vbox.addWidget(widget)

        # Add Scroll Bar
        dummy_widget = QWidget()
        dummy_widget.setLayout(vbox)

        scrollview = QScrollArea(self)
        scrollview.setWidget(dummy_widget)
        scrollview.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollview.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollview.setWidgetResizable(True)

        hbox = QHBoxLayout()
        hbox.addWidget(scrollview)
        self.setLayout(hbox)

    def on_value_changed(self, address, value):
        self.app.osc_client.send_message(address, value)

    def translate(self, text):
        return self.app.translator.translate(text)

    def translate_all_chinese(self):
        for widget in self.param_widgets:
            if utils.contains_chinese(widget.name):
                widget.translate_name()


class AvatarOSCRemote(base_window.BaseWindow):
    translate_all_chinese: QAction
    central_widget: AvatarWidget | None

    def __init__(self, app):
        super(AvatarOSCRemote, self).__init__(app)
        self.setWindowTitle("Vrchat OSC Tool")
        self.osc_client = app.osc_client
        self.central_widget = None
        menu_bar = self.menuBar()
        tool_menu = menu_bar.addMenu("Tools")

        self.translate_all_chinese = QAction("Translate all chinese")
        self.translate_all_chinese.triggered.connect(self.translate_all_chinese_action)
        tool_menu.addAction(self.translate_all_chinese)

    def translate_all_chinese_action(self):
        if self.central_widget:
            self.central_widget.translate_all_chinese()

    def send_osc_message(self, address, value):
        self.osc_client.send_message(address, value)

    def load_file(self, filename):
        with open(filename, 'r', encoding='utf-8-sig') as file:
            j = json.load(open(filename, 'r', encoding='utf-8-sig'))
            self.central_widget = AvatarWidget(self.app, j)
            self.setCentralWidget(self.central_widget)
