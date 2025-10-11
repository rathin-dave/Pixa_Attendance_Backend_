import os
from PIL import Image

# === Configuration ===
FOLDER_PATH = "./Student_Profile"   # Updated to match existing folder
MAX_SIZE_KB = 100          # Max allowed size in KB

def compress_image(image_path, max_size_kb):
    """Compress image until it is below max_size_kb."""
    try:
        # Open image
        img = Image.open(image_path)
        img = img.convert("RGB")  # Ensure compatibility for JPEG

        # Get initial size
        size_kb = os.path.getsize(image_path) / 1024
        if size_kb <= max_size_kb:
            print(f"✅ Skipped: {os.path.basename(image_path)} ({size_kb:.2f} KB)")
            return

        # Compress iteratively
        quality = 90
        while size_kb > max_size_kb and quality > 10:
            img.save(image_path, "JPEG", quality=quality)
            size_kb = os.path.getsize(image_path) / 1024
            quality -= 5

        print(f"📉 Compressed: {os.path.basename(image_path)} → {size_kb:.2f} KB (quality={quality})")

    except Exception as e:
        print(f"❌ Error compressing {image_path}: {e}")

def process_folder(folder_path):
    """Process all .jpg images in the folder."""
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".jpg"):
            image_path = os.path.join(folder_path, filename)
            compress_image(image_path, MAX_SIZE_KB)

if __name__ == "__main__":
    process_folder(FOLDER_PATH)
