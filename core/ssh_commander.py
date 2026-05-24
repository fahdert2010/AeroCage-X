#!/usr/bin/env python3
import subprocess
import sys
import os

# إضافة المسار الرئيسي ليتمكن الملف من قراءة مكتبة اللوجستيات لو تم استدعاؤه منفصلاً
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_vault import LoggerVault

class SSHCommander:
    def __init__(self, ip, password, username="root"):
        self.ip = ip
        self.password = password
        self.username = username
        # صياغة السلسلة الصخرية لـ SSH المحمي من التجميد بمهلة اتصال 5 ثوانٍ فقط
        self.base_ssh = f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 {username}@{ip}"

    def execute_pure_cmd(self, command):
        """تنفيذ أمر صافي على الطرف البعيد وجلب النتيجة والـ Return Code بدقة"""
        full_command = f"{self.base_ssh} \"{command}\""
        try:
            res = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except Exception as e:
            LoggerVault.log_exception(f"انهيار عتادي أثناء محاولة تشغيل الأمر عبر SSH: {command}", e)
            return -1, "", str(e)

    def verify_connection_and_get_summary(self):
        """[دالة فحص الاتصال الفوري]: استجواب نظام التشغيل البعيد وعرض ملخص العتاد"""
        # استعلام مدمج لجلب إصدار OpenWrt ونوع المعالج المعماري وحالة الراديو
        query = "cat /etc/openwrt_release 2>/dev/null | grep DISTRIB_DESCRIPTION; uname -m; uci show wireless | grep =wifi-device | wc -l"
        code, stdout, stderr = self.execute_pure_cmd(query)
        
        if code == 0 and stdout:
            lines = stdout.split('\n')
            os_ver = lines[0].split('=')[1].replace("'", "").replace('"', '') if '=' in lines[0] else "OpenWrt Linux"
            arch = lines[1] if len(lines) > 1 else "Unknown CPU"
            wifi_count = lines[2] if len(lines) > 2 else "0"
            
            summary = {
                "status": True,
                "os": os_ver,
                "architecture": arch,
                "radios_detected": wifi_count,
                "msg": f"🟢 اتصال مستقر عتادياً! النظام: [{os_ver}] | المعالج: [{arch}] | الكروت المتاحة: [{wifi_count}]"
            }
            return summary
        else:
            return {
                "status": False,
                "os": "",
                "architecture": "",
                "radios_detected": "0",
                "msg": f"❌ فشل صدم الاتصال بالأكسس البعيد! سبب الرفض بالنواة: {stderr if stderr else 'انتهت مهلة التوصيل (Timeout)'}"
            }

    def check_live_attack_processes(self):
        """[دالة فحص الهجمات الحية داخلياً]: تتبع لو كان هناك عمليات قذف تجري حالياً بالذاكرة البعيدة"""
        check_cmd = "pgrep -x aireplay-ng || pgrep -x mdk4 || pgrep -f 'airserv-ng'"
        code, stdout, _ = self.execute_pure_cmd(check_cmd)
        
        # إذا وجد pgrep أي PID نشط لهذه الأدوات
        if code == 0 and stdout:
            pids = stdout.replace('\n', ', ')
            return True, f"⚠️ تحذير: يوجد عمليات هجوم/بث نشطة بالخلفية البعيدة حالياً على الـ PIDs: [{pids}]"
        return False, "🟢 ذاكرة العتاد البعيد نظيفة تماماً ولا يوجد أي هجوم داخلي يجري حالياً."

if __name__ == "__main__":
    # منطق الفحص الحركي المستقل للدالة عبر قذف المتغيرات من السطر
    if len(sys.argv) < 3:
        print("💡 دليل الاستخدام للمطبخ المخبري:")
        print("   python3 ssh_commander.py [آيبي_الاكسس] [كلمة_السر]")
        sys.exit(1)
        
    target_ip = sys.argv[1]
    target_pass = sys.argv[2]
    
    print(f"🧪 [بدء الفحص المخبري الجراحي لـ SSH Commander على الهدف: {target_ip}]...")
    commander = SSHCommander(ip=target_ip, password=target_pass)
    
    # 1. اختبار دالة فحص الاتصال وتوليد الملخص
    print("[*] جاري استجواب العتاد البعيد وجلب تفاصيل المنظومة...")
    conn_res = commander.verify_connection_and_get_summary()
    print(conn_res["msg"])
    
    # 2. اختبار دالة فحص وجود هجوم يجري حالياً بالذاكرة
    if conn_res["status"]:
        print("\n[*] جاري مسح الذاكرة العشوائية للاكسس لملاحقة عمليات القذف الحية...")
        attack_status, attack_msg = commander.check_live_attack_processes()
        print(attack_status, "->", attack_msg)
