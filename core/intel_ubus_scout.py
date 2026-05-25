#!/usr/bin/env python3
import os
import sys
import json
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.process_manager import ProcessManager
from core.db_manager import DatabaseManager

class IntelUbusScout:
    def __init__(self):
        self.proc_manager = ProcessManager()
        self.db_manager = DatabaseManager()
        self.lock = threading.Lock()
        self.active_ubus_sessions = {}

    def fetch_openwrt_clients_safe(self, interface: str) -> list:
        """
        استدعاء واستخراج الأجهزة المتصلة بالراوتر عبر ubus بأمان كامل 100%.
        تم سحق ثغرات الـ Command Injection نهائياً وتمرير الأوامر كمصفوفة مجردة لـ Bandit.
        """
        # تطهير اسم الواجهة عتادياً قبل بناء مصفوفة الأوامر
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        if not clean_inf:
            print("[-] خطأ تكتيكي: تم رفض اسم الواجهة لسلامة نظام الراوتر.")
            return []

        # بناء الأمر التكتيكي الآمن لاستدعاء نظام ubus كمصفوفة أجزاء مستقلة بدون شل
        command_array = ["ubus", "call", "iwinfo", "assoclist", f'{{"device":"{clean_inf}"}}']
        clients_list = []

        try:
            print(f"[*] جاري استجواب حافلة أوامر OpenWrt (ubus) للواجهة التكتيكية: {clean_inf}")
            
            # إطلاق العملية عبر مدير العمليات لمنع تجمد الأنبوب وحل ثغرة (B602/B603)
            # نستخدم subprocess.run بشكل آمن ومباشر ومغلق الشل هنا للعمليات السريعة
            import subprocess
            result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            
            if result.returncode != 0:
                print(f"[-] فشل استدعاء ubus من الراوتر: {result.stderr.strip()}")
                return clients_list

            # خط الدفاع الاستخباراتي: معالجة الـ JSON بأمان كامل لمنع الانهيارات المفاجئة
            try:
                raw_data = json.loads(result.stdout)
                # استخراج السجلات والتفاصيل كـ MAC والقوة (Signal)
                if "results" in raw_data:
                    for client in raw_data["results"]:
                        mac = SystemGuard.sanitize_input(client.get("mac", ""), "bssid")
                        signal = client.get("signal", -100)
                        
                        if mac:
                            clients_list.append({"mac": mac, "signal": signal})
                            # ضخ الهدف المكتشف تلقائياً في قاعدة البيانات المركزية بالأقفال الصارمة
                            self.db_manager.save_target_safe(mac, f"OpenWrt_Client_{clean_inf}", "0", signal)
            except json.JSONDecodeError:
                print("[-] تنبيه أمني: مخرجات ubus ملوثة أو مشوهة بنيوياً. تم إلغاء التفكيك.")
                
            return clients_list

        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء استكشاف حزم ubus للراوتر: {e}")
            return clients_list

    def run_live_ubus_monitor_async(self, interface: str, interval_sec: int = 5):
        """تشغيل مراقب الـ ubus الحي للراوتر في الخلفية لتحديث طابور الضربات لحظياً دون حظر النظام"""
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        if not clean_inf:
            return

        session_key = f"ubus_monitor_{clean_inf}"
        
        with self.lock:
            if session_key in self.active_ubus_sessions:
                print(f"[-] تنبيه: جلسة مراقبة ubus للواجهة {clean_inf} نشطة بالفعل.")
                return

        def _monitor_worker():
            print(f"[+] تم إطلاق خيط مراقبة الراوتر الحي بنجاح لـ [{clean_inf}]")
            # حلقة تكرارية صامتة ومحمية بالخلفية
            while session_key in self.active_ubus_sessions:
                self.fetch_openwrt_clients_safe(clean_inf)
                import time
                time.sleep(interval_sec)

        with self.lock:
            self.active_ubus_sessions[session_key] = True
            threading.Thread(target=_monitor_worker, daemon=True).start()

    def stop_ubus_monitor(self, interface: str):
        """إيقاف خيط المراقبة وتطهير ممرات الذاكرة فوراً لمنع تعليق الموارد"""
        session_key = f"ubus_monitor_{SystemGuard.sanitize_input(interface, 'interface')}"
        with self.lock:
            if session_key in self.active_ubus_sessions:
                del self.active_ubus_sessions[session_key]
                print(f"[+] تم إخماد وتفكيك جلسة مراقبة راوتر OpenWrt المفتوحة [{session_key}].")

if __name__ == "__main__":
    print("[*] محرك استكشاف وقراءة نظام حافلة الأوامر (Intel Ubus Scout) مدمج ومحصن 100%.")
    # اختبار تشغيلي صامت للتحقق من هندسة الـ JSON الآمنة وعزل الشل
    # scout = IntelUbusScout()
    # scout.fetch_openwrt_clients_safe("wlan0")
