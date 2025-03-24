import os
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import json

# Ensure the necessary directories are in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import application modules
from core.file_tracker import FileTracker
from ui.file_tracker_tab import FileTrackerTab
from ui.duplicate_finder_tab import DuplicateFinderTab

class FileTrackerApp:
    """Main application class for File Tracker with Duplicate Finder"""
    
    def __init__(self):
        """Initialize the application"""
        self.root = tk.Tk()
        self.root.title("File Activity Tracker 1.2")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # Configuration files
        self.config_file = "file_tracker_config.json"
        self.history_file = "file_history.json"
        
        # Load configuration
        self.config = self.load_config()
        
        # Create the main application container
        self.create_main_container()
        
        # Initialize the file tracker
        self.tracker = FileTracker(self.config.get('watch_paths', []), self.history_file)
        
        # Create and initialize tabs
        self.create_tabs()
        
        # Set up application closing handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_config(self):
        """Load application configuration from file"""
        config = {'watch_paths': []}
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
        except Exception as e:
            print(f"Error loading configuration: {e}")
        return config
    
    def save_config(self):
        """Save application configuration to file"""
        try:
            # Update config with current settings
            self.config['watch_paths'] = self.file_tracker_tab.get_watch_paths()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration: {e}")
            messagebox.showerror("Configuration Error", 
                               f"Failed to save configuration: {str(e)}")
    
    def create_main_container(self):
        """Create the main application container"""
        # Create main frame to hold everything
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
    
    def create_tabs(self):
        """Create and initialize application tabs"""
        # Create File Tracker tab
        file_tracker_frame = ttk.Frame(self.notebook)
        self.notebook.add(file_tracker_frame, text="File Tracker")
        self.file_tracker_tab = FileTrackerTab(
            file_tracker_frame, 
            self.tracker, 
            self.config.get('watch_paths', [])
        )
        
        # Create Duplicate Finder tab
        duplicate_finder_frame = ttk.Frame(self.notebook)
        self.notebook.add(duplicate_finder_frame, text="Duplicate Finder")
        self.duplicate_finder_tab = DuplicateFinderTab(duplicate_finder_frame)
    
    def on_closing(self):
        """Handle application closing event"""
        try:
            # Stop the file tracker
            if hasattr(self, 'tracker'):
                self.tracker.stop()
            
            # Save configuration
            self.save_config()
            
            # Destroy the root window
            self.root.destroy()
        except Exception as e:
            print(f"Error during application shutdown: {e}")
    
    def run(self):
        """Start the application main loop"""
        # Start the file tracker
        self.tracker.start()
        
        # Start the main event loop
        self.root.mainloop()

if __name__ == "__main__":
    app = FileTrackerApp()
    app.run()
