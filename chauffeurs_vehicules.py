from PySide6 import QtWidgets, QtCore
from database import get_connection
from styles import primary_btn, section_title, make_table


class ChauffeursPage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("🚗 Chauffeurs"))
        hdr.addStretch()
        btn = primary_btn("+ Ajouter")
        btn.clicked.connect(self.open_form)
        hdr.addWidget(btn)
        layout.addLayout(hdr)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher...")
        self.search.textChanged.connect(lambda t: self.load_data(t))
        layout.addWidget(self.search)
        self.table = make_table(["ID", "Nom", "Prénom", "Matricule", "Permis", "Date embauche", "Société", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        query = """SELECT c.id,c.nom,c.prenom,c.matricule,c.permis,c.date_embauche,s.nom as societe
                   FROM chauffeur c LEFT JOIN societe s ON c.societe_id=s.id"""
        params = []
        if search:
            query += " WHERE c.nom LIKE ? OR c.prenom LIKE ? OR c.matricule LIKE ?"
            s = f"%{search}%"
            params = [s, s, s]
        rows = conn.execute(query, params).fetchall()
        conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else "—"))
            aw = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(aw)
            al.setContentsMargins(4, 2, 4, 2)
            be = QtWidgets.QPushButton("✏️")
            be.setStyleSheet("background:#1f3a6e;color:#82a2f5;border:none;border-radius:4px;padding:4px 8px;")
            bd = QtWidgets.QPushButton("🗑️")
            bd.setStyleSheet("background:#3d1c1c;color:#f85149;border:none;border-radius:4px;padding:4px 8px;")
            cid = row[0]
            be.clicked.connect(lambda _, id=cid: self.open_form(id))
            bd.clicked.connect(lambda _, id=cid: self.delete(id))
            al.addWidget(be); al.addWidget(bd)
            self.table.setCellWidget(i, 7, aw)

    def delete(self, cid):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Supprimer ce chauffeur ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM chauffeur WHERE id=?", (cid,))
            conn.commit(); conn.close()
            self.load_data()

    def open_form(self, cid=None):
        dlg = ChauffeurFormDialog(self, cid)
        if dlg.exec(): self.load_data()


class ChauffeurFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, cid=None):
        super().__init__(parent)
        self.cid = cid
        self.setWindowTitle("Modifier" if cid else "Nouveau chauffeur")
        self.setMinimumWidth(400)
        self.setStyleSheet("QDialog{background:#fff;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(24,24,24,24)
        self.nom = QtWidgets.QLineEdit()
        self.prenom = QtWidgets.QLineEdit()
        self.matricule = QtWidgets.QLineEdit()
        self.permis = QtWidgets.QLineEdit()
        self.date_emb = QtWidgets.QDateEdit()
        self.date_emb.setCalendarPopup(True)
        self.societe_cb = QtWidgets.QComboBox()
        conn = get_connection()
        socs = conn.execute("SELECT id,nom FROM societe").fetchall()
        conn.close()
        for s in socs: self.societe_cb.addItem(s['nom'], s['id'])
        layout.addRow("Nom *", self.nom)
        layout.addRow("Prénom *", self.prenom)
        layout.addRow("Matricule", self.matricule)
        layout.addRow("N° Permis", self.permis)
        layout.addRow("Date embauche", self.date_emb)
        layout.addRow("Société", self.societe_cb)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)
        if cid: self._load(cid)

    def _load(self, cid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM chauffeur WHERE id=?", (cid,)).fetchone()
        conn.close()
        if row:
            self.nom.setText(row['nom']); self.prenom.setText(row['prenom'])
            self.matricule.setText(row['matricule'] or ""); self.permis.setText(row['permis'] or "")
            if row['date_embauche']:
                self.date_emb.setDate(QtCore.QDate.fromString(row['date_embauche'], "yyyy-MM-dd"))
            for i in range(self.societe_cb.count()):
                if self.societe_cb.itemData(i) == row['societe_id']: self.societe_cb.setCurrentIndex(i)

    def _save(self):
        nom = self.nom.text().strip(); prenom = self.prenom.text().strip()
        if not nom or not prenom:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom et prénom obligatoires."); return
        conn = get_connection()
        dob = self.date_emb.date().toString("yyyy-MM-dd")
        try:
            if self.cid:
                conn.execute("UPDATE chauffeur SET nom=?,prenom=?,matricule=?,permis=?,date_embauche=?,societe_id=? WHERE id=?",
                    (nom,prenom,self.matricule.text(),self.permis.text(),dob,self.societe_cb.currentData(),self.cid))
            else:
                conn.execute("INSERT INTO chauffeur (nom,prenom,matricule,permis,date_embauche,societe_id) VALUES (?,?,?,?,?,?)",
                    (nom,prenom,self.matricule.text(),self.permis.text(),dob,self.societe_cb.currentData()))
            conn.commit(); conn.close(); self.accept()
        except Exception as e:
            conn.close(); QtWidgets.QMessageBox.warning(self, "Erreur", str(e))



class VehiculesPage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("🚌 Véhicules"))
        hdr.addStretch()
        btn = primary_btn("+ Ajouter")
        btn.clicked.connect(self.open_form)
        hdr.addWidget(btn)
        layout.addLayout(hdr)
        self.search = QtWidgets.QLineEdit()
        self.search.setPlaceholderText("🔍 Rechercher par matricule ou type...")
        self.search.textChanged.connect(lambda t: self.load_data(t))
        layout.addWidget(self.search)
        self.table = make_table(["ID", "Matricule", "Nbre places", "Type", "Société", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        query = "SELECT v.id,v.matricule,v.nbre_place,v.type,s.nom FROM vehicule v LEFT JOIN societe s ON v.societe_id=s.id"
        params = []
        if search:
            query += " WHERE v.matricule LIKE ? OR v.type LIKE ?"
            s = f"%{search}%"
            params = [s, s]
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
            vid = row[0]
            be.clicked.connect(lambda _, id=vid: self.open_form(id))
            bd.clicked.connect(lambda _, id=vid: self.delete(id))
            al.addWidget(be); al.addWidget(bd)
            self.table.setCellWidget(i, 5, aw)

    def delete(self, vid):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Supprimer ce véhicule ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM vehicule WHERE id=?", (vid,))
            conn.commit(); conn.close()
            self.load_data()

    def open_form(self, vid=None):
        dlg = VehiculeFormDialog(self, vid)
        if dlg.exec(): self.load_data()


class VehiculeFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, vid=None):
        super().__init__(parent)
        self.vid = vid
        self.setWindowTitle("Modifier véhicule" if vid else "Nouveau véhicule")
        self.setMinimumWidth(380)
        self.setStyleSheet("QDialog{background:#fff;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(24,24,24,24)
        self.matricule = QtWidgets.QLineEdit()
        self.nbre_place = QtWidgets.QSpinBox()
        self.nbre_place.setMinimum(1); self.nbre_place.setMaximum(200)
        self.vtype = QtWidgets.QComboBox()
        self.vtype.setEditable(True)
        self.vtype.addItems(["Bus", "Minibus", "Car", "Van", "Autre"])
        self.societe_cb = QtWidgets.QComboBox()
        conn = get_connection()
        socs = conn.execute("SELECT id,nom FROM societe").fetchall()
        conn.close()
        for s in socs: self.societe_cb.addItem(s['nom'], s['id'])
        layout.addRow("Matricule *", self.matricule)
        layout.addRow("Nombre de places", self.nbre_place)
        layout.addRow("Type", self.vtype)
        layout.addRow("Société", self.societe_cb)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)
        if vid: self._load(vid)

    def _load(self, vid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM vehicule WHERE id=?", (vid,)).fetchone()
        conn.close()
        if row:
            self.matricule.setText(row['matricule'])
            self.nbre_place.setValue(row['nbre_place'] or 1)
            idx = self.vtype.findText(row['type'] or "")
            if idx >= 0: self.vtype.setCurrentIndex(idx)
            else: self.vtype.setCurrentText(row['type'] or "")
            for i in range(self.societe_cb.count()):
                if self.societe_cb.itemData(i) == row['societe_id']: self.societe_cb.setCurrentIndex(i)

    def _save(self):
        mat = self.matricule.text().strip()
        if not mat:
            QtWidgets.QMessageBox.warning(self, "Erreur", "La matricule est obligatoire."); return
        conn = get_connection()
        try:
            if self.vid:
                conn.execute("UPDATE vehicule SET matricule=?,nbre_place=?,type=?,societe_id=? WHERE id=?",
                    (mat, self.nbre_place.value(), self.vtype.currentText(), self.societe_cb.currentData(), self.vid))
            else:
                conn.execute("INSERT INTO vehicule (matricule,nbre_place,type,societe_id) VALUES (?,?,?,?)",
                    (mat, self.nbre_place.value(), self.vtype.currentText(), self.societe_cb.currentData()))
            conn.commit(); conn.close(); self.accept()
        except Exception as e:
            conn.close(); QtWidgets.QMessageBox.warning(self, "Erreur", str(e))