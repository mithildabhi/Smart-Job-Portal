import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_PATH = os.path.join(BASE_DIR, "media", "applications")

OLD_PATH = os.path.join(MEDIA_PATH, "resumes \\2025")   # wrong folder
CORRECT_BASE = os.path.join(MEDIA_PATH, "resumes", "2025")

def ensure_path(path):
    """Create folder if not exists."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created: {path}")

def move_files(src, dst):
    """Move all files from src folder to dst folder."""
    if not os.path.exists(src):
        return

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)

        if os.path.isfile(s):
            shutil.move(s, d)
            print(f"Moved file: {s} → {d}")
        elif os.path.isdir(s):
            new_dst = os.path.join(dst, item)
            ensure_path(new_dst)
            move_files(s, new_dst)

def fix_media():
    print("🔧 Fixing Django media folder structure...")

    # Create correct folders
    ensure_path(CORRECT_BASE)

    # Identify wrong folder
    if os.path.exists(OLD_PATH):
        print(f"Found broken folder: {OLD_PATH}")

        # Move its contents into correct folder
        move_files(OLD_PATH, CORRECT_BASE)

        # Remove wrong folder
        shutil.rmtree(OLD_PATH)
        print(f"❌ Removed incorrect folder: {OLD_PATH}")

    else:
        print("No incorrect folder found.")

    print("\n✅ Folder structure fixed successfully!")

if __name__ == "__main__":
    fix_media()
