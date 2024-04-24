from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QFileDialog

if TYPE_CHECKING:
    from src.app import App


class BaseWindow(QMainWindow):
    app: App

    set_from_zh_action: QAction = None

    def __init__(self, app: App):
        super(BaseWindow, self).__init__()
        self.app = app

        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        self.pick_new_avatar_file = QAction("Pick New Avatar File")
        self.pick_new_avatar_file.triggered.connect(self.pick_new_avatar_file_action)
        file_menu.addAction(self.pick_new_avatar_file)

        self.delete_osc_files = QAction("Delete all OSC Files")
        self.delete_osc_files.triggered.connect(self.delete_osc_files_action)
        file_menu.addAction(self.delete_osc_files)

        translator_menu = menu.addMenu("Translation Settings")
        translator_menu.addAction(app.translator.set_from_zh_action)
        translator_menu.addAction(app.translator.set_from_ko_action)
        translator_menu.addAction(app.translator.set_from_jp_action)
        translator_menu.addAction(app.translator.set_from_auto_action)

    def pick_new_avatar_file_action(self):
        dialog = QFileDialog()
        # todo: add unix vrchat location i guess
        dialog.setDirectory(self.app.get_osc_directory())
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            filenames = dialog.selectedFiles()
            self.app.spawn_avatar_window(filenames[0])

    def delete_osc_files_action(self):
        osc_dir = QDir(self.app.get_osc_directory())
        osc_dir.removeRecursively()
