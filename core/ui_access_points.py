#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.ui_base import AeroCageUIBase
from core.db_manager import DatabaseManager

class AeroCageAccessPointsGUI(AeroCageUIBase):
    def __init__(self, root: tk.Tk):
        super().__init__(root, title="إدارة وتتبع نقاط الوصول اللاسلكية", width=800, height=520)
        
        self.db_manager = DatabaseManager()
        self.build_ap_interface()
        self.refresh_ap_list_async()

    def build_ap_interface(self):
        lbl_header = tk.Label(self.root, text="لوحة إدارة وتحليل نقاط الوصول اللاسلكية المكتشفة", font=("Courier", 12, "bold"))
        self.apply_cyber_theme(lbl_header, "label")
        lbl_header.pack(pady=10)

        control_frame = tk.Frame(self.root)
        self.apply_cyber_theme(control_frame, "frame")
        control_frame.pack(pady=5, fill=tk.X, padx=20)

        self.btn_refresh = tk.Button(control_frame, text="🔄 تحديث طابور النقاط", command=self.refresh_ap_list_async)
        self.apply_cyber_theme(self.btn_refresh, "button")
        self.btn_refresh.pack(side=tk.LEFT, padx=5)

        self.btn_inject_target = tk.Button(control_frame, text="🎯 تلقيم الهدف للموجه", command=self.inject_selected_ap_to_strike)
        self.apply_cyber_theme(self.btn_inject_target, "button", alert_style=True)
        self.btn_inject_target.pack(side=tk.RIGHT, padx=5)

        table_frame = tk.Frame(self.root)
        self.apply_cyber_theme(table_frame, "frame")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.tree = ttk.Treeview(table_frame, columns=("BSSID", "ESSID", "Channel", "Power", "LastSeen"), show="headings")
        self.tree.heading("BSSID", text="BSSID / MAC Address")
        self.tree.heading("ESSID", text="ESSID / Wi-Fi Name")
        self.tree.heading("Channel", text="القناة")
        self.tree.heading("Power", text="قوة الإشارة (Signal)")
        self.tree.heading("LastSeen", text="آخر رصد تكتيكي")
        
        for col in ("BSSID", "ESSID", "Channel", "Power", "LastSeen"):
            self.tree.column(col, anchor=tk.CENTER)

        # استدعاء دالة حقن ثيم الجدول الموحد من الأبui_base كود أنظف وموفر للمساحة
        self.configure_treeview_style(self.tree)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="الحالة: جاهز بانتظار قراءة نقاط البث...")
        lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9, "italic"), fg=self.fg_primary, bg=self.bg_entry)
        lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def refresh_ap_list_async(self):
        self.status_var.set("الحالة: جاري جلب وتحديث سجلات نقاط البث من قاعدة البيانات...")
        self.btn_refresh.config(state=tk.DISABLED)
        threading.Thread(target=self._fetch_ap_worker, daemon=True).start()

    def _fetch_ap_worker(self):
        try:
            # استدعاء دالة التجميع لمسح وتنظيف الجدول بأمان من الأب ui_base
            self.root.after(0, lambda: self.clear_treeview_records(self.tree))
            
            targets = self.db_manager.get_all_active_targets()
            rendered_count = 0
            for target in targets:
                bssid = target.get("bssid", "غير معروف")
                essid = target.get("essid", "مخفي")
                channel = target.get("channel", "1")
                power = target.get("power", -100)
                last_seen = target.get("last_seen", "غير محدد")
                
                self.root.after(0, self._append_row_to_tree, bssid, essid, channel, f"{power} dBm", last_seen)
                rendered_count += 1

            self.root.after(0, lambda: self.status_var.set(f"الحالة: تم تحميل {rendered_count} نقطة بث لاسلكية بنجاح."))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"🔴 خطأ جلب نقاط البث: {e}"))
        finally:
            self.root.after(0, lambda: self.btn_refresh.config(state=tk.NORMAL))

    def _append_row_to_tree(self, bssid, essid, channel, power, last_seen):
        self.tree.insert("", tk.END, values=(bssid, essid, channel, power, last_seen))

    def inject_selected_ap_to_strike(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تنبيه تكتيكي", "الرجاء اختيار نقطة بث من الجدول أولاً لتلقيمها!")
            return
        item_values = self.tree.item(selected_item, "values")
        messagebox.showinfo("تم التلقيم بنجاح", f"تم تثبيت الهدف المختار في المنظومة:\n\nالاسم: {item_values[1]}\nالماك: {item_values[0]}")

if __name__ == "__main__":
    SystemGuard.enforce_root_privileges("واجهة النقاط")
    root = tk.Tk()
    app = AeroCageAccessPointsGUI(root)
    root.mainloop()
