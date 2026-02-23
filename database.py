import sqlite3
import hashlib
import os

DB_PATH = "gestransport.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS role (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS societe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            description TEXT,
            telephone TEXT,
            adresse TEXT
        );

        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT,
            date_naissance TEXT,
            genre TEXT,
            identifiant TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role_id INTEGER,
            societe_id INTEGER,
            FOREIGN KEY (role_id) REFERENCES role(id),
            FOREIGN KEY (societe_id) REFERENCES societe(id)
        );

        CREATE TABLE IF NOT EXISTS ville (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS vehicule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricule TEXT NOT NULL UNIQUE,
            nbre_place INTEGER,
            type TEXT,
            societe_id INTEGER,
            FOREIGN KEY (societe_id) REFERENCES societe(id)
        );

        CREATE TABLE IF NOT EXISTS chauffeur (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            matricule TEXT UNIQUE,
            permis TEXT,
            date_embauche TEXT,
            societe_id INTEGER,
            FOREIGN KEY (societe_id) REFERENCES societe(id)
        );

        CREATE TABLE IF NOT EXISTS trajet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            heure_depart TEXT,
            heure_arrivee TEXT,
            ville_depart_id INTEGER,
            ville_arrivee_id INTEGER,
            vehicule_id INTEGER,
            chauffeur_id INTEGER,
            prix REAL DEFAULT 0,
            FOREIGN KEY (ville_depart_id) REFERENCES ville(id),
            FOREIGN KEY (ville_arrivee_id) REFERENCES ville(id),
            FOREIGN KEY (vehicule_id) REFERENCES vehicule(id),
            FOREIGN KEY (chauffeur_id) REFERENCES chauffeur(id)
        );

        CREATE TABLE IF NOT EXISTS client (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT
        );

        CREATE TABLE IF NOT EXISTS ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            siege INTEGER,
            montant REAL,
            statut TEXT DEFAULT 'payé',
            trajet_id INTEGER,
            client_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY (trajet_id) REFERENCES trajet(id),
            FOREIGN KEY (client_id) REFERENCES client(id),
            FOREIGN KEY (user_id) REFERENCES user(id)
        );
    """)

    # Seed default role and admin if not exists
    c.execute("SELECT COUNT(*) FROM role")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO role (nom, description) VALUES ('Admin', 'Administrateur système')")
        c.execute("INSERT INTO role (nom, description) VALUES ('Agent', 'Agent de vente')")

    c.execute("SELECT COUNT(*) FROM societe")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO societe (nom, description, telephone, adresse) VALUES ('Ma Société', 'Société principale', '', '')")

    c.execute("SELECT COUNT(*) FROM user")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO user (nom, prenom, identifiant, password, genre, role_id, societe_id)
                     VALUES ('Admin', 'Super', 'admin', ?, 'M', 1, 1)""",
                  (hash_password("admin123"),))

    conn.commit()
    conn.close()

def authenticate(identifiant, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT u.*, r.nom as role_nom, s.nom as societe_nom
        FROM user u
        LEFT JOIN role r ON u.role_id = r.id
        LEFT JOIN societe s ON u.societe_id = s.id
        WHERE u.identifiant=? AND u.password=?
    """, (identifiant, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None