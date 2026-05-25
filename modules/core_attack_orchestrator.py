#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
# ربط محاور مفسر بايثون بجذر المستودع تحت الـ sudo
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from modules.m2_hardware_tunnel import M2HardwareTunnelEngine
from modules.client_harvester import ClientHarvesterEngine
from modules.process_terminator import ProcessTerminatorEngine

SystemGuard.enforce_root_privileges("Core Attack & Recon Orchestrator")

class CoreAttackOrchestrator:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ap_ip = ap_ip
        self.ap_password = ap_password
        
        # استدعاء وبناء الكتائب الهجومية الموحدة والمطهرة بالملي من التكرار والثغرات
        self.tunnel_launcher = M2HardwareTunnelEngine(ap_ip, ap_password)
        self.harvester = ClientHarvesterEngine(ap_ip, ap_password)
        self.terminator = ProcessTerminatorEngine(ap_ip, ap_password)

    def execute_full_tactical_sequence(self, interface: str, radio: str, channel: str, port: int) -> bool:
        """
        🎯 تنفيذ وإدارة التسلسل التكتيكي القيادي بالكامل لترسانة العتاد:
        فحص البيئة ➔ حصاد الأجهزة والزبائن ➔ تهيئة كرت الوايرلس ➔ إطلاق الأيرسيرف بأمان وتثبيت القناة.
        """
        print(f"\n==========================================================")
        print(f"[🚀 ORCHESTRATOR] بدء تشغيل التسلسل القتالي المركزي لمنظومة AeroCage-X")
        print(f"==========================================================\n")

        # 🪐 الخطوة 1: استجواب صامت للبيئة عتادياً قبل التدمير
        env_report = self.tunnel_launcher.query_active_daemons_before_kill()
        if env_report["airserv_active"] or env_report["aireplay_active"]:
            print("[⚠️ تنبيه تكتيكي] تم اكتشاف عمليات هجومية جارية بالداخل من جلسات سابقة.")
            # تنظيف وتطهير قنوات العبور فوراً بربط الدالة الموحدة
            self.terminator.sever_all_remote_attack_daemons()
            time.sleep(1)

        # 🪐 الخطوة 2: قنص وحصاد بيانات الأجهزة والزبائن والماك أدرس الحية
        print("[*] جاري الانتقال لخطوة قنص وحصاد الزبائن المتصلين بالشبكة...")
        active_clients = self.harvester.harvest_active_clients_safe(interface)
        print(f"[+] تقرير الاستطلاع: تم رصد وثقيف ({len(active_clients)}) جهاز زبون نشط بالداخل.")

        # 🪐 الخطوة 3: تهيئة كرت الوايرلس وإطلاق سيرفر الأيرسيرف وتثبيت التردد والقناة بالملي
        print("[*] جاري الانتقال لخطوة تهيئة العتاد وإشعال سيرفر البث اللاسلكي...")
        success = self.tunnel_launcher.deploy_airserv_daemon_safe(
            mon_iface=interface, 
            target_port=port, 
            channel=channel
        )
        
        if success:
            print(f"\n[🟢 نجاح استراتيجي] تم إقفال وتسلسُل خط السلاح كامل الترسانة بنجاح فولاذي!")
            print(f"[+] المنظومة تبث عتاد الراوتر البعيد الآن للبورت: {port} وعلى التردد: {channel}\n")
            return True
        else:
            print(f"\n[🔴 فشل تكتيكي] تعذر إكمال تسلسل إطلاق العتاد. جاري سحب القوات وتنظيف البيئة قسرياً...")
            self.terminator.factory_reset_wireless_radio(radio)
            return False

if __name__ == "__main__":
    print("[+] المايسترو ومنظم كامل ترسانة العتاد والضربات الموحد (Orchestrator) جاهز للتشغيل والإنتاج الفعلي.")
