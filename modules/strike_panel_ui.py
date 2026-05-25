#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية والمساعدات الرسومية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.ui_base import AeroCageUIBase
from modules.strike_launcher import StrikeLauncher

class AeroCageStrikePanelGUI(AeroCageUIBase):
    def __init__(self, root: tk.Tk):
        # استدعاء مشيد الأب القياسي لتوحيد الثيم التكتيكي الداكن وأبعاد النافذة
        super().__init__(root, title="لوحة القيادة التكتيكية لإطلاق الضربات", width=760, height=460)
        
        # استدعاء وسيط الإطلاق المطور والمؤمن سابقاً ضد ثغرات Bandit
        self.strike_launcher = StrikeLauncher()
        self.active_target_bssid = None
        
        self.build_panel_interface()

    def build_panel_interface(self):
        """بناء وتنسيق عناصر واجهة ضربات الفصل اللاسلكي وفق الهوية السيبرانية للمنظومة"""
        # العنوان العلوي
        lbl_header = tk.Label(self.root, text="لوحة السيطرة والتحكم بضربات حزم الفصل (Strike Panel UI)", font=("Courier", 12, "bold"))
        self.apply_cyber_theme(lbl_header, "label")
        lbl_header.pack(pady=15)

        # إطار حقول استهداف المدخلات اللاسلكية
        frame_fields = tk.LabelFrame(self.root, text=" معلمات تلقيم وتوجيه القاذف اللاسلكي ", font=("Arial", 10, "bold"), fg=self.fg_primary, bg=self.bg_main, padx=15, pady=15)
        frame_fields.pack(pady=10, fill=tk.X, padx=30)

        tk.Label(frame_fields, text="كرت واجهة الشبكة (Interface):", fg=self.fg_text, bg=self.bg_main).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_interface = tk.Entry(frame_fields, width=20, font=("Arial", 10))
        self.apply_cyber_theme(self.ent_interface, "entry")
        self.ent_interface.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(frame_fields, text="عنوان ماك الهدف (Target BSSID):", fg=self.fg_text, bg=self.bg_main).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ent_bssid = tk.Entry(frame_fields, width=25, font=("Arial", 10))
        self.apply_cyber_theme(self.ent_bssid, "entry")
        self.ent_bssid.grid(row=1, column=1, pady=5, padx=10)

        # أزرار الإطلاق وقطع الهجمات الموجهة بالخلفية
        btn_frame = tk.Frame(self.root, bg=self.bg_main)
        btn_frame.pack(pady=20)

        self.btn_fire = tk.Button(btn_frame, text="🔥 إطلاق العاصفة اللاسلكية", command=self.trigger_launcher_async)
        self.apply_cyber_theme(self.btn_fire, "button", alert_style=True)
        self.btn_fire.pack(side=tk.LEFT, padx=15)

        self.btn_stop = tk.Button(btn_frame, text="🛑 كبح وقطع الضربات", command=self.trigger_stop_async)
        self.apply_cyber_theme(self.btn_stop, "button")
        self.btn_stop.pack(side=tk.LEFT, padx=15)

        # شريط الحالة التكتيكي السفلي الموحد للأب
        self.status_var = tk.StringVar(value="الحالة الاستراتيجية: خامل بانتظار أوامر التلقيم...")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10, "italic"), fg=self.fg_primary, bg=self.bg_entry)
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def trigger_launcher_async(self):
        """رمي عملية الإطلاق البرمي بالكامل للخلفية لمنع تجمد لوحة المستخدم نهائياً"""
        interface = self.ent_interface.get().strip()
        bssid = self.ent_bssid.get().strip()

        # تطهير وفحص المدخلات مسبقاً عبر حارس النواة لحمايتك من الاختراق العكسي و Bandit
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(bssid, "bssid").upper()

        if not clean_inf or not clean_mac:
            messagebox.showwarning("بيانات تالفة", "الرجاء إدخال اسم كرت الشبكة وعنوان ماك صحيح للهدف!")
            return

        self.btn_fire.config(state=tk.DISABLED)
        self.active_target_bssid = clean_mac
        self.status_var.set(f"الحالة الاستراتيجية: جاري تلقيم المعلمات والتشغيل الآمن عبر اللانشر المركزي لـ {clean_mac}...")

        # تشغيل الهجوم في مسار فرعي مستقل تماماً لتظل أزرار الشاشة مرنة ومستجيبة
        threading.Thread(target=self._launcher_worker, args=(clean_inf, clean_mac), daemon=True).start()

    def _launcher_worker(self, interface, bssid):
        """العامل الخلفي المعزول للاتصال باللانشر المطور وسحق ممرات الشل"""
        success = self.strike_launcher.launch_targeted_strike(interface, bssid) if hasattr(self.strike_launcher, 'launch_targeted_strike') else self.strike_launcher.launch_strike_session(interface, bssid)
        
        # تحديث الواجهة الرسومية بشكل متوافق وآمن خيطياً عبر after() من الأب ui_base
        if success:
            self.root.after(0, lambda: self.status_var.set(f"الحالة الاستراتيجية: الضربات تعمل بنشاط وقوة ضد الهدف {bssid} 🎯"))
        else:
            self.root.after(0, lambda: self.status_var.set("الحالة الاستراتيجية: فشل أمر الإطلاق. تحقق من القائمة البيضاء أو وضع الكرت."))
            self.root.after(0, lambda: messagebox.showerror("عطل في الإطلاق", "تعذر بدء جلسة الهجوم عبر اللanشر."))
            self.root.after(0, lambda: self.btn_fire.config(state=tk.NORMAL))

    def trigger_stop_async(self):
        """إيقاف الهجوم وجدولة التنظيف في خيط مستقل لضمان كبح الضربات فوراً وبدون تعليق الموارد"""
        if self.active_target_bssid:
            self.status_var.set(f"الحالة الاستراتيجية: جاري إرسال إشارة الكبح اللحظية لقطع الضربات عن {self.active_target_bssid}...")
            
            # استدعاء الإيقاف المحدد والموجه للـ PID المحلي لمنع تخريب بقية عمليات كالي
            threading.Thread(target=self.strike_launcher.stop_strike_session, args=(self.active_target_bssid,), daemon=True).start()
            
            self.root.after(0, lambda: self.status_var.set("الحالة الاستراتيجية: تم كبح الضربات الموجهة وتنظيف بيئة الذاكرة العشوائية."))
            self.active_target_bssid = None
            self.btn_fire.config(state=tk.NORMAL)
        else:
            messagebox.showinfo("تنبيه تكتيكي", "لا توجد ضربات أو هجمات لاسلكية نشطة حالياً لكبحها.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("خطأ صلاحيات تكتيكي", "لوحة الضربات الرسومية تتطلب تشغيل السكربت بصلاحيات الـ Root (sudo).")
        sys.exit(1)
        
    root = tk.Tk()
    app = AeroCageStrikePanelGUI(root)
    root.mainloop()
