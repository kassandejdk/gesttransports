
import sys
import os
# Ensure we run from the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets, QtGui
from database import init_db
from login import LoginWindow
from dashboard import Dashboard
from styles import APP_STYLE


class AppController:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setApplicationName("GestTransport")
        self.app.setStyle("Fusion")
        self.app.setStyleSheet(APP_STYLE)

        # Initialize DB
        init_db()

        self.login_win = None
        self.dashboard = None

    def start(self):
        self._show_login()
        sys.exit(self.app.exec())

    def _show_login(self):
        self.login_win = LoginWindow()
        self.login_win.login_success.connect(self._on_login)
        self.login_win.show()

    def _on_login(self, user):
        self.login_win.close()
        self.dashboard = Dashboard(user)
        self.dashboard.logout_requested.connect(self._on_logout)
        self.dashboard.showMaximized()

    def _on_logout(self):
        self.dashboard.close()
        self._show_login()


if __name__ == "__main__":
    controller = AppController()
    controller.start()