#!/usr/bin/env python3
from core.ui_base import G_OK, R_ERR, Y_WARN, D_DIV, RESET

class IntelFreqAnalyser:
    @staticmethod
    def process_and_draw_topology(current_aps, band_mode):
        """الحساب الرياضي لنسب التشويش وإرجاع المعرف الصافي لأفضل منفذ حركي"""
        valid_channels = [str(x) for x in range(1, 14)] if band_mode == "2G" else [str(x) for x in range(36, 166, 4)]
        channel_weights = {ch: 0 for ch in valid_channels}
        total_nets = len(current_aps)

        for ap in current_aps.values():
            ch = ap['channel']
            if ch in channel_weights: channel_weights[ch] += 1

        print(f"\n📊 [ تقرير كثافة وازدحام القنوات والنسبة المئوية للأثير المحيط حركياً - نطاق {band_mode} ]:")
        print(f"{D_DIV}========================================================================================================={RESET}")
        print(f" {'رقم القناة':<10} | {'عدد الشبكات عليها':<20} | {'النسبة المئوية':<15} | {'المخطط البياني والتوزيع الحركي'}")
        print(f"{D_DIV}========================================================================================================={RESET}")

        if total_nets == 0:
            print(" 🚫 لم يتم العثور على أي شبكات جيران نشطة حالياً لتحليل قنواتها.")
            print(f"{D_DIV}========================================================================================================={RESET}")
            return "1" if band_mode == "2G" else "36"

        best_channel = valid_channels[0] if valid_channels else "1"
        min_weight = 99999

        for ch in valid_channels:
            count = channel_weights[ch]
            percentage = int((count * 100) / total_nets) if total_nets > 0 else 0
            bar = "█" * count
            
            if percentage > 30: COLOR = R_ERR
            elif percentage > 15: COLOR = Y_WARN
            else: COLOR = G_OK

            print(f"{COLOR}  القناة [{ch:<2}]   | ({count:<2}) شبكات مشوشة      | {percentage:<3} %        | {bar}{RESET}")

            if count < min_weight:
                min_weight = count
                best_channel = ch

        print(f"{D_DIV}========================================================================================================={RESET}")
        print(f"🏆 التوصية العتادية للمنظومة ➡️ أفضل قناة حرة وصافية حالياً هي القناة: [{best_channel}]")
        print(f"{D_DIV}========================================================================================================={RESET}")
        
        # [قفل إصلاح العيب البرمجي]: إرجاع المتغير الصافي للملف الرئيسي
        return best_channel
