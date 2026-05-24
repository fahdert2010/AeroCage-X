#!/usr/bin/env python3
import sys
from core.ui_base import C_CYAN, G_OK, R_ERR, Y_WARN, D_DIV, RESET

class StrikePanelUI:
    @staticmethod
    def render(target_ap, channel, band, active_strikes, protected_logs):
        """رسم لوحة حرب الترددات والفرز المرقم للأهداف حياً لطلبك"""
        sys.stdout.write("\033[H\033[2J\033[H")
        print(f"🧪 {C_CYAN}[ AeroCage-X : محرك الضربات الموجهة والمواجهات التفاعلية المرقمة ]{RESET}")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"📡 الأكسس: [{target_ap}] | 📶 القناة المفرزة: [{channel}] | 🌐 النطاق: [{band}]")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        
        print(f"{G_OK}[ الهجمات الحية النشطة وقذف الحزم التتابعي الموقوت ]{RESET}")
        print(f" {'رقم':<4} | {'ماك الهدف (Client MAC)':<18} | {'الـ PID بكالي':<14} | {'الحالة العتادية للضربة'}")
        print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
        for num, s in active_strikes.items():
            print(f" [{num:<2}] | {s['client']:<18} | {s['pid']:<14} | {s['status']}")
            
        print(f"\n{Y_WARN}[ 🛡️ شبكات وأجهزة محمية عملياتياً - النيران الصديقة ]{RESET}")
        print(f" {'ماك الجهاز المحمي':<18} | {'اسم الشبكة المحجوبة (SSID)':<25} | {'سبب الحظر العتادي'}")
        print(f"{D_DIV} ─────────────────────────────────────────────────────────────────────────{RESET}")
        for log in protected_logs[-3:]:
            print(f" {log['mac']:<18} | {log['ssid']:<25} | {log['reason']}")
            
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print("💡 [دليل التحكم الحركي] ➡️ لإيقاف هجمة فردية، اكتب [رقم السطر] واضغط Enter.")
        print("                        ➡️ للإنهاء الجماعي والكامل، اكتب [all] واضغط Enter.")
        print("                        ➡️ للتراجع والعودة، اكتب [0] واضغط Enter.")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        sys.stdout.write("🔢 الإدخال العملياتي الحالي: ")
        sys.stdout.flush()
