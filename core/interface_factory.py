#!/usr/bin/env python3
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_vault import LoggerVault

class InterfaceFactory:
    def __init__(self, ssh_commander):
        self.commander = ssh_commander

    def neutralize_broadcasting(self, radio):
        """إخماد الـ Multicast والـ Beacons المزعجة لحماية المعالج ومنع اعادة تشغيل الاكسس قسرياً"""
        commands = [
            f"uci set wireless.default_{radio}.isolate='1' 2>/dev/null",
            f"uci commit wireless 2>/dev/null"
        ]
        combined = " && ".join(commands)
        code, _, _ = self.commander.execute_pure_cmd(combined)
        return code == 0

    def deploy_monitor_interface(self, radio, channel):
        """إنشاء كرت مراقبة نقي والاستعلام عن اسمه الحركي من النواة تلقائياً"""
        phy_device = radio.replace("radio", "phy")
        
        # تدمير أي واجهات مراقبة قديمة لتطهير بفر الذاكرة
        self.commander.execute_pure_cmd(f"iw dev wlan0mon del 2>/dev/null; iw dev phy0-mon0 del 2>/dev/null")
        
        # إرسال أمر البناء العتادي المباشر للنواة بدون uci reload حماية للتردد الآخر
        build_cmd = f"iw phy {phy_device} interface add mon_cage type monitor && ip link set mon_cage up"
        code, _, stderr = self.commander.execute_pure_cmd(build_cmd)
        
        if code != 0:
            LoggerVault.log_exception(f"فشل النواة البعيدة في بناء واجهة المراقبة: {stderr}")
            return None

        # تثبيت القناة المختارة فوراً على الكرت الجديد
        self.commander.execute_pure_cmd(f"iw dev mon_cage set channel {channel}")

        # الاستعلام الحركي من النواة لمعرفة الاسم الذي اعتمدته للكرت حياً
        _, stdout, _ = self.commander.execute_pure_cmd("iw dev | grep -B 1 'type monitor' | grep Interface | awk '{print $2}'")
        actual_name = stdout.strip()
        
        return actual_name if actual_name else "mon_cage"

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("💡 دليل فحص مصنع الكروت التلقائي:")
        print("   python3 interface_factory.py [IP] [PASS] [RADIO] [CHANNEL]")
        sys.exit(1)
        
    from core.ssh_commander import SSHCommander
    comm = SSHCommander(ip=sys.argv[1], password=sys.argv[2])
    factory = InterfaceFactory(comm)
    
    print("[*] جاري اختبار إخماد البث الموزع...")
    factory.neutralize_broadcasting(sys.argv[3])
    
    print("[*] جاري بناء كرت المراقبة واستخراج اسمه حياً من النواة...")
    iface_name = factory.deploy_monitor_interface(sys.argv[3], sys.argv[4])
    print(f"🟢 نجاح عتادي! الاسم الفعلي المعتمد في النواة البعيدة هو: [{iface_name}]")
