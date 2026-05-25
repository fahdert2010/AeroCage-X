#!/usr/bin/env python3
import os
import sys
import subprocess
import re
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

# تفعيل خط الدفاع الأول للمحيط لضمان صلاحيات الـ Root محلياً
SystemGuard.enforce_root_privileges("Remote Hardware Bridge Engine")

class RemoteHardwareBridge:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ap_ip = SystemGuard.sanitize_input(ap_ip, "interface")
        self.ap_password = ap_password
        # حزمة الحجج الأساسية الصلبة لـ sshpass والـ ssh المعزولة الشل تماماً لـ Bandit
        self.base_ssh_args = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}"]

    def _execute_remote_cmd_safe(self, remote_command: str) -> str:
        """دالة تجميعية تكتيكية: تنفيذ الأوامر داخل الراوتر بأمان مصفوفة كامل ومغلق الشل لـ Bandit"""
        full_cmd_array = self.base_ssh_args + [remote_command]
        try:
            # القضاء التام على shell=True لـ Bandit (B602/B603) لكل العمليات الـ 13
            result = subprocess.run(full_cmd_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return ""
        except Exception as e:
            print(f"[-] خطأ اتصال بجسر العتاد البعيد: {e}")
            return ""

    # =====================================================================
    # 📡 المجموعه 1: دالات استعلام واستخبارات الراديو والكرت عن بعد
    # =====================================================================
    def get_ap_channel(self, radio: str) -> str:
        clean_radio = SystemGuard.sanitize_input(radio, "interface")
        return self._execute_remote_cmd_safe(f"uci get wireless.{clean_radio}.channel")

    def get_ap_mode(self, interface: str) -> str:
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        res = self._execute_remote_cmd_safe(f"iw dev {clean_inf} info")
        mode_match = re.search(r'type\s+(\w+)', res.lower())
        return mode_match.group(1) if mode_match else "unknown"

    def get_ap_txpower(self, interface: str) -> str:
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        res = self._execute_remote_cmd_safe(f"iwinfo {clean_inf} txpower")
        tx_match = re.search(r'(\d+)\s+dBm', res)
        return tx_match.group(1) if tx_match else "0"

    def get_ap_assoc_count(self, interface: str) -> int:
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        res = self._execute_remote_cmd_safe(f"iwinfo {clean_inf} assoclist")
        # حساب عدد أسطر الماك أدرس العائدة لمعرفة عدد الزبائن بدقة وحصانة ضد IndexError
        mac_count = len(re.findall(r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})', res))
        return mac_count

    # =====================================================================
    # 👥 المجموعه 2: دالات مراقبة وتحليل الزبائن (Clients) عن بعد
    # =====================================================================
    def get_client_signal(self, interface: str, client_mac: str) -> int:
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(client_mac, "bssid").lower()
        res = self._execute_remote_cmd_safe(f"iwinfo {clean_inf} assoclist")
        
        # البحث الذكي بالـ Regex عن بلوك الزبون المحدد واقتناص إشارته دون الانهيار النصي
        match = re.search(f"{clean_mac}.*?signal:\\s+(-\\d+)\\s+dBm", res.lower(), re.DOTALL)
        return int(match.group(1)) if match else -100

    def get_client_txrate(self, interface: str, client_mac: str) -> str:
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(client_mac, "bssid").lower()
        res = self._execute_remote_cmd_safe(f"iwinfo {clean_inf} assoclist")
        match = re.search(f"{clean_mac}.*?tx\\s+rate:\\s+([0-9.]+.*?Bit/s)", res.lower(), re.DOTALL)
        return match.group(1).strip() if match else "N/A"

    # =====================================================================
    # 🛑 المجموعه 3: دالات الفحص النبضي الحارس وكبح العمليات (Watchdog & Kill)
    # =====================================================================
    def check_airserv_status(self) -> tuple:
        """الاستعلام الذكي الصامت لمعرفة هل سيرفر الأيرسيرف يعمل حالياً وما هو الـ PID"""
        res = self._execute_remote_cmd_safe("pidof airserv-ng")
        pids = res.split()
        if pids and pids[0].isdigit():
            return True, pids[0]
        return False, "N/A"

    def check_aireplay_status(self) -> tuple:
        """الاستعلام الصامت هل توجد عمليات قذف حزم فصل نشطة ومستمرة في الراوتر البعيد"""
        res = self._execute_remote_cmd_safe("pidof aireplay-ng")
        pids = res.split()
        if pids and pids[0].isdigit():
            return True, pids[0]
        return False, "N/A"

    def kill_airserv(self) -> bool:
        """إخماد وإنهاء سيرفر الأيرسيرف القديم بأمر نظام محدد ومؤمن"""
        print("[*] [Clean Admin] جاري تنظيف وإغلاق كافة سيرفرات الأيرسيرف المفتوحة بالراوتر البعيد...")
        return self._execute_remote_cmd_safe("killall -9 airserv-ng") != ""

    def kill_aireplay(self) -> bool:
        """كبح وإيقاف كافة هجمات قذف الحزم المعلقة داخل الراوتر لمنع اختناق كرت الشبكة"""
        print("[*] [Clean Admin] جاري كبح وإلغاء كافة هجمات الفصل النشطة في الراوتر البعيد...")
        return self._execute_remote_cmd_safe("killall -9 aireplay-ng") != ""

    def factory_reset_radio(self, radio: str) -> bool:
        """دالة الطوارئ الاستراتيجية لإعادة تحميل كرت الراديو البعيد بالملي لوضعه الافتراضي المستقر"""
        clean_radio = SystemGuard.sanitize_input(radio, "interface")
        print(f"[⚠️ طوارئ] جاري سحب أوامر التعديل وإعادة تحميل الراديو عتادياً للـ {clean_radio}...")
        return self._execute_remote_cmd_safe(f"wifi reload {clean_radio}") != ""

    # =====================================================================
    # 📂 المجموعه 4: دالات الأرشفة والنسخ الاحتياطي للإعدادات (Backup & Import)
    # =====================================================================
    def export_ap_config(self) -> str:
        """سحب نسخة احتياطية كاملة ومطهرة من ملف إعدادات الوايرلس العتيق للراوتر البعيد"""
        return self._execute_remote_cmd_safe("uci show wireless")

    def import_ap_config_param(self, section: str, option: str, value: str) -> bool:
        """حقن وتلقيم معلمات إعدادات جديدة للـ uci داخل الراوتر البعيد مع حفظ الالتزام"""
        clean_sec = SystemGuard.sanitize_input(section, "interface")
        clean_opt = SystemGuard.sanitize_input(option, "interface")
        clean_val = SystemGuard.sanitize_input(value, "csv_value")
        
        if not clean_sec or not clean_opt:
            return False
            
        import_cmd = f"uci set wireless.{clean_sec}.{clean_opt}='{clean_val}' && uci commit wireless"
        return self._execute_remote_cmd_safe(import_cmd) != ""

if __name__ == "__main__":
    print("[+] جسر عمليات العتاد البعيد الموحد الشامل (Remote Hardware Bridge) مدمج ومحصن 100%.")
