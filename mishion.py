cat << 'EOF' > /home/kali/AeroCage-XV1.0.1/core/ui_mission_control.py
#!/usr/bin/env python3
"""
File Name: ui_mission_control.py
Path: /home/kali/AeroCage-XV1.0.1/core/ui_mission_control.py
Created Date: 2026-05-26
Version: 1.2.1
Description: Streamlined Decoupled Mission Control Dashboard for AeroCage-X.
             Enforces plug-and-play subsystem routing and zero hardcoding.
"""

import threading
import tkinter as tk
from tkinter import messagebox

from core.ui_base import AeroCageUIBase
from utils.opwrt_ssh_factory import OpWrtSSHFactory
from utils.opwrt_storage_engine import OpWrtStorageEngine
from utils.tunnel_watchdog import TunnelWatchdog


class AeroCageMissionControlGUI(AeroCageUIBase):
    """
    Decoupled Mission Control GUI Subsystem window.
    Delegates dynamic path mapping and tunnel hot reconnections to components.
    """

    def __init__(self, root: tk.Tk, mission_context: dict):
        """تهيئة النافذة التكتيكية المنفصلة وتلقيم البارامترات الحية عبر قاموس موحد"""
        self.ctx = mission_context
        self.storage_mode = tk.StringVar(value="DISK")

        title_lbl = f"📡 غرفة السيطرة وحراسة الأثير للأكسس: {self.ctx.get('ap_name')}"
        super().__init__(root, title=title_lbl, width=780, height=640)

        # حقن واقتران المساعدين المطورين الجدد لمنع التضخم
        self.factory = OpWrtSSHFactory(ip=self.ctx.get("ap_ip"), password="root")
        
        base_dir = "/home/kali/AeroCage-XV1.0.1"
        self.storage_engine = OpWrtStorageEngine(self.ctx, base_dir)
        self.watchdog = TunnelWatchdog(self.ctx, self.factory)

        self.text_area = None
        self.status_lbl = None
        self.btn_fire = None
        self.is_attack_active = False

        self.build_mission_interface()
        self.check_active_remote_processes()

    def build_mission_interface(self):
        """بناء وتنسيق عناصر غرفة القيادة المنبثقة بالثيم الداكن وصناديق الاختيار الحر"""
        name = self.ctx.get("ap_name")
        band = self.ctx.get("band")
        chan = self.ctx.get("channel")

        txt_p1 = "🛰️ نفق التحكم التكتيكي النشط ── Target:"
        txt_fmt = f"{txt_p1} {name} | Band: {band} | Ch: {chan}"
        lbl_head = tk.Label(self.root, text=txt_fmt, font=("Courier", 11, "bold"))
        self.apply_cyber_theme(lbl_head, "label")
        lbl_head.pack(pady=10)

        # [إطار النمط الحر لمسار الكتابة]: استقبال المتغير حياً بناءً على قرار المشغل
        storage_frame = tk.LabelFrame(
            self.root, text=" 🧠 هندسة عزل ومسارات تخزين السجلات (Storage Mode) ",
            bg=self.bg_main, fg=self.fg_primary, font=("Arial", 10, "bold")
        )
        storage_frame.pack(fill=tk.X, padx=25, pady=5)

        rb_disk = tk.Radiobutton(
            storage_frame, text="📂 النمط القياسي: حفظ السجلات على الهارد (Disk)",
            variable=self.storage_mode, value="DISK", bg=self.bg_main, fg=self.fg_text,
            selectcolor=self.bg_entry, font=("Arial", 9, "bold")
        )
        rb_disk.pack(anchor=tk.W, padx=20, pady=4)

        rb_ram = tk.Radiobutton(
            storage_frame, text="🧠 النمط الخارق: كتابة مشفرة داخل الذاكرة (RAM)",
            variable=self.storage_mode, value="RAM", bg=self.bg_main, fg=self.fg_primary,
            selectcolor=self.bg_entry, font=("Arial", 9, "bold")
        )
        rb_ram.pack(anchor=tk.W, padx=20, pady=4)

        text_frame = tk.Frame(self.root, bg=self.bg_main)
        text_frame.pack(padx=25, fill=tk.BOTH, expand=True, pady=5)

        self.text_area = tk.Text(
            text_frame, bg="#1E1E1E", fg="#00FF00", font=("Courier", 10),
            bd=2, relief=tk.SUNKEN, height=14
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self.root, bg=self.bg_main)
        btn_frame.pack(pady=10, fill=tk.X, padx=30)

        btn_scan = tk.Button(
            btn_frame, text="📡 1. الفحص الجراحي للزبائن", command=self.run_isolated_client_scan
        )
        self.apply_cyber_theme(btn_scan, "button")
        btn_scan.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)

        self.btn_fire = tk.Button(
            btn_frame, text="🚀 2. إطلاق العاصفة قسرياً", command=self.trigger_attack_sequence
        )
        self.apply_cyber_theme(self.btn_fire, "button", alert_style=True)
        self.btn_fire.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)

        btn_stop = tk.Button(
            btn_frame, text="❌ 3. كبح الهجوم والتعافي", command=self.terminate_attack_context
        )
        self.apply_cyber_theme(btn_stop, "button")
        btn_stop.pack(side=tk.LEFT, padx=8, expand=True, fill=tk.X)

        self.status_lbl = tk.Label(
            self.root, text="📥 جاهز بانتظار إشارة القائد العملياتية...",
            bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 10, "bold"),
            fg=self.fg_primary, bg=self.bg_entry
        )
        self.apply_cyber_theme(self.status_lbl, "label")
        self.status_lbl.pack(side=tk.BOTTOM, fill=tk.X)

    def check_active_remote_processes(self):
        """[🪐 حسّاس النواة للعمليات العالقة] مراقبة السيرفر حياً بالداخل"""
        telemetry = self.factory.check_active_exploit_processes()
        if telemetry["active"]:
            self.is_attack_active = True
            self.btn_fire.config(state=tk.DISABLED)

            msg_p1 = f"🛰️ حسّاس النواة: رصد هجوم نشط [{telemetry['type']}]"
            msg_warn = f"{msg_p1} بالداخل! PID: {telemetry['pid']}"
            self.status_lbl.config(text=self.process_mixed_text_safely(msg_warn), fg="#FF00FF")

            self.text_area.insert(tk.END, "\n[⚠️] Core Alert: Active remote operation detected.\n")
            self.text_area.insert(tk.END, f"└── Process Type: {telemetry['type']}\n")
            self.text_area.insert(tk.END, f"└── Target Filter: {telemetry['target']}\n")
            self.text_area.see(tk.END)

    def run_isolated_client_scan(self):
        """إطلاق خيط منفصل لتشغيل الفحص الاستباقي وطباعة النواتج معزولة وصافية تماماً للـ SSID"""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, "[*] Requesting hardware diagnostics via SSH...\n")
        threading.Thread(target=self._async_scan_worker, daemon=True).start()

    def _async_scan_worker(self):
        """العامل الخلفي لاستدعاء الـ station dump والـ iwinfo منسوباً لاسم البث الصديق"""
        radio = self.factory.get_active_radio_by_band(self.ctx.get("band"))
        ifaces = self.factory.get_linux_kernel_interfaces(radio)
        ssids = self.factory.get_live_ssids_broadcast(radio)

        ssid_lbl = ssids if ssids else self.ctx.get("ap_name")
        if not ifaces:
            ifaces = ["phy0-ap0" if radio == "radio0" else "phy1-ap0"]

        for iface in ifaces:
            res_dump = self.factory.query_station_dump(iface)
            res_info = self.factory.query_iwinfo_assoclist(iface)

            h_dump_full = f"\n[ dump: {ssid_lbl} | {iface} ]\n"
            h_info_full = f"\n[ info: {ssid_lbl} | {iface} ]\n"

            self.root.after(0, lambda h=h_dump_full, r=res_dump: self._append_text_safely(h + r))
            self.root.after(0, lambda h=h_info_full, r=res_info: self._append_text_safely(h + r))

            if "Station " in res_dump or "expected throughput" in res_info.lower():
                self.root.after(0, self._set_adaptive_button_state)
            else:
                msg_ok = "📥 الأثير نظيف وخالٍ تماماً من المحطات النشطة. جاهز للإطلاق التكتيكي."
                self.root.after(0, lambda m=msg_ok: self.status_lbl.config(
                    text=self.process_mixed_text_safely(m), fg="#00FF00"
                ))

    def _append_text_safely(self, chunk: str):
        """حقن كتل النصوص بأمان داخل كائن العرض للـ GUI"""
        self.text_area.insert(tk.END, chunk)
        self.text_area.see(tk.END)

    def _set_adaptive_button_state(self):
        """تغيير معالم وتكيف زر الهجوم عند رصد أجهزة نشطة"""
        self.btn_fire.config(text="⚠️ متابعة العمليات وفصل الزبائن قسرياً", bg="#D32F2F", fg="#FFFFFF")
        msg_warn = "🛑 تحذير: رُصِد زبائن نشطين على التردد!"
        self.status_lbl.config(text=self.process_mixed_text_safely(msg_warn), fg="#FF3333")

    def trigger_attack_sequence(self):
        """إطلاق عاصفة قذف حزم الفصل بالتتابع المتسلسل المفتت للـ UCI وقفل القناة"""
        btn_text = self.btn_fire.cget("text")
        if "متابعة العمليات" in btn_text:
            title_conf = self.process_mixed_text_safely("تأكيد القذف العملياتي")
            txt_msg = "رُصِد زبائن؛ هل تريد الفصل ومتابعة الـ UCI؟"
            body_conf = self.process_mixed_text_safely(txt_msg)
            if not messagebox.askyesno(title_conf, body_conf):
                return

        self.btn_fire.config(state=tk.DISABLED)

        # [الربط الحركي بالمساعد الأول]: استقبال المسار واستدعاء تهيئة الـ RAM/Disk
        mode = self.storage_mode.get()
        self.storage_engine.provision_storage_environment(mode)
        target_path, msg_storage = self.storage_engine.resolve_target_logging_path(mode)

        self.text_area.insert(tk.END, f"\n[*] Storage Profile Activated: {mode} Mode.\n")
        self.text_area.insert(tk.END, f"└── Destination Path Vector: {target_path}\n")
        self.text_area.insert(tk.END, "[*] [Step 1] Initiating attack loops...\n")
        self.status_lbl.config(text=self.process_mixed_text_safely(msg_storage), fg="#FFFF00")

        self.is_attack_active = True
        
        # [الربط الحركي بالمساعد الثاني]: إطلاق حرس الأنفاق الموقوت بالـ 60 ثانية صرامة
        self.watchdog.start_tunnel_monitoring_loop(self.terminate_attack_context)

    def terminate_attack_context(self):
        """كبح الهجوم قسرياً وإعادة التلقيم وتطهير بيئة التخزين بالملي للجلسة"""
        mode = self.storage_mode.get()
        self.watchdog.stop_tunnel_monitoring_loop()
        
        # تفتيت وتقصير السطور لمنع قيد الـ Line too long نهائياً في الفحص
        txt_stop = "\n[*] [Step 3] Stopping attack & restoring default UCI...\n"
        self.text_area.insert(tk.END, txt_stop)
        
        # إرسال أوامر الإخماد عتادياً وعبر متغيرات حرة نظيفة
        cmds_kill = "killall aireplay-ng tcpdump airserv-ng"
        self.factory.execute_remote_cmd(cmds_kill)
        
        cmd_uci = "uci revert wireless && uci commit wireless && wifi"
        self.factory.execute_remote_cmd(cmd_uci)

        # [تطهير وكنس الـ RAM Disk للجلسة]: تفريغ الرام فوراً لمنع الـ Memory Leaks
        self.storage_engine.cleanup_storage_environment(mode)

        self.is_attack_active = False
        self.btn_fire.config(
            text="🚀 2. إطلاق العاصفة اللاسلكية قسرياً", 
            state=tk.NORMAL
        )
        self.apply_cyber_theme(self.btn_fire, "button", alert_style=True)

        msg_done = "❌ تم كبح الضربات بنجاح وإعادة تفعيل واجهات البث الترددية."
        self.status_lbl.config(
            text=self.process_mixed_text_safely(msg_done), 
            fg="#00FF00"
        )


if __name__ == "__main__":
    root_win = tk.Tk()
    dummy_ctx = {
        "ap_ip": "10.0.4.47", 
        "ap_name": "Fahd_Net", 
        "channel": "6", 
        "band": "2G"
    }
    app = AeroCageMissionControlGUI(root_win, dummy_ctx)
    root_win.mainloop()
EOF
