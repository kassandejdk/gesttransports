from PySide6 import QtWidgets, QtCore
from database import get_connection, hash_password
from styles import primary_btn, danger_btn, section_title, make_table, card_widget

class UsersPage(QtWidgets.QWidget):
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
        hdr.addWidget(section_title("👥 Utilisateurs"))
        hdr.addStretch()
        btn_add = primary_btn("+ Ajouter")
        btn_add.clicked.connect(self.open_form)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher par nom, prénom, identifiant...")
        self.search_input.textChanged.connect(self.filter_table)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.table = make_table(["ID", "Nom", "Prénom", "Identifiant", "Genre", "Téléphone", "Rôle", "Actions"])
        layout.addWidget(self.table)

    def load_data(self, search=""):
        conn = get_connection()
        c = conn.cursor()
        query = """
            SELECT u.id, u.nom, u.prenom, u.identifiant, u.genre, u.telephone, r.nom as role
            FROM user u LEFT JOIN role r ON u.role_id = r.id
        """
        params = []
        if search:
            query += " WHERE u.nom LIKE ? OR u.prenom LIKE ? OR u.identifiant LIKE ?"
            s = f"%{search}%"
            params = [s, s, s]
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val) if val else ""))
            action_widget = QtWidgets.QWidget()
            action_layout = QtWidgets.QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QtWidgets.QPushButton("✏️ Modifier")
            btn_edit.setStyleSheet("background:#1f3a6e;color:#82a2f5;border:none;border-radius:4px;padding:4px 8px;")
            btn_del = QtWidgets.QPushButton("🗑️ Supprimer")
            btn_del.setStyleSheet("background:#3d1c1c;color:#f85149;border:none;border-radius:4px;padding:4px 8px;")
            uid = row[0]
            btn_edit.clicked.connect(lambda _, id=uid: self.open_form(id))
            btn_del.clicked.connect(lambda _, id=uid: self.delete_user(id))
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_del)
            self.table.setCellWidget(i, 7, action_widget)

    def filter_table(self, text):
        self.load_data(text)

    def delete_user(self, uid):
        if uid == self.current_user['id']:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Vous ne pouvez pas supprimer votre propre compte.")
            return
        reply = QtWidgets.QMessageBox.question(self, "Confirmation", "Supprimer cet utilisateur ?")
        if reply == QtWidgets.QMessageBox.Yes:
            conn = get_connection()
            conn.execute("DELETE FROM user WHERE id=?", (uid,))
            conn.commit()
            conn.close()
            self.load_data()

    def open_form(self, uid=None):
        dlg = UserFormDialog(self, uid)
        if dlg.exec():
            self.load_data()


class UserFormDialog(QtWidgets.QDialog):
    def __init__(self, parent, uid=None):
        super().__init__(parent)
        self.uid = uid
        self.setWindowTitle("Modifier utilisateur" if uid else "Ajouter utilisateur")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background:#fff; color:#e6edf3; }
            QLabel { color:#8b949e; font-size:12px; }
        """)
        self._setup_ui()
        if uid:
            self._load(uid)

    def _setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        self.nom = QtWidgets.QLineEdit()
        self.prenom = QtWidgets.QLineEdit()
        self.telephone = QtWidgets.QLineEdit()
        self.date_naissance = QtWidgets.QDateEdit()
        self.date_naissance.setCalendarPopup(True)
        self.genre = QtWidgets.QComboBox()
        self.genre.addItems(["M", "F"])
        self.identifiant = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setPlaceholderText("Laisser vide pour ne pas modifier" if self.uid else "")
        self.role_cb = QtWidgets.QComboBox()
        self.societe_cb = QtWidgets.QComboBox()

        conn = get_connection()
        self._roles = [dict(r) for r in conn.execute("SELECT id, nom FROM role").fetchall()]
        self._societes = [dict(s) for s in conn.execute("SELECT id, nom FROM societe").fetchall()]
        conn.close()
        for r in self._roles:
            self.role_cb.addItem(r['nom'], r['id'])
        for s in self._societes:
            self.societe_cb.addItem(s['nom'], s['id'])

        layout.addRow("Nom *", self.nom)
        layout.addRow("Prénom *", self.prenom)
        layout.addRow("Téléphone", self.telephone)
        layout.addRow("Date naissance", self.date_naissance)
        layout.addRow("Genre", self.genre)
        layout.addRow("Identifiant *", self.identifiant)
        layout.addRow("Mot de passe", self.password)
        layout.addRow("Rôle", self.role_cb)
        layout.addRow("Société", self.societe_cb)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self._save)
        btns.rejected.connect(self.reject)
        btns.setStyleSheet("""
            QPushButton { background:#82a2f5; color:#0d1117; border:none; border-radius:6px; padding:8px 18px; font-weight:700; }
            QPushButton:hover { background:#9bb5ff; }
        """)
        layout.addRow(btns)

    def _load(self, uid):
        conn = get_connection()
        row = conn.execute("SELECT * FROM user WHERE id=?", (uid,)).fetchone()
        conn.close()
        if row:
            self.nom.setText(row['nom'])
            self.prenom.setText(row['prenom'])
            self.telephone.setText(row['telephone'] or "")
            if row['date_naissance']:
                self.date_naissance.setDate(QtCore.QDate.fromString(row['date_naissance'], "yyyy-MM-dd"))
            idx = self.genre.findText(row['genre'] or "M")
            if idx >= 0: self.genre.setCurrentIndex(idx)
            self.identifiant.setText(row['identifiant'])
            for i in range(self.role_cb.count()):
                if self.role_cb.itemData(i) == row['role_id']:
                    self.role_cb.setCurrentIndex(i)
            for i in range(self.societe_cb.count()):
                if self.societe_cb.itemData(i) == row['societe_id']:
                    self.societe_cb.setCurrentIndex(i)

    def _save(self):
        nom = self.nom.text().strip()
        prenom = self.prenom.text().strip()
        ident = self.identifiant.text().strip()
        if not nom or not prenom or not ident:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Nom, prénom et identifiant sont obligatoires.")
            return
        conn = get_connection()
        pw = self.password.text()
        dob = self.date_naissance.date().toString("yyyy-MM-dd")
        try:
            if self.uid:
                if pw:
                    conn.execute("""UPDATE user SET nom=?,prenom=?,telephone=?,date_naissance=?,genre=?,
                        identifiant=?,password=?,role_id=?,societe_id=? WHERE id=?""",
                        (nom, prenom, self.telephone.text(), dob, self.genre.currentText(),
                         ident, hash_password(pw), self.role_cb.currentData(),
                         self.societe_cb.currentData(), self.uid))
                else:
                    conn.execute("""UPDATE user SET nom=?,prenom=?,telephone=?,date_naissance=?,genre=?,
                        identifiant=?,role_id=?,societe_id=? WHERE id=?""",
                        (nom, prenom, self.telephone.text(), dob, self.genre.currentText(),
                         ident, self.role_cb.currentData(), self.societe_cb.currentData(), self.uid))
            else:
                if not pw:
                    QtWidgets.QMessageBox.warning(self, "Erreur", "Le mot de passe est obligatoire.")
                    return
                conn.execute("""INSERT INTO user (nom,prenom,telephone,date_naissance,genre,identifiant,password,role_id,societe_id)
                    VALUES (?,?,?,?,?,?,?,?,?)""",
                    (nom, prenom, self.telephone.text(), dob, self.genre.currentText(),
                     ident, hash_password(pw), self.role_cb.currentData(), self.societe_cb.currentData()))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            conn.close()
            QtWidgets.QMessageBox.warning(self, "Erreur", str(e))