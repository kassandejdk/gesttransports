from PySide6 import QtWidgets, QtGui, QtCore
from database import authenticate

class LoginWindow(QtWidgets.QWidget):
    login_success = QtCore.Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GestTransport — Connexion")
        self.setFixedSize(660, 760)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                color: #1a1f2e;
                font-family: 'Poppins', sans-serif;
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(0)

        icon_lbl = QtWidgets.QLabel("🚌")
        icon_lbl.setAlignment(QtCore.Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 52px; margin-bottom: 8px;")
        layout.addWidget(icon_lbl)

        title = QtWidgets.QLabel("GestTransport")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #6e7781; margin-bottom: 4px;")
        layout.addWidget(title)

        sub = QtWidgets.QLabel("Gérez vos agences de transport")
        sub.setAlignment(QtCore.Qt.AlignCenter)
        sub.setStyleSheet("font-size: 12px; color: #8b949e; margin-bottom: 36px;")
        layout.addWidget(sub)

        card = QtWidgets.QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(24, 24, 24, 24)

        card_layout.addWidget(self._label("Identifiant"))
        self.field_id = self._input("jdk")
        card_layout.addWidget(self.field_id)

        card_layout.addWidget(self._label("Mot de passe"))
        self.field_pw = self._input("••••••••", password=True)
        card_layout.addWidget(self.field_pw)

        self.error_lbl = QtWidgets.QLabel("")
        self.error_lbl.setStyleSheet("color: #f85149; font-size: 12px;")
        self.error_lbl.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(self.error_lbl)

        btn = QtWidgets.QPushButton("Se connecter")
        btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn.setStyleSheet("""
            QPushButton {
                background-color: #82a2f5;
                color: #0d1117;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: 700;
                height: 40px;
            }
            QPushButton:hover { background-color: #9bb5ff; }
            QPushButton:pressed { background-color: #6b8de0; }
        """)
        btn.clicked.connect(self._do_login)
        card_layout.addWidget(btn)

        layout.addWidget(card)

        hint = QtWidgets.QLabel("Compte par défaut : admin / admin123")
        hint.setAlignment(QtCore.Qt.AlignCenter)
        hint.setStyleSheet("color: #484f58; font-size: 11px; margin-top: 16px;")
        layout.addWidget(hint)

        self.field_pw.returnPressed.connect(self._do_login)
        self.field_id.returnPressed.connect(self._do_login)

    def _label(self, text):
        lbl = QtWidgets.QLabel(text)
        lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #8b949e; margin-bottom: 2px;")
        return lbl

    def _input(self, placeholder="", password=False):
        f = QtWidgets.QLineEdit()
        f.setPlaceholderText(placeholder)
        if password:
            f.setEchoMode(QtWidgets.QLineEdit.Password)
        f.setStyleSheet("""
            QLineEdit {
                background-color: #f5f7fa;
                border: 1px solid #d0d7de;
                border-radius: 8px;
                padding: 14px 12px;
                min-height: 30px;
                font-size: 13px;
                color: #1a1f2e;
            }
            QLineEdit:focus { border: 1px solid #82a2f5; }
        """)
        return f

    def _do_login(self):
        ident = self.field_id.text().strip()
        pw = self.field_pw.text()
        if not ident or not pw:
            self.error_lbl.setText("Veuillez remplir tous les champs.")
            return
        user = authenticate(ident, pw)
        if user:
            self.login_success.emit(user)
        else:
            self.error_lbl.setText("Identifiant ou mot de passe incorrect.")
            self.field_pw.clear()