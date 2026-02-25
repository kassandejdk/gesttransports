from PySide6 import QtWidgets, QtCore, QtGui
from database import get_connection
from styles import section_title

class DashboardHome(QtWidgets.QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(24)

        # message de bienvenue
        welcome = QtWidgets.QLabel(f"Bonjour, {self.current_user.get('prenom','')} {self.current_user.get('nom','')} 👋")
        welcome.setStyleSheet("font-size:22px;font-weight:700;color:#1a1f2e;")
        layout.addWidget(welcome)

        sub = QtWidgets.QLabel("Vue d'ensemble de votre activité")
        sub.setStyleSheet("color:#6e7781;font-size:13px;margin-top:-16px;")
        layout.addWidget(sub)

        self.stats_layout = QtWidgets.QHBoxLayout()
        self.stats_layout.setSpacing(16)
        layout.addLayout(self.stats_layout)

        layout.addWidget(section_title("📋 Derniers tickets vendus"))
        from styles import make_table
        self.recent_table = make_table(["#", "Client", "Trajet", "Montant", "Date", "Statut"])
        self.recent_table.setMaximumHeight(260)
        layout.addWidget(self.recent_table)

        layout.addWidget(section_title("🗓️ Prochains trajets"))
        self.upcoming_table = make_table(["Départ", "Arrivée", "H. Départ", "H. Arrivée", "Chauffeur", "Véhicule"])
        self.upcoming_table.setMaximumHeight(200)
        layout.addWidget(self.upcoming_table)
        layout.addStretch()

    def refresh(self):
        self._load_stats()
        self._load_recent_tickets()
        self._load_upcoming_trips()

    def _load_stats(self):
        # Clear
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        conn = get_connection()
        nb_tickets = conn.execute("SELECT COUNT(*) FROM ticket WHERE statut='payé'").fetchone()[0]
        total_rev = conn.execute("SELECT IFNULL(SUM(montant),0) FROM ticket WHERE statut='payé'").fetchone()[0]
        nb_trajets = conn.execute("SELECT COUNT(*) FROM trajet").fetchone()[0]
        nb_clients = conn.execute("SELECT COUNT(*) FROM client").fetchone()[0]
        nb_chauffeurs = conn.execute("SELECT COUNT(*) FROM chauffeur").fetchone()[0]
        nb_vehicules = conn.execute("SELECT COUNT(*) FROM vehicule").fetchone()[0]
        conn.close()

        stats = [
            ("🎫", "Tickets vendus", str(nb_tickets), "#fff", "#82a2f5"),
            ("💰", "Recettes", f"{total_rev:.0f} FCFA", "#fff", "#82a2f5"),
            ("🗺️", "Trajets", str(nb_trajets), "#fff", "#82a2f5"),
            ("👤", "Clients", str(nb_clients), "#fff", "#82a2f5"),
            ("🚗", "Chauffeurs", str(nb_chauffeurs), "#fff", "#82a2f5"),
            ("🚌", "Véhicules", str(nb_vehicules), "#fff", "#82a2f5"),
        ]
        for icon, label, value, bg, fg in stats:
            card = QtWidgets.QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border-radius: 10px;
                    padding: 4px;
                }}
            """)
            cl = QtWidgets.QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            cl.setSpacing(4)
            top = QtWidgets.QHBoxLayout()
            icon_lbl = QtWidgets.QLabel(icon)
            icon_lbl.setStyleSheet("font-size:22px;")
            top.addWidget(icon_lbl)
            top.addStretch()
            cl.addLayout(top)
            val_lbl = QtWidgets.QLabel(value)
            val_lbl.setStyleSheet(f"font-size:20px;font-weight:700;color:{fg};")
            cl.addWidget(val_lbl)
            lbl = QtWidgets.QLabel(label)
            lbl.setStyleSheet("color:#6e7781;font-size:11px;")
            cl.addWidget(lbl)
            self.stats_layout.addWidget(card)

    def _load_recent_tickets(self):
        conn = get_connection()
        rows = conn.execute("""
            SELECT tk.id, cl.nom||' '||cl.prenom,
                   vd.nom||' → '||va.nom, tk.montant, tk.date, tk.statut
            FROM ticket tk
            LEFT JOIN client cl ON tk.client_id=cl.id
            LEFT JOIN trajet t ON tk.trajet_id=t.id
            LEFT JOIN ville vd ON t.ville_depart_id=vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id=va.id
            ORDER BY tk.id DESC LIMIT 10
        """).fetchall()
        conn.close()
        self.recent_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(f"#{val:06d}" if j == 0 else str(val) if val else "—")
                if j == 3:
                    item.setText(f"{val:,.0f} FCFA")
                if j == 5:
                    item.setForeground(QtGui.QColor("#3fb950") if val == "payé" else QtGui.QColor("#f85149"))
                self.recent_table.setItem(i, j, item)

    def _load_upcoming_trips(self):
        conn = get_connection()
        rows = conn.execute("""
            SELECT vd.nom, va.nom, t.heure_depart, t.heure_arrivee,
                   c.nom||' '||c.prenom, v.matricule
            FROM trajet t
            LEFT JOIN ville vd ON t.ville_depart_id=vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id=va.id
            LEFT JOIN chauffeur c ON t.chauffeur_id=c.id
            LEFT JOIN vehicule v ON t.vehicule_id=v.id
            WHERE t.heure_depart >= datetime('now')
            ORDER BY t.heure_depart ASC LIMIT 5
        """).fetchall()
        conn.close()
        self.upcoming_table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.upcoming_table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else "—"))