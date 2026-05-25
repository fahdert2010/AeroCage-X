#!/usr/bin/env python3
import os
import sys
import logging
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

class LoggerVault:
    _lock = threading.Lock()
    _initialized = False

    @classmethod
    def initialize_vault(cls):
        """تهيئة مخزن السجلات بشكل آمن ومنع التكرار"""
        with cls._lock:
            if cls._initialized:
                return

            # تحديد مجلد السجلات ديناميكياً باستخدام pathlib الآمنة
            log_dir = BASE_DIR / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "aerocage_tactical.log"

            # إعداد محرك التسجيل القياسي الحصين ضد تداخل الخيوط (Thread-Safe)
            logging.basicConfig(
                filename=str(log_file),
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filemode="a" # الحفظ بصيغة الإضافة المستمرة دون مسح السابق
            )
            cls._initialized = True
            print(f"[+] تم تهيئة مخزن التقارير المركزي بأمان في: {log_file}")

    @classmethod
    def log_event(cls, level: str, message: str):
        """كتابة الأحداث والضربات التكتيكية في المخزن مع تطهير كامل للنصوص"""
        if not cls._initialized:
            cls.initialize_vault()

        # خط الدفاع: تنظيف الرسالة المقروءة من أي رموز سطر جديد لمنع الـ Log Injection
        clean_message = SystemGuard.sanitize_input(message, "csv_value")
        # إزالة أحرف السطر الجديد الإضافية لضمان بقاء الحدث في سطر واحد قياسي
        clean_message = clean_message.replace("\n", " ").replace("\r", " ")

        with cls._lock:
            level = level.upper()
            if level == "INFO":
                logging.info(clean_message)
            elif level == "WARNING":
                logging.warning(clean_message)
            elif level == "ERROR":
                logging.error(clean_message)
            elif level == "CRITICAL":
                logging.critical(clean_message)
            else:
                logging.info(f"[UNKNOWN_LEVEL] {clean_message}")

if __name__ == "__main__":
    # اختبار ذاتي للمخزن المطور
    LoggerVault.initialize_vault()
    LoggerVault.log_event("INFO", "تم تشغيل نظام فحص السجلات المطور بنجاح.")
    LoggerVault.log_event("WARNING", "تنبيه وهمي للاختبار التكتيكي للأقفال.")
