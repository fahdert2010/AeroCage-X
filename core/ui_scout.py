#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.ui_base import AeroCageUIBase
from core.db_manager import DatabaseManager

class AeroCageScoutGUI(AeroCageUIBase):
    def __init__(self, root: tk.Tk):
        super().__init__(root, title="مستكشف وراصد الإشارات اللاسلكية", width=820, height=520)
        
        self.db_manager = DatabaseManager()
        self.scouting_active = False
        self.build_scout_interface()

    def build_scout_interface(self):
        lbl_header = tk.Label(self.root, text="مركز الرصد والتقاط الإشارات الاستخباراتي (Scout Hub)", font=("Courier", 12, "bold"))
        self.apply_cyber_theme(lbl_header, "label")
        lbl_header.pack(pady=10)

        control_frame = tk.Frame(self.root)
        self.apply_cyber_theme(control_frame, "frame")
        control_frame.pack(pady=5, fill=tk.X, padx=20)

        self.btn_start = tk.Button(control_frame, text="📡 بدء الرصد والتقاط الحزم", command=self.start_scouting_async)
        self.apply_cyber_theme(self.btn_start, "button")
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_stop = tk.Button(control_frame, text="🛑 إيقاف الرصد والتحليل", command=self.stop_scouting, state=tk.DISABLED)
        self.apply_cyber_theme(self.btn_stop, "button", alert_style=True)
        self.btn_stop.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(self.root)
        self.apply_cyber_theme(table_frame, "frame")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.tree = ttk.Treeview(table_frame, columns=("BSSID", "ESSID", "Channel", "Power", "Status"), show="headings")
        self.tree.heading("BSSID", text="BSSID / MAC Address")
        self.tree.heading("ESSID", text="ESSID / Wi-Fi Name")
        self.tree.heading("Channel", text="القناة")
        self.tree.heading("Power", text="قوة الإشارة")
        self.tree.heading("Status", text="الحالة التكتيكية")
        
        for col in ("BSSID", "ESSID", "Channel", "Power", "Status"):
            self.tree.column(col, anchor=tk.CENTER)

        # استدعاء دالة حقن ثيم الجدول الموحد من الأبui_base كود أنظف وموفر للمساحة
        self.configure_treeview_style(self.tree)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="الحالة الاستراتيجية: خامل بانتظار إشارة الرصد...")
        lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9, "italic"), fg=self.fg_primary, bg=self.bg_entry)
        lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def start_scouting_async(self):
        if self.scouting_active:
            return
        self.scouting_active = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status_var.set("الحالة الاستراتيجية: تم تفعيل ممرات الاستكشاف وجاري التقاط حزم الإشارة حياً... 📡")
        threading.Thread(target=self._live_scout_loop_worker, daemon=True).start()

    def _live_scout_loop_worker(self):
        try:
            while self.scouting_active:
                targets = self.db_manager.get_all_active_targets()
                self.root.after(0, self._render_live_data, targets)
                time.sleep(2)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"🔴 خطأ داخلي في محرك الرصد: {e}"))

    def _render_live_data(self, targets):
        if not self.scouting_active:
            return
        # استدعاء دالة التجميع لمسح وتنظيف الجدول بأمان من الأب ui_base لمنع الـ Memory Bloat
        self.clear_treeview_records(self.tree)
            
        for target in targets:
            bssid = target.get("bssid", "غير معروف")
            essid = target.get("essid", "مخفي")
            channel = target.get("channel", "1")
            power = target.get("power", -100)
            status = target.get("status", "scouting")
            
            self.tree.insert("", tk.END, values=(bssid, essid, channel, f"{power} dBm", status))

    def stop_scouting(self):
        self.scouting_active = False
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status_var.set("الحالة الاستراتيجية: تم إغلاق محركات الرصد وتنظيف قنوات الذاكرة العشوائية.")

    def on_secure_close(self):
        self.scouting_active = False
        super().on_secure_close()

if __name__ == "__main__":
    SystemGuard.enforce_root_privileges("واجهة المستكشف")
    root = tk.Tk()
    app = AeroCageScoutGUI(root)
    root.mainloop()
