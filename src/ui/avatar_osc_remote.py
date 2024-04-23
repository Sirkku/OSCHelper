from __future__ import annotations

import json

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QAction
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QVBoxLayout, QScrollArea

import src.my_translator
import src.ui.base_window
from src import utils
from src.data.avatar_param import AvatarParam, OSCValueType


class AvatarParamWidget(QWidget):
    def btn_set1_pressed(self):
        if self.ap is None:
            return
        new_value = None
        match self.ap.osc_type:
            case OSCValueType.FLOAT:
                new_value = 1.0
            case OSCValueType.BOOL:
                new_value = True
            case OSCValueType.INT:
                try:
                    # reduce number by one if in range
                    new_value = int(self.ap.value)
                    if new_value == 255:
                        new_value = 0
                    else:
                        new_value += 1
                except ValueError:
                    new_value = int(0)
        self.on_edit_by_user(new_value)

    def btn_set0_pressed(self):
        if self.ap is None:
            return
        new_value = None
        match self.ap.osc_type:
            case OSCValueType.FLOAT:
                new_value = 0.0
            case OSCValueType.BOOL:
                new_value = False
            case OSCValueType.INT:
                try:
                    # reduce number by one if in range
                    new_value = int(self.ap.value)
                    if new_value == 0:
                        new_value = 255
                    else:
                        new_value -= 1
                except ValueError:
                    new_value = int(0)
        self.on_edit_by_user(new_value)

    def lineeditupdate(self) -> None:
        if self.ap is None:
            return
        new_value = None
        match self.ap.osc_type:
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
            self.on_edit_by_user(new_value)
        else:
            print("LineEdit for " + self.ap.name + " wasn't converted to anything?" + self.ap.osc_type)

    def on_edit_by_user(self, new_value: int | bool | float) -> None:
        if self.ap is None:
            return
        self.ap.value = new_value
        self.value_line_edit.setText(str(new_value))
        self.callback(self.ap.input_address, new_value)

    def on_update_by_remote(self, new_value: int | bool | float) -> None:
        if self.ap is None:
            return
        self.ap.value = new_value
        self.value_line_edit.setText(str(new_value))

    def translate_name(self) -> None:
        if self.ap is None:
            return
        self.translator(self.ap.name, self.receive_translation)

    def receive_translation(self, translation):
        if self.ap is None:
            return
        if translation == src.my_translator.MyTranslator.TRANSLATION_ERROR_SAME_LANGUAGE:
            translation = "already eng?"
        self.ap.translation = translation
        self.label.setText(self.ap.name + " (" + self.ap.translation + ")")

    def set_param(self, param: AvatarParam) -> None:
        self.ap = param
        self.osc_type_label.setText(OSCValueType.single_letter.get(self.ap.osc_type, "?"))
        label_text = self.ap.name
        if self.ap.translation is not None and self.ap.translation != "":
            label_text += " (" + self.ap.translation + ")"
        self.label.setText(label_text)

    def __init__(self, avatar_param, call_back, translator):
        super().__init__()
        self.callback = call_back
        self.translator = translator
        self.ap = avatar_param

        # UI
        self.hbox = QHBoxLayout()

        self.translate_btn = QPushButton("Translate")
        self.translate_btn.clicked.connect(self.translate_name)

        self.hbox.addWidget(self.translate_btn)
        self.label = QLabel(self.ap.name)
        self.hbox.addWidget(self.label)

        self.hbox.addStretch()

        self.osc_type_label = QLabel("?")
        self.osc_type_label.setMinimumSize(12, 24)
        self.osc_type_label.setMaximumSize(12, 24)
        self.hbox.addWidget(self.osc_type_label)

        self.value_line_edit = QLineEdit()
        self.value_line_edit.setText(str(self.ap.value))
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
        self.params = []

        # centerpiece
        vbox = QVBoxLayout()
        vbox.setSpacing(0)

        for j_param in avatar_json["parameters"]:
            if "input" not in j_param:
                continue
            param = AvatarParam()
            param.load_from_json(j_param)
            self.params.append(param)
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

    def translate(self, text, callback):
        return self.app.translator.translate(text, callback)

    def translate_all_chinese(self):
        for widget in self.param_widgets:
            if utils.contains_chinese(widget.ap.name):
                widget.translate_name()


class AvatarOSCRemote(src.ui.base_window.BaseWindow):
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
            j = json.load(file)
            self.central_widget = AvatarWidget(self.app, j)
            self.setCentralWidget(self.central_widget)
            return True
