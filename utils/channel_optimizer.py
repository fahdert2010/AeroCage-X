#!/usr/bin/env python3
import re

class ChannelOptimizer:
    @staticmethod
    def parse_scan_output(raw_stdout: str) -> list:
        """تفكيك مخرجات فحص iwinfo عن بعد وحمايتها من أخطاء الـ IndexError"""
        parsed_cells = []
        cell_blocks = raw_stdout.split("Cell ")
        
        for block in cell_blocks:
            if not block.strip():
                continue
            
            bssid_match = re.search(r'Address:\s+([0-9A-Fa-f:.-]+)', block)
            chan_match = re.search(r'Channel:\s+(\d+)', block)
            signal_match = re.search(r'Signal:\s+(-\d+)\s+dBm', block)
            essid_match = re.search(r'ESSID:\s+"([^"]*)"', block)

            if bssid_match and chan_match:
                parsed_cells.append({
                    "bssid": bssid_match.group(1).upper(),
                    "essid": essid_match.group(1) if essid_match else "Hidden_Network",
                    "channel": chan_match.group(1),
                    "power": int(signal_match.group(1)) if signal_match else -95
                })
        return parsed_cells

    @classmethod
    def calculate_best_channel(cls, parsed_cells: list) -> dict:
        """خوارزمية ذكية لحساب النسب المئوية للازدحام واكتشاف القناة الأقوى والأقل تداخلاً"""
        channel_load_scores = {}
        channel_counts = {}
        
        for cell in parsed_cells:
            chan = cell["channel"]
            power = cell["power"]
            
            channel_counts[chan] = channel_counts.get(chan, 0) + 1
            weight = 100 + power  # الشبكة الأقوى تزيد وزن الازدحام للقناة
            channel_load_scores[chan] = channel_load_scores.get(chan, 0) + max(5, weight)

        if not channel_counts:
            return {}

        total_networks = sum(channel_counts.values())
        best_channel = min(channel_load_scores, key=channel_load_scores.get)
        
        report_data = []
        for chan, count in sorted(channel_counts.items(), key=lambda x: int(x[0])):
            percentage = (count / total_networks) * 100
            load_status = "⚠️ مزدحم جداً" if channel_load_scores[chan] > 80 else "🟢 خفيف وآمن"
            report_data.append({
                "channel": chan,
                "count": count,
                "percentage": round(percentage, 1),
                "status": load_status
            })
            
        return {
            "best_channel": best_channel,
            "report": report_data,
            "counts": channel_counts
        }
