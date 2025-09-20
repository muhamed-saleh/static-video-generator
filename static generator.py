import os
import subprocess
import shutil

# --- C O N F I G U R A T I O N ---
IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp']
AUDIO_EXTS = ['.mp3', '.m4a', '.wav', '.ogg', '.flac']
ROOT_DEST_FOLDER = "batch-processed"
FFMPEG_PATH = "ffmpeg"
# -----------------------------------

def create_videos_smart():
    """
    Finds matching image/audio pairs, ignoring whitespace in names, and processes them.
    """
    
    print(f"[+] Creating root destination folder if needed: {ROOT_DEST_FOLDER}")
    os.makedirs(ROOT_DEST_FOLDER, exist_ok=True)

    print("[+] Scanning all folders for media files...")
    files_by_sanitized_name = {}
    
    # Walk through the current directory and all subdirectories
    for root, dirs, files in os.walk('.'):
        if ROOT_DEST_FOLDER in root:
            continue
            
        for filename in files:
            basename, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            if ext in IMAGE_EXTS or ext in AUDIO_EXTS:
                # --- NEW: Create a sanitized name by removing spaces and making it lowercase ---
                sanitized_name = basename.replace(" ", "").lower()
                
                if sanitized_name not in files_by_sanitized_name:
                    files_by_sanitized_name[sanitized_name] = {}
                
                full_path = os.path.join(root, filename)
                
                # Store both the original path and original basename
                if ext in IMAGE_EXTS:
                    files_by_sanitized_name[sanitized_name]['image'] = (full_path, basename)
                elif ext in AUDIO_EXTS:
                    files_by_sanitized_name[sanitized_name]['audio'] = (full_path, basename)

    print(f"[+] Found {len(files_by_sanitized_name)} potential groups. Now checking for complete pairs...")

    # --- Process all the pairs that have both an image and an audio file ---
    for sanitized_name, data in files_by_sanitized_name.items():
        if 'image' in data and 'audio' in data:
            image_path, image_basename = data['image'] # Unpack the tuple
            audio_path, audio_basename = data['audio'] # Unpack the tuple
            
            # --- Extract Reciter Name from the original image name ---
            words = image_basename.split()
            if not words:
                print(f"[!] Skipping group with empty name: {sanitized_name}")
                continue
            reciter_name = words[-1]
            
            reciter_folder_path = os.path.join(ROOT_DEST_FOLDER, reciter_name)
            os.makedirs(reciter_folder_path, exist_ok=True)
            
            # --- Use the original image basename for the output file ---
            output_filename = f"{image_basename}.mp4"
            output_path = os.path.join(os.path.dirname(image_path), output_filename)

            print("==========================================================")
            print(f"[v] Found Match for: {image_basename}")
            print(f"    > Deduced Reciter: {reciter_name}")
            print(f"[+] Creating video: {output_filename}...")
            
            command = [
                FFMPEG_PATH, '-y',
                '-loop', '1', '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264', '-r', '1',
                '-c:a', 'aac',
                '-shortest', output_path
            ]
            
            try:
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"[+] Moving files to folder: {reciter_folder_path}")
                shutil.move(image_path, reciter_folder_path)
                shutil.move(audio_path, reciter_folder_path)
                shutil.move(output_path, reciter_folder_path)
                print("[v] Done and organized!")

            except subprocess.CalledProcessError:
                print(f"[!!!] ERROR: FFmpeg failed for {image_basename}.")
            except Exception as e:
                print(f"[!!!] An unexpected error occurred: {e}")

    print("==========================================================")
    print("All matching pairs have been processed.")

if __name__ == "__main__":
    create_videos_smart()