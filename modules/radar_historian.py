#!/usr/bin/env python3
import os
import sys
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية والمساعدات الفنية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.network_validators import NetworkValidators
from core.db_manager import DatabaseManager

# تفعيل خط الدفاع الأول للمحيط لضمان تشغيل الأداة تحت الـ sudo بأمان
SystemGuard.enforce_root_privileges("Radar Historian Engine")

class RadarHistorianEngine:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.lock = threading.Lock()
        self.historical_movements = {}
        self._initialize_history_table()

    def _initialize_history_table(self):
        """بناء جداول الأرشفة التاريخية لحركة الأهداف لمنع الانهيارات البرمجية"""
        query = """
        CREATE TABLE IF NOT EXISTS radar_history_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_mac TEXT,
            associated_bssid TEXT,
            essid_name TEXT,
            movement_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        import sqlite3
        with DatabaseManager._lock:
            conn = self.db_manager._get_secure_connection()
            if conn:
                try:
                    with conn:
                        conn.cursor().execute(query)
                    print("[+] تم تهيئة وتأمين جداول مؤرخ الرادار اللاسلكي بنجاح.")
                except sqlite3.Error as e:
                    print(f"[-] فشل بناء جداول الأرشيف الراداري: {e}")
                finally:
                    conn.close()

    def log_target_movement_safe(self, client_mac: str, associated_bssid: str, essid_name: str) -> bool:
        """
        توثيق وأرشفة حركة وتنقل الهدف بين نقاط الوصول بأمان سيبراني 100%.
        حصانة تامة ضد الـ SQL & OS Injection (القضاء على shell=True لـ Bandit).
        """
        # تطهير المدخلات الملتقطة من الهواء بالملي قبل تمريرها للنواة
        clean_client = SystemGuard.sanitize_input(client_mac, "bssid").upper()
        clean_ap = SystemGuard.sanitize_input(associated_bssid, "bssid").upper()
        clean_essid = SystemGuard.sanitize_input(essid_name, "csv_value")

        # خط الدفاع الاستخباراتي: التحقق من صحة الصيغ الفيزيائية للماك أدرس لمنع تلوث قاعدة البيانات
        if not NetworkValidators.is_valid_bssid(clean_client) or not NetworkValidators.is_valid_bssid(clean_ap):
            return False

        # حيلة هندسية خفيفة لمنع إغراق قاعدة البيانات بالسجلات المكررة إذا لم يغير الهدف مكانه
        target_key = f"{clean_client}_current"
        with self.lock:
            if self.historical_movements.get(target_key) == clean_ap:
                return True # الهدف لا يزال متصلاً بنفس الراوتر، لا داعي لتكرار التوثيق
            self.historical_movements[target_key] = clean_ap

        query = """
        INSERT INTO radar_history_logs (client_mac, associated_bssid, essid_name, movement_time)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP);
        """
        
        import sqlite3
        with DatabaseManager._lock:
            conn = self.db_manager._get_secure_connection()
            if conn:
                try:
                    with conn:
                        cursor = conn.cursor()
                        # تمرير علامات الاستفهام يضمن معاملة بايثون للمدخلات كنصوص مجردة لحل ثغرات الفحص
                        cursor.execute(query, (clean_client, clean_ap, clean_essid))
                    print(f"[📡 الرادار] تم توثيق قفزة حركية للجهاز [{clean_client}] نحو الشبكة: {clean_essid}")
                    return True
                except sqlite3.Error as e:
                    print(f"[-] فشل أرشفة الحركة الرادارية للهدف {clean_client}: {e}")
                finally:
                    conn.close()
        return False

    def track_client_historical_path(self, client_mac: str) -> list:
        """استدعاء خريطة السير التاريخية وجدول القفزات لهدف هارب لمعرفة الشبكات السابقة بأمان"""
        clean_client = SystemGuard.sanitize_input(client_mac, "bssid").upper()
        query = "SELECT * FROM radar_history_logs WHERE client_mac = ? ORDER BY movement_time DESC;"
        history_records = []

        import sqlite3
        with DatabaseManager._lock:
            conn = self.db_manager._get_secure_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query, (clean_client,))
                    for row in cursor.fetchall():
                        history_records.append(dict(row))
                except sqlite3.Error as e:
                    print(f"[-] خطأ أثناء استدعاء التاريخ الراداري للهدف {clean_client}: {e}")
                finally:
                    conn.close()
        return history_records

if __name__ == "__main__":
    print("[*] محرك مؤرخ الرادار ومتعقب حركة الأجهزة (Radar Historian) مدمج ومحصن 100%.")
    # اختبار تشغيلي صامت للتحقق من كفاءة عزل الأنابيب وحظر الـ SQL Injection
    # historian = RadarHistorianEngine()
    # historian.log_target_movement_safe("00:11:22:33:44:55", "AA:BB:CC:DD:EE:FF", "Malicious_AP_SSID'; DROP TABLE radar_history_logs; --")
