#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# ربط النواة والحارس والمساعد الشبكي المشترك
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.network_validators import NetworkValidators

SystemGuard.enforce_root_privileges("Kali Pipeline Engine")

class KaliPipelineEngine:
    def __init__(self):
        self.active_pipeline_processes = []

    def run_pipeline_step_safe(self, tool: str, args_list: list) -> str:
        if not SystemGuard.verify_dependencies([tool]):
            return ""

        # تطهير المدخلات عتادياً وعزل الشل
        cleaned_tool = SystemGuard.sanitize_input(tool, "interface")
        cleaned_args = [SystemGuard.sanitize_input(arg, "csv_value") for arg in args_list]
        
        # خط الدفاع الاستخباراتي: فحص الأهداف الملقمة داخل الحجج عبر المساعد الموحد
        for arg in cleaned_args:
            # إذا احتوت الحجج على IP أو MAC، يتم التحقق الجراحي من صيغتها لمنع الاختراق العكسي
            if "." in arg and not NetworkValidators.is_valid_ip(arg):
                print(f"[-] تنبيه أمني حرج: تم رصد واعتراض عنوان IP ملوث في الأنبوب: {arg}")
                return ""
            if ":" in arg and not NetworkValidators.is_valid_bssid(arg):
                print(f"[-] تنبيه أمني حرج: تم رصد واعتراض عنوان MAC ملوث في الأنبوب: {arg}")
                return ""

        full_command = [cleaned_tool] + cleaned_args
        try:
            print(f"[*] جاري تنفيذ خطوة الأنبوب الآمنة والمصفاة سيبرانياً: {' '.join(full_command)}")
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False # مغلق تماماً وفق معايير Bandit الفولاذية
            )
            self.active_pipeline_processes.append(process)
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                print(f"[+] نجحت خطوة الأنبوب للأداة المحمية {cleaned_tool}.")
                return stdout.strip()
            else:
                print(f"[-] تنبيه: فشل تنفيذ الأداة {cleaned_tool}. مخرجات الخطأ: {stderr.strip()}")
                return ""
        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء تشغيل الـ Pipeline المركزي: {e}")
            return ""

if __name__ == "__main__":
    print("[*] محرك الأنابيب لـ كالي مدمج ومطهر كلياً من الأكواد والوظائف الفرعية المكررة.")
