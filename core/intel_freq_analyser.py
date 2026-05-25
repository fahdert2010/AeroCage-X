#!/usr/bin/env python3
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.channel_optimizer import ChannelOptimizer

SystemGuard.enforce_root_privileges("OpenWrt Frequency Analyser Engine")

class IntelFreqAnalyser:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ap_ip = SystemGuard.sanitize_input(ap_ip, "interface")
        self.ap_password = ap_password

    def scan_air_space_standard(self, ap_interface: str = "phy1-ap0") -> dict:
        """تشغيل مسح الأجواء الطبيعي عن بعد واستدعاء الخوارزمية المنفصلة للتحليل"""
        remote_cmd = f"iwinfo {clean_inf if hasattr(self, 'clean_inf') else SystemGuard.sanitize_input(ap_interface, 'interface')} scan"
        base_ssh_args = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}", remote_cmd]
        
        try:
            result = subprocess.run(base_ssh_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            if result.returncode == 0 and result.stdout:
                parsed_cells = ChannelOptimizer.parse_scan_output(result.stdout)
                return ChannelOptimizer.calculate_best_channel(parsed_cells)
        except Exception as e:
            print(f"[-] خطأ مسح الأجواء العادي: {e}")
        return {}

    def switch_channel_with_confirmation(self, radio_name: str, target_channel: str) -> bool:
        """🤖 خط الحماية الفولاذي: سؤال المستخدم وطلب التأكيد الإجباري قبل التغيير بالـ UCI"""
        clean_radio = SystemGuard.sanitize_input(radio_name, "interface")
        clean_chan = "".join(ch for ch in str(target_channel) if ch.isdigit())

        root_box = tk.Tk()
        root_box.withdraw()
        user_response = messagebox.askyesno(
            "تأكيد التعديل التكتيكي", 
            f"هل تريد فعلاً تعديل تردد الراديو ({clean_radio}) وتثبيته على القناة الجديدة ({clean_chan})؟"
        )
        root_box.destroy()

        if not user_response:
            print("[*] تم إلغاء أمر التعديل بناءً على رغبة القائد.")
            return False

        # حزمة أوامر الـ UCI المتفق عليها في تجاربك الميدانية
        uci_command = f"uci set wireless.{clean_radio}.channel='{clean_chan}' && uci commit wireless && wifi reload {clean_radio}"
        base_ssh_args = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}", uci_command]

        try:
            result = subprocess.run(base_ssh_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            return result.returncode == 0
        except Exception:
            return False
