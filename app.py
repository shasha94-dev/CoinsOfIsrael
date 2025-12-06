import os
import json
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

IMAGE_FOLDER = 'images'
THUMB_FOLDER = 'thumbnails' # New folder
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

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
        if not os.path.isdir(series_path):
            continue

        series_img = None
        for f in os.listdir(series_path):
            if is_image(f):
                series_img = os.path.join(series_name, f).replace("\\", "/")
                break

        for year in os.listdir(series_path):
            year_path = os.path.join(series_path, year)
            if not os.path.isdir(year_path):
                continue

            for coin_name in os.listdir(year_path):
                coin_path = os.path.join(year_path, coin_name)
                if not os.path.isdir(coin_path):
                    continue

                folder_contents = os.listdir(coin_path)
                subdirs = [d for d in folder_contents if os.path.isdir(os.path.join(coin_path, d))]
                images_in_root = [f for f in folder_contents if is_image(f)]
                images_in_root.sort()

                coin_stats = get_json_data(os.path.join(coin_path, 'details.json'))

                # --- PART A: Root Images ---
                if images_in_root:
                    subtype_label = "ללא תיוג" if subdirs else None
                    
                    # Original Full Paths
                    img_paths = [os.path.join(series_name, year, coin_name, img).replace("\\", "/") for img in images_in_root]
                    
                    # Determine Thumbnail Path (Check if exists, otherwise use original)
                    primary_thumb = img_paths[0] # Default to original
                    possible_thumb = os.path.join(THUMB_FOLDER, primary_thumb)
                    # We pass a flag or the path prefix to frontend
                    use_thumb = os.path.exists(possible_thumb)

                    collection.append({
                        'series': series_name, 'series_img': series_img, 'year': year,
                        'name': coin_name, 'subtype': subtype_label, 
                        'images': img_paths, 
                        'thumb_src': primary_thumb, # The relative path is the same
                        'thumb_available': use_thumb, # Boolean to tell frontend where to look
                        'has_image': True, 'stats': coin_stats
                    })
                
                # --- PART B: Subtypes ---
                for subtype in subdirs:
                    subtype_path = os.path.join(coin_path, subtype)
                    subtype_imgs = [f for f in os.listdir(subtype_path) if is_image(f)]
                    subtype_imgs.sort()
                    subtype_stats = get_json_data(os.path.join(subtype_path, 'details.json'))
                    final_stats = {**coin_stats, **subtype_stats}

                    if subtype_imgs:
                        img_paths = [os.path.join(series_name, year, coin_name, subtype, img).replace("\\", "/") for img in subtype_imgs]
                        
                        primary_thumb = img_paths[0]
                        possible_thumb = os.path.join(THUMB_FOLDER, primary_thumb)
                        use_thumb = os.path.exists(possible_thumb)

                        collection.append({
                            'series': series_name, 'series_img': series_img, 'year': year,
                            'name': coin_name, 'subtype': subtype,
                            'images': img_paths, 
                            'thumb_src': primary_thumb,
                            'thumb_available': use_thumb,
                            'has_image': True, 'stats': final_stats
                        })
                    else:
                        collection.append({
                            'series': series_name, 'series_img': series_img, 'year': year,
                            'name': coin_name, 'subtype': subtype, 'images': [],
                            'has_image': False, 'stats': final_stats
                        })
                        
                # --- PART C: Empty ---
                if not images_in_root and not subdirs:
                    collection.append({
                        'series': series_name, 'series_img': series_img, 'year': year,
                        'name': coin_name, 'subtype': None, 'images': [],
                        'has_image': False, 'stats': coin_stats
                    })

    return collection

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
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

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

# NEW ROUTE FOR THUMBNAILS
@app.route('/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    return send_from_directory(THUMB_FOLDER, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
