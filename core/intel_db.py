#!/usr/bin/env python3
import os
import sys
import sqlite3
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.db_manager import DatabaseManager

class IntelDatabase(DatabaseManager):
    def __init__(self):
        # استدعاء مشيد الأب (DatabaseManager) لتوحيد مراجع الاتصال وملف قاعدة البيانات
        super().__init__()
        # تهيئة جدول الاستخبارات المتقدم فوراً
        self.initialize_intel_tables()

    def initialize_intel_tables(self):
        """بناء جداول الاستخبارات المتقدمة والأمنية في قاعدة البيانات الموحدة"""
        query = """
        CREATE TABLE IF NOT EXISTS intel_recon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bssid TEXT NOT EXISTS UNIQUE,
            essid TEXT,
            encryption_type TEXT DEFAULT 'OPEN',
            cipher TEXT DEFAULT 'NONE',
            auth_type TEXT DEFAULT 'NONE',
            recon_notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # استخدام قفل الأب (DatabaseManager._lock) لمنع أي تضارب بين خيوط الفحص والضربات
        with DatabaseManager._lock:
            conn = self._get_secure_connection()
            if conn:
                try:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(query)
                    print("[+] تم تهيئة وتأمين جداول الاستخبارات المتقدمة (Intel Recon Table) بنجاح.")
                except sqlite3.Error as e:
                    print(f"[-] فشل إنشاء بنية جداول الاستخبارات: {e}")
                finally:
                    conn.close()

    def update_intel_recon_safe(self, bssid: str, essid: str, enc: str, cipher: str, auth: str, notes: str = "") -> bool:
        """
        تحديث مستودع الاستخبارات اللاسلكية ببيانات الأهداف بأمان 100% وحصانة كاملة ضد الـ SQL Injection.
        يتم تمرير المعلمات عبر علامات الاستفهام لمنع تفسير الأسماء الملوثة القادمة من الهواء كأوامر تخريبية.
        """
        # تطهير المدخلات القادمة من الهواء عتادياً قبل إرسالها للنواة
        clean_bssid = SystemGuard.sanitize_input(bssid, "bssid")
        clean_essid = SystemGuard.sanitize_input(essid, "csv_value")
        clean_enc = SystemGuard.sanitize_input(enc, "interface")
        clean_cipher = SystemGuard.sanitize_input(cipher, "interface")
        clean_auth = SystemGuard.sanitize_input(auth, "interface")
        clean_notes = SystemGuard.sanitize_input(notes, "csv_value")

        query = """
        INSERT INTO intel_recon (bssid, essid, encryption_type, cipher, auth_type, recon_notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(bssid) DO UPDATE SET
            essid=excluded.essid,
            encryption_type=excluded.encryption_type,
            cipher=excluded.cipher,
            auth_type=excluded.auth_type,
            recon_notes=excluded.recon_notes,
            updated_at=CURRENT_TIMESTAMP;
        """

        with DatabaseManager._lock:
            conn = self._get_secure_connection()
            if conn:
                try:
                    with conn: # سياق الحماية الآمن للـ Commit والـ Rollback
                        cursor = conn.cursor()
                        cursor.execute(query, (clean_bssid, clean_essid, clean_enc, clean_cipher, clean_auth, clean_notes))
                    return True
                except sqlite3.Error as e:
                    print(f"[-] فشل ضخ البيانات الاستخباراتية للهدف {clean_bssid}: {e}")
                finally:
                    conn.close() # خط الدفاع الحتمي لمنع تعليق التداخل البرمجي لقاعدة البيانات
        return False

    def query_target_recon_data(self, bssid: str) -> dict:
        """استدعاء السجل الاستخباراتي الكامل لهدف معين بأمان وحصانة"""
        clean_mac = SystemGuard.sanitize_input(bssid, "bssid")
        query = "SELECT * FROM intel_recon WHERE bssid = ?;"
        result_dict = {}

        with DatabaseManager._lock:
            conn = self._get_secure_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query, (clean_mac,))
                    row = cursor.fetchone()
                    if row:
                        result_dict = dict(row)
                except sqlite3.Error as e:
                    print(f"[-] خطأ أثناء استدعاء بيانات الاستطلاع للهدف {clean_mac}: {e}")
                finally:
                    conn.close()
        return result_dict

if __name__ == "__main__":
    print("[*] محرك ومستودع استخبارات الأهداف اللاسلكية (Intel DB) مدمج ومؤمن بنسبة 100%.")
    # اختبار تشغيلي صامت يثبت كفاءة الوراثة البرمجية النظيفة من المدير المركزي
    intel = IntelDatabase()
    intel.update_intel_recon_safe("11:22:33:44:55:66", "Target_Malicious_SSID'; DROP TABLE intel_recon; --", "WPA2", "CCMP", "PSK", "ملاحظة فحص تكتيكي")
    print(f"[+] مخرجات الفحص الآمن ضد حيلة الحقن: {intel.query_target_recon_data('11:22:33:44:55:66')}")
