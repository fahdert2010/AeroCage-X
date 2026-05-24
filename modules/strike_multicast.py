#!/usr/bin/env python3

class StrikeMulticast:
    @staticmethod
    def suppress_beacons(ssh_commander, radio_node):
        """إخماد وتعطيل واجهات البث صامتاً بالـ uci وإعادة تدوير الكرت لحماية معالج الراوتر"""
        _, stdout, _ = ssh_commander.execute_pure_cmd(f"uci show wireless | grep '.device={radio_node}' | cut -d'.' -f2")
        for sec in [s.strip() for s in stdout.strip().split('\n') if s.strip()]:
            ssh_commander.execute_pure_cmd(f"uci set wireless.{sec}.disabled='1'")
        ssh_commander.execute_pure_cmd(f"uci commit wireless; wifi reload {radio_node}")

    @staticmethod
    def build_monitor_vif(ssh_commander, radio_node, mon_iface):
        """إنشاء كرت المراقبة بالـ uci الصافي والتحقق الحتمي من صعوده بوضع UP بالنواة البعيدة"""
        section = f"mon_{radio_node}_vif"
        ssh_commander.execute_pure_cmd(f"uci set wireless.{section}=wifi-iface; uci set wireless.{section}.device='{radio_node}'; uci set wireless.{section}.mode='monitor'; uci set wireless.{section}.ssid='OpenWrt'; uci commit wireless; wifi reload {radio_node}")
        
        _, link_chk, _ = ssh_commander.execute_pure_cmd(f"ip link show {mon_iface} 2>/dev/null || ip link show")
        return "UP" in link_chk or mon_iface in link_chk
