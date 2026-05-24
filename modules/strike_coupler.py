#!/usr/bin/env python3
import time

class StrikeCoupler:
    @staticmethod
    def get_dynamic_port(band_mode, ap_id):
        base = 666 if band_mode == "2G" else 777
        return base + int(ap_id)

    @staticmethod
    def start_heartbeat_pulse(ssh_commander, mon_iface, is_running_flag):
        _, air_pid, _ = ssh_commander.execute_pure_cmd(f"pgrep -f 'airserv-ng -d {mon_iface}'")
        pid = air_pid.strip()
        if not pid: return False, "N/A"
        return True, pid
