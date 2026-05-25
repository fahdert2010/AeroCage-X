#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from utils.network_validators import NetworkValidators

# تفعيل خط الدفاع الأول للمحيط التكتيكي
SystemGuard.enforce_root_privileges("Recon Analyzer Engine")

class ReconAnalyzerEngine:
    def __init__(self):
        # التحقق من وجود التبعيات الأساسية قبل تشغيل خطوط التحليل
        SystemGuard.verify_dependencies(["tshark"])

    def analyze_recon_log_safe(self, log_file_path: str) -> list:
        """
        تحليل وقراءة تقارير الاستطلاع النصية بأمان كامل وحصانة ضد أخطاء الترميز.
        تستخدم المساعد الموحد للتحقق من سلامة الأهداف.
        """
        path = Path(log_file_path)
        valid_targets = []

        if not path.exists():
            print(f"[-] خطأ استخباراتي: ملف تقرير الاستطلاع غير موجود في: {path}")
            return valid_targets

        try:
            # استخدام errors='ignore' يحميك من انهيار الـ UnicodeDecodeError عند قراءة أحرف الهواء المشوهة
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # اقتناص الماك أدرس ديناميكياً باستخدام كلاس التحقق الموحد لمنع الأخطاء الهيكلية
                    extracted_macs = NetworkValidators.extract_bssids_from_text(line)
                    
                    for mac in extracted_macs:
                        if NetworkValidators.is_valid_bssid(mac):
                            # تنظيف وتطهير النص المقروء لحماية بقية المنظومة
                            clean_mac = SystemGuard.sanitize_input(mac, "bssid")
                            valid_targets.append({"bssid": clean_mac, "source": path.name})

            print(f"[+] تم تحليل تقرير الاستطلاع وتوثيق {len(valid_targets)} هدف مصفى وآمن سيبرانياً.")
            return valid_targets

        except Exception as e:
            print(f"[-] عطل غير متوقع في محرك تحليل تقارير الاستطلاع: {e}")
            return valid_targets

    def run_deep_packet_analysis(self, pcap_path: str, output_txt_path: str) -> bool:
        """
        تشغيل فحص عميق للحزم اللاسلكية عبر tshark بأمان كامل وبدون فتح شل.
        تم سحق ثغرة الـ Command Injection نهائياً (إلغاء shell=True لـ Bandit B602/B603).
        """
        clean_pcap = SystemGuard.sanitize_input(pcap_path, "csv_value")
        clean_out = SystemGuard.sanitize_input(output_txt_path, "csv_value")

        if not Path(clean_pcap).exists():
            return False

        # بناء الأمر كمصفوفة أجزاء مستقلة تماماً ومغلقة الشل لحمايتك وسحق ثغرات Bandit
        command_array = ["tshark", "-r", clean_pcap, "-T", "fields", "-e", "wlan.sa", "-e", "wlan.da"]

        try:
            print(f"[*] جاري تفعيل كاشف الحزم العميقة الآمن لفك شفرة الملف: {clean_pcap}")
            
            # تشغيل آمن ومباشر ومغلق الشل
            result = subprocess.run(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
            
            if result.returncode == 0 and result.stdout:
                with open(clean_out, "w", encoding="utf-8") as out_f:
                    out_f.write(result.stdout)
                print(f"[+] انتهى التحليل العميق بنجاح وتم حفظ النتائج المصفاة في: {clean_out}")
                return True
            else:
                print(f"[-] فشل تحليل tshark للحزم: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            print(f"[-] خطأ فادح أثناء تشغيل خط الأنابيب لتحليل الحزم العميقة: {e}")
            return False

if __name__ == "__main__":
    print("[*] محرك تحليل تقارير الاستطلاع اللاسلكي (Recon Analyzer) مدمج ومحصن بنسبة 100%.")
