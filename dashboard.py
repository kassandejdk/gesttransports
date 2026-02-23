from PySide6 import QtWidgets, QtGui, QtCore
from styles import APP_STYLE

class Dashboard(QtWidgets.QMainWindow):
    logout_requested = QtCore.Signal()

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setWindowTitle("GestTransport — Dashboard")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(APP_STYLE)
        self._pages = {}
        self._active_btn = None
        self._setup_ui()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QtWidgets.QFrame()
        sidebar.setFixedWidth(230)
        # sidebar.setStyleSheet("""
        #     QFrame {
        #         background-color: #ffffff;
               
        #     }
        # """)
        side_layout = QtWidgets.QVBoxLayout(sidebar)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(0)

        # Logo area
        logo_area = QtWidgets.QWidget()
        # logo_area.setStyleSheet("background:#010409;border-bottom:1px solid #d0d7de;")
        logo_layout = QtWidgets.QVBoxLayout(logo_area)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        logo_icon = QtWidgets.QLabel("🚌 GestTransport")
        logo_icon.setStyleSheet("font-size:15px;")
        # logo_text = QtWidgets.QLabel("")
        # logo_text.setStyleSheet("font-size:16px;font-weight:700;color:#82a2f5;margin-top:4px;")
        logo_sub = QtWidgets.QLabel(f"@{self.current_user.get('identifiant','')}")
        logo_sub.setStyleSheet("font-size:11px;color:#484f58;")
        logo_layout.addWidget(logo_icon)
        # logo_layout.addWidget(logo_text)
        logo_layout.addWidget(logo_sub)
        side_layout.addWidget(logo_area)

        # Nav buttons
        nav_scroll = QtWidgets.QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        nav_widget = QtWidgets.QWidget()
        nav_widget.setStyleSheet("background:transparent;")
        nav_layout = QtWidgets.QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(2)

        nav_items = [
            ("🏠", "Tableau de bord", "home"),
            ("🎫", "Tickets", "tickets"),
            ("🗺️", "Trajets", "trajets"),
            ("👤", "Clients", "clients"),
            ("🚗", "Chauffeurs", "chauffeurs"),
            ("🚌", "Véhicules", "vehicules"),
            ("🏢", "Sociétés", "societes"),
            ("👥", "Utilisateurs", "users"),
        ]

        self._nav_buttons = {}
        for icon, label, key in nav_items:
            btn = self._make_nav_btn(icon, label, key)
            self._nav_buttons[key] = btn
            nav_layout.addWidget(btn)

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_widget)
        side_layout.addWidget(nav_scroll)

        # User info + logout at bottom
        bottom = QtWidgets.QWidget()
        bottom.setStyleSheet("background:#f5f5f5;border-top:1px solid #d0d7de;padding:4px;")
        bottom_layout = QtWidgets.QVBoxLayout(bottom)
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        user_lbl = QtWidgets.QLabel(f"👤 {self.current_user.get('prenom','')} {self.current_user.get('nom','')}")
        user_lbl.setStyleSheet("color:#000;font-size:12px;font-weight:600;")
        role_lbl = QtWidgets.QLabel(f"  {self.current_user.get('role_nom','')}")
        role_lbl.setStyleSheet("color:#484f58;font-size:11px;")
        btn_logout = QtWidgets.QPushButton("🚪 Se déconnecter")
        btn_logout.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn_logout.setStyleSheet("""
            QPushButton {
                background:#f85149;color:#fff;
                border-radius:6px;padding:8px;font-size:12px;
                text-align:left;padding-left:12px;
            }
            QPushButton:hover{background:#82a2f5;}
        """)
        btn_logout.clicked.connect(self.logout_requested.emit)
        bottom_layout.addWidget(user_lbl)
        bottom_layout.addWidget(role_lbl)
        bottom_layout.addSpacing(8)
        bottom_layout.addWidget(btn_logout)
        side_layout.addWidget(bottom)

        main_layout.addWidget(sidebar)

        # ── Content area ──
        self.stack = QtWidgets.QStackedWidget()
        self.stack.setStyleSheet("background-color:#f5f7fa;")
        main_layout.addWidget(self.stack)

        # Load pages
        self._load_pages()

        # Default page
        self._switch_page("home")

    def _make_nav_btn(self, icon, label, key):
        btn = QtWidgets.QPushButton(f"  {icon}  {label}")
        btn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6e7781;
                border: none;
                border-radius: 6px;
                padding: 10px 12px;
                text-align: left;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #1f3a6e;
                color: #e6edf3;
            }
            QPushButton:checked {
                background: #1f3a6e;
                color: #82a2f5;
                font-weight: 700;
            }
        """)
        btn.clicked.connect(lambda: self._switch_page(key))
        return btn

    def _load_pages(self):
        from dashboard_home import DashboardHome
        from users import UsersPage
        from trajets import TrajetsPage
        from tickets import TicketsPage
        from chauffeurs_vehicules import ChauffeursPage, VehiculesPage
        from clients_societes import ClientsPage, SocietePage

        pages = {
            "home": DashboardHome(self.current_user),
            "tickets": TicketsPage(self.current_user),
            "trajets": TrajetsPage(self.current_user),
            "clients": ClientsPage(self.current_user),
            "chauffeurs": ChauffeursPage(self.current_user),
            "vehicules": VehiculesPage(self.current_user),
            "societes": SocietePage(self.current_user),
            "users": UsersPage(self.current_user),
        }
        for key, page in pages.items():
            scroll = QtWidgets.QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            # scroll.setStyleSheet("QScrollArea{border:none;background:#0d1117;}")
            self.stack.addWidget(scroll)
            self._pages[key] = (page, scroll)

    def _switch_page(self, key):
        # Deactivate previous
        if self._active_btn:
            self._active_btn.setChecked(False)
        # Activate new
        btn = self._nav_buttons.get(key)
        if btn:
            btn.setChecked(True)
            self._active_btn = btn
        if key in self._pages:
            _, scroll = self._pages[key]
            self.stack.setCurrentWidget(scroll)
            # Refresh dashboard stats when returning
            if key == "home":
                self._pages["home"][0].refresh()

    def refresh_page(self, key):
        if key in self._pages:
            page, _ = self._pages[key]
            if hasattr(page, 'load_data'):
                page.load_data()