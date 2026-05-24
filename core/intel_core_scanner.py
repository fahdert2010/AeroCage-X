#!/usr/bin/env python3
import os
import re
import sqlite3
from datetime import datetime
from core.intel_db import IntelDBManager
from core.ui_base import G_OK, R_ERR, Y_WARN, RESET

class IntelCoreScanner:
    def __init__(self):
        self.intel_db = IntelDBManager()
        self.original_db = "/home/kali/AeroCage-X/data/aerocage_unified.db"

    def get_trusted_bssids(self, ssh_commander):
        """[صمام قفل التخمين]: قنص الماكات الحقيقية لكافة كروت البث بالراوتر لمنع الإنذارات الكاذبة"""
        trusted = []
        _, stdout, _ = ssh_commander.execute_pure_cmd("ubus call network.wireless status 2>/dev/null")
        if stdout.strip():
            try:
                import json
                raw_data = json.loads(stdout)
                for r_data in raw_data.values():
                    if "interfaces" in r_data:
                        for iface in r_data["interfaces"]:
                            ifname = iface.get("ifname")
                            if ifname:
                                _, h_out, _ = ssh_commander.execute_pure_cmd(f"ubus call hostapd.{ifname} get_config 2>/dev/null")
                                if h_out.strip():
                                    mac = json.loads(h_out).get("bssid", "").upper()
                                    if mac: trusted.append(mac)
            except Exception: pass
        return trusted

    def decode_hex_ssid(self, raw_ssid):
        try:
            if not raw_ssid or raw_ssid.strip() == "": return "[Hidden_SSID]"
            if "\\x" in raw_ssid:
                return raw_ssid.encode('utf-8').decode('unicode-escape').encode('latin1').decode('utf-8', errors='ignore').strip()
            return raw_ssid.strip()
        except Exception: return "[Hidden_SSID]"

    def parse_live_iwinfo_scan(self, ssh_commander, interface):
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
                clean_essid = self.decode_hex_ssid(essid_match.group(1) if essid_match else "")
                
                privacy = "OPEN"
                if "Encryption:" in cell and "none" not in cell.lower():
                    privacy = "WPA3" if "wpa3" in cell.lower() else "WPA2"
                if "wps" in cell.lower(): privacy += " + [WPS]"

                aps[bssid] = {'bssid': bssid, 'essid': clean_essid, 'channel': chan_match.group(1), 'signal': sig_match.group(1) + " dBm", 'privacy': privacy}
        return aps

    def sync_history(self, current_aps, scanner_name, band, trusted_bssids):
        scan_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_count, change_count, total_scanned = 0, 0, len(current_aps)
        
        with sqlite3.connect(self.intel_db.db_path) as conn:
            cursor = conn.cursor()
            for bssid, ap in current_aps.items():
                # المقارنة بالماكات الفيزيائية الحقيقية لمنع بتر الإنذارات الكاذبة لطلبك
                if "FAHD" in ap['essid'].upper() and bssid not in trusted_bssids and not bssid.startswith("30:23") and not bssid.startswith("00:07"):
                    print(f" {R_ERR}[🚨 إنذار أمني: Rogue AP Real]{RESET} انتحال اسم شبكتك! ESSID: {ap['essid']} | الماك الخبيث: {bssid}")

                cursor.execute("SELECT essid, channel FROM radar_history WHERE scanner_ap_name = ? AND bssid = ?;", (scanner_name, bssid))
                history = cursor.fetchone()
                if not history:
                    print(f" {G_OK}[+ شبكة جديدة مكتشفة بالأثير]{RESET} ESSID: {ap['essid']:<30} | BSSID: {bssid} | CH: {ap['channel']:<2} | {ap['privacy']}")
                    cursor.execute("""INSERT INTO radar_history (scanner_ap_name, scanner_band, bssid, essid, channel, privacy, signal, first_seen, last_seen, scan_time) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (scanner_name, band, bssid, ap['essid'], ap['channel'], ap['privacy'], ap['signal'], scan_time_str, scan_time_str, scan_time_str))
                    new_count += 1
                else:
                    hist_essid, hist_channel = history; changes = []
                    if hist_channel != ap['channel']: changes.append(f"CH: {hist_channel} ➡️ {ap['channel']}")
                    if hist_essid != ap['essid']: changes.append(f"SSID: {hist_essid} ➡️ {ap['essid']}")
                    if changes:
                        print(f" {Y_WARN}[⚠️ تغير تكتيكي بالأجواء]{RESET} الماك: {bssid} | " + " | ".join(changes))
                        cursor.execute("""UPDATE radar_history SET essid = ?, channel = ?, signal = ?, privacy = ?, last_seen = ?, scan_time = ? 
                                           WHERE scanner_ap_name = ? AND bssid = ?;""", (ap['essid'], ap['channel'], ap['signal'], ap['privacy'], scan_time_str, scan_time_str, scanner_name, bssid))
                        change_count += 1
                    else:
                        cursor.execute("UPDATE radar_history SET last_seen = ?, signal = ?, privacy = ? WHERE scanner_ap_name = ? AND bssid = ?;", (scan_time_str, ap['signal'], ap['privacy'], scanner_name, bssid))
            conn.commit()
        return new_count, change_count, total_scanned
