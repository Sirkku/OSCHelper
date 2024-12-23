from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from src.vrc_osc.avatar import AvatarParam


class ToggleButton(QWidget):
    def __init__(self, ap: AvatarParam, state_on=True, state_off=False, parent=None):
        super(QWidget, self).__init__(parent)
        self.state_on = state_on
        self.state_off = state_off
        self.ap = ap
        self.my_layout = QHBoxLayout(self)
        self.button = QPushButton(self)
        self.button.setCheckable(True)
        self.button.setChecked(self.ap.value)
        self.button.clicked.connect(self.btn_clicked)
        self.my_layout.addWidget(self.button)
        self.setLayout(self.my_layout)

    def btn_clicked(self):
        if self.button.isChecked():
            self.ap.value = self.state_on
        else:
            self.ap.value = self.state_off


