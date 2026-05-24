#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.ui_base import UIBase, R_ERR, G_OK, D_DIV, RESET
from core.ssh_commander import SSHCommander
from core.intel_ubus_scout import IntelUbusScout

class UIScout:
    @staticmethod
    def run(db):
        UIBase.show_header("رادار فحص واستعلام الزبائن اللحظي عبر UBUS")
        aps = db.get_all_access_points()
        if not aps:
            print(f" ❌ {R_ERR}خطأ: لا يوجد أجهزة في قاعدة البيانات!{RESET}")
            UIBase.return_prompt(); return

        print(f" [ المتاح عتادياً بالمنظومة ]:")
        for idx, row in enumerate(aps): print(f"   [{idx+1}] {row[1]} ({row[2]})")
        
        idx = input("\n🔢 اختر رقم الأكسس بوينت للاستعلام: ").strip()
        if not idx.isdigit() or int(idx) > len(aps): return
        ap_id, ap_name, ap_ip, ap_user, ap_pass, g_name = aps[int(idx)-1]
        
        mode = input("🌐 اختر النطاق المستهدف [1: للـ 2G | 2: للـ 5G]: ").strip()
        selected_band = "5G" if mode == "2" else "2G"
        
        print(f"\n[*] جاري سحب مقابس UBUS للاكسس [{ap_name}] عبر العنوان [{ap_ip}]...")
        comm = SSHCommander(ip=ap_ip, password=ap_pass, username=ap_user)
        
        # [قفل مزامنة الأخطاء]: استدعاء اسم الدالة الموحدة المفتتة والمطهرة حيوياً عتادياً
        raw_ifaces, down_ifaces = IntelUbusScout.query_interfaces(comm, selected_band)
        if not raw_ifaces:
            print(f"❌ {R_ERR}لا توجد واجهات بث نشطة عتادياً بالراوتر حالياً لهذا التردد!{RESET}")
            UIBase.return_prompt(); return
            
        print(f"\n{G_OK}[ واجهات البث والـ Monitor النشطة للتردد {selected_band} ]:{RESET}")
        for i_name, i_data in raw_ifaces.items():
            print(f"  📡 الواجهة: {i_name:<10} | 📶 القناة الحالية: {i_data['channel']:<2} | 🌐 الـ SSID: {i_data['ssid']}")
            clients = IntelUbusScout.get_live_clients(comm, i_data['service'])
            if clients:
                print(f"      └── 📊 [ الأجهزة المتصلة حالياً بالبث: {len(clients)} ]")
                for c in clients: print(f"          📱 MAC: {c['mac']} | 📶 الإشارة: {c['signal']:<8} | 🚀 السرعة: {c['rate']}")
            else:
                print(f"      └── {D_DIV}عامل الاستقرار: لا توجد أجهزة متصلة بالبث حالياً في هذه الواجهة.{RESET}")
            print(f"  {D_DIV}───────────────────────────────────────────────────────────────────────{RESET}")
        UIBase.return_prompt()
