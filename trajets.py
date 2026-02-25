from PySide6 import QtWidgets, QtCore
from database import get_connection
from styles import primary_btn, section_title, make_table

class TrajetsPage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("🗺️ Trajets"))
        hdr.addStretch()
        btn_add = primary_btn("+ Nouveau trajet")
        btn_add.clicked.connect(self.open_form)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        # Search
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par ville de départ ou d'arrivée...")
        self.search_input.textChanged.connect(lambda t: self.load_data(t))
        layout.addWidget(self.search_input)

        self.table = make_table(["ID", "Départ", "Arrivée", "H. Départ", "H. Arrivée", "Chauffeur", "Véhicule", "Prix (FCFA)", "Places", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        query = """
            SELECT t.id,
                   vd.nom as depart, va.nom as arrivee,
                   t.heure_depart, t.heure_arrivee,
                   c.nom||' '||c.prenom as chauffeur,
                   v.matricule, t.prix,
                   v.nbre_place
            FROM trajet t
            LEFT JOIN ville vd ON t.ville_depart_id = vd.id
            LEFT JOIN ville va ON t.ville_arrivee_id = va.id
            LEFT JOIN chauffeur c ON t.chauffeur_id = c.id
            LEFT JOIN vehicule v ON t.vehicule_id = v.id
        """
        params = []
        if search:
            query += " WHERE vd.nom LIKE ? OR va.nom LIKE ?"
            s = f"%{search}%"
            params = [s, s]
        query += " ORDER BY t.id DESC"
        rows = conn.execute(query, params).fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else "—"))
            aw = QtWidgets.QWidget()
            al = QtWidgets.QHBoxLayout(aw)
            al.setContentsMargins(4, 2, 4, 2)
            btn_e = QtWidgets.QPushButton("✏️")
            btn_e.setStyleSheet("background:#1f3a6e;color:#82a2f5;border:none;border-radius:4px;padding:4px 8px;")
            btn_d = QtWidgets.QPushButton("🗑️")
            btn_d.setStyleSheet("background:#3d1c1c;color:#f85149;border:none;border-radius:4px;padding:4px 8px;")
            tid = row[0]
            btn_e.clicked.connect(lambda _, id=tid: self.open_form(id))
            btn_d.clicked.connect(lambda _, id=tid: self.delete(id))
            al.addWidget(btn_e)
            al.addWidget(btn_d)
            self.table.setCellWidget(i, 9, aw)

    def delete(self, tid):
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Supprimer ce trajet ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM trajet WHERE id=?", (tid,))
            conn.commit()
            conn.close()
            self.load_data()

    def open_form(self, tid=None):
        dlg = TrajetFormDialog(self, tid)
        if dlg.exec():
            self.load_data()


class TrajetFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, tid=None):
        super().__init__(parent)
        self.tid = tid
        self.setWindowTitle("Modifier trajet" if tid else "Nouveau trajet")
        self.setMinimumWidth(460)
        self.setStyleSheet("QDialog{background:#fff;color:#e6edf3;} QLabel{color:#8b949e;font-size:12px;}")
        self._setup_ui()
        if tid:
            self._load(tid)

    def _setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        conn = get_connection()
        self._villes = [dict(r) for r in conn.execute("SELECT id,nom FROM ville ORDER BY nom").fetchall()]
        self._chauffeurs = [dict(r) for r in conn.execute("SELECT id,nom,prenom FROM chauffeur").fetchall()]
        self._vehicules = [dict(r) for r in conn.execute("SELECT id,matricule,nbre_place FROM vehicule").fetchall()]
        conn.close()

        self.vd_cb = QtWidgets.QComboBox()
        self.va_cb = QtWidgets.QComboBox()

        # ajouter une ville directement depuis le formulaire de trajet
        vd_row = QtWidgets.QHBoxLayout()
        vd_row.addWidget(self.vd_cb)
        btn_vd = QtWidgets.QPushButton("+")
        btn_vd.setFixedWidth(50)
        btn_vd.setStyleSheet("background:#82a2f5;color:#e6edf3;border:none;border-radius:4px;")
        btn_vd.clicked.connect(lambda: self._add_ville(self.vd_cb))
        vd_row.addWidget(btn_vd)

        va_row = QtWidgets.QHBoxLayout()
        va_row.addWidget(self.va_cb)
        btn_va = QtWidgets.QPushButton("+")
        btn_va.setFixedWidth(50)
        btn_va.setStyleSheet("background:#82a2f5;color:#e6edf3;border:none;border-radius:4px;")
        btn_va.clicked.connect(lambda: self._add_ville(self.va_cb))
        va_row.addWidget(btn_va)

        self.chauf_cb = QtWidgets.QComboBox()
        self.veh_cb = QtWidgets.QComboBox()
        self.h_dep = QtWidgets.QDateTimeEdit()
        self.h_dep.setCalendarPopup(True)
        self.h_dep.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.h_arr = QtWidgets.QDateTimeEdit()
        self.h_arr.setCalendarPopup(True)
        self.h_arr.setDisplayFormat("dd/MM/yyyy HH:mm")
        self.prix = QtWidgets.QDoubleSpinBox()
        self.prix.setMaximum(9999999)
        self.prix.setSuffix(" FCFA")

        self._populate_combos()

        layout.addRow("Ville départ *", vd_row)
        layout.addRow("Ville arrivée *", va_row)
        layout.addRow("Heure départ *", self.h_dep)
        layout.addRow("Heure arrivée *", self.h_arr)
        layout.addRow("Chauffeur", self.chauf_cb)
        layout.addRow("Véhicule", self.veh_cb)
        layout.addRow("Prix", self.prix)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet("QPushButton{background:#82a2f5;color:#0d1117;border:none;border-radius:6px;padding:8px 18px;font-weight:700;}")
        layout.addRow(btns)

    def _populate_combos(self):
        self.vd_cb.clear()
        self.va_cb.clear()
        conn = get_connection()
        self._villes = [dict(r) for r in conn.execute("SELECT id,nom FROM ville ORDER BY nom").fetchall()]
        conn.close()
        for v in self._villes:
            self.vd_cb.addItem(v['nom'], v['id'])
            self.va_cb.addItem(v['nom'], v['id'])
        self.chauf_cb.clear()
        self.chauf_cb.addItem("— Aucun —", None)
        for ch in self._chauffeurs:
            self.chauf_cb.addItem(f"{ch['nom']} {ch['prenom']}", ch['id'])
        self.veh_cb.clear()
        self.veh_cb.addItem("— Aucun —", None)
        for veh in self._vehicules:
            self.veh_cb.addItem(f"{veh['matricule']} ({veh['nbre_place']} places)", veh['id'])

    def _add_ville(self, cb):
        nom, ok = QtWidgets.QInputDialog.getText(self, "Nouvelle ville", "Nom de la ville :")
        if ok and nom.strip():
            conn = get_connection()
            try:
                conn.execute("INSERT INTO ville (nom) VALUES (?)", (nom.strip(),))
                conn.commit()
            except: pass
            conn.close()
            self._populate_combos()
            idx = cb.findText(nom.strip())
            if idx >= 0: cb.setCurrentIndex(idx)

    def _load(self, tid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM trajet WHERE id=?", (tid,)).fetchone()
        conn.close()
        if row:
            for i in range(self.vd_cb.count()):
                if self.vd_cb.itemData(i) == row['ville_depart_id']:
                    self.vd_cb.setCurrentIndex(i)
            for i in range(self.va_cb.count()):
                if self.va_cb.itemData(i) == row['ville_arrivee_id']:
                    self.va_cb.setCurrentIndex(i)
            if row['heure_depart']:
                self.h_dep.setDateTime(QtCore.QDateTime.fromString(row['heure_depart'], "yyyy-MM-dd HH:mm"))
            if row['heure_arrivee']:
                self.h_arr.setDateTime(QtCore.QDateTime.fromString(row['heure_arrivee'], "yyyy-MM-dd HH:mm"))
            for i in range(self.chauf_cb.count()):
                if self.chauf_cb.itemData(i) == row['chauffeur_id']:
                    self.chauf_cb.setCurrentIndex(i)
            for i in range(self.veh_cb.count()):
                if self.veh_cb.itemData(i) == row['vehicule_id']:
                    self.veh_cb.setCurrentIndex(i)
            self.prix.setValue(row['prix'] or 0)

    def _save(self):
        conn = get_connection()
        dep = self.h_dep.dateTime().toString("yyyy-MM-dd HH:mm")
        arr = self.h_arr.dateTime().toString("yyyy-MM-dd HH:mm")
        try:
            if self.tid:
                conn.execute("""UPDATE trajet SET ville_depart_id=?,ville_arrivee_id=?,
                    heure_depart=?,heure_arrivee=?,chauffeur_id=?,vehicule_id=?,prix=? WHERE id=?""",
                    (self.vd_cb.currentData(), self.va_cb.currentData(),
                     dep, arr, self.chauf_cb.currentData(), self.veh_cb.currentData(),
                     self.prix.value(), self.tid))
            else:
                conn.execute("""INSERT INTO trajet (ville_depart_id,ville_arrivee_id,
                    heure_depart,heure_arrivee,chauffeur_id,vehicule_id,prix)
                    VALUES (?,?,?,?,?,?,?)""",
                    (self.vd_cb.currentData(), self.va_cb.currentData(),
                     dep, arr, self.chauf_cb.currentData(), self.veh_cb.currentData(),
                     self.prix.value()))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            conn.close()
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))