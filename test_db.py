# /home/kali/AeroCageX/test_db.py
from core.db_manager import DBManager

def run_isolated_db_test():
    print("🧪 [بدء الفحص المخبري المستقل للنواة وقاعدة البيانات] 🧪")
    db = DBManager()

    # 1. اختبار إضافة المجموعات والقيود
    print("\n[*] جاري اختبار حقن المجموعات الصامت...")
    status1, msg1 = db.add_group("المنطقة_الشمالية")
    print(msg1)
    
    # محاولة تكرار نفس الاسم عمداً لاستجواب الحارس البرمجي
    print("[*] جاري استجواب حارس القيود لاسم المجموعة المكرر...")
    status2, msg2 = db.add_group("المنطقة_الشمالية")
    print(f"استجابة النظام (متوقعة الحظر): {msg2}")

    # 2. جلب المجموعات والتأكد من الترقيم الديناميكي
    groups = db.get_all_groups()
    print(f"\n[+] المجموعات الحالية المستقرة بالذاكرة (العدد: {len(groups)}):")
    for display_num, internal_id, name in groups:
        print(f"  [{display_num}] - الاسم عتادياً: {name} (المعرف الحقيقي بالخلفية: {internal_id})")

    # 3. اختبار إضافة جهاز أكسس بوينت وربطه بالمجموعة الأولى
    if groups:
        target_group_id = groups[0][1] # جلب الـ internal_id للمجموعة الأولى
        print("\n[*] جاري اختبار حقن جهاز أكسس بوينت جديد...")
        status3, msg3 = db.add_access_point(
            name="KT412_Main_Gate", 
            ip="10.0.4.151", 
            password="secret_ssh_pass", 
            group_id=target_group_id
        )
        print(msg3)

        # محاولة تكرار نفس الآيبي عمداً للتأكد من سحق الأخطاء
        print("[*] جاري استجواب النظام بآيبي مكرر عمداً...")
        status4, msg4 = db.add_access_point(
            name="KT412_Backup_Gate", 
            ip="10.0.4.151", # نفس الآيبي
            password="another_pass", 
            group_id=target_group_id
        )
        print(f"استجابة النظام (متوقعة الحظر): {msg4}")

    # 4. جلب وعرض الأجهزة النشطة
    aps = db.get_all_access_points()
    print(f"\n[+] أجهزة الأكسس بوينت المسجلة حياً بالمنظومة (العدد: {len(aps)}):")
    for display_num, internal_id, name, ip, user, pwd, group_name in aps:
        print(f"  [{display_num}] - {name} | IP: {ip} | المالك: {user} | المجموعة: {group_name}")

    # 5. اختبار القفل الصارم عند محاولة حذف مجموعة ممتلئة بأعضاء
    if groups:
        print("\n[*] جاري استجواب حارس الحذف الصارم لمجموعة تحتوي على أعضاء...")
        status5, msg5 = db.delete_group(groups[0][1])
        print(f"استجابة نظام القفل العسكري: {msg5}")

if __name__ == "__main__":
    run_isolated_db_test()
