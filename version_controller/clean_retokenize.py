import os
import shutil

def delete_object_cache():
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to 'object_cache' inside 'grep++'
    grep_plus_plus_dir = os.path.join(current_dir, 'grep++')
    object_cache_dir = os.path.join(grep_plus_plus_dir, 'object_cache')
    
    # Check if the directory exists
    if os.path.exists(object_cache_dir):
        try:
            # Delete the directory and all its contents
            shutil.rmtree(object_cache_dir)
            print(f"Deleted the directory: {object_cache_dir}")
        except Exception as e:
            print(f"Error deleting directory: {e}")
    else:
        print(f"The directory {object_cache_dir} does not exist.")

if __name__ == "__main__":
    delete_object_cache()
    with open('object_cache.py') as f:
        code = f.read()
        exec(code)

