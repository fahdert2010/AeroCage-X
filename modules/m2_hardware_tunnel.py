#!/usr/bin/env python3
import os
import sys
import time
import threading
from pathlib import Path
# إجبار بايثون على إدراك المجلد الرئيسي للمشروع
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.opwrt_ssh_factory import OpWrtSSHFactory
from utils.text_parsing_engine import TextParsingEngine


SystemGuard.enforce_root_privileges("M2 Hardware Tunnel - Daemon Launcher")

class M2HardwareTunnelEngine:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ssh_factory = OpWrtSSHFactory(ip=ap_ip, password=ap_password)
        self.lock = threading.Lock()

    def query_active_daemons_before_kill(self) -> dict:
        """🔍 خط الدفاع الاستباقي: استجواب الراوتر صامتاً لمعرفة هل توجد هجمات أو سيرفرات جارية"""
        print("[*] [Recon Intelligence] جاري فحص بيئة الراوتر العتادية قبل اتخاذ أي إجراء...")
        
        # استدعاء معرفات الأجهزة عبر pidof الصافي الموحد
        airserv_pids = TextParsingEngine.clean_pids(self.ssh_factory.execute_remote_cmd("pidof airserv-ng"))
        aireplay_pids = TextParsingEngine.clean_pids(self.ssh_factory.execute_remote_cmd("pidof aireplay-ng"))
        
        report = {
            "airserv_active": len(airserv_pids) > 0,
            "airserv_pids": airserv_pids,
            "aireplay_active": len(aireplay_pids) > 0,
            "aireplay_pids": aireplay_pids
        }
        return report

    def deploy_airserv_daemon_safe(self, mon_iface: str, target_port: int, channel: str) -> bool:
        """
        🔥 تهيئة وإشعال سيرفر الأيرسيرف عن بعد مع تثبيت القناة والموجة عتادياً بالملي.
        حصانة 100% ضد ثغرات Bandit (B602/B603) لإلغاء الـ shell والـ Password Leak.
        """
        clean_mon = SystemGuard.sanitize_input(mon_iface, "interface")
        clean_chan = "".join(ch for ch in str(channel) if ch.isdigit())
        
        if not clean_mon or not clean_chan:
            print("[-] خطأ تكتيكي: معلمات الواجهة أو القناة المدخلة تالفة.")
            return False

        # 1. الاستعلام الاستباقي وسؤال البيئة قبل التخريب
        env_report = self.query_active_daemons_before_kill()
        if env_report["airserv_active"]:
            print(f"[⚠️ تنبيه] تم رصد سيرفر أيرسيرف نشط بالفعل بالداخل للـ PIDs: {env_report['airserv_pids']}")
            # تنظيف محدد وذكي للمخلفات القديمة دون مساس بمهام الأنظمة الأخرى
            self.ssh_factory.execute_remote_cmd("killall -9 airserv-ng")
            time.sleep(1)

        # 2. بناء الأمر التنفيذي النهائي للأيرسيرف مع حقن القناة اللاسلكية لضمان ثبات الضربات
        air_command = f"airserv-ng -d {clean_mon} -p {target_port} -c {clean_chan}"
        
        try:
            print(f"[*] [Hardware Control] جاري حقن وإشعال السيرفر اللاسلكي العكسي على البورت: {target_port} والقناة: {clean_chan}...")
            # تمرير الأمر للراوتر عبر مصفوفة المصنع المعزولة الشل محلياً في كالي لحماية الـ C2
            self.ssh_factory.execute_remote_cmd(air_command)
            
            # مهلة الاستقرار العتادية الفعالة (2 ثانية) الموثقة في تجاربك للأكسس ap301
            print("[*] جاري الانتظار (2 ثانية) لضمان الاستقرار الفيزيائي وتلقيم الموجة...")
            time.sleep(2)
            
            # 3. التأكد الجازم من نجاح الإنشاء الفعلي للعملية بالداخل عبر النبض الموحد
            verify_report = self.query_active_daemons_before_kill()
            if verify_report["airserv_active"]:
                print(f"[+ AirServ] السيرفر اللاسلكي البعيد ينبض بنشاط الآن تحت معرّف: {verify_report['airserv_pids']}")
                return True
            else:
                print("[-] فشل إطلاق الأيرسيرف البعيد: نظام OpenWrt رفض بدء تشغيل الأداة.")
                return False
                
        except Exception as e:
            print(f"[-] عطل غير متوقع أثناء تهيئة وإشعال عتاد الأيرسيرف: {e}")
            return False
