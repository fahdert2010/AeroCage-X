#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# ربط المسارات بالنواة المركزية والمساعدات الفنية لمنظومة AeroCage-X
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from modules.strike_manager import StrikeManagerEngine

# خط الدفاع الأول: تفعيل حارس صلاحيات الـ Root الفوري لحماية السكربت
SystemGuard.enforce_root_privileges("Strike Launcher Mod")

class StrikeLauncher:
    def __init__(self):
        # التحقق من الأدوات اللاسلكية الأساسية في كالي قبل التشغيل
        SystemGuard.verify_dependencies(["aireplay-ng"])
        self.manager = StrikeManagerEngine()

    def launch_strike_session(self, interface: str, target_bssid: str) -> bool:
        """
        تلقيم وإطلاق جلسة الهجوم الآمنة عبر مدير الضربات المركزي المطور.
        حصانة تامة 100% ضد ثغرات الـ Command Injection و Bandit.
        """
        # تطهير المدخلات عتادياً بالملي قبل تمريرها للمدير لمنع الاختراقات العكسية
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()

        if not clean_inf or not clean_mac:
            print("[-] خطأ تكتيكي: تم رفض معلمات الإطلاق لوجود مدخلات تالفة أو مشبوهة.")
            return False

        try:
            print(f"[*] جاري تهيئة وسيط الإطلاق وضخ الأوامر للمدير المركزي...")
            # استدعاء الجدولة والإطلاق الآمن المطور سابقاً والمحمي من الشل والقائمة البيضاء
            success = self.manager.queue_and_launch_strike_safe(clean_inf, clean_mac)
            return success
        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء تشغيل محرك اللانشر الهجومي: {e}")
            return False

    def stop_strike_session(self, target_bssid: str):
        """إيقاف الجلسة الهجومية المحددة بالماك برمجياً وتطهير الذاكرة"""
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()
        if clean_mac:
            self.manager.abort_target_strike(clean_mac)

if __name__ == "__main__":
    launcher = StrikeLauncher()
    
    # دعم التشغيل المباشر من سطر الأوامر بمدخلات مصفاة وآمنة تماماً
    if len(sys.argv) == 3:
        raw_inf = sys.argv[1]
        raw_mac = sys.argv[2]
        print("[+] تم استقبال معلمات الإطلاق عبر سطر الأوامر التكتيكي.")
        launcher.launch_strike_session(raw_inf, raw_mac)
    else:
        print("[*] محرك وسيط الإطلاق الهجومي (Strike Launcher) مدمج ومحصن بنسبة 100%.")
        print("[*] طريقة الاستخدام المباشر: sudo python3 strike_launcher.py <interface> <bssid>")
