#!/usr/bin/env python3
import os
import sys
import re
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.intel_db import IntelDBManager
from core.ui_base import C_CYAN, G_OK, R_ERR, Y_WARN, D_DIV, RESET

class RadarHistorian:
    def __init__(self):
        self.intel_db = IntelDBManager()
        self.competitors_pattern = r"تواصل|سوا|عبيد|TWASUL"

    def decode_raw_ssid(self, raw_ssid):
        """[مفسّر التطهير]: معالجة وفك ترميز النصوص اللاتينية والعربية لمنع القراءات المخزية المشوهة"""
        try:
            if "\\x" in raw_ssid or "\\u" in raw_ssid:
                return raw_ssid.encode('utf-8').decode('unicode-escape').encode('latin1').decode('utf-8', errors='ignore').strip()
            return raw_ssid.strip()
        except Exception:
            return raw_ssid.strip() if raw_ssid else "[Hidden_SSID]"

    def parse_live_iwinfo_scan(self, ssh_commander, interface):
        code, stdout, _ = ssh_commander.execute_pure_cmd(f"iwinfo {interface} scan 2>/dev/null")
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
                # تفجير وترميم النصوص العربية حياً من بفر النواة
                clean_essid = self.decode_raw_ssid(raw_essid)
                
                aps[bssid] = {
                    'bssid': bssid, 'essid': clean_essid,
                    'channel': chan_match.group(1),
                    'signal': sig_match.group(1) + " dBm",
                    'privacy': "WPA/WPA2" if "Encryption:" in cell and "none" not in cell.lower() else "OPEN"
                }
        return aps

    def commit_and_track_live_changes(self, ssh_commander, interface, scanner_name, band):
        current_aps = self.parse_live_iwinfo_scan(ssh_commander, interface)
        scan_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n⚡ {C_CYAN}[ AeroScout-Intel : رادار الفحص وتتبع التغيرات الاستخباراتية للأثير ]{RESET}")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"📡 جهاز الفحص: [{scanner_name}] | الواجهة: [{interface}] | ⏱️ الوقت: [{scan_time_str}]")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

        if not current_aps:
            print(f"  └── {R_ERR}[❌] خطأ عتادي: فشل جلب البيانات أو الكروت مغلقة حالياً.{RESET}")
            return

        fahd_nets, comp_nets, other_nets = [], [], []
        
        with sqlite3.connect(self.intel_db.db_path) as conn:
            cursor = conn.cursor()
            for bssid, ap in current_aps.items():
                cursor.execute("SELECT essid, channel, first_seen FROM radar_history WHERE scanner_ap_name = ? AND bssid = ?;", (scanner_name, bssid))
                history = cursor.fetchone()
                
                f_seen = history if history else scan_time_str
                ap["first_seen"] = f_seen

                if not history:
                    cursor.execute("""INSERT INTO radar_history (scanner_ap_name, scanner_band, bssid, essid, channel, privacy, signal, first_seen, last_seen, scan_time) 
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (scanner_name, band, bssid, ap['essid'], ap['channel'], ap['privacy'], ap['signal'], scan_time_str, scan_time_str, scan_time_str))
                else:
                    cursor.execute("UPDATE radar_history SET essid = ?, channel = ?, signal = ?, last_seen = ?, scan_time = ? WHERE scanner_ap_name = ? AND bssid = ?;",
                                   (ap['essid'], ap['channel'], ap['signal'], scan_time_str, scan_time_str, scanner_name, bssid))

                if "FAHD" in ap['essid'].upper():
                    fahd_nets.append(ap)
                elif re.search(self.competitors_pattern, ap['essid'], re.IGNORECASE):
                    comp_nets.append(ap)
                else:
                    other_nets.append(ap)
            conn.commit()

        # عرض رقمي أنيق وراق للـ 3 جداول يعيد هيبة المنظومة
        for title, net_list, color in [("🔹 تصنيف: شبكاتك التابعة (Fahd_Net)", fahd_nets, G_OK), 
                                       ("🔹 تصنيف: Networks المنافسة الرئيسية", comp_nets, R_ERR), 
                                       ("🔹 تصنيف: باقي الشبكات والمصادر المحيطة", other_nets, C_CYAN)]:
            print(f"\n{color}{title}{RESET}")
            print(f"{D_DIV}----------------------------------------------------------------------------------------------------------{RESET}")
            if not net_list:
                print(f"  └── {D_DIV}لا توجد شبكات ممسوحة تنتمي لهذا التصنيف حالياً.{RESET}")
            for ap in net_list:
                print(f"{color}  %-44.44s | %-18s | CH: %-2s | %-8s | %-20s{RESET}" % (ap['essid'], ap['bssid'], ap['channel'], ap['privacy'], ap['first_seen']))
            print(f"{D_DIV}----------------------------------------------------------------------------------------------------------{RESET}")

        from core.intel_freq_analyser import IntelFreqAnalyser
        IntelFreqAnalyser.process_and_draw_topology(current_aps, band)
