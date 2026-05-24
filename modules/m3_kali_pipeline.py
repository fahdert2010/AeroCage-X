#!/usr/bin/env python3
import os, csv, subprocess, time

class M3KaliPipeline:
    @staticmethod
    def start_recon_stream(ap_name, band, channel, socket):
        """بناء المجلد الشجري العسكري باسم الأكسس والنطاق وقذف الأيردمب الموجه للكتابة حياً"""
        path = f"/home/kali/AeroCage-X/storage/recon/{ap_name}/{band}/CH_{channel}"
        os.makedirs(path, exist_ok=True)
        csv_prefix = os.path.join(path, "live_capture")
        subprocess.run(f"rm -f {csv_prefix}*", shell=True)
        subprocess.Popen(f"nohup airodump-ng --channel {channel} --write {csv_prefix} --output-format csv {socket} >/dev/null 2>&1 &", shell=True)
        return f"{csv_prefix}-01.csv"

    @staticmethod
    def retry_parse_pipeline(csv_path):
        """[مهندس التتابع الموقوت]: محاولة أولى وثانية بمهل تصاعدية لقراءة ملف الـ CSV حياً لطلبك"""
        # المحاولة 1: انتظر مهلة أولية خفيفة ثم افحص
        time.sleep(2.5)
        stations, ap_map = M3KaliPipeline.raw_csv_parse(csv_path)
        if stations: return stations, ap_map, "🚀 نجحت المحاولة الأولى (قراءة فورية طازجة)"

        # المحاولة 2: إذا فشل، امنح الأيردمب مهلة انتظار أطول قليلاً للاستقرار العتادي
        print("  ⏱️ [المحاولة 1 فارغة] -> جاري تمديد الانتظار العملياتي للمحاولة 2 (4 ثوانٍ إضافية)...")
        time.sleep(4.0)
        stations, ap_map = M3KaliPipeline.raw_csv_parse(csv_path)
        if stations: return stations, ap_map, "🚀 نجحت المحاولة الثانية (تم التزامن عتادياً)"

        return [], {}, "❌ المحاولتان فارغتان: لم يتم رصد أهداف أو الأيردمب لم يبدأ الضخ بعد."

    @staticmethod
    def raw_csv_parse(csv_path):
        """قضم وتفكيك سكاكين الـ CSV حياً بصمامات أمان حتمية لمنع الـ IndexError"""
        if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0: return [], {}
        try:
            with open(csv_path, "r", encoding="utf-8", errors="ignore") as f: content = f.read()
            sections = content.split("\n\n")
            if len(sections) < 2 or "Station MAC" not in content: return [], {}
            
            ap_map = {}
            for r in csv.reader(sections[0].strip().split("\n")):
                if r and len(r) >= 14 and not r[0].startswith("BSSID"): ap_map[r[0].strip().upper()] = r[13].strip()
                
            stations = []
            for r in csv.reader(sections[1].strip().split("\n")):
                if not r or len(r) < 6 or r[0].startswith("Station MAC"): continue
                if r[5].strip().upper() in ap_map:
                    stations.append({"client": r[0].strip().upper(), "bssid": r[5].strip().upper(), "ssid": ap_map[r[5].strip().upper()], "power": r[3]})
            return stations, ap_map
        except Exception: return [], {}
