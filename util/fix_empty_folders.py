import os

def create_gitkeeps(start_path):
    count = 0
    # Walk through the directory tree
    for root, dirs, files in os.walk(start_path):
        # Ignore hidden files like .DS_Store
        visible_files = [f for f in files if not f.startswith('.')]
        
        # If a folder has no visible files (images or json), add a .gitkeep
        if not visible_files:
            gitkeep_path = os.path.join(root, '.gitkeep')
            # Only create if it doesn't exist
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    pass # Create empty file
                print(f"✅ Secured folder: {root}")
                count += 1

    if count == 0:
        print("All folders are already secured!")
    else:
        print(f"\nCreated {count} .gitkeep files. You can now commit and push.")

if __name__ == "__main__":
    create_gitkeeps('images')
