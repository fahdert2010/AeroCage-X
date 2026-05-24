#!/usr/bin/env python3
import sys
import re

C_CYAN = "\033[38;5;111m"; G_OK = "\033[38;5;150m"; R_ERR = "\033[38;5;167m"
Y_WARN = "\033[38;5;221m"; D_DIV = "\033[38;5;242m"; W_TEXT = "\033[38;5;253m"; RESET = "\033[0m"

class UIBase:
    @staticmethod
    def clear_screen():
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()

    @staticmethod
    def show_header(title):
        UIBase.clear_screen()
        print(f"{C_CYAN}🧪 AeroCage-X : {title}{RESET}")
        print(f"{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    @staticmethod
    def return_prompt():
        print(f"\n{D_DIV}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        input(f"💡 {W_TEXT}اضغط [Enter] للعودة...{RESET}")

    @staticmethod
    def is_valid_ip(ip_str):
        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        return bool(re.match(pattern, ip_str)) and all(0 <= int(p) <= 255 for p in ip_str.split('.'))

    @staticmethod
    def input_guard(prompt_text, check_type="text", db_instance=None, db_check_mode=None):
        """[حارس الإدخال المطور]: التقاط البيانات حياً، وقبول 0 للتراجع، وطباعة الخطأ في نفس السطر"""
        while True:
            sys.stdout.write(f"{prompt_text}")
            sys.stdout.flush()
            user_input = input().strip()
            
            # منح خيار التراجع الصريح للمستخدم عملياتياً لمنع التجميد لطلبك
            if user_input in ["0", "exit"]:
                return "0"

            clean_val = re.sub(r'[;&|`$]', '', user_input).strip()
            if not clean_val:
                sys.stdout.write(f"\033[A\r{R_ERR}❌ خطأ: الحقل فارغ!{RESET} " + " " * 30 + "\n")
                continue
                
            if check_type == "ip" and not UIBase.is_valid_ip(clean_val):
                sys.stdout.write(f"\033[A\r{R_ERR}❌ خطأ: صيغة عنوان الـ IP مشوهة!{RESET} " + " " * 30 + "\n")
                continue

            if db_instance and db_check_mode:
                with db_instance._get_connection() as conn:
                    if db_check_mode == "group" and conn.execute("SELECT 1 FROM groups WHERE name=?;", (clean_val,)).fetchone():
                        sys.stdout.write(f"\033[A\r{R_ERR}❌ خطأ: اسم المجموعة مكرر بالمنظومة!{RESET}\n")
                        continue
                    elif db_check_mode == "ap_name" and conn.execute("SELECT 1 FROM access_points WHERE name=?;", (clean_val,)).fetchone():
                        sys.stdout.write(f"\033[A\r{R_ERR}❌ خطأ: اسم الأكسس مكرر ومسجل مسبقاً!{RESET}\n")
                        continue
                    elif db_check_mode == "ap_ip" and conn.execute("SELECT 1 FROM access_points WHERE ip=?;", (clean_val,)).fetchone():
                        sys.stdout.write(f"\033[A\r{R_ERR}❌ خطأ: عنوان الـ IP مكرر عملياتياً!{RESET}\n")
                        continue
            return clean_val
