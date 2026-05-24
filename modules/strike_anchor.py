#!/usr/bin/env python3
import json

class StrikeAnchor:
    @staticmethod
    def detect_radio_and_bssid(ssh_commander, selected_band, iface_name):
        """[ملف 1]: قنص اسم الراديو والـ BSSID الحقيقي للكرت حياً من الـ ubus لمنع الخرف"""
        _, uci_b0, _ = ssh_commander.execute_pure_cmd("uci get wireless.radio0.band 2>/dev/null")
        radio_node = "radio0" if selected_band.lower() in str(uci_b0).lower() else "radio1"
        
        _, h_out, _ = ssh_commander.execute_pure_cmd(f"ubus call hostapd.{iface_name} get_config 2>/dev/null")
        try: bssid = json.loads(h_out).get("bssid", "00:00:00:00:00:00").upper()
        except Exception: bssid = "00:00:00:00:00:00"
        return radio_node, bssid

    @staticmethod
    def backup_original_channel(ssh_commander, radio_node):
        """قفل وحفظ القناة الأصلية للـ AP قبل الصعق"""
        _, stdout, _ = ssh_commander.execute_pure_cmd(f"uci get wireless.{radio_node}.channel 2>/dev/null")
        return stdout.strip() if stdout.strip().isdigit() else "1"

    @staticmethod
    def restore_original_channel(ssh_commander, radio_node, original_channel):
        """إعادة المذبذب العتادي لوضعه الطبيعي وعمل ريلود مخصص للراديو"""
        ssh_commander.execute_pure_cmd(f"uci set wireless.{radio_node}.channel='{original_channel}'; uci commit wireless; wifi reload {radio_node}")
        return True
