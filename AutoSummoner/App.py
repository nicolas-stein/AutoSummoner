"""Entry point of the AutoSummoner applicatioàn"""
import sys

from PyQt5.QtWidgets import QApplication

from AutoSummoner.Ui import AutoChampionSelectWidget
from AutoSummoner.Ui.MainWindow import MainWindow


def run() -> int:
    """
    Entry point of AutoSummoner.
    Initializes the application, creates the main window, and starts the event loop.
    :return: The exit code of the application.
    """
    app = QApplication(sys.argv)

    sys.modules["AutoChampionSelectWidget"] = AutoChampionSelectWidget

    window = MainWindow()
    window.show()

    return app.exec()
