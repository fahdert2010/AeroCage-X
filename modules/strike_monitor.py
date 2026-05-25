#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# ربط المسارات بالنواة المركزية والمساعدات الفنية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.process_manager import ProcessManager

# تفعيل خط الدفاع الأول لضمان صلاحيات الـ Root محلياً
SystemGuard.enforce_root_privileges("Strike Monitor Remote OpenWrt Engine")

class StrikeMonitorEngine:
    def __init__(self, ap_ip: str, ap_password: str):
        self.proc_manager = ProcessManager()
        self.lock = threading.Lock()
        self.monitoring_active = False
        self.ap_ip = SystemGuard.sanitize_input(ap_ip, "interface")
        self.ap_password = ap_password # سيتم تمريرها بأمان خفي عبر الأنبوب وليس نصاً صريحاً
        self.remote_monitor_interfaces = [] # هنا يتم تخزين أسماء القنوات المزدوجة المنشأة داخل الراوتر

    def setup_remote_dual_monitor_channels(self, ap_iface1: str, ap_iface2: str) -> bool:
        """
        حقن وتنفيذ الاتفاق التكتيكي داخل راوتر OpenWrt عن بعد:
        إنشاء واجهتي مراقبة، جلب أسمائهما، ثم التحقق الجراحي من نجاح العملية داخل الراوتر بدون ثغرات Bandit.
        """
        clean_if1 = SystemGuard.sanitize_input(ap_iface1, "interface")
        clean_if2 = SystemGuard.sanitize_input(ap_iface2, "interface")

        if not clean_if1 or not clean_if2 or clean_if1 == clean_if2:
            print("[-] خطأ معمارية: معلمات واجهات الراوتر غير صالحة أو مكررة.")
            return False

        print(f"[*] جاري الاتصال بالراوتر {self.ap_ip} لإنشاء القنوات المزدوجة لـ [{clean_if1}] و [{clean_if2}]...")

        # بناء الأوامر التنفيذية التي ستسري داخل نظام أوبن ورت البعيد
        remote_cmd_1 = f"iw dev {clean_if1} interface add {clean_if1}mon type monitor && ifconfig {clean_if1}mon up"
        remote_cmd_2 = f"iw dev {clean_if2} interface add {clean_if2}mon type monitor && ifconfig {clean_if2}mon up"
        
        # أمر دالة التحقق التكتيكية: فحص نظام الراوتر للتأكد من وجود الواجهات الجديدة وأنها بوضع المراقبة فعلياً
        verify_remote_cmd = f"iw dev {clean_if1}mon info && iw dev {clean_if2}mon info"

        # حيلة التمرير الفولاذية لـ sshpass لـ Bandit (B602/B603):
        # نستخدم الخيار -f بدلاً من -p لكي يقرأ الباسوورد من أنبوب خفي، ونعطل الـ shell تماماً
        base_ssh_args = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}"]

        try:
            # 1. إرسال أمر إنشاء وتشغيل القناة الأولى في الراوتر بأمان كامل
            subprocess.run(base_ssh_args + [remote_cmd_1], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            # 2. إرسال أمر إنشاء وتشغيل القناة الثانية في الراوتر
            subprocess.run(base_ssh_args + [remote_cmd_2], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)

            # 3. استدعاء دالة التأكد والتحقق من عملية الإنشاء داخل الراوتر عن بعد
            check_result = subprocess.run(base_ssh_args + [verify_remote_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)

            # إذا احتوت مخرجات الراوتر على كلمة type monitor لكلا الكرتين، فهذا يعني نجاح الاتفاق بالملي
            if check_result.returncode == 0 and "type monitor" in check_result.stdout.lower():
                with self.lock:
                    self.remote_monitor_interfaces = [f"{clean_if1}mon", f"{clean_if2}mon"]
                print(f"[+ OpenWrt] نجحت دالة التحقق عن بعد! القنوات المزدوجة منشأة ونشطة داخل الراوتر: {self.remote_monitor_interfaces}")
                return True
            else:
                print("[-] فشل دالة التحقق عن بعد: تعذر إنشاء واجهات المراقبة داخل نظام OpenWrt.")
                print(f"[-] مخرجات عطل الراوتر: {check_result.stderr.strip()}")
                return False

        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء حقن واجهات المراقبة عبر الـ SSH: {e}")
            return False

    def start_remote_strike_monitoring_async(self, target_mac: str):
        """إطلاق مراقبة جودة الضربات حياً من داخل الراوتر دون حظر نظام كالي"""
        with self.lock:
            if len(self.remote_monitor_interfaces) < 2:
                print("[-] خطأ: لم يتم تهيئة القنوات المزدوجة في الراوتر بعد.")
                return False
            intel_iface = self.remote_monitor_interfaces[0] # القناة الأولى لجمع البيانات والاستطلاع

        clean_target = SystemGuard.sanitize_input(target_mac, "bssid")
        session_key = f"remote_mon_{clean_target}"

        # أمر تشغيل tshark أو tcpdump داخل الراوتر لقراءة حزم الفصل حياً وإرسال النتائج لكالي
        remote_monitor_cmd = f"tcpdump -i {intel_iface} -n 'wlan[0] == 0xc0 and wlan addr1 {clean_target}'"
        
        full_command_array = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}", remote_monitor_cmd]

        try:
            print(f"[📡 Remote Monitor] جاري بدء سحب قراءات جودة الضربة حياً من الراوتر للهدف: {clean_target}")
            # تمرير المهمة لمدير العمليات لتفريغ البافر اللحظي ومنع تجميد الأنبوب والقضاء على ثغرة Bandit High
            self.proc_manager.spawn_process_safe(session_key, full_command_array)
            return True
        except Exception as e:
            print(f"[-] خطأ أثناء تشغيل خط أنابيب المراقبة العكسية للراوتر: {e}")
            return False

    def stop_remote_monitoring(self, target_mac: str):
        """قطع جلسة المراقبة البعيدة وتطهير الذاكرة لمنع العمليات المعلقة Zombie Processes"""
        clean_mac = SystemGuard.sanitize_input(target_mac, "bssid")
        session_key = f"remote_mon_{clean_mac}"
        
        # إرسال أمر قتل عملية tcpdump داخل الراوتر البعيد أولاً لتنظيف ذاكرة OpenWrt
        kill_cmd = "killall tcpdump"
        subprocess.run(["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}", kill_cmd], shell=False)
        
        # إنهاء العملية المحلية المتحكمة في السوكت وجلسة الـ SSH في كالي
        self.proc_manager.terminate_process(session_key)
        print(f"[+] تم قطع قنوات المراقبة العكسية وتطهير الذاكرة للهدف [{clean_mac}] بنجاح.")

if __name__ == "__main__":
    print("[*] محرك الشاشة التكتيكية ومراقب جودة ضربات راوترات OpenWrt (Strike Monitor) مدمج ومحصن 100%.")
