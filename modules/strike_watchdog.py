#!/usr/bin/env python3
import csv
import sys
import os

class StrikeWatchdog:
    def __init__(self):
        pass

    def verify_strike_efficiency(self, live_csv_path, target_client_mac):
        """[حسّاس اللوست اللحظي]: قراءة ملف الـ CSV الخاص بالرادار وعزل عداد الحزم المفقودة للتأكد من سقوط الضحية"""
        if not live_csv_path or not os.path.exists(live_csv_path):
            return "يتم قذفه 🚀"

        try:
            with open(live_csv_path, mode='r', errors='ignore') as f:
                reader = csv.reader(f)
                for row in reader:
                    # ملاحقة أسطر الأجهزة المتصلة (Clients) في القسم السفلي لملف الأيردومب
                    if len(row) >= 6 and target_client_mac.upper() in row[0].upper():
                        # حقل الحزم المرسلة وحقل الحزم المفقودة (Lost) عتادياً
                        try:
                            packets = int(row[4].strip() if row[4].strip().isdigit() else 0)
                            lost = int(row[5].strip() if row[5].strip().isdigit() else 0)
                            
                            # إذا قفز عداد الفقدان بشكل ملحوظ يثبت برهان سقوط الاتصال
                            if lost > 25 and (lost / (packets + lost + 1)) > 0.30:
                                return "بدء مفعوله وتم الفصل 🎯"
                        except (ValueError, IndexError):
                            pass
            return "يتم قذفه 🚀"
        except Exception:
            return "يتم قذفه 🚀" # العودة للحالة الآمنة لو كان الملف مقفلاً برمجياً بسبب الكتابة اللحظية
