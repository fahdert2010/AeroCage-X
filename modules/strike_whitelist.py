#!/usr/bin/env python3
import sys
import os

class StrikeWhitelist:
    def __init__(self):
        # الكلمات الدلالية الثابتة والمحمية أمنياً لحساباتك والمحيط
        self.protected_keywords = ["fahd", "cam", "camera"]

    def is_target_safe(self, bssid, ssid, privacy):
        """
        [فحص الحارس الصارم]: التحقق من هوية الهدف قبل القذف.
        يعيد True إذا كان الهدف مصرحاً لتجارب الفصل، و False إذا كان محمياً.
        """
        ssid_lower = str(ssid).lower().strip()
        privacy_upper = str(privacy).upper().strip()
        
        # 1. تفتيش الكلمات الدلالية لشبكاتك وكاميرات المراقبة
        for keyword in self.protected_keywords:
            if keyword in ssid_lower:
                return False, "شبكة شخصية/كاميرا محمية 🔒"

        # 2. حظر شبكات البيوت المحيطة المشفرة تلقائياً (WPA2/WPA3/WEP)
        # إذا كانت الشبكة مشفرة ولم تكن هي الأكسس المستهدف بالتجربة (يتم مطابقتها لاحقاً بالرئيسي)
        if any(enc in privacy_upper for enc in ["WPA2", "WPA3", "WEP"]):
            # نترك مساحة للملف الرئيسي ليمرر لو كان هذا الماك هو الهدف الفعلي للتجربة
            return False, "شبكة منزلية مشفرة محظورة 🛡️"

        return True, "صالح للاختبار 🚀"

if __name__ == "__main__":
    # مطبخ الفحص المخبري المستقل للمكتبة من السطر
    if len(sys.argv) < 3:
        print("💡 دليل فحص مكتبة الحماية:")
        print("   python3 strike_whitelist.py [اسم_الشبكة] [نوع_التشفيير]")
        sys.exit(1)
        
    test_ssid = sys.argv[1]
    test_privacy = sys.argv[2]
    
    guard = StrikeWhitelist()
    is_safe, reason = guard.is_target_safe("00:11:22:33:44:55", test_ssid, test_privacy)
    print(f"📊 نتيجة الاستجواب المخبري -> هل يسمح بالقذف؟ {is_safe} | السبب عتادياً: {reason}")
