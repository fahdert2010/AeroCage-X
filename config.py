# /home/kali/AeroCageX/config.py
import os

# المسارات الرئيسية للمنظومة
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")

DB_PATH = os.path.join(DATA_DIR, "aerocage.db")
LOG_PATH = os.path.join(LOGS_DIR, "error_vault.log")

def initialize_environment():
    """تأمين بناء المجلدات الحيوية عتادياً عند أول إقلاع للمنصة"""
    for folder in [DATA_DIR, LOGS_DIR, STORAGE_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

# استدعاء فوري عند الاستيراد للتأكد من جهوزية البيئة
initialize_environment()
