#!/usr/bin/env python3

class StrikeMonitor:
    @staticmethod
    def build_and_check_link(ssh_commander, radio_node, mon_iface):
        """إنشاء كرت المراقبة الـ هاردوير بالـ uci الصافي والتحقق من صعوده بالنواة البعيدة"""
        section = f"mon_{radio_node}_vif"
        ssh_commander.execute_pure_cmd(f"uci set wireless.{section}=wifi-iface")
        ssh_commander.execute_pure_cmd(f"uci set wireless.{section}.device='{radio_node}'")
        ssh_commander.execute_pure_cmd(f"uci set wireless.{section}.mode='monitor'")
        ssh_commander.execute_pure_cmd(f"uci set wireless.{section}.ssid='OpenWrt'")
        ssh_commander.execute_pure_cmd(f"uci commit wireless; wifi reload {radio_node}")
        
        _, link_chk, _ = ssh_commander.execute_pure_cmd(f"ip link show {mon_iface} 2>/dev/null || ip link show")
        if "UP" in link_chk or mon_iface in link_chk:
            return True, f"🟢 تم بناء كرت المراقبة بالـ uci وصعود الواجهة بنجاح عملياتي."
        return False, f"❌ فشل صعود الكرت عتادياً بالنواة! تحقق من معمارية شريحة الراديو."
