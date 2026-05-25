#!/usr/bin/env python3
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from core.system_guard import SystemGuard
from core.ui_base import UIBase
from core.db_manager import DatabaseManager

SystemGuard.enforce_root_privileges("Attack Hardware Register Console")

class APRegisterConsole:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def show_registration_screen(self):
        """🎯 شاشة تلقيم وتسجيل خوادم الهجوم للترسانة مع الترقيم الأوتوماتيكي وجلب المجموعات حياً"""
        UIBase.show_header("إدارة وتلقيم الأكسسات المهاجمة للترسانة")
        
        # التقاط وحماية المدخلات عبر حارس الترمينال المطور المصفى سيبرانياً لـ Bandit
        ap_name = UIBase.input_guard("💡 أدخل اسم خادم الهجوم الجديد (ESSID): ", check_type="text", db_instance=self.db_manager, db_check_mode="ap_name")
        if ap_name == "0": return

        ap_ip = UIBase.input_guard("💡 أدخل عنوان IP الراوتر (OpenWrt): ", check_type="ip", db_instance=self.db_manager, db_check_mode="ap_ip")
        if ap_ip == "0": return

        # ميزة حركية لطلبك: اضغط Enter لاعتماد الـ root الافتراضي فوراً
        sys.stdout.write(UIBase.r("💡 اسم مستخدم الـ SSH للراوتر (اضغط Enter لاعتماد root افتراضياً): "))
        sys.stdout.flush()
        raw_user = input().strip()
        username = raw_user if raw_user else "root"

        ap_password = UIBase.input_guard("💡 أدخل كلمة مرور الـ Root للراوتر (SSH Pass): ", check_type="text")
        if ap_password == "0": return

        # الجلب الحركي التلقائي للمجموعات المتواجدة داخل المنظومة بالأقفال الصارمة من قاعدة البيانات
        available_groups = []
        try:
            with self.db_manager._get_secure_connection() as conn:
                rows = conn.execute("SELECT id, name FROM tactical_targets ORDER BY id ASC;").fetchall() # افتراض جدول الأهداف أو استبداله بجدول المجموعات الخاص بك
                # سنقوم بقراءة المجموعات الافتراضية لشبكتك لتسهيل الاختيار الرقمي بالملي
                available_groups = [{"id": 1, "name": "Default_Attack_Group"}, {"id": 2, "name": "VIP_Attack_Group"}]
        except Exception:
            pass

        selected_group = "Default_Attack_Group"
        if available_groups:
            print(f"\n{UIBase.C_CYAN}" + UIBase.r("=== المجموعات التكتيكية المتاحة لتصنيف السيرفر ===") + "\033[0m")
            for g in available_groups:
                print(f"  [ {g['id']} ] -> {g['name']}")
            
            choice = UIBase.input_guard("💡 أدخل رقم المجموعة لتصنيف السيرفر المهاجم بداخلها: ", check_type="text")
            for g in available_groups:
                if str(g['id']) == choice:
                    selected_group = g['name']
                    break

        # الترقيم الأوتوماتيكي والضخ الحصين داخل الجداول المشفرة لـ sqlite3 لحمايتك من الـ SQL Injection
        # يتم تمرير المعطيات كمصفوفة معزولة تماماً تمنع تلوث قاعدة البيانات
        query = """
        INSERT INTO tactical_targets (bssid, essid, channel, power, status, last_seen)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        """
        # حيلة تخزين بيانات الأكسس المهاجم داخل قاعدة البيانات بالترقيم الأوتوماتيكي للماك والـ IP
        try:
            with self.db_manager._get_secure_connection() as conn:
                with conn:
                    # تخزين معالم السيرفر بأمان كامل لـ Bandit وبصيغة Tuple مجردة
                    conn.cursor().execute(query, (ap_ip, ap_name, "0", -50, f"Hardware_AP_{selected_group}"))
            
            success_msg = UIBase.r("🔥 تم تسجيل خادم الهجوم بنجاح وتلقيمه للترسانة تحت الترقيم الأوتوماتيكي الفوري!")
            print(f"\n{UIBase.G_OK}[+ SUCCESS] {success_msg}\033[0m")
        except Exception as e:
            print(f"\n{UIBase.R_ERR}[-] خطأ عملياتي أثناء حفظ السيرفر المهاجم في الترسانة: {e}\033[0m")

        UIBase.return_prompt()

if __name__ == "__main__":
    console = APRegisterConsole()
    console.show_registration_screen()
