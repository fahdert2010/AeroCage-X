#!/usr/bin/env python3
import re
import sqlite3
from datetime import datetime
from core.intel_db import IntelDBManager
from core.ui_base import G_OK, Y_WARN, RESET

class IntelCoreScanner:
    def __init__(self):
        self.intel_db = IntelDBManager()

    def decode_hex_ssid(self, raw_ssid):
        try:
            if not raw_ssid or raw_ssid.strip() == "": return "[Hidden_SSID]"
            if "\\x" in raw_ssid:
                bytes_str = raw_ssid.encode('utf-8').decode('unicode-escape').encode('latin1')
                return bytes_str.decode('utf-8', errors='ignore').strip()
            return raw_ssid.strip()
        except Exception:
            return raw_ssid.strip() if raw_ssid else "[Hidden_SSID]"

    def parse_live_iwinfo_scan(self, ssh_commander, interface):
        # [حارس الـ Shell Injection]: تنظيف صارم لاسم الواجهة الممررة للنواة البعيدة
        clean_iface = re.sub(r'[^a-zA-Z0-9.-]', '', interface)
        code, stdout, _ = ssh_commander.execute_pure_cmd(f"iwinfo {clean_iface} scan 2>/dev/null")
        if code != 0 or not stdout: return {}

        aps = {}
        cells = stdout.split("Cell ")
        for cell in cells:
            if not cell.strip(): continue
            mac_match = re.search(r"Address:\s*(([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})", cell, re.IGNORECASE)
            essid_match = re.search(r'ESSID:\s*"(.*?)"', cell)
            chan_match = re.search(r"Channel:\s*(\d+)", cell)
            sig_match = re.search(r"Signal:\s*(-?\d+)", cell)

            if mac_match and chan_match and sig_match:
                bssid = mac_match.group(1).upper()
                raw_essid = essid_match.group(1) if essid_match else "[Hidden_SSID]"
                clean_essid = self.decode_hex_ssid(raw_essid)
                
                aps[bssid] = {
                    'bssid': bssid, 'essid': clean_essid, 'channel': chan_match.group(1),
                    'signal': sig_match.group(1) + " dBm",
                    'privacy': "WPA/WPA2" if "Encryption:" in cell and "none" not in cell.lower() else "OPEN"
                }
        return aps

    def sync_history(self, current_aps, scanner_name, band):
        """[تأمين الـ SQL]: استخدام المعاملات ? لغلق ثغرات حقن قاعدة البيانات للأبد"""
        scan_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_count, change_count = 0, 0
        with sqlite3.connect(self.intel_db.db_path) as conn:
            cursor = conn.cursor()
            for bssid, ap in current_aps.items():
                cursor.execute("SELECT essid, channel FROM radar_history WHERE scanner_ap_name = ? AND bssid = ?;", (scanner_name, bssid))
                history = cursor.fetchone()
                if not history:
                    print(f" {G_OK}[+ شبكة جديدة]{RESET} ESSID: {ap['essid']:<30} | BSSID: {bssid} | CH: {ap['channel']:<2} | Sign: {ap['signal']}")
                    cursor.execute("""INSERT INTO radar_history (scanner_ap_name, scanner_band, bssid, essid, channel, privacy, signal, first_seen, last_seen, scan_time) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (scanner_name, band, bssid, ap['essid'], ap['channel'], ap['privacy'], ap['signal'], scan_time_str, scan_time_str, scan_time_str))
                    new_count += 1
                else:
                    hist_essid, hist_channel = history; changes = []
                    if hist_channel != ap['channel']: changes.append(f"القناة انكسرت: {hist_channel} ➡️ {ap['channel']}")
                    if hist_essid != ap['essid']: changes.append(f"الاسم تغير: {hist_essid} ➡️ {ap['essid']}")
                    if changes:
                        print(f" {Y_WARN}[⚠️ رصد تغير تكتيكي]{RESET} الماك: {bssid} | " + " | ".join(changes))
                        cursor.execute("""UPDATE radar_history SET essid = ?, channel = ?, signal = ?, last_seen = ?, scan_time = ? 
                                           WHERE scanner_ap_name = ? AND bssid = ?;""", (ap['essid'], ap['channel'], ap['signal'], scan_time_str, scan_time_str, scanner_name, bssid))
                        change_count += 1
                    else:
                        cursor.execute("UPDATE radar_history SET last_seen = ?, signal = ? WHERE scanner_ap_name = ? AND bssid = ?;", (scan_time_str, ap['signal'], scanner_name, bssid))
            conn.commit()
        return new_count, change_count
