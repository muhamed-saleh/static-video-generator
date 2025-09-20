import os
import subprocess
import shutil

# --- C O N F I G U R A T I O N ---
# Add or remove file extensions you want the script to find.
IMAGE_EXTS = ['.jpg', '.jpeg', '.png', '.webp']
AUDIO_EXTS = ['.mp3', '.m4a', '.wav', '.ogg', '.flac']

# This is the main folder where all the organized subfolders will be created.
ROOT_DEST_FOLDER = "batch-processed"

# This assumes 'ffmpeg.exe' is in your system's PATH.
# If it's not, you can put the full path here, like: "C:\\ffmpeg\\bin\\ffmpeg.exe"
FFMPEG_PATH = "ffmpeg"
# -----------------------------------

def create_videos():
    """Finds matching image/audio pairs and processes them."""
    
    print(f"[+] Creating root destination folder if needed: {ROOT_DEST_FOLDER}")
    os.makedirs(ROOT_DEST_FOLDER, exist_ok=True)

    print("[+] Scanning all folders for media files...")
    files_by_basename = {}
    
    # Walk through the current directory and all subdirectories
    for root, dirs, files in os.walk('.'):
        # IMPORTANT: This prevents the script from re-processing already moved files
        if ROOT_DEST_FOLDER in root:
            continue
            
        for filename in files:
            # Split the filename into its name and extension
            basename, ext = os.path.splitext(filename)
            ext = ext.lower() # Make extension lowercase for consistent matching
            
            # Group files by their base name
            if ext in IMAGE_EXTS or ext in AUDIO_EXTS:
                if basename not in files_by_basename:
                    files_by_basename[basename] = {}
                
                full_path = os.path.join(root, filename)
                
                if ext in IMAGE_EXTS:
                    files_by_basename[basename]['image'] = full_path
                elif ext in AUDIO_EXTS:
                    files_by_basename[basename]['audio'] = full_path

    print(f"[+] Found {len(files_by_basename)} potential groups. Now checking for complete pairs...")

    # --- Process all the pairs that have both an image and an audio file ---
    for basename, paths in files_by_basename.items():
        if 'image' in paths and 'audio' in paths:
            image_path = paths['image']
            audio_path = paths['audio']
            
            # --- NEW LOGIC: Extract the last word as the reciter's name ---
            words = basename.split()
            if not words:
                print(f"[!] Skipping file with empty name.")
                continue
            reciter_name = words[-1] # This gets the last item from the list of words
            
            # --- Create the reciter's personal subfolder ---
            reciter_folder_path = os.path.join(ROOT_DEST_FOLDER, reciter_name)
            os.makedirs(reciter_folder_path, exist_ok=True)
            
            output_filename = f"{basename}.mp4"
            # Create the video in its original folder first, then move it
            output_path = os.path.join(os.path.dirname(image_path), output_filename)

            print("==========================================================")
            print(f"[v] Found Match: {basename}")
            print(f"    > Deduced Reciter: {reciter_name}")
            print(f"[+] Creating video: {output_filename}...")
            
            # --- The FFmpeg Command ---
            command = [
                FFMPEG_PATH, '-y',
                '-loop', '1',
                '-i', image_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-r', '1',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            # --- Run the command and move files on success ---
            try:
                # hide ffmpeg's console output for a cleaner look
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print(f"[+] Moving files to folder: {reciter_folder_path}")
                shutil.move(image_path, reciter_folder_path)
                shutil.move(audio_path, reciter_folder_path)
                shutil.move(output_path, reciter_folder_path)
                print("[v] Done and organized!")

            except subprocess.CalledProcessError as e:
                print(f"[!!!] ERROR: FFmpeg failed for {basename}.")
                print(f"      Check for corrupt files or other FFmpeg issues.")
            except Exception as e:
                print(f"[!!!] An unexpected error occurred: {e}")

    print("==========================================================")
    print("All matching pairs have been processed.")

# This makes the script runnable
if __name__ == "__main__":
    create_videos()