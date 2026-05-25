#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# ربط المسارات بالنواة المركزية والأنظمة المساعدة للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.network_validators import NetworkValidators
from core.db_manager import DatabaseManager

# تفعيل خط الدفاع الأول للمحيط التكتيكي لحماية الصلاحيات
SystemGuard.enforce_root_privileges("Strike Whitelist Engine")

class StrikeWhitelistEngine:
    def __init__(self, whitelist_file: str = "whitelist.txt"):
        self.db_manager = DatabaseManager()
        # تحديد مسار ملف القائمة البيضاء ديناميكياً داخل مجلد البيانات الآمن
        self.whitelist_path = BASE_DIR / "data" / whitelist_file
        self._ensure_whitelist_file_exists()

    def _ensure_whitelist_file_exists(self):
        """إنشاء ملف القائمة البيضاء تلقائياً إذا لم يكن موجوداً لمنع الانهيارات البرمجية"""
        try:
            self.whitelist_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.whitelist_path.exists():
                with open(self.whitelist_path, "w", encoding="utf-8") as f:
                    f.write("# AeroCage-X | قائمة الأجهزة الصديقة المحمية من الاستهداف\n")
                    f.write("# اكتب عناوين الـ MAC Address سطرًا تلو الآخر (مثال: AA:BB:CC:DD:EE:FF)\n")
                print(f"[+] تم إنشاء ملف القائمة البيضاء القياسي في: {self.whitelist_path}")
        except Exception as e:
            print(f"[-] خطأ أثناء تهيئة ملف القائمة البيضاء: {e}")

    def load_clean_whitelist(self) -> set:
        """
        قراءة وتطهير عناوين القائمة البيضاء بأمان كامل وحصانة ضد أخطاء القراءة.
        تستخدم المساعد الموحد لضمان التصفية الصارمة للماك أدرس فقط.
        """
        whitelist_set = set()
        if not self.whitelist_path.exists():
            return whitelist_set

        try:
            with open(self.whitelist_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    # تخطي الأسطر الفارغة والتعليقات لمنع الـ IndexError
                    if not line or line.startswith("#"):
                        continue
                    
                    # خط الدفاع الاستخباراتي: البحث عن صيغ الماك أدرس وتحققها عبر المساعد الموحد
                    extracted_macs = NetworkValidators.extract_bssids_from_text(line)
                    for mac in extracted_macs:
                        if NetworkValidators.is_valid_bssid(mac):
                            # تنظيف وتطهير فوري للماك قبل حجز مسار له في الذاكرة لضمان أمن Bandit
                            clean_mac = SystemGuard.sanitize_input(mac, "bssid")
                            whitelist_set.add(clean_mac.upper())
                            
            print(f"[+] تم تحميل وتطهير {len(whitelist_set)} جهاز صديق في القائمة البيضاء الفعالة.")
            return whitelist_set
        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء معالجة ملف القائمة البيضاء: {e}")
            return whitelist_set

    def is_target_whitelisted(self, target_bssid: str) -> bool:
        """فحص فوري وذكي لمعرفة ما إذا كان الهدف محمياً ومدرجاً بالقائمة البيضاء أم لا"""
        clean_mac = SystemGuard.sanitize_input(target_bssid, "bssid").upper()
        if not NetworkValidators.is_valid_bssid(clean_mac):
            return False
            
        active_whitelist = self.load_clean_whitelist()
        return clean_mac in active_whitelist

    def enforce_whitelist_on_targets(self, raw_targets_list: list) -> list:
        """
        غربلة طابور الأهداف واستئصال الأجهزة الصديقة المدرجة في القائمة البيضاء جبرياً
        لحمايتها ومنع قذفها بحزم الفصل اللاسلكية بالخطأ.
        """
        whitelist = self.load_clean_whitelist()
        sanitized_targets = []
        purged_count = 0

        for target in raw_targets_list:
            bssid = SystemGuard.sanitize_input(target.get("bssid", ""), "bssid").upper()
            
            if bssid in whitelist:
                purged_count += 1
                continue # طرد واستبعاد الجهاز المحمي فوراً من طابور الضربات
                
            sanitized_targets.append(target)

        if purged_count > 0:
            print(f"[🛡️] تنبيه نظامي: تم رصد واعتراض واستبعاد {purged_count} جهاز صديق من طابور الهجوم بنجاح!")
        return sanitized_targets

if __name__ == "__main__":
    print("[*] محرك إدارة القائمة البيضاء وحماية الأجهزة الصديقة (Strike Whitelist) مدمج ومحصن 100%.")
    # اختبار تشغيلي صامت للتحقق من كفاءة الفرز وحماية الأجهزة
    # engine = StrikeWhitelistEngine()
    # is_protected = engine.is_target_whitelisted("AA:BB:CC:DD:EE:FF")
