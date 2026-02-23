from PySide6 import QtWidgets
from database import get_connection
from styles import primary_btn, section_title, make_table

# ======================= CLIENTS =======================

class ClientsPage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("👤 Clients"))
        hdr.addStretch()
        btn = primary_btn("+ Ajouter")
        btn.clicked.connect(self.open_form)
        hdr.addWidget(btn)
        layout.addLayout(hdr)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher...")
        self.search.textChanged.connect(lambda t: self.load_data(t))
        layout.addWidget(self.search)
        self.table = make_table(["ID", "Nom", "Prénom", "Téléphone", "Nb tickets", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        query = """SELECT c.id,c.nom,c.prenom,c.telephone,COUNT(tk.id) as nb_tickets
                   FROM client c LEFT JOIN ticket tk ON c.id=tk.client_id"""
        params = []
        if search:
            query += " WHERE c.nom LIKE ? OR c.prenom LIKE ? OR c.telephone LIKE ?"
            s = f"%{search}%"
            params = [s,s,s]
        query += " GROUP BY c.id ORDER BY c.nom"
        rows = conn.execute(query, params).fetchall()
        conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else "—"))
            aw = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(aw)
            al.setContentsMargins(4,2,4,2)
            be = QtWidgets.QPushButton("✏️")
            be.setStyleSheet("background:#1f3a6e;color:#82a2f5;border:none;border-radius:4px;padding:4px 8px;")
            bd = QtWidgets.QPushButton("🗑️")
            bd.setStyleSheet("background:#3d1c1c;color:#f85149;border:none;border-radius:4px;padding:4px 8px;")
            cid = row[0]
            be.clicked.connect(lambda _, id=cid: self.open_form(id))
            bd.clicked.connect(lambda _, id=cid: self.delete(id))
            al.addWidget(be); al.addWidget(bd)
            self.table.setCellWidget(i, 5, aw)

    def delete(self, cid):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Supprimer ce client ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM client WHERE id=?", (cid,))
            conn.commit(); conn.close()
            self.load_data()

    def open_form(self, cid=None):
        dlg = ClientFormDialog(self, cid)
        if dlg.exec(): self.load_data()


class ClientFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, cid=None):
        super().__init__(parent)
        self.cid = cid
        self.setWindowTitle("Modifier client" if cid else "Nouveau client")
        self.setMinimumWidth(360)
        self.setStyleSheet("QDialog{background:#fff;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(24,24,24,24)
        self.nom = QtWidgets.QLineEdit()
        self.prenom = QtWidgets.QLineEdit()
        self.telephone = QtWidgets.QLineEdit()
        layout.addRow("Nom *", self.nom)
        layout.addRow("Prénom *", self.prenom)
        layout.addRow("Téléphone", self.telephone)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)
        if cid: self._load(cid)

    def _load(self, cid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM client WHERE id=?", (cid,)).fetchone()
        conn.close()
        if row:
            self.nom.setText(row['nom']); self.prenom.setText(row['prenom'])
            self.telephone.setText(row['telephone'] or "")

    def _save(self):
        nom = self.nom.text().strip(); prenom = self.prenom.text().strip()
        if not nom or not prenom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom et prénom obligatoires."); return
        conn = get_connection()
        try:
            if self.cid:
                conn.execute("UPDATE client SET nom=?,prenom=?,telephone=? WHERE id=?",
                    (nom, prenom, self.telephone.text(), self.cid))
            else:
                conn.execute("INSERT INTO client (nom,prenom,telephone) VALUES (?,?,?)",
                    (nom, prenom, self.telephone.text()))
            conn.commit(); conn.close(); self.accept()
        except Exception as e:
            conn.close(); QtWidgets.QMessageBox.warning(self, "Erreur", str(e))


# ======================= SOCIETE =======================

class SocietePage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("🏢 Sociétés"))
        hdr.addStretch()
        btn = primary_btn("+ Ajouter")
        btn.clicked.connect(self.open_form)
        hdr.addWidget(btn)
        layout.addLayout(hdr)
        self.table = make_table(["ID", "Nom", "Téléphone", "Adresse", "Description", "Actions"])
        layout.addWidget(self.table)

    def load_data(self):
        conn = get_connection()
        rows = conn.execute("SELECT id,nom,telephone,adresse,description FROM societe").fetchall()
        conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else "—"))
            aw = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(aw)
            al.setContentsMargins(4,2,4,2)
            be = QtWidgets.QPushButton("✏️")
            be.setStyleSheet("background:#1f3a6e;color:#82a2f5;border:none;border-radius:4px;padding:4px 8px;")
            sid = row[0]
            be.clicked.connect(lambda _, id=sid: self.open_form(id))
            al.addWidget(be)
            self.table.setCellWidget(i, 5, aw)

    def open_form(self, sid=None):
        dlg = SocieteFormDialog(self, sid)
        if dlg.exec(): self.load_data()


class SocieteFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, sid=None):
        super().__init__(parent)
        self.sid = sid
        self.setWindowTitle("Modifier société" if sid else "Nouvelle société")
        self.setMinimumWidth(400)
        self.setStyleSheet("QDialog{background:#fff;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(24,24,24,24)
        self.nom = QtWidgets.QLineEdit()
        self.desc = QtWidgets.QLineEdit()
        self.tel = QtWidgets.QLineEdit()
        self.adresse = QtWidgets.QLineEdit()
        layout.addRow("Nom *", self.nom)
        layout.addRow("Description", self.desc)
        layout.addRow("Téléphone", self.tel)
        layout.addRow("Adresse", self.adresse)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)
        if sid: self._load(sid)

    def _load(self, sid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM societe WHERE id=?", (sid,)).fetchone()
        conn.close()
        if row:
            self.nom.setText(row['nom']); self.desc.setText(row['description'] or "")
            self.tel.setText(row['telephone'] or ""); self.adresse.setText(row['adresse'] or "")

    def _save(self):
        nom = self.nom.text().strip()
        if not nom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Le nom est obligatoire."); return
        conn = get_connection()
        if self.sid:
            conn.execute("UPDATE societe SET nom=?,description=?,telephone=?,adresse=? WHERE id=?",
                (nom, self.desc.text(), self.tel.text(), self.adresse.text(), self.sid))
        else:
            conn.execute("INSERT INTO societe (nom,description,telephone,adresse) VALUES (?,?,?,?)",
                (nom, self.desc.text(), self.tel.text(), self.adresse.text()))
        conn.commit(); conn.close(); self.accept()