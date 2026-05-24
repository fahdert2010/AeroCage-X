#!/usr/bin/env python3
import sys
import os
import sqlite3
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.ui_base import UIBase, C_CYAN, G_OK, R_ERR, Y_WARN, D_DIV, RESET
from core.ssh_commander import SSHCommander
from core.intel_ubus_scout import IntelUbusScout
from core.intel_freq_analyser import IntelFreqAnalyser
from core.intel_core_scanner import IntelCoreScanner

ORIGINAL_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "aerocage.db")

class AeroScoutIntelHub:
    def __init__(self):
        self.scanner = IntelCoreScanner()
        self.competitors_pattern = r"تواصل|سوا|عبيد|TWASUL"

    def get_legacy_access_points(self):
        if not os.path.exists(ORIGINAL_DB_PATH): return []
        try:
            with sqlite3.connect(ORIGINAL_DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, ip, username, password FROM access_points ORDER BY id ASC;")
                return cursor.fetchall()
        except Exception: return []

    def main_menu(self):
        while True:
            UIBase.clear_screen()
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"📡 {G_OK}[ منصة السجلات والتحليل الاستخباراتي للتغيرات اللاسلكية : AeroScout-Intel ]{RESET}")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f" [{G_OK}1{RESET}] بدء جولة الفحص الحي وقراءة التغييرات والنسب المئوية للأجواء")
            print(f" [{R_ERR}0{RESET}] إغلاق نفق المنظومة المنفصلة والخروج")
            print(f"{C_CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            
            opt = input("🔢 الاختيار: ").strip()
            if opt in ["0", "exit", ""]: break
            elif opt == "1":
                UIBase.show_header("بدء جولة الفحص الحي وتحليل عتاد الأجواء")
                aps = self.get_legacy_access_points()
                if not aps:
                    print(f" ❌ {R_ERR}قاعدة بيانات الأكسسات فارغة!{RESET}"); UIBase.return_prompt(); continue
                    
                print(f" [ اختر اسم الأكسس بوينت الذي سيقوم بالمسح حياً ]:")
                for idx, (ap_id, ap_name, ap_ip, ap_user, ap_pass) in enumerate(aps):
                    print(f"   [{idx+1}] الاسم: {ap_name} | IP: {ap_ip}")
                    
                ap_idx = input("\n🔢 رقم الأكسس: ").strip()
                if not ap_idx.isdigit() or int(ap_idx) > len(aps): continue
                ap_id, ap_name, ap_ip, ap_user, ap_pass = aps[int(ap_idx)-1]
                
                band_opt = input("🌐 اختر نطاق التردد التشغيلي للفحص [1: للـ 2G | 2: للـ 5G]: ").strip()
                selected_band = "5G" if band_opt == "2" else "2G"
                
                print(f"\n[*] جاري تصفية واجهات البث الموجه عبر UBUS...")
                comm = SSHCommander(ip=ap_ip, password=ap_pass, username=ap_user)
                
                raw_ifaces = IntelUbusScout.get_filtered_interfaces(comm, selected_band)
                if not raw_ifaces:
                    print(f"❌ {R_ERR}لا توجد واجهات نشطة لهذا التردد حالياً في الراوتر!{RESET}")
                    UIBase.return_prompt(); continue
                
                print(f"\n{G_OK}[ واجهات البث النشطة الموزعة ونطاق أجهزتك للتردد {selected_band} ]:{RESET}")
                iface_list = list(raw_ifaces.keys())
                for i_idx, i_name in enumerate(iface_list):
                    print(f"  [{i_idx+1}] الواجهة: {i_name:<10} | 📶 القناة الحالية: {raw_ifaces[i_name]['channel']:<2} | 🌐 الـ SSID: {raw_ifaces[i_name]['ssid']}")
                    clients = IntelUbusScout.get_live_clients_for_iface(comm, raw_ifaces[i_name]['service'])
                    if clients:
                        print(f"      └── 📊 [ الأجهزة المتصلة حالياً بالبث: {len(clients)} ]")
                        for c in clients:
                            print(f"          📱 MAC: {c['mac']} | 📶 الإشارة: {c['signal']:<8} | 🚀 السرعة: {c['tx_rate']}")
                    else:
                        print(f"      └── {D_DIV}عامل الاستقرار: لا توجد أجهزة متصلة بالبث حالياً.{RESET}")
                    print(f"  {D_DIV}───────────────────────────────────────────────────────────────────────{RESET}")
                    
                if_opt = input("\n🔢 اختر رقم واجهة البث لقفل الهاردوير والمسح من خلالها: ").strip()
                if not if_opt.isdigit() or int(if_opt) > len(iface_list): continue
                actual_interface = iface_list[int(if_opt)-1]
                
                print(f"\n[*] جاري قذف طلب المسح لـ iwinfo scan على الكرت الحقيقي [{actual_interface}]...")
                current_aps = self.scanner.parse_live_iwinfo_scan(comm, actual_interface)
                self.scanner.sync_history(current_aps, ap_name, selected_band)
                
                fahd_nets, comp_nets, other_nets = [], [], []
                for bssid, ap in current_aps.items():
                    if "FAHD" in ap['essid'].upper(): fahd_nets.append(ap)
                    elif re.search(self.competitors_pattern, ap['essid'], re.IGNORECASE): comp_nets.append(ap)
                    else: other_nets.append(ap)

                for title, net_list, color in [("🔹 تصنيف: شبكاتك التابعة (Fahd_Net)", fahd_nets, G_OK), 
                                               ("🔹 تصنيف: Networks المنافسة الرئيسية", comp_nets, R_ERR), 
                                               ("🔹 تصنيف: باقي الشبكات والمصادر المحيطة", other_nets, C_CYAN)]:
                    print(f"\n{color}{title}{RESET}")
                    print(f"{D_DIV}----------------------------------------------------------------------------------------------------------{RESET}")
                    for ap in net_list:
                        print(f"{color}  %-44.44s | %-18s | CH: %-2s | %-8s | Privacy: %-8s{RESET}" % (ap['essid'], ap['bssid'], ap['channel'], ap['signal'], ap['privacy']))
                    print(f"{D_DIV}----------------------------------------------------------------------------------------------------------{RESET}")

                IntelFreqAnalyser.process_and_draw_topology(current_aps, selected_band)
                UIBase.return_prompt()

if __name__ == "__main__":
    hub = AeroScoutIntelHub()
    hub.main_menu()
