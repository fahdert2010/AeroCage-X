#!/usr/bin/env python3
import os
import sys
import time
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية والأنظمة المشتركة للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.process_manager import ProcessManager

# تفعيل خط الدفاع الأول للمحيط التكتيكي لضمان صلاحيات الـ Root
SystemGuard.enforce_root_privileges("Strike Watchdog Engine")

class StrikeWatchdogEngine:
    def __init__(self):
        self.proc_manager = ProcessManager()
        self.watchdog_active = False
        self.monitored_targets = {}
        self.lock = threading.Lock()

    def register_target_for_monitoring(self, interface: str, target_bssid: str, command_array: list):
        """تسجيل وتلقيم هدف جديد في طابور الحراسة والمراقبة المستمرة"""
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid")
        
        if not clean_inf or not clean_mac or not command_array:
            return

        with self.lock:
            target_key = f"{clean_inf}_{clean_mac}"
            self.monitored_targets[target_key] = {
                "interface": clean_inf,
                "bssid": clean_mac,
                "command": command_array
            }
            print(f"[+] تم تسجيل الهدف [{clean_mac}] بنجاح في طابور رقابة الكلب الحارس.")

    def start_watchdog_loop_async(self, check_interval_sec: int = 5):
        """إطلاق محرك الحراسة والرقابة في الخلفية بأمان عالي ودون حظر المنظومة"""
        if self.watchdog_active:
            return

        self.watchdog_active = True
        threading.Thread(target=self._watchdog_core_worker, args=(check_interval_sec,), daemon=True).start()
        print("[*] تم تفعيل الكلب الحارس (Strike Watchdog) في الخلفية بنشاط...")

    def _watchdog_core_worker(self, interval: int):
        """العامل الخلفي المعزول لفحص حالة الأدوات اللاسلكية وإعادة إنعاشها برمجياً"""
        while self.watchdog_active:
            try:
                # أخذ نسخة من الأهداف لمنع أخطاء تداخل الذاكرة أثناء التكرار الخيطي
                with self.lock:
                    current_queue = list(self.monitored_targets.items())

                for target_key, info in current_queue:
                    mac = info["bssid"]
                    cmd_array = info["command"]
                    
                    with self.proc_manager.lock:
                        process = self.proc_manager.active_processes.get(mac)

                    # خط الدفاع الاستراتيجي: إذا كانت العملية مفقودة أو ماتت في نظام لينكس
                    if process is None or process.poll() is not None:
                        print(f"[⚠️] تنبيه حارس: تم رصد سقوط أو انهيار عملية القذف للهدف [{mac}]. جاري إنعاش الهجوم فوراً...")
                        
                        # تنظيف المخلفات القديمة من الذاكرة لمنع الـ Zombie Processes
                        self.proc_manager.terminate_process(mac)
                        
                        # إعادة إطلاق الهجوم الموجه بأمان كامل ومغلق الشل تماماً عبر مدير العمليات المركزي
                        # يغلق ثغرات Bandit (B602/B603) لأن shell=False مجبرة داخلياً في المحرك
                        self.proc_manager.spawn_process_safe(mac, cmd_array)
                
                # حل مشكلة استهلاك المعالج القاتل: إجبار الخيط على النوم والراحة لعدم حرق الـ CPU
                time.sleep(interval)
                
            except Exception as e:
                print(f"[-] عطل داخلي صامت في محرك الكلب الحارس: {e}")
                time.sleep(interval)

    def unregister_and_stop_target(self, target_bssid: str):
        """حذف الهدف من طابور الحراسة وإخماد عمليته الهجومية نهائياً"""
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid")
        
        with self.lock:
            # تنظيف طابور الحراسة
            keys_to_remove = [k for k, v in self.monitored_targets.items() if v["bssid"] == clean_mac]
            for k in keys_to_remove:
                del self.monitored_targets[k]
                
        # قطع العملية برمجياً عبر المدير المركزي
        self.proc_manager.terminate_process(clean_mac)
        print(f"[+] تم سحب حراسة الهدف [{clean_mac}] وقطع ضرباته بنجاح.")

    def stop_watchdog_completely(self):
        """إيقاف محرك الكلب الحارس بالكامل وتطهير الذاكرة"""
        self.watchdog_active = False
        with self.lock:
            self.monitored_targets.clear()
        print("[+] تم إخماد وتفكيك منظومة الكلب الحارس (Watchdog Disabled).")

if __name__ == "__main__":
    print("[*] محرك الكلب الحارس ومراقبة استقرار الهجمات (Strike Watchdog) مدمج ومحصن 100%.")
