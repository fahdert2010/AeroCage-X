#!/usr/bin/env python3
import subprocess
import os

class StrikeCleanup:
    @staticmethod
    def restore_and_purge(comm, radio_node, orig_chan, mon_iface, active_strikes, suppressed_sections):
        """[تطهير محصور]: إنهاء عمليات كالي الحالية حصرًا، وتصفير قيود الـ uci التي لمسناها نحن فقط عملياتياً لطلبك"""
        print(f"\n[*] بدء التطهير والارتجاع الجراحي المحصور بجلسة هذا الهجوم فقط...")
        
        # 1. تنظيف كالي محلياً لجلسة هذا الهجوم بالـ PIDs دون لمس بقية الأنفاق
        for num, s in active_strikes.items():
            pid = s.get("pid", "N/A")
            if pid and pid != "N/A": subprocess.run(f"kill -9 {pid} 2>/dev/null", shell=True)
                
        subprocess.run(f"pkill -f 'airodump-ng --channel .* {comm.ip}:'", shell=True)
        sh_p = "/home/kali/AeroCage-X/storage/active_strikes.sh"
        if os.path.exists(sh_p):
            try: os.remove(sh_p)
            except Exception: pass

        # 2. ارتجاع الـ UCI للراوتر البعيد وإلغاء الـ disabled للسكاشن الملموسة لطلبك
        for sec in suppressed_sections:
            comm.execute_pure_cmd(f"uci del wireless.{sec}.disabled 2>/dev/null")
            
        section_mon = f"mon_{radio_node}_vif"
        comm.execute_pure_cmd(f"uci del wireless.{section_mon} 2>/dev/null")
        comm.execute_pure_cmd("uci commit wireless")
        
        # [سحق الـ AttributeError]: استدعاء الاسم الحقيقي الصافي للدالة المحدثة بالنواة
        from modules.strike_anchor import StrikeAnchor
        StrikeAnchor.restore_original_channel(comm, radio_node, orig_chan)
        print("🟢 تم تطهير الراوتر البعيد وكالي بنجاح، وعادت شبكات هوت سبوت فهد للعمل حياً بالكامل.")
        return True
