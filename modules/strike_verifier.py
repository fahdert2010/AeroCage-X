#!/usr/bin/env python3

class StrikeVerifier:
    @staticmethod
    def check_strike_effect(stations, active_strikes):
        """[ملف 4]: فاحص فاعلية الهجمة اللحظي ومراقبة السقوط الحركي للأهداف لطلبك"""
        power_map = {s["client"]: s["power"] for s in stations}
        
        for num, s in active_strikes.items():
            client = s["client"]
            if client in power_map:
                current_p = int(power_map[client].replace("-","").strip()) if power_map[client].strip().replace("-","").isdigit() else 99
                if current_p >= 85 or current_p == 0:
                    s["status"] = "🎯 تم السقوط الفعلي والتعطيل (Signal Dropped)"
                else:
                    s["status"] = f"يتم قذفه حياً 🚀 (إشارته: -{current_p} dBm)"
            else:
                s["status"] = "💤 الهدف غادر النطاق وانقطع الربط"
        return active_strikes
