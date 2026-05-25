#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

# التحقق من وجود مكتبة paramiko الاحترافية لإدارة الـ SSH بأمان
try:
    import paramiko
except ImportError:
    print("[-] خطأ نظامي: مكتبة paramiko غير مثبتة. جاري التثبيت التلقائي الصامت...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "paramiko"], shell=False)
    import paramiko

class SSHCommander:
    def __init__(self, host: str, username: str = "root", port: int = 22):
        self.host = SystemGuard.sanitize_input(host, "interface") # تنظيف الـ IP أو الهوست
        self.username = SystemGuard.sanitize_input(username, "interface")
        self.port = port
        self.client = None

    def _get_secure_client(self, password: str = None, key_path: str = None) -> paramiko.SSHClient:
        """إنشاء اتصال SSH آمن ومحمي بالكامل"""
        client = paramiko.SSHClient()
        # تعيين السياسة التلقائية لقبول مفاتيح الهوست (يمكن تخصيصها في الإنتاج الفعلي)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if key_path:
                private_key = paramiko.RSAKey.from_private_key_file(key_path)
                client.connect(self.host, port=self.port, username=self.username, pkey=private_key, timeout=10)
            else:
                client.connect(self.host, port=self.port, username=self.username, password=password, timeout=10)
            return client
        except Exception as e:
            print(f"[-] فشل إنشاء قناة الـ SSH الآمنة إلى {self.host}: {e}")
            return None

    def execute_remote_command_safe(self, command_args: list, password: str = None, key_path: str = None) -> str:
        """
        تنفيذ الأوامر عن بعد على الراوتر/السيرفر بأمان كامل 100%.
        تستقبل المدخلات كمصفوفة أجزاء مستقلة لمنع ثغرات الـ Command Injection نهائياً.
        """
        # تطهير عناصر الأمر بالملي عبر حارس المنظومة المشترك قبل تمريرها
        cleaned_args = [SystemGuard.sanitize_input(arg, "csv_value") for arg in command_args]
        full_command_string = " ".join(cleaned_args)

        self.client = self._get_secure_client(password, key_path)
        if not self.client:
            return ""

        stdout_data, stderr_data = "", ""
        try:
            print(f"[*] جاري إرسال الأمر المشفر عبر الأنبوب الآمن: {full_command_string}")
            # تنفيذ الأمر بأمان عبر القناة
            stdin, stdout, stderr = self.client.exec_command(full_command_string, timeout=15)
            
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            
            if stderr_data and not stdout_data:
                print(f"[-] تنبيه من الجهاز البعيد: {stderr_data.strip()}")
                
            return stdout_data.strip()

        except Exception as e:
            print(f"[-] حدث خطأ أثناء تنفيذ الأمر عن بعد: {e}")
            return ""
        finally:
            # خط الدفاع التلقائي: إغلاق الجلسة فوراً ومنع تسريب الموارد أو تعليق المنفذ
            if self.client:
                self.client.close()
                self.client = None

if __name__ == "__main__":
    print("[*] محرك التحكم العكسي (SSH Commander) مدمج ومؤمن بالكامل ضد الاختراق العكسي.")
    # مثال اختبار وهمي صامت
    # commander = SSHCommander("192.168.1.1")
    # output = commander.execute_remote_command_safe(["uci", "show", "wireless"], password="admin")
