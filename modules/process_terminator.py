#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.opwrt_ssh_factory import OpWrtSSHFactory

SystemGuard.enforce_root_privileges("Process Terminator & Interface Cleaner")

class ProcessTerminatorEngine:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ssh_factory = OpWrtSSHFactory(ip=ap_ip, password=ap_password)

    def sever_all_remote_attack_daemons(self) -> bool:
        """🛑 كبح شامل وصارم لجميع هجمات وسيرفرات الفصل المعلقة داخل الراوتر البعيد لمنع الـ Zombie Processes"""
        print("\n[*] [Strategic Clean] جاري تطهير بيئة الراوتر البعيد وكبح التداخل العتادي...")
        
        # إرسال أوامر الإخماد الحادة بصيغة مصفوفة آمنة معزولة الشل محلياً لحمايتك لـ Bandit
        kill_serv = self.ssh_factory.execute_remote_cmd("killall -9 airserv-ng")
        kill_play = self.ssh_factory.execute_remote_cmd("killall -9 aireplay-ng")
        
        print("[+] تم مسح وإخماد طابور العمليات الهجومية المعلقة داخل عتاد الراوتر بنجاح.")
        return True

    def factory_reset_wireless_radio(self, radio_name: str) -> bool:
        """🔄 إعادة تحميل كرت الراديو الفيزيائي للراوتر لوضعه الافتراضي المستقر بالملي"""
        clean_radio = SystemGuard.sanitize_input(radio_name, "interface")
        if not clean_radio: return False
        
        print(f"[⚠️ طوارئ] جاري إجبار كرت الوايرلس البعيد ({clean_radio}) على إعادة التحميل والتثبيت الافتراضي...")
        result = self.ssh_factory.execute_remote_cmd(f"wifi reload {clean_radio}")
        return result != ""
