#!/usr/bin/env python3
import sqlite3
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "aerocage.db")

class DBManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.db_path = DB_PATH
        self._create_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _create_tables(self):
        query_groups = "CREATE TABLE IF NOT EXISTS groups (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);"
        query_aps = """CREATE TABLE IF NOT EXISTS access_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, ip TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL DEFAULT 'root', password TEXT NOT NULL, group_id INTEGER,
            FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE RESTRICT
        );"""
        with self._get_connection() as conn:
            conn.execute(query_groups)
            conn.execute(query_aps)
            conn.commit()

    @staticmethod
    def is_valid_ip(ip_str):
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        return bool(re.match(pattern, ip_str)) and all(0 <= int(p) <= 255 for p in ip_str.split('.'))

    def add_group(self, group_name):
        try:
            with self._get_connection() as conn:
                conn.execute("INSERT INTO groups (name) VALUES (?);", (group_name.strip(),))
                conn.commit()
            return True, "🟢 تم إضافة المجموعة بنجاح."
        except sqlite3.IntegrityError:
            return False, "❌ خطأ عملياتي: اسم المجموعة موجود بالفعل بالذاكرة ومكرر!"

    def get_all_groups(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM groups ORDER BY id ASC;")
            return cursor.fetchall()

    def delete_group(self, group_id):
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM groups WHERE id = ?;", (group_id,))
                conn.commit()
            return True, "🟢 تم حذف المجموعة بنجاح."
        except sqlite3.IntegrityError:
            return False, "❌ قفل عتادي: المجموعة تحتوي على أجهزة نشطة حالياً!"

    def add_access_point(self, name, ip, username, password, group_id=None):
        if not self.is_valid_ip(ip): return False, "❌ خطأ: صيغة عنوان الـ IP غير صحيحة!"
        query = "INSERT INTO access_points (name, ip, username, password, group_id) VALUES (?, ?, ?, ?, ?);"
        try:
            with self._get_connection() as conn:
                conn.execute(query, (name.strip(), ip.strip(), username.strip(), password.strip(), group_id))
                conn.commit()
            return True, "🟢 تم تسجيل وحفظ جهاز الأكسس بنجاح."
        except sqlite3.IntegrityError:
            return False, "❌ قفل عسكري: الاسم أو عنوان الـ IP مستخدم مسبقاً ومكرر بالمنظومة!"

    def get_all_access_points(self):
        query = """SELECT ap.id, ap.name, ap.ip, ap.username, ap.password, g.name 
                   FROM access_points ap LEFT JOIN groups g ON ap.group_id = g.id ORDER BY ap.id ASC;"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def delete_access_point(self, ap_id):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM access_points WHERE id = ?;", (ap_id,))
            conn.commit()
        return True, "🟢 تم مسح وإلغاء صلاحية الجهاز بنجاح."
