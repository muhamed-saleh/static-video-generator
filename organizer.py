import os
import shutil

# --- C O N F I G U R A T I O N ---
# اسم المجلد الرئيسي الذي يحتوي على الملفات غير المنظمة
PROCESSED_FOLDER = "batch-processed"
# -----------------------------------

def organize_files():
    """
    Scans the PROCESSED_FOLDER, finds all related files (image, audio, video),
    and moves them into subfolders named after the reciter.
    """
    
    # التأكد من أن المجلد الرئيسي موجود
    if not os.path.isdir(PROCESSED_FOLDER):
        print(f"[!] Error: The folder '{PROCESSED_FOLDER}' was not found.")
        print("    Please make sure this script is in the parent 'batch' folder.")
        return

    print(f"[+] Starting to organize the '{PROCESSED_FOLDER}' folder...")

    # الخطوة الأولى: تجميع كل الملفات حسب اسمها الأساسي
    files_by_basename = {}
    
    # os.listdir() يقرأ فقط الملفات والمجلدات في المستوى الأول من المجلد المحدد
    for filename in os.listdir(PROCESSED_FOLDER):
        full_path = os.path.join(PROCESSED_FOLDER, filename)
        
        # نتأكد من أننا نتعامل مع ملف وليس مجلد فرعي
        if os.path.isfile(full_path):
            # نفصل الاسم عن الامتداد
            basename, ext = os.path.splitext(filename)
            
            # نقوم بإنشاء قائمة لكل اسم أساسي إذا لم تكن موجودة
            if basename not in files_by_basename:
                files_by_basename[basename] = []
            
            # نضيف المسار الكامل للملف إلى القائمة الخاصة به
            files_by_basename[basename].append(full_path)

    print(f"[+] Found {len(files_by_basename)} groups of files to organize.")

    # الخطوة الثانية: المرور على المجموعات، استخلاص اسم القارئ، وإنشاء المجلدات ثم النقل
    for basename, file_paths in files_by_basename.items():
        # استخلاص اسم القارئ (الكلمة الأخيرة من الاسم الأساسي)
        words = basename.split()
        if not words:
            print(f"[!] Skipping group with empty name.")
            continue
        reciter_name = words[-1]
        
        # تحديد مسار المجلد الفرعي الخاص بالقارئ
        reciter_folder_path = os.path.join(PROCESSED_FOLDER, reciter_name)
        
        # إنشاء المجلد إذا لم يكن موجوداً
        os.makedirs(reciter_folder_path, exist_ok=True)

        print("==========================================================")
        print(f"[v] Organizing set for: {basename}")
        print(f"    > Moving to folder: {reciter_folder_path}")

        # نقل كل الملفات في المجموعة إلى المجلد الجديد
        try:
            for old_path in file_paths:
                # نحصل على اسم الملف فقط لنقوم ببناء المسار الجديد بشكل صحيح
                filename_only = os.path.basename(old_path)
                new_path = os.path.join(reciter_folder_path, filename_only)
                shutil.move(old_path, new_path)
            print("[v] Set moved successfully!")
        except Exception as e:
            print(f"[!!!] An error occurred while moving files for {basename}: {e}")

    print("==========================================================")
    print("Organization complete.")

# لتشغيل السكريبت
if __name__ == "__main__":
    organize_files()