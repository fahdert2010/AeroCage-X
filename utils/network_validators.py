#!/usr/bin/env python3
import re

class NetworkValidators:
    # الأنماط القياسية الصلبة لسلامة مدخلات ومخرجات المنظومة
    BSSID_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b')
    IP_REGEX = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')

    @classmethod
    def is_valid_bssid(cls, bssid: str) -> bool:
        """التحقق الحازم من صحة صيغة الماك أدرس لمنع الصدمات البرمجية"""
        if not bssid:
            return False
        return bool(cls.BSSID_REGEX.match(bssid.strip()))

    @classmethod
    def is_valid_ip(cls, ip: str) -> bool:
        """التحقق من صحة صيغة الـ IPv4 قبل تمريرها لأنابيب الفحص"""
        if not ip:
            return False
        return bool(cls.IP_REGEX.match(ip.strip()))

    @classmethod
    def extract_bssids_from_text(cls, text: str) -> list:
        """اقتناص كافة عينات الماك أدرس المتواجدة داخل أسطر النصوص أو مخرجات tshark"""
        return cls.BSSID_REGEX.findall(text)
