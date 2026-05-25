#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.opwrt_ssh_factory import OpWrtSSHFactory
from utils.text_parsing_engine import TextParsingEngine
from core.db_manager import DatabaseManager

SystemGuard.enforce_root_privileges("Client Harvester & Signal Monitor")

class ClientHarvesterEngine:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ssh_factory = OpWrtSSHFactory(ip=ap_ip, password=ap_password)
        self.db_manager = DatabaseManager()

    def harvest_active_clients_safe(self, ap_interface: str) -> list:
        """🎯 قنص وحصاد عناوين الأجهزة المتصلة بالراوتر وتوثيق إشاراتها وقنواتها بأمان 100%"""
        clean_inf = SystemGuard.sanitize_input(ap_interface, "interface")
        if not clean_inf: return []

        # الأوامر التكتيكية الصافية لاستجواب قائمة الزبائن داخل أوبن ورت
        remote_cmd = f"iwinfo {clean_inf} assoclist"
        raw_stdout = self.ssh_factory.execute_remote_cmd(remote_cmd)
        clients_found = []

        if not raw_stdout:
            return clients_found

        try:
            # استخدام محرك التفكيك العتادي الموحد لاقتناص الماك أدرس وقوة الإشارة وحمايتك من IndexError
            import re
            mac_blocks = re.findall(r'(([0-9a-fa-f]{2}[:-]){5}([0-9a-fa-f]{2})).*?signal:\s+(-\d+)\s+dBm', raw_stdout.lower(), re.DOTALL)
            
            for block in mac_blocks:
                mac = SystemGuard.sanitize_input(block[0], "bssid").upper()
                signal = int(block[2]) if len(block) > 2 else -90
                
                clients_found.append({"mac": mac, "signal": signal})
                # ضخ صيد الزبائن الحركي تلقائياً في قاعدة البيانات وتحديث طابور الأهداف
                self.db_manager.save_target_safe(mac, f"OPWRT_CLIENT_{clean_inf}", "0", signal)
                
            print(f"[+ Harvester] تم اقتناص وفحص وتطهير {len(clients_found)} زبون نشط متصل بالراوتر حالياً.")
            return clients_found
        except Exception as e:
            print(f"[-] عطل أثناء حصاد وقنص بيانات الأجهزة المتصلة: {e}")
            return clients_found
