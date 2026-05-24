#!/usr/bin/env python3
import json
from core.intel_ubus_scout import IntelUbusScout

class M1HostScout:
    @staticmethod
    def get_radio_and_bssids(comm, band, ifaces):
        """قنص راديو النطاق والماكات الفيزيائية الحقيقية حياً من الـ ubus لمنع الخرف والتوائم الخبيثة"""
        _, uci_b0, _ = comm.execute_pure_cmd("uci get wireless.radio0.band 2>/dev/null")
        radio = "radio0" if band.lower() in str(uci_b0).lower() else "radio1"
        
        for name in ifaces.keys():
            _, h_out, _ = comm.execute_pure_cmd(f"ubus call hostapd.{name} get_config 2>/dev/null")
            try: ifaces[name]['bssid'] = json.loads(h_out).get("bssid", "00:00:00:00:00:00").upper()
            except Exception: ifaces[name]['bssid'] = "00:00:00:00:00:00"
        return radio, ifaces

    @staticmethod
    def print_live_clients(comm, ifaces):
        """طباعة كروت البث المتاحة وقضم متصلي الـ hostapd بالماك والإشارة والسرعات حياً"""
        total = 0
        for name, data in ifaces.items():
            print(f"  📡 الواجهة: {name:<10} | 📶 BSSID الحقيقي: {data.get('bssid','N/A')} | 🌐 SSID: {data['ssid']}")
            clients = IntelUbusScout.get_live_clients(comm, data['service'])
            if clients:
                total += len(clients)
                for c in clients: print(f"      📱 MAC: {c['mac']} | 📶 الإشارة: {c['signal']:<8} | 🚀 السرعة: {c['rate']}")
            else: print("      └── 💤 عامل الاستقرار: لا توجد أجهزة متصلة حالياً.")
        return total
