import os
from pathlib import Path
from dotenv import load_dotenv

# تحديد المسار الرئيسي للمشروع ديناميكياً ليناسب Kali و OpenWrt
BASE_DIR = Path(__file__).resolve().parent

# تحميل متغيرات البيئة من ملف .env خفي
load_dotenv(BASE_DIR / ".env")

class Config:
    VERSION = "1.0.0"
    APP_NAME = "AeroCage-X"
    
    # تأمين المسارات بشكل متوافق مع جميع أنظمة التشغيل
    LOG_DIR = BASE_DIR / "logs"
    DATA_DIR = BASE_DIR / "data"
    
    # جلب البيانات الحساسة من البيئة وليس كتابتها يدوياً
    DB_NAME = os.getenv("ACX_DB_NAME", "aerocage_core.db")
    DB_USER = os.getenv("ACX_DB_USER", "admin")
    DB_PASSWORD = os.getenv("ACX_DB_PASSWORD", "SuperSecretPassword123!")
    
    @classmethod
    def initialize_dirs(cls):
        """دالة ذكية لإنشاء المجلدات تلقائياً إذا لم تكن موجودة لمنع أخطاء التشغيل"""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

# تفعيل إنشاء المجلدات فور استدعاء الملف
Config.initialize_dirs()
