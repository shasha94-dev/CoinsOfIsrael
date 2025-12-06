import os
from PIL import Image

# Configuration
SOURCE_FOLDER = 'images'
DEST_FOLDER = 'thumbnails'
MAX_SIZE = (400, 400)  # Max width/height in pixels
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

def is_image(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def generate():
    print(f"🚀 Starting thumbnail generation from '{SOURCE_FOLDER}' to '{DEST_FOLDER}'...")
    
    processed_count = 0
    skipped_count = 0
    error_count = 0

    for root, dirs, files in os.walk(SOURCE_FOLDER):
        # Determine destination path mirroring the source
        relative_path = os.path.relpath(root, SOURCE_FOLDER)
        target_dir = os.path.join(DEST_FOLDER, relative_path)

        # Create destination folder if not exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        for file in files:
            if is_image(file):
                source_file = os.path.join(root, file)
                dest_file = os.path.join(target_dir, file)

                # Skip if thumbnail already exists (Remove this check if you want to overwrite)
                if os.path.exists(dest_file):
                    skipped_count += 1
                    continue

                try:
                    with Image.open(source_file) as img:
                        # Convert to RGB if needed (e.g. for transparent PNGs saving as JPG, 
                        # though here we save as original format so RGBA is fine for PNG)
                        
                        # Create thumbnail (modifies img in place, preserves aspect ratio)
                        img.thumbnail(MAX_SIZE)
                        
                        # Save
                        img.save(dest_file)
                        print(f"✅ Created: {relative_path}/{file}")
                        processed_count += 1
                except Exception as e:
                    print(f"❌ Error processing {file}: {e}")
                    error_count += 1

    print("-" * 30)
    print(f"Done! Created: {processed_count}, Skipped: {skipped_count}, Errors: {error_count}")

if __name__ == "__main__":
    generate()
