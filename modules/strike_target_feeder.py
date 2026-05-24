#!/usr/bin/env python3
from core.intel_ubus_scout import IntelUbusScout

class StrikeTargetFeeder:
    @staticmethod
    def extract_live_pool(ssh_commander, ifaces):
        """[ملف تكتيكي منفصل]: حصاد وتجميع ماكات الأجهزة المتصلة حياً بالراوتر البعيد عبر ubus"""
        pool = []
        for i_name, i_data in ifaces.items():
            # استدعاء دالة ubus الجلب الصافية للـ hostapd الموحدة
            clients = IntelUbusScout.get_live_clients(ssh_commander, i_data['service'])
            for c in clients:
                pool.append({
                    "mac": c["mac"],
                    "ssid": i_data['ssid'],
                    "bssid": "30:23:03:E8:C8:9D" # ماك الراوتر البعيد الموحد
                })
        return pool
