#!/usr/bin/env python3
import json

class IntelUbusScout:
    @staticmethod
    def query_interfaces(ssh_commander, target_band):
        """[النواة الموحدة]: استجواب الواجهات عتادياً بناءً على التردد الفيزيائي الصافي"""
        _, stdout, _ = ssh_commander.execute_pure_cmd("ubus call network.wireless status")
        if not stdout.strip(): return {}, []

        try: raw_data = json.loads(stdout)
        except Exception: return {}, []

        filtered, down_ifaces = {}, []
        for radio, r_data in raw_data.items():
            band_attr = str(r_data.get("config", {}).get("band", "2g")).lower().strip()
            if target_band.lower() != band_attr: continue

            current_ch = str(r_data.get("config", {}).get("channel", "1"))
            if "interfaces" in r_data:
                for iface in r_data["interfaces"]:
                    ifname = iface.get("ifname")
                    if not ifname: continue
                    
                    config = iface.get("config", {})
                    ssid = config.get("ssid", ifname)
                    service = "monitor" if config.get("mode") == "monitor" else f"hostapd.{ifname}"
                    filtered[ifname] = {"ssid": ssid, "channel": current_ch, "service": service}
        return filtered, down_ifaces

    @staticmethod
    def scout_2g(ssh_commander): return IntelUbusScout.query_interfaces(ssh_commander, "2G")
    @staticmethod
    def scout_5g(ssh_commander): return IntelUbusScout.query_interfaces(ssh_commander, "5G")

    @staticmethod
    def get_live_clients(ssh_commander, service_name):
        if service_name == "monitor": return []
        _, stdout, _ = ssh_commander.execute_pure_cmd(f"ubus call {service_name} get_clients 2>/dev/null")
        if not stdout.strip(): return []
        try:
            raw_data = json.loads(stdout).get("clients", {})
            return [{"mac": m, "signal": f"{c.get('signal')} dBm", "rate": f"{c.get('rate',{}).get('tx',0)/1000000:.1f} Mbps"} for m, c in raw_data.items()]
        except Exception: return []
