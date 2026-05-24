#!/usr/bin/env python3
import subprocess
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_vault import LoggerVault

class TunnelCoupler:
    def __init__(self, ssh_commander):
        self.commander = ssh_commander

    def generate_dynamic_port(self, db_id, mode="2G"):
        """توليد بورت خماسي يستند إلى البادئة الترددية والمعرف الرقمي"""
        prefix = "666" if mode == "2G" else "777"
        formatted_id = f"{int(db_id):02d}"
        return int(f"{prefix}{formatted_id}")

    def establish_airserv_tunnel(self, monitor_interface, target_channel, port):
        """إطلاق خادم البث بالـ nohup المباشر والصافي عتادياً"""
        # مسح المقابس القديمة تنظيفاً للذاكرة
        self.commander.execute_pure_cmd(f"killall -q airserv-ng; fuser -k {port}/tcp 2>/dev/null")
        time.sleep(1)

        # حقن الأمر بالـ nohup النقي المتوافق مع عتادك
        sh_bullet = f"nohup airserv-ng -p {port} -c {target_channel} -d {monitor_interface} >/dev/null 2>&1 &"
        self.commander.execute_pure_cmd(sh_bullet)
        time.sleep(2)

        # التحقق الفعلي من فتح بورت الاستماع داخل نواة الأكسس
        code, stdout, _ = self.commander.execute_pure_cmd(f"netstat -an | grep ':{port}' || netstat -an | grep '{port}'")
        return len(stdout.strip()) > 0

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("💡 دليل فحص موصل الأنفاق:")
        print("   python3 tunnel_coupler.py [IP] [PASS] [DB_ID] [IFACE_NAME] [CHANNEL]")
        sys.exit(1)
        
    # الترتيب الصارم والصحيح لسحب المتغيرات من السطر لمنع التعارض
    target_ip = sys.argv[1]
    target_pass = sys.argv[2]
    db_id = sys.argv[3]
    iface_name = sys.argv[4]
    channel = sys.argv[5]
    
    from core.ssh_commander import SSHCommander
    comm = SSHCommander(ip=target_ip, password=target_pass)
    coupler = TunnelCoupler(comm)
    
    dyn_port = coupler.generate_dynamic_port(db_id, mode="2G")
    print(f"⚙️ البورت الديناميكي المولد: [{dyn_port}]")
    success = coupler.establish_airserv_tunnel(iface_name, channel, dyn_port)
    print(f"🟢 حالة استقرار النفق بـ nohup في الذاكرة: {success}")
