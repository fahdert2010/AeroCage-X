# /home/kali/AeroCageX/core/logger_vault.py
import logging
from config import LOG_PATH

# إعداد حارس السجلات الصارم
logging.basicConfig(
    filename=LOG_PATH,
    filemode='a',
    format='%(asctime)s | [%(levelname)s] | %(filename)s:%(lineno)d | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.ERROR
)

class LoggerVault:
    @staticmethod
    def log_exception(error_msg, exception_obj=None):
        """تسجيل الأخطاء والـ Stacks البرمجية بشكل معزول وصامت"""
        if exception_obj:
            logging.exception(f"{error_msg} -> {str(exception_obj)}")
        else:
            logging.error(error_msg)
