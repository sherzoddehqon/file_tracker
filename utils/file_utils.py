import os
import shutil
import datetime

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_file_info(filepath):
    """Get detailed information about a file"""
    try:
        stat_info = os.stat(filepath)
        size = stat_info.st_size
        created = datetime.datetime.fromtimestamp(stat_info.st_ctime)
        modified = datetime.datetime.fromtimestamp(stat_info.st_mtime)
        accessed = datetime.datetime.fromtimestamp(stat_info.st_atime)
        
        return {
            'name': os.path.basename(filepath),
            'path': filepath,
            'size': size,
            'size_formatted': format_file_size(size),
            'created': created,
            'modified': modified,
            'accessed': accessed,
            'extension': os.path.splitext(filepath)[1].lower()
        }
    except Exception as e:
        print(f"Error getting file info for {filepath}: {e}")
        return None

def safe_delete_file(filepath):
    """Safely delete a file"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")
        return False

def safe_move_file(source, destination_dir):
    """Safely move a file to a destination directory"""
    try:
        if not os.path.exists(source):
            return False
        
        # Create destination directory if it doesn't exist
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        # Generate destination filepath
        filename = os.path.basename(source)
        destination = os.path.join(destination_dir, filename)
        
        # Handle filename conflicts
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(destination):
            new_name = f"{name}_{counter}{ext}"
            destination = os.path.join(destination_dir, new_name)
            counter += 1
        
        # Move the file
        shutil.move(source, destination)
        return destination
    except Exception as e:
        print(f"Error moving file {source}: {e}")
        return False

def safe_copy_file(source, destination_dir):
    """Safely copy a file to a destination directory"""
    try:
        if not os.path.exists(source):
            return False
        
        # Create destination directory if it doesn't exist
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        # Generate destination filepath
        filename = os.path.basename(source)
        destination = os.path.join(destination_dir, filename)
        
        # Handle filename conflicts
        counter = 1
        name, ext = os.path.splitext(filename)
        while os.path.exists(destination):
            new_name = f"{name}_{counter}{ext}"
            destination = os.path.join(destination_dir, new_name)
            counter += 1
        
        # Copy the file
        shutil.copy2(source, destination)
        return destination
    except Exception as e:
        print(f"Error copying file {source}: {e}")
        return False

def open_file_location(filepath):
    """Open the directory containing the file"""
    try:
        dir_path = os.path.dirname(filepath)
        if os.path.exists(dir_path):
            if os.name == 'nt':  # Windows
                os.startfile(dir_path)
            elif os.name == 'posix':  # Linux/Unix/Mac
                try:
                    os.system(f'xdg-open "{dir_path}"')
                except:
                    os.system(f'open "{dir_path}"')
            return True
        return False
    except Exception as e:
        print(f"Error opening location for {filepath}: {e}")
        return False
