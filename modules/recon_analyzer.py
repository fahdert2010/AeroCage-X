#!/usr/bin/env python3
import subprocess
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.logger_vault import LoggerVault

class ReconAnalyzer:
    def __init__(self, ssh_commander):
        self.commander = ssh_commander

    def scan_radio_interfaces(self):
        """[دالة الاستعلام الصامت بالـ ubus]: جلب كافّة الواجهات اللاسلكية وحالتها وقنواتها بدقة JSON المطلقة"""
        cmd = "ubus call network.wireless status"
        code, stdout, stderr = self.commander.execute_pure_cmd(cmd)
        
        if code != 0 or not stdout:
            LoggerVault.log_exception(f"فشل استجواب ubus لشبكة الوايرلس: {stderr}")
            return {}

        try:
            raw_data = json.loads(stdout)
        except Exception as e:
            LoggerVault.log_exception("تحطم قراءة الـ JSON لـ network.wireless status", e)
            return {}

        interfaces = {}
        
        # قضم شجرة الـ JSON المستخرجة من قلب معالجات أجهزتك الحقيقية
        for radio, radio_data in raw_data.items():
            if "interfaces" in radio_data:
                for iface_info in radio_data["interfaces"]:
                    iface_name = iface_info.get("ifname")
                    if not iface_name:
                        continue
                        
                    # التقاط الحالة العتادية الحقيقية (الفعالة والمعطلة)
                    is_up = iface_info.get("up", False)
                    config = iface_info.get("config", {})
                    
                    # عزل الـ SSID ورقم القناة الفعلي
                    ssid = config.get("ssid", "بث مخفي أو بدون واجهة بث")
                    channel = "غير محددة"
                    
                    # جلب القناة التشغيلية الصافية للراديو
                    if "config" in radio_data:
                        channel = str(radio_data["config"].get("channel", "1"))

                    interfaces[iface_name] = {
                        "radio": radio,
                        "ssid": ssid,
                        "channel": channel,
                        "status": "UP" if is_up else "DOWN"
                    }
        return interfaces

    def get_interface_clients(self, interface_name):
        """[دالة قضم حزم الـ ubus hostapd]: استخراج بيانات المتصلين حياً (الماك - الإشارة - السرعة)"""
        # استدعاء الواجهة الحقيقية الحية في جهازك (مثل hostapd.phy1-ap0)
        cmd = f"ubus call hostapd.{interface_name} get_clients"
        code, stdout, _ = self.commander.execute_pure_cmd(cmd)
        
        if code != 0 or not stdout:
            return []

        try:
            raw_data = json.loads(stdout)
        except Exception:
            return []

        clients = []
        clients_dict = raw_data.get("clients", {})
        
        for mac, client_data in clients_dict.items():
            # التقاط قوة الإشارة الحركية بالديسيبل الصافي
            signal = f"{client_data.get('signal', 'N/A')} dBm"
            
            # التقاط حقل السرعة الحية وقسمته رياضياً لإظهاره بالـ Mbps
            raw_rate = client_data.get("rate", {}).get("tx", 0)
            tx_rate = f"{raw_rate / 1000000:.1f} Mbps" if raw_rate > 0 else "N/A"
            
            clients.append({
                "mac": mac,
                "signal": signal,
                "tx_rate": tx_rate
            })
        return clients

    def generate_formatted_report(self, mode="2G"):
        """[اللوحة المستقبلية الهادئة]: عرض الزبائن حياً عتادياً وعزل الواجهات المعطلة بالألوان المريحة للعين"""
        all_ifaces = self.scan_radio_interfaces()
        
        C_CYAN = "\033[38;5;111m"; G_OK = "\033[38;5;150m"; R_ERR = "\033[38;5;167m"; D_DIV = "\033[38;5;242m"; RESET = "\033[0m"
        
        print(f"\n⚙️ {C_CYAN}[ AeroCage-X : رادار استعلام الزبائن اللحظي عبر UBUS - النطاق: {mode} ]{RESET}")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        if not all_ifaces:
            print(f"  └── {D_DIV}عامل الفحص: لم يتم العثور على أي واجهات لاسلكية تشغيلية حية في هذا النطاق.{RESET}")
            return 0
            
        active_count = 0
        for iface, data in all_ifaces.items():
            try:
                channel_num = int(data["channel"])
                is_5g = channel_num > 14
            except ValueError:
                channel_num = 1
                is_5g = False
                
            if (mode == "2G" and is_5g) or (mode == "5G" and not is_5g):
                continue

            status_str = f"{G_OK}UP{RESET}" if data["status"] == "UP" else f"{R_ERR}DOWN - معطلة عتادياً{RESET}"
            print(f"📡 الواجهة: {iface:<12} | الحالة: {status_str:<4} | 📶 القناة: {data['channel']:<3} | 🌐 الـ SSID: {data['ssid']}")
            
            if data["status"] == "DOWN":
                print(f"{D_DIV}───────────────────────────────────────────────────────────────────────────{RESET}")
                continue

            # استجواب المتصلين حياً من الـ ubus للواجهة النشطة
            clients = self.get_interface_clients(iface)
            if not clients:
                print(f"  └── {D_DIV}عامل الاستقرار: لا توجد أجهزة مرتبطة عتادياً حالياً لحمايتها.{RESET}")
            else:
                print(f"  └── 📊 [ الأجهزة المتصلة حالياً بالبث: {len(clients)} ]")
                for idx, client in enumerate(clients):
                    print(f"      [{idx+1}] 📱 MAC: {client['mac']} | 📶 الإشارة: {client['signal']:<8} | 🚀 السرعة: {client['tx_rate']}")
                    active_count += 1
            print(f"{D_DIV}───────────────────────────────────────────────────────────────────────────{RESET}")
            
        return active_count

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("💡 دليل الاستخدام البرمجي للمطبخ المخبري:")
        print("   python3 recon_analyzer.py [آيبي_الاكسس] [كلمة_السر] [النطاق: 2G أو 5G]")
        sys.exit(1)
        
    target_ip = sys.argv[1]
    target_pass = sys.argv[2]
    target_mode = sys.argv[3]
    
    from core.ssh_commander import SSHCommander
    commander = SSHCommander(ip=target_ip, password=target_pass)
    
    analyzer = ReconAnalyzer(commander)
    analyzer.generate_formatted_report(mode=target_mode)
