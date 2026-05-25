import sqlite3
from config import Config

class DatabaseEngine:
    @staticmethod
    def get_connection():
        """إنشاء اتصال آمن وقراءة المسار من ملف الإعدادات"""
        db_path = Config.DATA_DIR / Config.DB_NAME
        try:
            conn = sqlite3.connect(db_path)
            # تفعيل دعم الأسماء الصريحة للأعمدة لسهولة التعامل
            conn.row_factory = sqlite3.Row 
            return conn
        except sqlite3.Error as e:
            print(f"[-] خطأ فادح أثناء الاتصال بقاعدة البيانات: {e}")
            return None

    @classmethod
    def initialize_database(cls):
        """إنشاء الجداول الأساسية للمشروع بشكل آمن ومحمي"""
        query = """
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT NOT EXISTS UNIQUE,
            mac_address TEXT,
            status TEXT DEFAULT 'unknown',
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        # استخدام معالج السياق 'with' يضمن إغلاق الاتصال تلقائياً حتى لو انهار الكود
        with cls.get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    conn.commit()
                    print("[+] تم تهيئة قاعدة بيانات AeroCage-X بنجاح.")
                    return True
                except sqlite3.Error as e:
                    print(f"[-] خطأ أثناء إنشاء الجداول: {e}")
        return False

    @classmethod
    def add_target_safe(cls, ip, mac):
        """إدخال بيانات الأهداف بطريقة محمية 100% من ثغرات الـ SQL Injection"""
        query = "INSERT OR IGNORE INTO targets (ip_address, mac_address) VALUES (?, ?)"
        
        with cls.get_connection() as conn:
            if conn:
                try:
                    cursor = conn.cursor()
                    # تمرير المتغيرات كـ Tuple (منفصلة تماماً عن نص الاستعلام) لضمان الأمان
                    cursor.execute(query, (ip, mac))
                    conn.commit()
                    return True
                except sqlite3.Error as e:
                    print(f"[-] فشل إضافة الهدف: {e}")
        return False

if __name__ == "__main__":
    # تشغيل الفحص الذاتي عند تشغيل الملف مباشرة
    print("[*] جاري اختبار محرك قواعد البيانات...")
    DatabaseEngine.initialize_database()
    # تجربة إضافة هدف آمن
    DatabaseEngine.add_target_safe("192.168.1.1", "AA:BB:CC:DD:EE:FF")
