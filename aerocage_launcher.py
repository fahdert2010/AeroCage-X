#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess
from pathlib import Path
import arabic_reshaper
from bidi.algorithm import get_display

def fix_arabic_text(text):
    """دالة مطورة لحل كابوس تقطيع وعكس النصوص العربية المتداخلة مع الإنجليزية في Tkinter"""
    if not text:
        return ""
    # إعادة تشكيل الحروف العربية لتلتصق ببعضها بشكل قياسي وصحيح
    reshaped = arabic_reshaper.reshape(text)
    # عكس اتجاه الحروف لتتناسب مع واجهة الـ RTL دون تدمير ترتيب الكلمات الإنجليزية المرافقة
    return get_display(reshaped)


# ربط المسارات بالنواة المركزية والمكتبات المساعدة للمنظومة
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.remote_hardware_bridge import RemoteHardwareBridge
from modules.core_attack_orchestrator import CoreAttackOrchestrator
from modules.silent_sigint_sniffer import SilentSigIntSniffer

# تفعيل خط الدفاع الأول الرسومي فوراً لحماية كامل الترسانة الـ 43
SystemGuard.enforce_root_privileges("منظومة القيادة العليا AeroCage-X", graphical=True)

class AeroCageMasterLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("AeroCage-X | منظومة القيادة والسيطرة العليا 2026")
        self.root.geometry("850x680")
        self.root.configure(bg="#121212") # الهوية السيبرانية الداكنة للمنصة
        
        self.BASE_DIR = Path(__file__).resolve().parent
        self.active_subsystems = {}
        
        # متغيرات الاستهداف المركزي الموحد للأكسس البعيد
        self.ap_ip = None
        self.ap_password = None
        
        self.build_master_ui()

    def build_master_ui(self):
        lbl_master = tk.Label(self.root, text="AERO CAGE - X  |  MASTER COMMAND CENTER", font=("Courier", 16, "bold"), fg="#00FF00", bg="#121212")
        lbl_master.pack(pady=20)
        
        # لوحة تهيئة الاتصال بالأكسس البعيد وتمرير الصلاحيات
        conn_frame = tk.LabelFrame(self.root, text=" إعدادات الاتصال المركزي بالراوتر (OpenWrt) ", font=("Arial", 10, "bold"), fg="#00FF00", bg="#121212", padx=15, pady=10)
        conn_frame.pack(pady=10, fill=tk.X, padx=40)
        
        btn_configure = tk.Button(conn_frame, text=fix_arabic_text("🔒 تهيئة وتلقيم بيانات الـ Root للراوتر"), font=("Arial", 10, "bold"), bg="#1E1E1E", fg="#FFFFFF", activebackground="#00FF00", activeforeground="#000000", command=self.prompt_target_credentials)
        btn_configure.pack(fill=tk.X, pady=5)
        
        btn_zone = tk.Frame(self.root, bg="#121212")
        btn_zone.pack(pady=10, fill=tk.BOTH, expand=True)

        # 🪐 مصفوفة الأزرار والعمليات الاستراتيجية الموحدة والمطهرة من التكرار
        modules_map = [
            ("🌐 1. إدارة وتتبع نقاط الوصول اللاسلكية (Access Points UI)", "core/ui_access_points.py"),
            ("👥 2. إدارة مجموعات الاستهداف التكتيكية (Groups UI)", "core/ui_groups.py"),
            ("📡 3. مستكشف وراصد الإشارات وفحص الزباين (Scout UI)", "core/ui_scout.py"),
            ("📊 4. مركز الاستخبارات والجمع الفني والفرز (CSV Parser)", "modules/strike_csv_parser.py"),
            ("⚡ 5. محرك إدارة وتلقيم الأنابيب البرمجية (Pipeline)", "modules/m3_kali_pipeline.py"),
            ("🚀 6. لوحة قيادة وتوجيه ضربات الفصل اللاسلكي (AirSurf)", "core/ui_strike.py"),
            ("🪐 7. تشغيل الأوركسترا والمايسترو المركزي للعتاد (Orchestrator)", "LAUNCH_ORCHESTRATOR"),
            ("💀 8. جناح الاعتراض الصامت واقتناص التذاكر والـ WebFig", "LAUNCH_SILENT_SNIFFER")
        ]

        for text, path in modules_map:
            if path in ["LAUNCH_ORCHESTRATOR", "LAUNCH_SILENT_SNIFFER"]:
                bg_color = "#1B5E20" if path == "LAUNCH_ORCHESTRATOR" else "#4A148C"
                btn = tk.Button(btn_zone, text=fix_arabic_text(text), font=("Arial", 11, "bold"), bg=bg_color, fg="#FFFFFF", activebackground="#00FF00", activeforeground="#000000", bd=2, relief=tk.RAISED, height=2, command=lambda p=path: self.trigger_integrated_module(p))
            else:
                btn = tk.Button(btn_zone, text=fix_arabic_text(text), font=("Arial", 11, "bold"), bg="#1E1E1E", fg="#FFFFFF", activebackground="#00FF00", activeforeground="#000000", bd=2, relief=tk.RAISED, height=2, command=lambda p=path, t=text: self.spawn_subsystem_safe(p, t))
            btn.pack(fill=tk.X, padx=50, pady=5)

        self.lbl_env = tk.Label(self.root, text="بيئة النظام: خامل | الصلاحيات: ROOT | الحالة: بانتظار تلقيم بيانات الراوتر...", bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9, "italic"), fg="#FF3333", bg="#1E1E1E")
        self.lbl_env.pack(side=tk.BOTTOM, fill=tk.X)

    def prompt_target_credentials(self):
        """تلقيم وحفظ معلمات خوادم الترسانة المهاجمة بالأتمتة الرسومية المنسقة النظيفة"""
        try:
            from core.ui_hardware_register import AeroCageHardwareRegisterGUI
            import tkinter as tk
            
            # فحص ذاتي ذكي لمعرفة مقبض قاعدة البيانات الفعلي المعتمد في كودك (db_instance أو db_manager)
            db_handle = self.db_instance if hasattr(self, 'db_instance') else self.db_manager if hasattr(self, 'db_manager') else None
            if db_handle is None:
                from core.db_manager import DatabaseManager
                db_handle = DatabaseManager()

            # إنشاء النافذة وتمرير المقبض النظيف
            sub_win = tk.Toplevel(self.root)
            AeroCageHardwareRegisterGUI(sub_win, db_handle)
            
            self.lbl_env.config(text="بيئة النظام: تم استدعاء مركز تلقيم الخوادم المهاجمة للترسانة بنجاح | الحالة: نشط", fg="#00FF00")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("خطأ في الاستدعاء", f"تعذر فتح شاشة إدارة الترسانة العتادية المخصصة: {e}")



    def trigger_integrated_module(self, action_key):
        """التحكم والتشغيل المتسلسل للمحركات المدمجة الكبرى بالاعتماد على النواة الصلبة المطهرة"""
        if not self.ap_ip or not self.ap_password:
            messagebox.showwarning("نقص بيانات", "الرجاء تلقيم بيانات الاتصال بالراوتر (الزر العلوي) أولاً قبل بدء العملية التكتيكية!")
            return

        if action_key == "LAUNCH_ORCHESTRATOR":
            # استدعاء أوركسترا العتاد المطور والمنظف من عيب killall الأعمى وثغرات الشل
            orchestrator = CoreAttackOrchestrator(self.ap_ip, self.ap_password)
            # تنفيذ التسلسل القتالي القيادي الصافي لـ 14 ملفاً مدمجاً بسطر واحد
            success = orchestrator.execute_full_tactical_sequence(interface="phy1-ap0", radio="radio1", channel="6", port=666)
            if success:
                messagebox.showinfo("المايسترو نشط", "تم تهيئة العتاد وحصاد الأجهزة وإطلاق سيرفر الأيرسيرف وثبات القناة بنجاح عسكري!")
            
        elif action_key == "LAUNCH_SILENT_SNIFFER":
            # إطلاق جناح التجسس الصامت واقتناص الـ webfig والـ HTTP بشكل منفصل ومستقل 100%
            sniffer = SilentSigIntSniffer(self.ap_ip, self.ap_password)
            sniffer.start_silent_intel_harvesting(ap_interface="phy1-ap0")
            messagebox.showinfo("جناح التجسس نشط", "بدأ محرك الاعتراض الصامت في امتصاص حزم البيانات وتصفية الغنائم داخل قاعدة البيانات.")

    def spawn_subsystem_safe(self, script_relative_path, module_title):
        full_script_path = self.BASE_DIR / script_relative_path
        if not full_script_path.exists():
            messagebox.showerror("خطأ في المنظومة", f"الملف البرمجي غير موجود في المسار: {script_relative_path}")
            return

        env_context = os.environ.copy()
        try:
            print(f"[*] جاري إطلاق الواجهة الفرعية المؤمنة [{module_title}]...")
            # إطلاق نظيف ومغلق الشل تماماً يضمن توريث الـ Sudo بالملي لـ Bandit B602/B603
            subprocess.Popen([sys.executable, str(full_script_path)], env=env_context, shell=False)
        except Exception as e:
            messagebox.showerror("فشل الإطلاق", f"تعذر تشغيل الوحدة الفرعية: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AeroCageMasterLauncher(root)
    root.mainloop()
