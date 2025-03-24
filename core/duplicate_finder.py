import os
import hashlib
import datetime
from difflib import SequenceMatcher

class DuplicateFinder:
    """Class to handle duplicate file detection"""
    def __init__(self):
        self.is_scanning = False
        self.scan_stopped = False
        
    def calculate_file_hash(self, filepath, blocksize=65536):
        """Calculate MD5 hash of file contents"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as file:
                buf = file.read(blocksize)
                while len(buf) > 0:
                    if self.scan_stopped:
                        return None
                    hasher.update(buf)
                    buf = file.read(blocksize)
            return hasher.hexdigest()
        except Exception as e:
            print(f"Error hashing file {filepath}: {e}")
            return None
    
    def find_duplicates_by_hash(self, directories, callback=None):
        """
        Find duplicates by comparing file content hashes
        
        Args:
            directories: List of directory paths to scan
            callback: Function to call with progress updates (progress_percent, message)
            
        Returns:
            Dictionary with hash as key and list of duplicate file paths as value
        """
        self.is_scanning = True
        self.scan_stopped = False
        
        # Dictionary to store files by hash
        files_by_hash = {}
        total_files = 0
        processed_files = 0
        
        # First pass: Count total files for progress reporting
        for directory in directories:
            for root, _, files in os.walk(directory):
                total_files += len(files)
        
        # Process files
        for directory in directories:
            for root, _, files in os.walk(directory):
                for filename in files:
                    if self.scan_stopped:
                        self.is_scanning = False
                        return {}
                    
                    filepath = os.path.join(root, filename)
                    try:
                        file_hash = self.calculate_file_hash(filepath)
                        if file_hash:
                            if file_hash not in files_by_hash:
                                files_by_hash[file_hash] = []
                            files_by_hash[file_hash].append(filepath)
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")
                    
                    processed_files += 1
                    if callback:
                        progress = (processed_files / total_files) * 100
                        callback(progress, f"Processing files: {processed_files}/{total_files}")
        
        # Filter to keep only duplicate sets
        duplicates = {h: files for h, files in files_by_hash.items() if len(files) > 1}
        
        self.is_scanning = False
        return duplicates
    
    def find_duplicates_by_name_size(self, directories, callback=None):
        """
        Find duplicates by comparing file names and sizes
        
        Args:
            directories: List of directory paths to scan
            callback: Function to call with progress updates
            
        Returns:
            Dictionary with name_size as key and list of duplicate file paths as value
        """
        self.is_scanning = True
        self.scan_stopped = False
        
        # Dictionary to store files by name and size
        files_by_name_size = {}
        total_files = 0
        processed_files = 0
        
        # First pass: Count total files for progress reporting
        for directory in directories:
            for root, _, files in os.walk(directory):
                total_files += len(files)
        
        # Process files
        for directory in directories:
            for root, _, files in os.walk(directory):
                for filename in files:
                    if self.scan_stopped:
                        self.is_scanning = False
                        return {}
                    
                    filepath = os.path.join(root, filename)
                    try:
                        file_size = os.path.getsize(filepath)
                        key = (filename, file_size)
                        
                        if key not in files_by_name_size:
                            files_by_name_size[key] = []
                        files_by_name_size[key].append(filepath)
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")
                    
                    processed_files += 1
                    if callback:
                        progress = (processed_files / total_files) * 100
                        callback(progress, f"Processing files: {processed_files}/{total_files}")
        
        # Filter to keep only duplicate sets
        duplicates = {f"{name}_{size}": files for (name, size), files in files_by_name_size.items() if len(files) > 1}
        
        self.is_scanning = False
        return duplicates
    
    def find_similar_files(self, directories, similarity_threshold=0.8, callback=None):
        """
        Find similar but not identical files using fuzzy matching
        
        Args:
            directories: List of directory paths to scan
            similarity_threshold: Minimum similarity ratio (0.0-1.0)
            callback: Function to call with progress updates
            
        Returns:
            Dictionary with group_id as key and list of similar file paths as value
        """
        self.is_scanning = True
        self.scan_stopped = False
        
        # Get all files
        all_files = []
        for directory in directories:
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    all_files.append((filepath, filename))
        
        total_comparisons = len(all_files) * (len(all_files) - 1) // 2
        processed_comparisons = 0
        
        # Dictionary to store similar file groups
        similar_files = {}
        group_count = 0
        
        # Compare each file with every other file
        for i in range(len(all_files)):
            filepath1, filename1 = all_files[i]
            
            for j in range(i + 1, len(all_files)):
                if self.scan_stopped:
                    self.is_scanning = False
                    return {}
                
                filepath2, filename2 = all_files[j]
                
                # Compare filenames using sequence matcher
                similarity = SequenceMatcher(None, filename1, filename2).ratio()
                
                if similarity >= similarity_threshold:
                    group_key = f"group_{group_count}"
                    
                    # Check if either file is already in a group
                    existing_group = None
                    for key, files in similar_files.items():
                        if filepath1 in files or filepath2 in files:
                            existing_group = key
                            break
                    
                    if existing_group:
                        # Add to existing group
                        if filepath1 not in similar_files[existing_group]:
                            similar_files[existing_group].append(filepath1)
                        if filepath2 not in similar_files[existing_group]:
                            similar_files[existing_group].append(filepath2)
                    else:
                        # Create a new group
                        similar_files[group_key] = [filepath1, filepath2]
                        group_count += 1
                
                processed_comparisons += 1
                if callback and processed_comparisons % 100 == 0:  # Update less frequently
                    progress = (processed_comparisons / total_comparisons) * 100
                    callback(progress, f"Comparing files: {processed_comparisons}/{total_comparisons}")
        
        self.is_scanning = False
        return similar_files
    
    def scan_directories(self, directories, callback=None):
        """
        Scan directories and return file statistics
        
        Args:
            directories: List of directory paths to scan
            callback: Function to call with progress updates
            
        Returns:
            Dictionary with statistics
        """
        self.is_scanning = True
        self.scan_stopped = False
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'extensions': {},
            'largest_files': []
        }
        
        # Process files
        for directory in directories:
            for root, _, files in os.walk(directory):
                for filename in files:
                    if self.scan_stopped:
                        self.is_scanning = False
                        return stats
                    
                    filepath = os.path.join(root, filename)
                    try:
                        # Get file size
                        file_size = os.path.getsize(filepath)
                        stats['total_files'] += 1
                        stats['total_size'] += file_size
                        
                        # Track file extension
                        _, extension = os.path.splitext(filename)
                        extension = extension.lower()
                        if extension in stats['extensions']:
                            stats['extensions'][extension]['count'] += 1
                            stats['extensions'][extension]['size'] += file_size
                        else:
                            stats['extensions'][extension] = {
                                'count': 1,
                                'size': file_size
                            }
                        
                        # Track largest files
                        stats['largest_files'].append((filepath, file_size))
                        stats['largest_files'].sort(key=lambda x: x[1], reverse=True)
                        stats['largest_files'] = stats['largest_files'][:10]  # Keep only top 10
                        
                    except Exception as e:
                        print(f"Error processing file {filepath}: {e}")
                    
                    if callback and stats['total_files'] % 100 == 0:
                        callback(0, f"Scanned {stats['total_files']} files...")
        
        self.is_scanning = False
        return stats
    
    def stop_scan(self):
        """Stop the current scan"""
        self.scan_stopped = True
        
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
