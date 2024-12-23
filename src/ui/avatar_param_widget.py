from __future__ import annotations

from typing import Optional, Callable

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSizePolicy, QCheckBox

import src.my_translator
from src.vrc_osc.avatar import AvatarParam, OSCValueType


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
                    # increase by one and wrap around
                    new_value = int(self.ap.value)
                    if new_value == 255:
                        new_value = 0
                    else:
                        new_value += 1
                except ValueError:
                    new_value = int(0)
        self.ap.value = new_value

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
                    # reduce by one and wrap around
                    new_value = int(self.ap.value)
                    if new_value == 0:
                        new_value = 255
                    else:
                        new_value -= 1
                except ValueError:
                    new_value = int(0)
        self.ap.value = new_value

    def on_line_edit_edit_finished(self) -> None:
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
            self.ap.value = new_value
        else:
            print("LineEdit for " + self.ap.name + " wasn't converted to anything?" + self.ap.osc_type)

    def select_box_clicked(self, state):
        self.ap.selected = self.select_box.isChecked()

    def translate_name(self) -> None:
        if self.ap is None:
            return
        self.translator(self.ap.name, self._receive_translation)

    def on_value_update(self, new_value) -> None:
        """
        Handle value changes received by on_update_by_vrchat. Compare to on_edit_by_user
        1. store new value in data/ui
        """
        new_text = ""
        if self.ap.osc_type == OSCValueType.FLOAT:
            new_text = "{:.7f}".format(new_value)
        else:
            new_text = str(new_value)
        self.value_line_edit.setText(new_text)

    def _receive_translation(self, translation):
        if self.ap is None:
            return
        if translation == src.my_translator.MyTranslator.TRANSLATION_ERROR_SAME_LANGUAGE:
            translation = "already eng?"
        self.ap.translation = translation
        self._set_label_text()

    def set_param(self, param: AvatarParam) -> None:
        if self.ap is not None:
            self.ap.unsubscribe(self.on_value_update)
        self.ap = param
        self.osc_type_label.setText(OSCValueType.single_letter.get(self.ap.osc_type, "?"))
        self._set_label_text()
        self.select_box.setChecked(self.ap.selected)
        self.ap.subscribe(self.on_value_update)

    def _set_label_text(self):
        label_text = self.ap.name
        if self.ap.translation:
            label_text += " (" + self.ap.translation + ")"
        if not self.ap.input_address:
            label_text += " [RO]"
        self.label.setText(label_text)

    def __init__(self,
                 avatar_param: AvatarParam,
                 translator: Callable[[str, Callable[[str], None]], None]):
        super().__init__()
        self.ap: Optional[AvatarParam] = None
        self.translator = translator
        # defer self.ap until after ui creation

        self.hbox = QHBoxLayout()

        self.translate_btn = QPushButton("Translate")
        self.translate_btn.clicked.connect(self.translate_name)
        self.hbox.addWidget(self.translate_btn)

        self.select_box = QCheckBox("", self)
        self.select_box.setMinimumSize(24, 24)
        self.select_box.setMaximumSize(24, 24)
        self.select_box.stateChanged.connect(self.select_box_clicked)
        self.hbox.addWidget(self.select_box)

        self.label = QLabel("", self)
        self.label.setWordWrap(True)
        self.hbox.addWidget(self.label, stretch=100)

        self.hbox.addStretch()

        self.osc_type_label = QLabel("?")
        self.osc_type_label.setMinimumSize(12, 24)
        self.osc_type_label.setMaximumSize(12, 24)
        self.hbox.addWidget(self.osc_type_label)

        self.value_line_edit = QLineEdit()
        self.value_line_edit.setMaximumSize(72, 24)
        self.value_line_edit.editingFinished.connect(self.on_line_edit_edit_finished)
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

        self.set_param(avatar_param)
        self.ap.subscribe(self.on_value_update)

    def __del__(self):
        self.ap.unsubscribe(self.on_value_update)