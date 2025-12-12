import os
import json
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

IMAGE_FOLDER = 'images'
THUMB_FOLDER = 'thumbnails'
FOLDER_MAP_FILE = 'folder_map.json'  # <-- NEW
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

# Load the folder translations into memory
folder_map = {}
if os.path.exists(FOLDER_MAP_FILE):
    with open(FOLDER_MAP_FILE, 'r', encoding='utf-8') as f:
        folder_map = json.load(f)

def get_trans_obj(hebrew_text):
    """
    Helper to create a bilingual dict: {'he': '...', 'en': '...'}
    Uses folder_map if available, otherwise falls back to Hebrew for both.
    """
    return {
        'he': hebrew_text,
        'en': folder_map.get(hebrew_text, hebrew_text) # Fallback to Hebrew if no translation
    }

def is_image(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

def get_json_data(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}
    
def scan_collection():
    collection = []
    
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    for series_name in os.listdir(IMAGE_FOLDER):
        series_path = os.path.join(IMAGE_FOLDER, series_name)
        if not os.path.isdir(series_path): continue

        series_img = None
        for f in os.listdir(series_path):
            if is_image(f):
                series_img = os.path.join(series_name, f).replace("\\", "/")
                break

        for year in os.listdir(series_path):
            year_path = os.path.join(series_path, year)
            if not os.path.isdir(year_path): continue

            for coin_name in os.listdir(year_path):
                coin_path = os.path.join(year_path, coin_name)
                if not os.path.isdir(coin_path): continue

                folder_contents = os.listdir(coin_path)
                subdirs = [d for d in folder_contents if os.path.isdir(os.path.join(coin_path, d))]
                images_in_root = [f for f in folder_contents if is_image(f)]
                images_in_root.sort()

                coin_stats = get_json_data(os.path.join(coin_path, 'details.json'))

                # --- Create Bilingual Objects ---
                series_obj = get_trans_obj(series_name)
                name_obj = get_trans_obj(coin_name)
                
                # --- PART A: Root Images ---
                if images_in_root:
                    # 'subtype' is None here, but we can make it a dict for consistency if needed
                    # or handle null in frontend
                    subtype_obj = None 
                    if subdirs:
                         subtype_obj = {'he': "ללא תיוג", 'en': "Untagged"}

                    img_paths = [os.path.join(series_name, year, coin_name, img).replace("\\", "/") for img in images_in_root]
                    primary_thumb = img_paths[0]
                    use_thumb = os.path.exists(os.path.join(THUMB_FOLDER, primary_thumb))

                    collection.append({
                        'series': series_obj, 'series_img': series_img, 'year': year,
                        'name': name_obj, 'subtype': subtype_obj, 
                        'images': img_paths, 'thumb_src': primary_thumb, 'thumb_available': use_thumb,
                        'has_image': True, 'stats': coin_stats
                    })
                
                # --- PART B: Subtypes ---
                for subtype in subdirs:
                    subtype_path = os.path.join(coin_path, subtype)
                    subtype_imgs = [f for f in os.listdir(subtype_path) if is_image(f)]
                    subtype_imgs.sort()
                    subtype_stats = get_json_data(os.path.join(subtype_path, 'details.json'))
                    final_stats = {**coin_stats, **subtype_stats}
                    
                    subtype_obj = get_trans_obj(subtype)

                    if subtype_imgs:
                        img_paths = [os.path.join(series_name, year, coin_name, subtype, img).replace("\\", "/") for img in subtype_imgs]
                        primary_thumb = img_paths[0]
                        use_thumb = os.path.exists(os.path.join(THUMB_FOLDER, primary_thumb))

                        collection.append({
                            'series': series_obj, 'series_img': series_img, 'year': year,
                            'name': name_obj, 'subtype': subtype_obj,
                            'images': img_paths, 'thumb_src': primary_thumb, 'thumb_available': use_thumb,
                            'has_image': True, 'stats': final_stats
                        })
                    else:
                        collection.append({
                            'series': series_obj, 'series_img': series_img, 'year': year,
                            'name': name_obj, 'subtype': subtype_obj, 'images': [],
                            'has_image': False, 'stats': final_stats
                        })
                        
                # --- PART C: Empty ---
                if not images_in_root and not subdirs:
                    collection.append({
                        'series': series_obj, 'series_img': series_img, 'year': year,
                        'name': name_obj, 'subtype': None, 'images': [],
                        'has_image': False, 'stats': coin_stats
                    })

    return collection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    # You will need to manually update about.json to have {"he":..., "en":...} structure
    # or handle it in the script
    data = get_json_data(os.path.join(IMAGE_FOLDER, 'about.json'))
    return render_template('about.html', data=data)

@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

@app.route('/api/translations')
def get_translations():
    """Serves the master translation dictionary"""
    return jsonify(get_json_data(FOLDER_MAP_FILE))
    
@app.route('/api/data')
def get_data():
    coins = scan_collection()
    order_config = get_json_data(os.path.join(IMAGE_FOLDER, 'order.json'))
    return jsonify({'coins': coins, 'config': order_config})

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    return send_from_directory(THUMB_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
