#!/usr/bin/env python3
from core.ui_base import UIBase, G_OK, R_ERR, Y_WARN, D_DIV, W_TEXT, RESET

class UIGroups:
    @staticmethod
    def manage(db):
        while True:
            UIBase.show_header("لوحة التحكم وإدارة مجموعات الفرز اللوجستي")
            groups = db.get_all_groups()
            
            if groups:
                print(f" {W_TEXT}{'رقم السطر':<10} | {'اسم المجموعة بالذاكرة'}{RESET}")
                print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
                for idx, (g_id, g_name) in enumerate(groups):
                    print(f" [{idx+1:<8}] | {g_name}")
            else:
                print(f" ⚠️ {Y_WARN}لا توجد أي مجموعات فرز مسجلة حالياً في قاعدة البيانات.{RESET}")
                
            print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f" [{G_OK}1{RESET}] إنشاء وحقن مجموعة فرز جديدة")
            print(f" [{R_ERR}2{RESET}] حذف مجموعة فرز")
            print(f" [{D_DIV}0{RESET}] العودة إلى القائمة الكبرى")
            print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            opt = input("🔢 الاختيار: ").strip()
            if opt in ["0", ""]: break
            elif opt == "1":
                UIBase.show_header("حقن مجموعة فرز جديدة")
                g_name = UIBase.input_guard("📝 اسم المجموعة الجديد: ", "text", db, "group")
                if g_name != "0":
                    db.add_group(g_name)
                    print(f"\n{G_OK}🟢 تم إضافة مجموعة الفرز اللوجستي بنجاح ونظافة.{RESET}")
                UIBase.return_prompt()
            elif opt == "2":
                if not groups: continue
                idx = input("🔢 أدخل رقم السطر للمجموعة المراد حذفها: ").strip()
                if idx.isdigit() and int(idx) <= len(groups):
                    # [سحق الـ Tuple]: استخراج الـ ID الرقمي الصافي المفتت وحسم خطأ الحذف لقاعدة البيانات
                    real_g_id = groups[int(idx)-1][0]
                    success, msg = db.delete_group(real_g_id)
                    print(f"\n{msg}")
                UIBase.return_prompt()
