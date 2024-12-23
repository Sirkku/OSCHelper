from __future__ import annotations
import sys
from PyQt6.QtWidgets import *
import src.app


def main():


    app = QApplication(sys.argv)
    my_app = src.app.App()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
