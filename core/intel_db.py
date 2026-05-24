#!/usr/bin/env python3
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "aerocage_unified.db")

class IntelDBManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.db_path = DB_PATH
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _create_tables(self):
        with self._get_connection() as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);")
            conn.execute("""CREATE TABLE IF NOT EXISTS access_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, ip TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL DEFAULT 'root', password TEXT NOT NULL, group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT
            );""")
            conn.execute("""CREATE TABLE IF NOT EXISTS radar_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, scan_time TEXT NOT NULL, scanner_ap_name TEXT NOT NULL,
                scanner_band TEXT NOT NULL, bssid TEXT NOT NULL, essid TEXT, channel TEXT, privacy TEXT, signal TEXT,
                first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, UNIQUE(scanner_ap_name, bssid)
            );""")
            conn.commit()

    def add_group(self, group_name):
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT INTO groups (name) VALUES (?);", (group_name.strip(),))
                conn.commit()
            return True, "🟢 تم إضافة المجموعة بنجاح."
        except sqlite3.IntegrityError: return False, "❌ مكرر"

    def get_all_groups(self):
        with self._get_connection() as conn:
            return conn.execute("SELECT id, name FROM groups ORDER BY id ASC;").fetchall()

    def delete_group(self, group_id):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM groups WHERE id = ?;", (int(group_id),))
                conn.commit()
            return True, "🟢 تم حذف المجموعة بنجاح."
        except sqlite3.IntegrityError: return False, "❌ قفل عتادي: المجموعة ممتلئة"

    def add_access_point(self, name, ip, username, password, group_id=None):
        query = "INSERT INTO access_points (name, ip, username, password, group_id) VALUES (?, ?, ?, ?, ?);"
        try:
            with self._get_connection() as conn:
                conn.execute(query, (name.strip(), ip.strip(), username.strip(), password.strip(), group_id))
                conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    def get_all_access_points(self):
        query = """SELECT ap.id, ap.name, ap.ip, ap.username, ap.password, g.name 
                   FROM access_points ap LEFT JOIN groups g ON ap.group_id = g.id ORDER BY ap.id ASC;"""
        with self._get_connection() as conn:
            return conn.execute(query).fetchall()

    def delete_access_point(self, ap_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM access_points WHERE id = ?;", (int(ap_id),))
            conn.commit()
