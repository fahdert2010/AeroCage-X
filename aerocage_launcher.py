#!/usr/bin/env python3
import sys
import os

# [قفل الأمان الكلي للمسارات]: شحن مسار جذر الفريمورك قسرياً في الذاكرة لمنع الـ ModuleNotFoundError للأبد
sys.path.insert(0, "/home/kali/AeroCage-X")

from core.intel_db import IntelDBManager
from core.ui_base import UIBase, C_CYAN, G_OK, R_ERR, RESET
from core.ui_access_points import UIAccessPoints
from core.ui_groups import UIGroups
from core.ui_scout import UIScout
from core.ui_strike import UIStrike

class AeroCageLauncher:
    def __init__(self):
        self.db = IntelDBManager()

    def main_hub(self):
        while True:
            UIBase.clear_screen()
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"🔥 {G_OK}[ لوحة السيطرة الكبرى وحرب الترددات اللاسلكية الموزعة : AeroCage-X الموحد ]{RESET}")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f" [{G_OK}1{RESET}] إدارة وحقن أجهزة الأكسس بوينت البعيدة")
            print(f" [{G_OK}2{RESET}] إدارة وتشييد مجموعات الفرز اللوجستي")
            print(f" [{C_CYAN}3{RESET}] رادار فحص واستعلام الزبائن اللحظي صامتاً (UBUS الموحد)")
            print(f" [{C_CYAN}4{RESET}] منصة السجلات والتحليل الاستخباراتي للأجواء والنسب المئوية")
            print(f" [{G_OK}5{RESET}] محرك الضربات الموجهة والمواجهات التفاعلية (المحمي من الانهيار)")
            print(f" [{R_ERR}0{RESET}] قفل الصلاحيات والخروج الآمن من الفريمورك")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            opt = input("🔢 الاختيار العملياتي: ").strip()
            if opt in ["0", "exit"]:
                UIBase.clear_screen()
                print(f"\n{R_ERR}[-] تم قفل الصلاحيات وإغلاق نفق منصة AeroCage-X بنجاح. خروج نظيف.{RESET}\n")
                break
            elif opt == "1": UIAccessPoints.manage(self.db)
            elif opt == "2": UIGroups.manage(self.db)
            elif opt == "3": UIScout.run(self.db)
            elif opt == "4":
                # تصحيح ربط ملف رادار الأجواء التاريخي بالاسم الفعلي المستقر بالقرص
                from aeroscout_intel_hub import AeroScoutIntelHub
                hub = AeroScoutIntelHub()
                hub.main_menu()
            elif opt == "5": UIStrike.launch(self.db)

if __name__ == "__main__":
    launcher = AeroCageLauncher()
    launcher.main_hub()
