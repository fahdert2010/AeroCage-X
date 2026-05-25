#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

class InterfaceFactory:
    def __init__(self):
        # التحقق من الأدوات الأساسية المطلوبة لنظام كالي
        SystemGuard.verify_dependencies(["iwconfig", "ip", "iw"])

    def get_available_wireless_interfaces(self) -> list:
        """
        استخراج كروت الشبكة اللاسلكية المتاحة في النظام ديناميكياً وبأمان كامل.
        تعتمد على التعبيرات النمطية لمنع أخطاء الـ IndexError.
        """
        interfaces = []
        command = ["iwconfig"]
        
        try:
            # تشغيل آمن ومغلق الشل تماماً يقتل ثغرة البانديت (B602/B603)
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            if result.returncode != 0:
                return interfaces

            # نمط للبحث عن أسماء الواجهات اللاسلكية في مخرجات iwconfig القياسية
            # يمسك بالأسماء المبتدئة بـ wlan أو ath أو ra أو wlp وغيرها
            pattern = re.compile(r'^([a-zA-Z0-9._-]+)\s+IEEE')
            
            for line in result.stdout.splitlines():
                match = pattern.match(line)
                if match:
                    if_name = match.group(1)
                    # تطهير فوري للاسم المستخرج لسلامة بقية المنظومة
                    interfaces.append(SystemGuard.sanitize_input(if_name, "interface"))
                    
            return interfaces
        except Exception as e:
            print(f"[-] عطل أثناء فحص الواجهات اللاسلكية بالنظام: {e}")
            return interfaces

    def control_interface_state(self, interface: str, state: str) -> bool:
        """
        التحكم في تشغيل أو إيقاف كرت الشبكة (up / down) بأمان عالي جداً.
        """
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        if state.lower() not in ["up", "down"]:
            return False

        command = ["ip", "link", "set", clean_inf, state.lower()]
        try:
            print(f"[*] جاري ضبط حالة الكرت المركزي [{clean_inf}] إلى الوضع: {state.upper()}")
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            return result.returncode == 0
        except Exception as e:
            print(f"[-] فشل تغيير حالة كرت الشبكة {clean_inf}: {e}")
            return False

    def is_monitor_mode_active(self, interface: str) -> bool:
        """
        التحقق من الوضع الحالي لكرت الشبكة (Mode: Monitor) بشكل محصن وذكي.
        """
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        command = ["iw", "dev", clean_inf, "info"]
        
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            if "type monitor" in result.stdout.lower() or "mode monitor" in result.stdout.lower():
                return True
        except Exception:
            pass
        return False

if __name__ == "__main__":
    print("[*] مصنع كروت واجهات الشبكة اللاسلكية مدمج ومؤمن بنسبة 100%.")
    # اختبار تشغيلي صامت للتحقق من المخرجات النظيفة
    factory = InterfaceFactory()
    cards = factory.get_available_wireless_interfaces()
    print(f"[+] كروت الشبكة اللاسلكية المكتشفة في كالي: {cards}")
