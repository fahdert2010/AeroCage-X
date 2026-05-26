cat << 'EOF' > /home/kali/AeroCage-XV1.0.1/utils/tunnel_watchdog.py
#!/usr/bin/env python3
"""
File Name: tunnel_watchdog.py
Path: /home/kali/AeroCage-XV1.0.1/utils/tunnel_watchdog.py
Created Date: 2026-05-26
Version: 1.2.1
Description: Ultimate Reverse SSH Tunnel Watchdog Subsystem for AeroCage-X.
             Enforces thread-safe locked hot reconnections and telemetry cache.
"""

import subprocess
import threading
import time


class TunnelWatchdog:
    """
    Decoupled Subsystem Watchdog Engine.
    Monitors live heartbeat sockets and processes background hot reconnections.
    """

    def __init__(self, mission_context: dict, ssh_factory_instance):
        """تهيئة الحارس وحقن كبسولة السياق التكتيكي والاقتران بمصنع الـ SSH"""
        self.ctx = mission_context
        self.factory = ssh_factory_instance
        self.is_monitoring = False
        self.on_timeout_callback = None

        # [مجمع النبض الموحد المعزول]: كاش محلي صامت لحماية معالج الراوتر البعيد
        self.last_known_alive = True

        # [صمام الخيط الأحادي التمكين]: قفل حركي لمنع انفجار الـ Threads بالخلفية
        self.is_reconnecting = False

    def start_tunnel_monitoring_loop(self, timeout_callback_func):
        """إطلاق خيط الحراسة الخلفي الصامت وتثبيت دالة الإلغاء الطارئة للواجهة"""
        self.on_timeout_callback = timeout_callback_func
        self.is_monitoring = True

        threading.Thread(
            target=self._async_watchdog_worker_loop,
            daemon=True
        ).start()

    def stop_tunnel_monitoring_loop(self):
        """كبح محرك الحراسة وتصفير المؤشرات لتطهير بافر الذاكرة العشوائية"""
        self.is_monitoring = False

    def _execute_background_reconnection(self):
        """[محرك الإنعاش الخارق المعزول]: حفر نفق الـ SSH صامتاً بدون تكرار"""
        # التصفير الكلي للثوابت: القراءة الحية للبورتات المتسلسلة الديناميكية للمهمة
        r_port = int(self.ctx["remote_port"])
        l_port = int(self.ctx["local_port"])

        cmd_tunnel = [
            "sshpass", "-p", "root", "ssh", "-N", "-R",
            f"{r_port}:localhost:{l_port}", f"root@{self.factory.ip}",
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/shm/null"
        ]
        try:
            with subprocess.Popen(
                cmd_tunnel, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            ) as proc:
                proc.wait(timeout=1.0)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            pass
        finally:
            # تحرير القفل فور انتهاء المحاولة بسلام للسماح بالدورة التالية عند الحاجة
            self.is_reconnecting = False

    def _async_watchdog_worker_loop(self):
        """المحرك الخلفي الموقوت بالـ 60 ثانية صرامة لمنع اللانهائية وحماية كالي"""
        start_drop_time = None
        print("[🪐 Watchdog] Background heartbeat listener established safely.")

        while self.is_monitoring:
            time.sleep(2)

            # الاستجواب العتادي الحصري والوحيد وتحديث بافر الكاش محلياً في كالي
            is_alive = self.factory.verify_ssh_heartbeat()
            self.last_known_alive = is_alive

            if not is_alive:
                if start_drop_time is None:
                    start_drop_time = time.time()
                    print("[⚠️] Watchdog Sensor: Tunnel drop registered live!")

                elapsed_time = time.time() - start_drop_time

                # [تفعيل صمام الخيط الأحادي]: نتحقق من القفل، لو كان الحارس يعمل بالفعل، نمنع الانفجار
                if not self.is_reconnecting:
                    self.is_reconnecting = True
                    threading.Thread(
                        target=self._execute_background_reconnection,
                        daemon=True
                    ).start()

                # [صمام قيد الدقيقة الواحدة]: لو تخطى الانقطاع 60 ثانية، يستدعي كبح الهجوم قسرياً
                if elapsed_time >= 60.0:
                    # عزل النص القاتل وتفتيته في متغير قصير لمنع قيد الـ Line too long نهائياً
                    txt_evac = "[🚨 Watchdog] Critical Timeout. Evacuating asset."
                    print(txt_evac)
                    self.is_monitoring = False
                    if self.on_timeout_callback:
                        self.on_timeout_callback()
                    break
            else:
                if start_drop_time is not None:
                    start_drop_time = None
                    print("[🟢 Watchdog] Heartbeat recovered. System stabilized.")


if __name__ == "__main__":
    print("[+] Ultimate Tunnel Watchdog Engine Upgraded 1000%.")
EOF
chmod +x /home/kali/AeroCage-XV1.0.1/utils/tunnel_watchdog.py
