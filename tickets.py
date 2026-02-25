from PySide6 import QtWidgets, QtCore, QtPrintSupport, QtGui
from database import get_connection
from styles import primary_btn, section_title, make_table
from datetime import datetime

class TicketsPage(QtWidgets.QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self._setup_ui()
        self.load_data()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        hdr = QtWidgets.QHBoxLayout()
        hdr.addWidget(section_title("🎫 Tickets de voyage"))
        hdr.addStretch()
        btn_add = primary_btn("+ Vendre un ticket")
        btn_add.clicked.connect(self.open_form)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        flt = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par client, trajet...")
        self.search_input.textChanged.connect(lambda t: self.load_data(t))
        flt.addWidget(self.search_input)
        self.filter_status = QtWidgets.QComboBox()
        self.filter_status.addItems(["Tous", "payé", "annulé"])
        self.filter_status.currentTextChanged.connect(lambda: self.load_data(self.search_input.text()))
        flt.addWidget(self.filter_status)
        layout.addLayout(flt)

        self.table = make_table(["ID", "Date", "Client", "Trajet", "Siège", "Montant", "Statut", "Agent", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        query = """
            SELECT tk.id, tk.date,
                   cl.nom||' '||cl.prenom as client,
                   vd.nom||' → '||va.nom as trajet,
                   tk.siege, tk.montant, tk.statut,
                   u.nom||' '||u.prenom as agent
            FROM ticket tk
            LEFT JOIN client cl ON tk.client_id = cl.id
            LEFT JOIN trajet t ON tk.trajet_id = t.id
            LEFT JOIN ville vd ON t.ville_depart_id = vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id = va.id
            LEFT JOIN user u ON tk.user_id = u.id
            WHERE 1=1
        """
        params = []
        if search:
            query += " AND (cl.nom LIKE ? OR cl.prenom LIKE ? OR vd.nom LIKE ? OR va.nom LIKE ?)"
            s = f"%{search}%"
            params += [s, s, s, s]
        st = self.filter_status.currentText()
        if st != "Tous":
            query += " AND tk.statut=?"
            params.append(st)
        query += " ORDER BY tk.id DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(val) if val else "—")
                if j == 6:  # statut
                    item.setForeground(QtGui.QColor("#3fb950") if val == "payé" else QtGui.QColor("#f85149"))
                self.table.setItem(i, j, item)
            aw = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(aw)
            al.setContentsMargins(4, 2, 4, 2)
            btn_p = QtWidgets.QPushButton("🖨️ Imprimer")
            btn_p.setStyleSheet("background:#21262d;color:#e6edf3;border:none;border-radius:4px;padding:4px 8px;font-size:11px;")
            btn_a = QtWidgets.QPushButton("❌ Annuler")
            btn_a.setStyleSheet("background:#3d1c1c;color:#f85149;border:none;border-radius:4px;padding:4px 8px;font-size:11px;")
            tid = row[0]
            btn_p.clicked.connect(lambda _, id=tid: self.print_ticket(id))
            btn_a.clicked.connect(lambda _, id=tid: self.cancel_ticket(id))
            al.addWidget(btn_p)
            al.addWidget(btn_a)
            self.table.setCellWidget(i, 8, aw)

    def cancel_ticket(self, tid):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Annuler ce ticket ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("UPDATE ticket SET statut='annulé' WHERE id=?", (tid,))
            conn.commit()
            conn.close()
            self.load_data()

    def print_ticket(self, tid):
        conn = get_connection()
        row = conn.execute("""
            SELECT tk.*, cl.nom as cl_nom, cl.prenom as cl_prenom, cl.telephone as cl_tel,
                   vd.nom as v_dep, va.nom as v_arr,
                   t.heure_depart, t.heure_arrivee, t.prix,
                   c.nom||' '||c.prenom as chauffeur,
                   veh.matricule as vehicule
            FROM ticket tk
            LEFT JOIN client cl ON tk.client_id = cl.id
            LEFT JOIN trajet t ON tk.trajet_id = t.id
            LEFT JOIN ville vd ON t.ville_depart_id = vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id = va.id
            LEFT JOIN chauffeur c ON t.chauffeur_id = c.id
            LEFT JOIN vehicule veh ON t.vehicule_id = veh.id
            WHERE tk.id=?
        """, (tid,)).fetchone()
        conn.close()
        if not row:
            return
        r = dict(row)
        html = f"""
        <html><body style="font-family:Arial;font-size:14px;margin:20px;">
        <div style="border:2px solid #333;padding:20px;max-width:500px;margin:auto;">
            <h2 style="text-align:center;color:#1a3a8a;">🚌 GestTransport</h2>
            <h3 style="text-align:center;border-bottom:1px solid #ccc;padding-bottom:10px;">TICKET DE VOYAGE</h3>
            <table width="100%" style="margin-top:10px;">
                <tr><td><b>N° Ticket:</b></td><td>#{r['id']:06d}</td></tr>
                <tr><td><b>Date achat:</b></td><td>{r['date']}</td></tr>
                <tr><td><b>Client:</b></td><td>{r['cl_nom']} {r['cl_prenom']}</td></tr>
                <tr><td><b>Téléphone:</b></td><td>{r['cl_tel'] or '—'}</td></tr>
                <tr><td colspan="2" style="padding-top:10px;"><b>──────── TRAJET ────────</b></td></tr>
                <tr><td><b>Départ:</b></td><td>{r['v_dep']}</td></tr>
                <tr><td><b>Arrivée:</b></td><td>{r['v_arr']}</td></tr>
                <tr><td><b>H. Départ:</b></td><td>{r['heure_depart']}</td></tr>
                <tr><td><b>H. Arrivée:</b></td><td>{r['heure_arrivee']}</td></tr>
                <tr><td><b>Siège N°:</b></td><td>{r['siege']}</td></tr>
                <tr><td><b>Chauffeur:</b></td><td>{r['chauffeur'] or '—'}</td></tr>
                <tr><td><b>Véhicule:</b></td><td>{r['vehicule'] or '—'}</td></tr>
                <tr><td colspan="2" style="padding-top:10px;"><b>──────── PAIEMENT ────────</b></td></tr>
                <tr><td><b>Montant:</b></td><td style="font-size:16px;font-weight:bold;color:#1a3a8a;">{r['montant']:,.0f} FCFA</td></tr>
                <tr><td><b>Statut:</b></td><td style="color:{'green' if r['statut']=='payé' else 'red'};">{r['statut'].upper()}</td></tr>
            </table>
            <p style="text-align:center;margin-top:20px;font-size:11px;color:#888;">
                Bon voyage ! Merci de votre confiance.<br>
                Ce ticket est valable uniquement pour le trajet indiqué.
            </p>
        </div>
        </body></html>
        """
        dlg = PrintPreviewDialog(self, html, f"Ticket #{tid:06d}")
        dlg.exec()

    def open_form(self):
        dlg = TicketFormDialog(self, self.current_user)
        if dlg.exec():
            self.load_data()


class PrintPreviewDialog(QtWidgets.QDialog):
    def __init__(self, parent, html, title="Document"):
        super().__init__(parent)
        self.html = html
        self.setWindowTitle(f"Aperçu — {title}")
        self.setMinimumSize(600, 700)
        self.setStyleSheet("QDialog{background:#fff;}")
        layout = QtWidgets.QVBoxLayout(self)
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setHtml(html)
        self.text_edit.setStyleSheet("background:white;color:black;border:none;")
        layout.addWidget(self.text_edit)
        btn_row = QtWidgets.QHBoxLayout()
        btn_print = primary_btn("🖨️ Imprimer")
        btn_print.clicked.connect(self._print)
        btn_close = QtWidgets.QPushButton("Fermer")
        btn_close.setStyleSheet("background:#21262d;color:#e6edf3;border:none;border-radius:6px;padding:8px 18px;")
        btn_close.clicked.connect(self.reject)
        btn_row.addStretch()
        btn_row.addWidget(btn_print)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _print(self):
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        dlg = QtPrintSupport.QPrintDialog(printer, self)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.text_edit.print_(printer)


class TicketFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.setWindowTitle("Vendre un ticket")
        self.setMinimumWidth(480)
        self.setStyleSheet("QDialog{background:#f5f7fa;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        self._setup_ui()

    def _setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # Client section
        client_row = QtWidgets.QHBoxLayout()
        self.client_cb = QtWidgets.QComboBox()
        self._load_clients()
        btn_new_client = QtWidgets.QPushButton("+ Nouveau")
        btn_new_client.setStyleSheet("background:#21262d;color:#e6edf3;border:none;border-radius:4px;padding:6px;")
        btn_new_client.clicked.connect(self._add_client)
        client_row.addWidget(self.client_cb)
        client_row.addWidget(btn_new_client)

        # Trajet
        self.trajet_cb = QtWidgets.QComboBox()
        self._load_trajets()
        self.trajet_cb.currentIndexChanged.connect(self._update_montant)

        self.siege = QtWidgets.QSpinBox()
        self.siege.setMinimum(1)
        self.siege.setMaximum(200)
        self.montant = QtWidgets.QDoubleSpinBox()
        self.montant.setMaximum(9999999)
        self.montant.setSuffix(" FCFA")

        layout.addRow("Client *", client_row)
        layout.addRow("Trajet *", self.trajet_cb)
        layout.addRow("N° Siège *", self.siege)
        layout.addRow("Montant", self.montant)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)

    def _load_clients(self):
        self.client_cb.clear()
        conn = get_connection()
        clients = conn.execute("SELECT id, nom, prenom, telephone FROM client ORDER BY nom").fetchall()
        conn.close()
        for c in clients:
            self.client_cb.addItem(f"{c['nom']} {c['prenom']} ({c['telephone'] or '—'})", c['id'])

    def _load_trajets(self):
        self.trajet_cb.clear()
        conn = get_connection()
        trajets = conn.execute("""
            SELECT t.id, vd.nom||' → '||va.nom as label, t.prix, t.heure_depart
            FROM trajet t
            LEFT JOIN ville vd ON t.ville_depart_id=vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id=va.id
            ORDER BY t.heure_depart DESC
        """).fetchall()
        conn.close()
        for t in trajets:
            self.trajet_cb.addItem(f"{t['label']} ({t['heure_depart']})", (t['id'], t['prix']))

    def _update_montant(self):
        data = self.trajet_cb.currentData()
        if data:
            self.montant.setValue(data[1] or 0)

    def _add_client(self):
        dlg = ClientQuickAdd(self)
        if dlg.exec():
            self._load_clients()
            self.client_cb.setCurrentIndex(self.client_cb.count() - 1)

    def _save(self):
        if not self.client_cb.currentData() or not self.trajet_cb.currentData():
            QtWidgets.QMessageBox.warning(self, "Erreur", "Client et trajet sont obligatoires.")
            return
        trajet_data = self.trajet_cb.currentData()
        conn = get_connection()
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute("""INSERT INTO ticket (date, siege, montant, statut, trajet_id, client_id, user_id)
                        VALUES (?,?,?,?,?,?,?)""",
                     (now, self.siege.value(), self.montant.value(), "payé",
                      trajet_data[0], self.client_cb.currentData(), self.current_user['id']))
        conn.commit()
        conn.close()
        self.accept()


class ClientQuickAdd(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Nouveau client")
        self.setStyleSheet("QDialog{background:#f5f7fa;color:#e6edf3;} QLabel{color:#8b949e;}")
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.nom = QtWidgets.QLineEdit()
        self.prenom = QtWidgets.QLineEdit()
        self.tel = QtWidgets.QLineEdit()
        layout.addRow("Nom *", self.nom)
        layout.addRow("Prénom *", self.prenom)
        layout.addRow("Téléphone", self.tel)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)

    def _save(self):
        nom = self.nom.text().strip()
        prenom = self.prenom.text().strip()
        if not nom or not prenom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom et prénom obligatoires.")
            return
        conn = get_connection()
        conn.execute("INSERT INTO client (nom,prenom,telephone) VALUES (?,?,?)", (nom, prenom, self.tel.text()))
        conn.commit()
        conn.close()
        self.accept()