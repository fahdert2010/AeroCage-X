#!/usr/bin/env python3
import os
import sys
import tkinter as tk
import arabic_reshaper
from bidi.algorithm import get_display
from tkinter import messagebox, ttk
from pathlib import Path

# ربط المسارات بالنواة المركزية
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

class AeroCageUIBase:
    def __init__(self, root: tk.Tk, title: str, width: int = 750, height: int = 480):
        self.root = root
        self.title = SystemGuard.sanitize_input(title, "csv_value")
        self.width = width
        self.height = height
        
        # الألوان التكتيكية الموحدة للمنظومة (Dark Cyberpunk Theme)
        self.bg_main = "#121212"       
        self.bg_panel = "#1E1E1E"      
        self.fg_primary = "#00FF00"    
        self.fg_alert = "#FF3333"      
        self.fg_text = "#FFFFFF"       
        self.bg_entry = "#2D2D2D"      
        
        self.setup_base_window()

    def setup_base_window(self):
        # تشكيل وعكس عنوان النافذة ليظهر سليمًا في شريط النظام العلوي
        clean_title = get_display(arabic_reshaper.reshape(f"AeroCage-X | {self.title}"))
        self.root.title(clean_title)
        self.root.configure(bg=self.bg_main)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width // 2) - (self.width // 2)
        y = (screen_height // 2) - (self.height // 2)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_secure_close)

    def apply_cyber_theme(self, widget, widget_type: str = "label", alert_style: bool = False):
        """تطبيق ألوان وتنسيقات الثيم مع إصلاح وتوصيل الحروف العربية تلقائياً للأزرار والعناوين"""
        try:
            current_text = widget.cget("text")
            if current_text and widget_type in ["label", "button"]:
                reshaped = arabic_reshaper.reshape(current_text)
                widget.configure(text=get_display(reshaped))
        except Exception:
            pass

        if widget_type == "label":
            widget.configure(bg=self.bg_main, fg=self.fg_alert if alert_style else self.fg_primary)
        elif widget_type == "frame" or widget_type == "labelframe":
            widget.configure(bg=self.bg_main, fg=self.fg_primary) if widget_type == "labelframe" else widget.configure(bg=self.bg_main)
        elif widget_type == "entry":
            widget.configure(bg=self.bg_entry, fg=self.fg_text, insertbackground="white", bd=1, relief=tk.SOLID)
        elif widget_type == "button":
            bg_color = self.fg_alert if alert_style else "#005500"
            widget.configure(
                bg=bg_color, fg=self.fg_text, activebackground=self.fg_primary, 
                activeforeground=self.bg_main, font=("Arial", 10, "bold"), bd=2, relief=tk.RAISED
            )

    def configure_treeview_style(self, tree_widget: ttk.Treeview):
        """🎮 وظيفة تجميعية تكتيكية: توحيد ثيم وتصميم وعكس عناوين الجداول الرسومية لمنع التقطيع والعكس"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.bg_panel, fieldbackground=self.bg_panel, foreground=self.fg_text, rowheight=25)
        style.configure("Treeview.Heading", background=self.bg_entry, foreground=self.fg_primary, font=("Arial", 10, "bold"))
        
        try:
            for col in tree_widget["columns"]:
                old_heading = tree_widget.heading(col, "text")
                if old_heading:
                    reshaped = arabic_reshaper.reshape(old_heading)
                    tree_widget.heading(col, text=get_display(reshaped))
        except Exception:
            pass
        
    @staticmethod
    def clear_treeview_records(tree_widget: ttk.Treeview):
        for item in tree_widget.get_children():
            tree_widget.delete(item)

    def on_secure_close(self):
        try:
            print(f"[*] جاري إغلاق وتفريغ مسار الذاكرة للواجهة التكتيكية: {self.title}")
            self.root.destroy()
        except Exception as e:
            print(f"[-] تنبيه أثناء إغلاق النافذة: {e}")
            sys.exit(0)
