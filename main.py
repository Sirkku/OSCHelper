from __future__ import annotations
import sys
from PyQt6.QtWidgets import *
from src.app import App


def main():
    app = QApplication(sys.argv)
    my_app = App()
    my_app.run()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
