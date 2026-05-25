#!/usr/bin/env python3
import re

class TextParsingEngine:
    BSSID_PATTERN = re.compile(r'address:\s+([0-9a-fa-f:.-]+)', re.IGNORECASE)
    ESSID_PATTERN = re.compile(r'essid:\s+"([^"]*)"', re.IGNORECASE)
    CHANNEL_PATTERN = re.compile(r'channel:\s+(\d+)', re.IGNORECASE)
    SIGNAL_PATTERN = re.compile(r'signal:\s+(-\d+)\s+dBm', re.IGNORECASE)
    PID_PATTERN = re.compile(r'^\d+$')

    @classmethod
    def extract_ap_cells(cls, raw_stdout: str) -> list:
        """تفكيك كتل مسح الأجواء وعزل الحقول التالفة صامتاً"""
        cells = []
        blocks = raw_stdout.split("Cell ")
        for block in blocks:
            if not block.strip(): continue
            bssid = cls.BSSID_PATTERN.search(block)
            essid = cls.ESSID_PATTERN.search(block)
            chan = cls.CHANNEL_PATTERN.search(block)
            sig = cls.SIGNAL_PATTERN.search(block)

            if bssid and chan:
                cells.append({
                    "bssid": bssid.group(1).upper(),
                    "essid": essid.group(1) if essid else "Hidden_Network",
                    "channel": chan.group(1),
                    "power": int(sig.group(1)) if sig else -95
                })
        return cells

    @classmethod
    def clean_pids(cls, raw_stdout: str) -> list:
        """تنظيف وتصفية مخرجات pidof و pgrep واستخراج الأرقام الصافية فقط"""
        pids = []
        for word in raw_stdout.split():
            if cls.PID_PATTERN.match(word.strip()):
                pids.append(word.strip())
        return pids
