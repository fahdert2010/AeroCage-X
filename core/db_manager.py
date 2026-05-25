#!/usr/bin/env python3
import os
import sys
import sqlite3
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

class DatabaseManager:
    _lock = threading.Lock()
    _db_initialized = False

    def __init__(self):
        # تحديد مسار قاعدة البيانات ديناميكياً باستخدام pathlib الآمنة
        self.db_dir = BASE_DIR / "data"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.db_dir / "aerocage_core.db"
        
        # تهيئة الجداول تلقائياً عند التشغيل الأول للمنظومة
        if not DatabaseManager._db_initialized:
            self.initialize_core_tables()

    def _get_secure_connection(self):
        """إنشاء اتصال آمن ومحمي بملف قاعدة البيانات"""
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=10)
            conn.row_factory = sqlite3.Row  # تفعيل القراءة المرنة عبر أسماء الأعمدة
            return conn
        except sqlite3.Error as e:
            print(f"[-] خطأ فادح أثناء فتح قناة قاعدة البيانات: {e}")
            return None

    def initialize_core_tables(self):
        """بناء الجداول الاستراتيجية للمنظومة بأمان ومنع التكرار"""
        query = """
        CREATE TABLE IF NOT EXISTS tactical_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bssid TEXT UNIQUE,
            essid TEXT,
            channel TEXT,
            power INTEGER,
            status TEXT DEFAULT 'discovered',
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with DatabaseManager._lock:
            conn = self._get_connection() if hasattr(self, '_get_connection') else self._get_secure_connection()
            if conn:
                try:
                    with conn:
                        cursor = conn.cursor()
                        cursor.execute(query)
                    DatabaseManager._db_initialized = True
                    print(f"[+] تم تهيئة وتأمين جداول قاعدة البيانات بنجاح في: {self.db_path}")
                except sqlite3.Error as e:
                    print(f"[-] فشل تهيئة بنية قاعدة البيانات: {e}")
                finally:
                    conn.close()

    def save_target_safe(self, bssid: str, essid: str, channel: str, power: int) -> bool:
        """
        إدخال أو تحديث بيانات الأجهزة المكتشفة بأمان كامل 100% وحصانة ضد SQL Injection.
        تم تمرير القيم كـ Tuple مستقلة تماماً عن نص الاستعلام.
        """
        # تطهير المدخلات عتادياً قبل إرسالها إلى قاعدة البيانات لحمايتك
        clean_bssid = SystemGuard.sanitize_input(bssid, "bssid")
        clean_essid = SystemGuard.sanitize_input(essid, "csv_value")
        clean_chan = "".join(ch for ch in str(channel) if ch.isdigit())
        
        try:
            clean_power = int(power)
        except ValueError:
            clean_power = -100 # قيمة افتراضية للإشارة المعدومة

        query = """
        INSERT INTO tactical_targets (bssid, essid, channel, power, last_seen)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(bssid) DO UPDATE SET
            essid=excluded.essid,
            channel=excluded.channel,
            power=excluded.power,
            last_seen=CURRENT_TIMESTAMP;
        """

        with DatabaseManager._lock:
            conn = self._get_secure_connection()
            if conn:
                try:
                    with conn:  # استخدام معالج السياق يضمن عمل commit أو rollback تلقائياً
                        cursor = conn.cursor()
                        # تمرير علامات الاستفهام يمنع تفسير أي نص خبيث كأمر SQL لقاعدة البيانات
                        cursor.execute(query, (clean_bssid, clean_essid, clean_chan, clean_power))
                    return True
                except sqlite3.Error as e:
                    print(f"[-] فشل إدخال/تحديث بيانات الهدف {clean_bssid}: {e}")
                finally:
                    conn.close() # خط الدفاع الحتمي: إغلاق السوكت والاتصال دائماً لمنع الـ Locks
        return False

    def get_all_active_targets(self) -> list:
        """جلب طابور الأهداف النشطة بشكل مصفى وآمن تماماً"""
        query = "SELECT * FROM tactical_targets ORDER BY power DESC;"
        targets_list = []

        with DatabaseManager._lock:
            conn = self._get_secure_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    # تحويل المخرجات إلى قواميس مصفوفة لسهولة التعامل مع الواجهات الرسومية
                    for row in cursor.fetchall():
                        targets_list.append(dict(row))
                except sqlite3.Error as e:
                    print(f"[-] خطأ أثناء استدعاء طابور الأهداف: {e}")
                finally:
                    conn.close()
        return targets_list

if __name__ == "__main__":
    print("[*] محرك وقاعدة بيانات AeroCage-X مدمج ومحصن بنسبة 100%.")
    # اختبار تشغيلي صامت للتحقق من سلامة الأقفال والسياق
    db = DatabaseManager()
    db.save_target_safe("AA:BB:CC:DD:EE:FF", "Test_AP", "11", -45)
