import os
import json
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

IMAGE_FOLDER = 'images'
THUMB_FOLDER = 'thumbnails'
FOLDER_MAP_FILE = 'folder_map.json'
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

# Load translations
folder_map = {}
if os.path.exists(FOLDER_MAP_FILE):
    with open(FOLDER_MAP_FILE, 'r', encoding='utf-8') as f:
        folder_map = json.load(f)

def get_trans_obj(hebrew_text):
    return {
        'he': hebrew_text,
        'en': folder_map.get(hebrew_text, hebrew_text)
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

    # 1. LOOP CATEGORIES (Circulation vs Sets)
    for category_name in os.listdir(IMAGE_FOLDER):
        category_path = os.path.join(IMAGE_FOLDER, category_name)
        if not os.path.isdir(category_path) or category_name in ['thumbnails', 'static']: 
            continue

        cat_obj = get_trans_obj(category_name)

        # 2. LOOP SERIES (Standard for EVERY category now)
        for series_name in os.listdir(category_path):
            series_path = os.path.join(category_path, series_name)
            if not os.path.isdir(series_path): continue

            series_obj = get_trans_obj(series_name)
            series_img = None
            
            # Find series hero image
            for f in os.listdir(series_path):
                if is_image(f):
                    series_img = os.path.join(category_name, series_name, f).replace("\\", "/")
                    break

            # 3. LOOP YEARS
            for year in os.listdir(series_path):
                year_path = os.path.join(series_path, year)
                if not os.path.isdir(year_path): continue

                # 4. LOOP COINS
                for coin_name in os.listdir(year_path):
                    coin_path = os.path.join(year_path, coin_name)
                    if not os.path.isdir(coin_path): continue

                    # Process Coin
                    process_coin_item(collection, category_name, series_name, year, coin_name, coin_path, cat_obj, series_obj, series_img)

    return collection

def process_coin_item(collection, category_name, series_dir_name, year, coin_name, coin_path, cat_obj, series_obj, series_img):
    """Helper to process a single coin folder"""
    folder_contents = os.listdir(coin_path)
    subdirs = [d for d in folder_contents if os.path.isdir(os.path.join(coin_path, d))]
    images_in_root = [f for f in folder_contents if is_image(f)]
    images_in_root.sort()

    coin_stats = get_json_data(os.path.join(coin_path, 'details.json'))
    name_obj = get_trans_obj(coin_name)

    # Helper to build path
    def build_img_path(img_file, sub_folder=None):
        parts = [category_name, series_dir_name, year, coin_name]
        if sub_folder: parts.append(sub_folder)
        parts.append(img_file)
        return os.path.join(*parts).replace("\\", "/")

    # --- PART A: Root Images ---
    if images_in_root:
        subtype_obj = None 
        if subdirs: subtype_obj = {'he': "ללא תיוג", 'en': "Untagged"}

        img_paths = [build_img_path(img) for img in images_in_root]
        primary_thumb = img_paths[0]
        use_thumb = os.path.exists(os.path.join(THUMB_FOLDER, primary_thumb))

        collection.append({
            'category': cat_obj, 'series': series_obj, 'series_img': series_img, 'year': year,
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
            img_paths = [build_img_path(img, subtype) for img in subtype_imgs]
            primary_thumb = img_paths[0]
            use_thumb = os.path.exists(os.path.join(THUMB_FOLDER, primary_thumb))

            collection.append({
                'category': cat_obj, 'series': series_obj, 'series_img': series_img, 'year': year,
                'name': name_obj, 'subtype': subtype_obj,
                'images': img_paths, 'thumb_src': primary_thumb, 'thumb_available': use_thumb,
                'has_image': True, 'stats': final_stats
            })
        else:
            collection.append({
                'category': cat_obj, 'series': series_obj, 'series_img': series_img, 'year': year,
                'name': name_obj, 'subtype': subtype_obj, 'images': [],
                'has_image': False, 'stats': final_stats
            })
            
    # --- PART C: Empty ---
    if not images_in_root and not subdirs:
        collection.append({
            'category': cat_obj, 'series': series_obj, 'series_img': series_img, 'year': year,
            'name': name_obj, 'subtype': None, 'images': [],
            'has_image': False, 'stats': coin_stats
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    # Note: You might want to update about.json logic if it moves, but for now we leave it
    # We assume about.json is still directly in 'images' or moved to 'images/מחזור'
    # For safety, put about.json in the root 'images' folder alongside the two new folders.
    data = get_json_data(os.path.join(IMAGE_FOLDER, 'about.json'))
    return render_template('about.html', data=data)

@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

@app.route('/api/data')
def get_data():
    coins = scan_collection()
    order_config = get_json_data(os.path.join(IMAGE_FOLDER, 'order.json'))
    return jsonify({'coins': coins, 'config': order_config})

@app.route('/api/translations')
def get_translations():
    return jsonify(get_json_data(FOLDER_MAP_FILE))

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    return send_from_directory(THUMB_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=5000)
