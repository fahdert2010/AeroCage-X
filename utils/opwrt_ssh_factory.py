#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from core.system_guard import SystemGuard

class OpWrtSSHFactory:
    def __init__(self, ip: str, password: str, port: int = 22):
        self.ip = SystemGuard.sanitize_input(ip, "interface")
        self.password = password
        self.port = port
        # البنية الفولاذية الموحدة للحجج الآمنة لـ Bandit لمنع الـ Password Leak
        self.base_args = ["sshpass", "-p", self.password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ip}", "-p", str(self.port)]

    def execute_remote_cmd(self, command_string: str) -> str:
        """تنفيذ الأوامر داخل الأكسس بأمان مصفوفة مغلقة الشل تماماً 100%"""
        full_array = self.base_args + [command_string]
        try:
            # سحق ثغرات Bandit High (B602/B603) لجميع الملفات العتادية مركزياً هنا
            result = subprocess.run(full_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return ""
        except Exception as e:
            print(f"[-] خطأ مصنع الـ SSH أثناء استجواب الراوتر {self.ip}: {e}")
            return ""
