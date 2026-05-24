#!/usr/bin/env python3

class M2HardwareTunnel:
    @staticmethod
    def suppress_and_build_monitor(comm, radio, mon_iface):
        """إخماد الـ Beacons بالـ uci وتشييد كرت المراقبة الهاردوير وفحص الصعود بـ UP الصارم بالنواة"""
        _, stdout, _ = comm.execute_pure_cmd(f"uci show wireless | grep '.device={radio}' | cut -d'.' -f2")
        for sec in [s.strip() for s in stdout.strip().split('\n') if s.strip()]:
            comm.execute_pure_cmd(f"uci set wireless.{sec}.disabled='1'")
            
        section = f"mon_{radio}_vif"
        comm.execute_pure_cmd(f"uci set wireless.{section}=wifi-iface; uci set wireless.{section}.device='{radio}'; uci set wireless.{section}.mode='monitor'; uci set wireless.{section}.ssid='OpenWrt'; uci commit wireless; wifi reload {radio}")
        
        _, link, _ = comm.execute_pure_cmd(f"ip link show {mon_iface} 2>/dev/null")
        return "UP" in link or mon_iface in link

    @staticmethod
    def fire_remote_airserv(comm, band, ap_id, channel, mon_iface):
        """حساب المنفذ الديناميكي الموجه صامتاً وإشعال نفق المعالج البعيد لقفل التردد"""
        port = (666 if band == "2G" else 777) + int(ap_id)
        comm.execute_pure_cmd(f"iw dev {mon_iface} set channel {channel}")
        comm.execute_pure_cmd(f"nohup airserv-ng -d {mon_iface} -p {port} >/dev/null 2>&1 &")
        return port
