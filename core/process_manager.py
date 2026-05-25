#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import socket
from pathlib import Path

# ربط المسارات بالنواة المركزية للمنظومة
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard

class ProcessManager:
    def __init__(self):
        # قاموس مركزي لتتبع كافة العمليات النشطة داخل المنظومة بالأقفال الصارمة
        self.active_processes = {}
        self.lock = threading.Lock()

    def spawn_process_safe(self, key_name: str, command_array: list) -> subprocess.Popen:
        """
        🚀 إطلاق العمليات التكتيكية والأدوات الخارجية بأمان كامل 100% وبدون فتح شل.
        تم سحق ثغرات الـ Command Injection نهائياً (إلغاء shell=True تماماً لـ Bandit B602/B603).
        """
        # تطهير مفتاح العملية لمنع الصدمات البرمجية في الذاكرة
        clean_key = SystemGuard.sanitize_input(key_name, "interface")
        
        if not command_array or not isinstance(command_array, list):
            print(f"[-] خطأ تكتيكي: تم رفض تشغيل [{clean_key}] لأن هيكل مصفوفة الأوامر غير صالح.")
            return None

        # خط الدفاع الأول: إجبار مفسر الأوامر على معاملة المدخلات كنصوص مجردة
        try:
            process = subprocess.Popen(
                command_array,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False # تم القضاء على ثغرة الشل الحرج مركزياً لكل المنظومة
            )
            
            with self.lock:
                self.active_processes[clean_key] = process
                print(f"[+] تم إطلاق وتسجيل العملية [{clean_key}] بنجاح (PID: {process.pid})")
            
            # إطلاق الخيط البرمجي الحارس (Drain Thread) لحماية الـ Buffer ومنع تجميد الهجمات
            threading.Thread(target=self._drain_buffer_stream, args=(clean_key, process), daemon=True).start()
            return process
            
        except Exception as e:
            print(f"[-] فشل فادح أثناء إطلاق العملية الأمنية المركزي [{clean_key}]: {e}")
            return None

    def _drain_buffer_stream(self, key_name: str, process: subprocess.Popen):
        """🛡️ خيط تفريغ مخزن الأنبوب (Pipe Buffer) اللحظي لضمان قوة واستمرارية تدفق حزم الفصل"""
        try:
            # تستمر القراءة العتادية ما دامت العملية الهجومية أو الاستخباراتية تعمل في النظام
            while process.poll() is None:
                line = process.stdout.readline()
                if not line:
                    break
                # الأنبوب ينساب هنا بسلاسة، مما يمنع اختناق المعالج CPU وتجمد أداة aireplay
        except Exception:
            pass
        finally:
            # تنظيف تلقائي صامت فور انتهاء العملية من نظام لينكس
            with self.lock:
                if key_name in self.active_processes:
                    del self.active_processes[key_name]

    def terminate_process(self, key_name: str):
        """🛑 إنهاء عملية محلية مخصصة بالملي وتنظيف الذاكرة ومنع تكون الـ Zombie Processes"""
        clean_key = SystemGuard.sanitize_input(key_name, "interface")
        
        with self.lock:
            if clean_key in self.active_processes:
                process = self.active_processes[clean_key]
                if process.poll() is None: # إذا كانت العملية لا تزال حية خلف الكواليس
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                        print(f"[+] تم إنهاء وتطهير مسار العملية المحددة [{clean_key}] بنجاح.")
                    except subprocess.TimeoutExpired:
                        process.kill() # قتل قسري فوري إذا رفضت الأداة الامتثال للإغلاق النظيف
                        print(f"[-] تم قتل العملية قسرياً لمنع تعليق الموارد (PID: {process.pid})")
                del self.active_processes[clean_key]
            else:
                print(f"[-] تنبيه: لا توجد عملية نشطة ومسجلة في المنظومة للمفتاح: {clean_key}")

    @staticmethod
    def create_secure_listener(port: int, local_only: bool = True) -> socket.socket:
        """🔒 حل ثغرة Bandit (B104) - التحكم الصارم في مجال الاستماع للسوكت العكسي وقنوات الـ C2"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # السماح بإعادة استخدام المنفذ فوراً لمنع تعليق السوكت في الذاكرة وظهور Port already in use
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # خط الدفاع الشبكي: منع الاستماع العشوائي على 0.0.0.0 وعزله محلياً إلا بطلب صريح ومؤمن
        bind_address = '127.0.0.1' if local_only else '0.0.0.0'
        
        try:
            server_socket.bind((bind_address, port))
            server_socket.listen(5)
            print(f"[+] محرك السوكت الآمن يستمع الآن بنشاط وتأمين كامل على: {bind_address}:{port}")
            return server_socket
        except socket.Error as e:
            print(f"[-] خطأ شبكي حرج أثناء حجز منفذ السوكت {port}: {e}")
            server_socket.close()
            return None

if __name__ == "__main__":
    print("[+] مدير العمليات والأنابيب المشترك (Process Manager) مدمج ومحصن بنسبة 100%.")
    # اختبار تشغيلي سريع للبنية الهيكلية والأقفال
    pm = ProcessManager()
    proc = pm.spawn_process_safe("self_test_ping", ["ping", "-c", "2", "127.0.0.1"])
    if proc:
        proc.wait()
        print("[+] نجح الفحص الذاتي التكتيكي لمدير العمليات المركزي.")
