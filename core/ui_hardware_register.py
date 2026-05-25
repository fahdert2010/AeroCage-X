#!/usr/bin/env python3
import os
import sys
import tkinter as tk
import arabic_reshaper
from bidi.algorithm import get_display
from tkinter import messagebox, ttk
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.ui_base import AeroCageUIBase

class AeroCageHardwareRegisterGUI(AeroCageUIBase):
    def __init__(self, root: tk.Tk, db_instance):
        super().__init__(root, title="إدارة وتلقيم الأكسسات المهاجمة للترسانة", width=550, height=480)
        self.db_manager = db_instance
        self.build_register_form()

    def build_register_form(self):
        def fix_ar(text): return get_display(arabic_reshaper.reshape(text))

        # 1. جلب المجموعات الحية من قاعدة البيانات بالأقفال الصارمة لملء القائمة المنسدلة
        available_groups = []
        try:
            with self.db_manager._get_secure_connection() as conn:
                rows = conn.execute("SELECT DISTINCT tactical_group FROM tactical_targets;").fetchall()
                available_groups = [row["tactical_group"] for row in rows if row["tactical_group"]]
        except Exception: pass
        if not available_groups: available_groups = ["Default_Attack_Group"]

        # العنوان الرئيسي للواجهة
        lbl_title = tk.Label(self.root, text=fix_ar("⚙️ مركز تسجيل وتلقيم الخوادم المهاجمة للترسانة"), font=("Courier", 12, "bold"))
        self.apply_cyber_theme(lbl_title, "label")
        lbl_title.pack(pady=20)

        # إطار الحقول الرئيسي
        form_frame = tk.Frame(self.root, bg=self.bg_main)
        form_frame.pack(padx=30, fill=tk.X)

        # الحقول الخمسة المنسقة والملونة بالثيم الداكن بالملي
        tk.Label(form_frame, text=fix_ar("اسم خادم الهجوم (ESSID):"), fg=self.fg_text, bg=self.bg_main).grid(row=0, column=0, sticky=tk.W, pady=8)
        self.ent_name = tk.Entry(form_frame, width=24)
        self.apply_cyber_theme(self.ent_name, "entry")
        self.ent_name.grid(row=0, column=1, pady=8, padx=15)

        tk.Label(form_frame, text=fix_ar("عنوان IP الراوتر (OpenWrt):"), fg=self.fg_text, bg=self.bg_main).grid(row=1, column=0, sticky=tk.W, pady=8)
        self.ent_ip = tk.Entry(form_frame, width=24)
        self.ent_ip.insert(0, "192.168.1.1")
        self.apply_cyber_theme(self.ent_ip, "entry")
        self.ent_ip.grid(row=1, column=1, pady=8, padx=15)

        tk.Label(form_frame, text=fix_ar("اسم مستخدم الـ SSH للراوتر:"), fg=self.fg_text, bg=self.bg_main).grid(row=2, column=0, sticky=tk.W, pady=8)
        self.ent_user = tk.Entry(form_frame, width=24)
        self.ent_user.insert(0, "root") # مستخدم روت افتراضي لتوفير وقتك
        self.apply_cyber_theme(self.ent_user, "entry")
        self.ent_user.grid(row=2, column=1, pady=8, padx=15)

        tk.Label(form_frame, text=fix_ar("كلمة مرور الـ Root للراوتر:"), fg=self.fg_text, bg=self.bg_main).grid(row=3, column=0, sticky=tk.W, pady=8)
        self.ent_pass = tk.Entry(form_frame, width=24, show="*")
        self.apply_cyber_theme(self.ent_pass, "entry")
        self.ent_pass.grid(row=3, column=1, pady=8, padx=15)

        tk.Label(form_frame, text=fix_ar("اختر المجموعة الاستراتيجية:"), fg=self.fg_text, bg=self.bg_main).grid(row=4, column=0, sticky=tk.W, pady=8)
        fixed_groups = [fix_ar(g) for g in available_groups]
        self.combo_group = ttk.Combobox(form_frame, values=fixed_groups, state="readonly", width=22)
        self.combo_group.set(fixed_groups)
        self.combo_group.grid(row=4, column=1, pady=8, padx=15)

        # إطار الأزرار الصريح والظاهر مرئياً بالكامل
        btn_frame = tk.Frame(self.root, bg=self.bg_main)
        btn_frame.pack(pady=35, fill=tk.X, padx=40)

        def save_action():
            ap_name = self.ent_name.get().strip()
            ap_ip = self.ent_ip.get().strip()
            ap_user = self.ent_user.get().strip() if self.ent_user.get().strip() else "root"
            ap_pass = self.ent_pass.get().strip()
            
            chosen_group = self.combo_group.get()
            selected_group = "Default_Attack_Group"
            for g in available_groups:
                if fix_ar(g) == chosen_group:
                    selected_group = g
                    break

            if not ap_name or not ap_ip or not ap_pass:
                messagebox.showwarning("بيانات ناقصة", "الرجاء ملء كافة حقول التلقيم الإلزامية!", parent=self.root)
                return

            # الحفاظ الحتمي على حمايتك وسحق ثغرات الـ SQL Injection لـ Bandit
            query = "INSERT INTO tactical_targets (bssid, essid, channel, power, status, last_seen) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);"
            try:
                with self.db_manager._get_secure_connection() as conn:
                    with conn: conn.cursor().execute(query, (ap_ip, ap_name, "0", -50, f"Hardware_AP_{selected_group}"))
                messagebox.showinfo("نجاح التلقيم", "🔥 تم حفظ وتلقيم السيرفر المهاجم في الترسانة بنجاح!")
                self.root.destroy()
            except Exception as e:
                messagebox.showerror("خطأ نظامي", f"تعذر أرشفة خادم الهجوم: {e}")

        # زر 1: زر إضافة وحفظ الخادم الفعلي والمستقر بالثيم
        btn_save = tk.Button(btn_frame, text=fix_ar("💾 تثبيت وحفظ الخادم"), command=save_action)
        self.apply_cyber_theme(btn_save, "button")
        btn_save.pack(side=tk.LEFT, padx=15, expand=True, fill=tk.X)

        # زر 2: زر الإلغاء والخروج النظيف
        btn_close = tk.Button(btn_frame, text=fix_ar("❌ إلغاء وإغلاق"), command=self.root.destroy)
        self.apply_cyber_theme(btn_close, "button", alert_style=True)
        btn_close.pack(side=tk.LEFT, padx=15, expand=True, fill=tk.X)

if __name__ == "__main__":
    from core.db_manager import DatabaseManager
    root = tk.Tk()
    app = AeroCageHardwareRegisterGUI(root, DatabaseManager())
    root.mainloop()
