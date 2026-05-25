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

class AeroCageGroupsGUI(AeroCageUIBase):
    def __init__(self, root: tk.Tk):
        # استدعاء مشيد الأب المركزي الموحد
        super().__init__(root, title="إدارة مجموعات الاستهداف التكتيكية", width=780, height=500)
        
        self.db_manager = DatabaseManager()
        self.build_groups_interface()
        self.load_groups_async()

    def build_groups_interface(self):
        lbl_header = tk.Label(self.root, text="مركز إدارة وتصنيف مجموعات الاستهداف اللاسلكية", font=("Courier", 12, "bold"))
        self.apply_cyber_theme(lbl_header, "label")
        lbl_header.pack(pady=10)

        control_frame = tk.Frame(self.root)
        self.apply_cyber_theme(control_frame, "frame")
        control_frame.pack(pady=5, fill=tk.X, padx=20)

        lbl_select = tk.Label(control_frame, text="اختر المجموعة الاستراتيجية:", font=("Arial", 10))
        self.apply_cyber_theme(lbl_select, "label")
        lbl_select.pack(side=tk.LEFT, padx=5)

        self.combo_group = ttk.Combobox(control_frame, values=["جميع الأهداف المكتشفة", "أهداف عالية الأهمية (VIP)", "شبكات مصفاة وآمنة"], state="readonly", width=25)
        self.combo_group.set("جميع الأهداف المكتشفة")
        self.combo_group.bind("<<ComboboxSelected>>", lambda e: self.load_groups_async())
        self.combo_group.pack(side=tk.LEFT, padx=10)

        self.btn_refresh = tk.Button(control_frame, text="🔄 تحديث حركي", command=self.load_groups_async)
        self.apply_cyber_theme(self.btn_refresh, "button")
        self.btn_refresh.pack(side=tk.LEFT, padx=10)

        table_frame = tk.Frame(self.root)
        self.apply_cyber_theme(table_frame, "frame")
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)

        self.tree = ttk.Treeview(table_frame, columns=("BSSID", "ESSID", "Channel", "Power", "Status"), show="headings")
        self.tree.heading("BSSID", text="عنوان MAC / BSSID")
        self.tree.heading("ESSID", text="اسم الشبكة / ESSID")
        self.tree.heading("Channel", text="القناة")
        self.tree.heading("Power", text="قوة الإشارة")
        self.tree.heading("Status", text="الحالة التكتيكية")
        
        for col in ("BSSID", "ESSID", "Channel", "Power", "Status"):
            self.tree.column(col, anchor=tk.CENTER)

        # حقن ميزة تجميع وتوحيد الثيم للجداول الرسومية مباشرة من الأبui_base
        self.configure_treeview_style(self.tree)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="الحالة: جاهز بانتظار استدعاء سجلات المجموعات...")
        lbl_status = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 9, "italic"), fg=self.fg_primary, bg=self.bg_entry)
        lbl_status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_groups_async(self):
        selected_type = self.combo_group.get()
        self.status_var.set(f"الحالة: جاري جلب المجموعات لـ [{selected_type}] من قاعدة البيانات...")
        self.btn_refresh.config(state=tk.DISABLED)
        threading.Thread(target=self._fetch_and_render_worker, args=(selected_type,), daemon=True).start()

    def _fetch_and_render_worker(self, group_type):
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
                status = target.get("status", "discovered")
                
                if group_type == "أهداف عالية الأهمية (VIP)" and int(power) < -60:
                    continue
                elif group_type == "شبكات مصفاة وآمنة" and status != "secured":
                    continue
                
                self.root.after(0, self._append_row_to_tree, bssid, essid, channel, f"{power} dBm", status)
                rendered_count += 1

            self.root.after(0, lambda: self.status_var.set(f"الحالة: تم تحميل {rendered_count} سجل بنجاح لـ [{group_type}]."))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"🔴 خطأ فرز المجموعات: {e}"))
        finally:
            self.root.after(0, lambda: self.btn_refresh.config(state=tk.NORMAL))

    def _append_row_to_tree(self, bssid, essid, channel, power, status):
        self.tree.insert("", tk.END, values=(bssid, essid, channel, power, status))

if __name__ == "__main__":
    SystemGuard.enforce_root_privileges("واجهة المجموعات")
    root = tk.Tk()
    app = AeroCageGroupsGUI(root)
    root.mainloop()
