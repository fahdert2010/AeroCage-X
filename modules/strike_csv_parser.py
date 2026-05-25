#!/usr/bin/env python3
import os
import sys
import csv
from pathlib import Path

# 🛡️ خط الحماية المركزي: حقن وإجبار مفسر بايثون على قراءة المجلد الأب للمستودع تحت الـ sudo
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from core.ui_base import AeroCageUIBase
from core.system_guard import SystemGuard
from utils.network_validators import NetworkValidators

# تفعيل خط الدفاع الأول للمحيط التكتيكي
SystemGuard.enforce_root_privileges("Strike CSV Parser")

class StrikeCSVParser:
# بقية كود الفرز والقراءة القديم الخاص بك كما هو تماماً دون مساس...
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        
    def parse_results_safely(self) -> list:
        """قراءة وتطهير ملف نتائج الفحص اللاسلكي وحمايته بالاعتماد على الفلاتر المشتركة"""
        parsed_records = []
        if not self.file_path.exists():
            print(f"[-] خطأ: ملف النتائج غير موجود في المسار التكتيكي: {self.file_path}")
            return parsed_records

        try:
            with open(self.file_path, mode='r', encoding='utf-8', errors='ignore') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    cleaned_row = {}
                    for key, val in row.items():
                        if key is not None:
                            # استخدام الحارس الموحد لتنظيف المدخلات وحقن حماية الـ CSV Injection
                            clean_key = SystemGuard.sanitize_input(str(key), "csv_value")
                            clean_val = SystemGuard.sanitize_input(str(val), "csv_value")
                            
                            # ميزة استراتيجية: التحقق الإضافي الصارم إذا كان الحقل يمثل عنوان ماك
                            if "bssid" in clean_key.lower() or "mac" in clean_key.lower():
                                if not NetworkValidators.is_valid_bssid(clean_val):
                                    clean_val = "00:00:00:00:00:00" # تصفير الماك الملوث فوراً
                                    
                            cleaned_row[clean_key] = clean_val
                    if cleaned_row:
                        parsed_records.append(cleaned_row)
                        
            print(f"[+] تم تحليل وتطهير {len(parsed_records)} سجل بنجاح عبر النواة والمساعد الشبكي الموحد.")
            return parsed_records
        except Exception as e:
            print(f"[-] عطل غير متوقع في محرك القراءة والتطهير المطور: {e}")
        return parsed_records

if __name__ == "__main__":
    print("[*] محرك فحص وتطهير ملفات الـ CSV مدمج ومحمي ومرتبط بالمساعد الشبكي الموحد.")
