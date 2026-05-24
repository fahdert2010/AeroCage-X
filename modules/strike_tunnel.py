#!/usr/bin/env python3
import time

class StrikeTunnel:
    @staticmethod
    def suppress_and_build_monitor(comm, radio, mon_iface, target_channel):
        """[محتوى الهاردوير]: قفل القناة على الراديو بالـ uci قسرياً لمنع تعليق المذبذب والـ Resource busy لطلبك"""
        _, stdout, _ = comm.execute_pure_cmd(f"uci show wireless | grep '.device={radio}' | cut -d'.' -f2")
        for sec in [s.strip() for s in stdout.strip().split('\n') if s.strip()]:
            comm.execute_pure_cmd(f"uci set wireless.{sec}.disabled='1'")
            
        section = f"mon_{radio}_vif"
        # تثبيت القناة التكتيكية مباشرة بقلب الراديو بالـ uci لفك قفل الهاردوير المشغول
        comm.execute_pure_cmd(f"uci set wireless.{radio}.channel='{target_channel}'")
        comm.execute_pure_cmd(f"uci set wireless.{section}=wifi-iface; uci set wireless.{section}.device='{radio}'; uci set wireless.{section}.mode='monitor'; uci set wireless.{section}.ssid='OpenWrt'; uci commit wireless; wifi reload {radio}")
        time.sleep(2) # مهلة الاستقرار العتادي للريلود
        
        _, link, _ = comm.execute_pure_cmd(f"ip link show {mon_iface} 2>/dev/null")
        return "UP" in link or mon_iface in link

    @staticmethod
    def fire_remote_airserv(comm, band, ap_id, channel, mon_iface):
        """[مصنع الأنفاق الجديد]: شحن الترتيب العملياتي الصحيح والآمن للـ airserv-ng لطلبك من واقع تجاربك"""
        port = (666 if band == "2G" else 777) + int(ap_id)
        # السنتاكس الصخر والأصيل المستقر لإنهاء الـ bind Address in use
        cmd = f"nohup airserv-ng -c {channel} -d {mon_iface} -p {port} >/dev/null 2>&1 &"
        comm.execute_pure_cmd(cmd)
        return port
