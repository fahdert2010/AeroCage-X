#!/usr/bin/env python3
import os
import subprocess

class StrikeReconLogger:
    @staticmethod
    def setup_tunnel(selected_band, ap_id, target_channel, mon_iface, ssh_commander):
        """حساب البورت الديناميكي الآمن وإشعال سيرفر الـ airserv البعيد"""
        port = (666 if selected_band == "2G" else 777) + int(ap_id)
        ssh_commander.execute_pure_cmd(f"iw dev {mon_iface} set channel {target_channel}")
        ssh_commander.execute_pure_cmd(f"nohup airserv-ng -d {mon_iface} -p {port} >/dev/null 2>&1 &")
        return port

    @staticmethod
    def start_airodump_tree(ap_name, band, channel, target_socket):
        """تأسيس المجلد الشجري العسكري وصعق الـ airodump للكتابة حياً بالـ CSV"""
        path = f"/home/kali/AeroCage-X/storage/recon/{ap_name}/{band}/CH_{channel}"
        os.makedirs(path, exist_ok=True)
        csv_prefix = os.path.join(path, "live_capture")
        subprocess.run(f"rm -f {csv_prefix}*", shell=True)
        
        subprocess.Popen(f"nohup airodump-ng --channel {channel} --write {csv_prefix} --output-format csv {target_socket} >/dev/null 2>&1 &", shell=True)
        return f"{csv_prefix}-01.csv"
