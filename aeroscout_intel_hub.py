#!/usr/bin/env python3
import sys, os, sqlite3, re

sys.path.insert(0, "/home/kali/AeroCage-X")
from core.ui_base import UIBase, C_CYAN, G_OK, R_ERR, Y_WARN, D_DIV, RESET
from core.ssh_commander import SSHCommander
from core.intel_ubus_scout import IntelUbusScout
from core.intel_core_scanner import IntelCoreScanner

ORIGINAL_DB_PATH = "/home/kali/AeroCage-X/data/aerocage_unified.db"

class AeroScoutIntelHub:
    def __init__(self):
        self.scanner = IntelCoreScanner()

    def get_legacy_access_points(self):
        if not os.path.exists(ORIGINAL_DB_PATH): return []
        try:
            with sqlite3.connect(ORIGINAL_DB_PATH) as conn:
                return conn.execute("SELECT id, name, ip, username, password FROM access_points ORDER BY id ASC;").fetchall()
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
                aps = self.get_legacy_access_points()
                if not aps: print(" ❌ قاعدة البيانات فارغة!"); UIBase.return_prompt(); continue
                
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
                
                raw_ifaces, down_ifaces = IntelUbusScout.query_interfaces(comm, selected_band)
                if not raw_ifaces: print("❌ لا توجد واجهات نشطة!"); UIBase.return_prompt(); continue
                
                print(f"\n{G_OK}[ واجهات البث النشطة الموزعة ونطاق أجهزتك للتردد {selected_band} ]:{RESET}")
                iface_list = list(raw_ifaces.keys())
                for i_idx, i_name in enumerate(iface_list):
                    print(f"  [{i_idx+1}] الواجهة: {i_name:<10} | 📶 القناة الحالية: {raw_ifaces[i_name]['channel']:<2} | 🌐 الـ SSID: {raw_ifaces[i_name]['ssid']}")
                    clients = IntelUbusScout.get_live_clients(comm, raw_ifaces[i_name]['service'])
                    if clients:
                        print(f"      └── 📊 [ الأجهزة المتصلة حالياً بالبث: {len(clients)} ]")
                        for c in clients: print(f"          📱 MAC: {c['mac']} | 📶 الإشارة: {c['signal']:<8} | 🚀 السرعة: {c['rate']}")
                    else: print(f"      └── {D_DIV}عامل الاستقرار: لا توجد أجهزة متصلة بالبث حالياً.{RESET}")
                    print(f"  {D_DIV}───────────────────────────────────────────────────────────────────────{RESET}")
                    
                if_opt = input("\n🔢 اختر رقم واجهة البث لقفل الهاردوير والمسح من خلالها: ").strip()
                if not if_opt.isdigit() or int(if_opt) > len(iface_list): continue
                actual_interface = iface_list[int(if_opt)-1]
                
                print(f"\n[*] جاري قذف طلب المسح لـ iwinfo scan على الكرت الحقيقي [{actual_interface}]...")
                current_aps = self.scanner.parse_live_iwinfo_scan(comm, actual_interface)
                
                trusted_macs = self.scanner.get_trusted_macs()
                # [فك خناق التقارير الكاملة]: السكربت الآن يطبع كاااافة الماكات والتحذيرات للأثير دون بتر لطلبك
                self.scanner.sync_history(current_aps, ap_name, selected_band, trusted_macs)
                UIBase.return_prompt()
