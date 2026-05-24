#!/usr/bin/env python3
import getpass
from core.ui_base import UIBase, G_OK, R_ERR, Y_WARN, D_DIV, W_TEXT, RESET

class UIAccessPoints:
    @staticmethod
    def manage(db):
        while True:
            UIBase.show_header("لوحة التحكم وإدارة أجهزة الأكسس بوينت")
            aps = db.get_all_access_points()
            if aps:
                print(f" {W_TEXT}{'رقم':<4} | {'اسم الجهاز':<20} | {'عنوان IP':<15} | {'المجموعة المنتمية لها'}{RESET}")
                print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
                for idx, (ap_id, ap_name, ap_ip, ap_user, ap_pass, g_name) in enumerate(aps):
                    print(f" [{idx+1:<2}] | {ap_name:<20} | {ap_ip:<15} | {g_name if g_name else 'بدون مجموعة'}")
            else:
                print(f" ⚠️ {Y_WARN}لا توجد أي أجهزة مسجلة حالياً في قاعدة البيانات.{RESET}")
                
            print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f" [{G_OK}1{RESET}] إدخال وحقن أكسس بوينت جديد")
            print(f" [{R_ERR}2{RESET}] مسح وإلغاء جهاز أكسس من النظام")
            print(f" [{Y_WARN}3{RESET}] التعديل التكتيكي لمعطيات وكلمة سر أكسس مسجل")
            print(f" [{D_DIV}0{RESET}] العودة إلى القائمة الكبرى")
            print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            opt = input("🔢 الاختيار: ").strip()
            if opt in ["0", ""]: break
            elif opt == "1":
                UIBase.show_header("حقن وتسجيل أكسس بوينت جديد (اكتب 0 للتراجع)")
                name = UIBase.input_guard("📝 اسم الأكسس: ", "text", db, "ap_name")
                if name == "0": continue
                ip = UIBase.input_guard("🌐 عنوان الـ IP: ", "ip", db, "ap_ip")
                if ip == "0": continue
                username = input("👤 اسم المستخدم [الافتراضي root]: ").strip()
                if not username: username = "root"
                password = getpass.getpass("🔒 كلمة سر الـ SSH (مخفية صامتاً): ").strip()
                
                groups = db.get_all_groups()
                g_id = None
                if groups:
                    print(f"\n{Y_WARN}[ المجموعات المتاحة ]{RESET}")
                    for idx_g, g_id_val, g_name in zip(range(len(groups)), [g[0] for g in groups], [g[1] for g in groups]):
                        print(f"  [{idx_g+1}] {g_name}")
                    g_opt = input("🔢 رقم المجموعة لربط الجهاز بها (اضغط Enter لتخطيه): ").strip()
                    if g_opt.isdigit() and int(g_opt) <= len(groups): g_id = groups[int(g_opt)-1][0]

                db.add_access_point(name, ip, username, password, group_id=g_id)
                print(f"\n{G_OK}🟢 تم تسجيل وحفظ جهاز الأكسس بنجاح وآمن من التكرار.{RESET}")
                UIBase.return_prompt()
            elif opt == "2":
                if not aps: continue
                idx = input("🔢 أدخل رقم السطر للجهاز المراد حذفه: ").strip()
                if idx.isdigit() and int(idx) <= len(aps):
                    db.delete_access_point(aps[int(idx)-1][0])
                    print(f"\n{G_OK}🟢 تم مسح الجهاز بنجاح من قاعدة البيانات.{RESET}")
                UIBase.return_prompt()
            elif opt == "3":
                if not aps: continue
                idx = input("🔢 أدخل رقم السطر للجهاز المراد تعديل معطياته: ").strip()
                if not idx.isdigit() or int(idx) > len(aps): continue
                target_ap = aps[int(idx)-1]
                ap_id = target_ap[0]
                
                UIBase.show_header(f"تعديل الأكسس بوينت [{target_ap[1]}] (اضغط Enter للحفاظ على القديم)")
                new_name = input(f"📝 الاسم الحالي ({target_ap[1]}) -> الجديد: ").strip()
                if not new_name: new_name = target_ap[1]
                new_ip = input(f"🌐 الـ IP الحالي ({target_ap[2]}) -> الجديد: ").strip()
                if not new_ip: new_ip = target_ap[2]
                if not UIBase.is_valid_ip(new_ip): print(f"{R_ERR}❌ IP غير صالح{RESET}"); time.sleep(1); continue
                new_user = input(f"👤 اليوزر الحالي ({target_ap[3]}) -> الجديد: ").strip()
                if not new_user: new_user = target_ap[3]
                new_pass = getpass.getpass("🔒 كلمة السر الجديدة (اتركها فارغة للحفاظ على القديمة): ").strip()
                if not new_pass: new_pass = target_ap[4]
                
                # تحديث الخانات صامتاً بالنواة وقفل التكرار لطلبك
                with db._get_connection() as conn:
                    conn.execute("UPDATE access_points SET name=?, ip=?, username=?, password=? WHERE id=?;", (new_name, new_ip, new_user, new_pass, ap_id))
                    conn.commit()
                print(f"\n{G_OK}🟢 تم تعديل وحفظ بيانات الأكسس بوينت عتادياً بنجاح وبأعلى حماية.{RESET}")
                UIBase.return_prompt()
