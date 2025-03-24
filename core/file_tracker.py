import os
import datetime
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileTracker(FileSystemEventHandler):
    """Class to track file activity and maintain history"""
    
    def __init__(self, watch_paths, history_file):
        """Initialize the file tracker"""
        self.watch_paths = watch_paths
        self.history_file = history_file
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.today_files = set()
        self.history = {}
        self.observer = None
        self.load_history()

    def load_history(self):
        """Load existing history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                    if self.today in self.history:
                        self.today_files = set(self.history[self.today])
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = {}

    def save_history(self):
        """Save current history to file"""
        try:
            self.history[self.today] = list(self.today_files)
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_current_files_for_date(self, date_str, path):
        """Add currently existing files in the path to history for a specific date"""
        try:
            if not os.path.exists(path):
                return False

            current_files = set()
            for root, _, files in os.walk(path):
                for file in files:
                    try:
                        full_path = os.path.join(root, file)
                        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
                        file_date_str = file_modified.strftime('%Y-%m-%d')
                        if file_date_str == date_str:
                            current_files.add(full_path)
                    except Exception as e:
                        print(f"Error processing file {file}: {e}")
                        continue

            if date_str in self.history:
                existing_files = set(self.history[date_str])
                existing_files.update(current_files)
                self.history[date_str] = list(existing_files)
            else:
                self.history[date_str] = list(current_files)

            self.save_history()
            return True
            
        except Exception as e:
            print(f"Error adding current files: {e}")
            return False

    def start(self):
        """Start the file observer"""
        if self.observer is None:
            self.observer = Observer()
            for path in self.watch_paths:
                if os.path.exists(path):
                    self.observer.schedule(self, path, recursive=True)
            self.observer.start()

    def stop(self):
        """Stop the file observer"""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None

    def on_modified(self, event):
        """Handle modified file event"""
        if not event.is_directory:
            self.today_files.add(event.src_path)
            self.save_history()

    def on_created(self, event):
        """Handle created file event"""
        if not event.is_directory:
            self.today_files.add(event.src_path)
            self.save_history()

    def get_files_for_date(self, date_str, selected_paths=None):
        """Get files for a specific date from history, filtered by selected paths"""
        all_files = self.history.get(date_str, [])
        if not selected_paths:
            return all_files
        return [f for f in all_files if any(f.startswith(path) for path in selected_paths)]

    def clean_history_for_path(self, removed_path):
        """Remove files from history that were in the removed folder"""
        try:
            for date in self.history:
                self.history[date] = [f for f in self.history[date]
                                    if not f.startswith(removed_path)]
            self.save_history()
            return True
        except Exception as e:
            print(f"Error cleaning history: {e}")
            return False
