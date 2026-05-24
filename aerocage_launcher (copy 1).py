#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.db_manager import DBManager
from core.ui_base import UIBase, C_CYAN, G_OK, R_ERR, RESET
from core.ui_access_points import UIAccessPoints
from core.ui_groups import UIGroups
from core.ui_scout import UIScout
from core.ui_strike import UIStrike

class AeroCageLauncher:
    def __init__(self):
        self.db = DBManager()

    def main_hub(self):
        while True:
            UIBase.clear_screen()
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"🔥 {G_OK}[ لوحة السيطرة الكبرى وحرب الترددات اللاسلكية الموزعة : AeroCage-X ]{RESET}")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f" [{G_OK}1{RESET}] إدارة وحقن أجهزة الأكسس بوينت البعيدة")
            print(f" [{G_OK}2{RESET}] إدارة وتشييد مجموعات الفرز اللوجستي")
            print(f" [{C_CYAN}3{RESET}] رادار فحص واستعلام الزبائن اللحظي صامتاً (UBUS)")
            print(f" [{C_CYAN}4{RESET}] محرك الضربات الموجهة والمواجهات التفاعلية المرقمة")
            print(f" [{R_ERR}0{RESET}] قفل الصلاحيات والخروج الآمن من الفريمورك")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            opt = input("🔢 الاختيار الحركي: ").strip()
            if opt == "0" or opt == "exit":
                UIBase.clear_screen()
                print(f"\n{R_ERR}[-] تم قفل الصلاحيات وإغلاق نفق منصة AeroCage-X بنجاح. خروج نظيف.{RESET}\n")
                break
            elif opt == "1": UIAccessPoints.manage(self.db)
            elif opt == "2": UIGroups.manage(self.db)
            elif opt == "3": UIScout.run(self.db)
            elif opt == "4": UIStrike.launch(self.db)

if __name__ == "__main__":
    launcher = AeroCageLauncher()
    launcher.main_hub()
