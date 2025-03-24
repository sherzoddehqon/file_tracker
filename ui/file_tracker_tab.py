import os
import datetime
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import Calendar

class FileTrackerTab:
    """UI component for the file tracker tab"""
    
    def __init__(self, parent_frame, tracker, watch_paths):
        """Initialize the file tracker tab"""
        self.parent = parent_frame
        self.tracker = tracker
        self.watch_paths = watch_paths
        self.path_vars = {}  # Dictionary to store checkbox variables
        self.is_processing = False
        
        # Create UI elements
        self.create_widgets()
        self.update_paths_listbox()
    
    def create_widgets(self):
        """Create UI widgets for the file tracker tab"""
        # Create main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Top status frame with progress bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=2)
        
        self.status_label = ttk.Label(status_frame, text="")
        self.status_label.pack(side=tk.LEFT, pady=2)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Paths Frame with checkboxes
        paths_frame = ttk.LabelFrame(main_frame, text="Watched Folders")
        paths_frame.pack(fill=tk.X, pady=5)
        
        # Create a canvas and scrollbar for the paths
        paths_canvas = tk.Canvas(paths_frame, height=100)  # Set fixed height for better visibility
        paths_scroll = ttk.Scrollbar(paths_frame, orient="vertical", command=paths_canvas.yview)
        self.paths_checkbox_frame = ttk.Frame(paths_canvas)
        
        paths_canvas.configure(yscrollcommand=paths_scroll.set)
        
        # Pack the widgets
        paths_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        paths_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a window inside the canvas for the checkboxes
        paths_canvas.create_window((0, 0), window=self.paths_checkbox_frame, anchor="nw")
        
        # Configure the canvas to scroll with mousewheel
        self.paths_checkbox_frame.bind("<Configure>", 
            lambda e: paths_canvas.configure(scrollregion=paths_canvas.bbox("all")))
        paths_canvas.bind("<Configure>", 
            lambda e: paths_canvas.itemconfig(paths_canvas.find_all()[0] if paths_canvas.find_all() else 0, width=e.width))
        
        # Buttons Frame
        buttons_frame = ttk.Frame(paths_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Add Folder", command=self.add_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Remove Selected", command=self.remove_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Select All", command=self.select_all_paths).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Deselect All", command=self.deselect_all_paths).pack(side=tk.LEFT, padx=5)
        
        # Calendar Frame
        cal_frame = ttk.LabelFrame(main_frame, text="Select Date")
        cal_frame.pack(fill=tk.X, pady=5)
        
        self.cal = Calendar(cal_frame, selectmode='day',
                          year=datetime.datetime.now().year,
                          month=datetime.datetime.now().month,
                          day=datetime.datetime.now().day)
        self.cal.pack(padx=5, pady=5)
        self.cal.bind("<<CalendarSelected>>", self.on_date_select)
        
        self.date_label = ttk.Label(cal_frame, text="Selected Date: None")
        self.date_label.pack(pady=2)
        
        # Files Frame
        files_frame = ttk.LabelFrame(main_frame, text="Files for Selected Date")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        files_scroll = ttk.Scrollbar(files_frame)
        files_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.files_listbox = tk.Listbox(files_frame, yscrollcommand=files_scroll.set)
        self.files_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        files_scroll.config(command=self.files_listbox.yview)
        self.files_listbox.bind('<Double-Button-1>', self.open_file_location)

        ttk.Button(main_frame, text="Refresh Files", command=self.refresh_files).pack(pady=5)
    
    def get_watch_paths(self):
        """Get the current watch paths"""
        return self.watch_paths
    
    def update_paths_listbox(self):
        """Update the watched paths listbox with checkboxes"""
        # Clear existing checkboxes
        for widget in self.paths_checkbox_frame.winfo_children():
            widget.destroy()
        
        # Clear existing variables
        self.path_vars.clear()
        
        # Create new checkboxes
        for path in self.watch_paths:
            var = tk.BooleanVar(value=True)
            self.path_vars[path] = var
            
            # Create a frame for each path to hold the checkbox and label
            path_frame = ttk.Frame(self.paths_checkbox_frame)
            path_frame.pack(fill=tk.X, padx=2, pady=1)
            
            # Create and pack the checkbox
            cb = ttk.Checkbutton(path_frame, variable=var, 
                               command=self.refresh_files)
            cb.pack(side=tk.LEFT)
            
            # Create and pack the label
            label = ttk.Label(path_frame, text=path)
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            # Bind click events to toggle checkbox
            label.bind('<Button-1>', lambda e, v=var: self.toggle_checkbox(v))
            path_frame.bind('<Button-1>', lambda e, v=var: self.toggle_checkbox(v))
    
    def toggle_checkbox(self, var):
        """Toggle a checkbox state"""
        var.set(not var.get())
        self.refresh_files()
    
    def select_all_paths(self):
        """Select all paths"""
        for var in self.path_vars.values():
            var.set(True)
        self.refresh_files()
    
    def deselect_all_paths(self):
        """Deselect all paths"""
        for var in self.path_vars.values():
            var.set(False)
        self.refresh_files()
    
    def get_selected_paths(self):
        """Get the selected paths"""
        return [path for path, var in self.path_vars.items() if var.get()]
    
    def add_path(self):
        """Add a path to watch"""
        path = filedialog.askdirectory(title="Select Folder to Monitor")
        if path:
            abs_path = os.path.abspath(path)
            if abs_path not in self.watch_paths:
                self.watch_paths.append(abs_path)
                self.update_paths_listbox()
                
                def scan_path():
                    self.parent.after(0, self.start_processing, f"Scanning folder: {abs_path}")
                    selected_date = self.cal.get_date()
                    date_obj = datetime.datetime.strptime(selected_date, '%m/%d/%y')
                    date_str = date_obj.strftime('%Y-%m-%d')
                    success = self.tracker.add_current_files_for_date(date_str, abs_path)
                    if success:
                        self.parent.after(0, self.stop_processing, f"Added folder: {abs_path}")
                    else:
                        self.parent.after(0, self.stop_processing, f"Error adding folder: {abs_path}")
                    self.parent.after(100, self.refresh_files)
                
                threading.Thread(target=scan_path).start()
                
                # Restart the tracker with the new path
                self.tracker.stop()
                self.tracker.watch_paths = self.watch_paths
                self.tracker.start()
            else:
                self.status_label.config(text="This folder is already being monitored")
    
    def remove_path(self):
        """Remove a path from watch list"""
        selection = self.get_selected_paths()
        if selection:
            removed_path = selection[0]
            self.watch_paths.remove(removed_path)
            self.update_paths_listbox()
            
            def clean_path():
                self.parent.after(0, self.start_processing, f"Removing folder: {removed_path}")
                success = self.tracker.clean_history_for_path(removed_path)
                if success:
                    self.parent.after(0, self.stop_processing, f"Removed folder: {removed_path}")
                else:
                    self.parent.after(0, self.stop_processing, f"Error removing folder: {removed_path}")
                self.parent.after(100, self.refresh_files)
            
            threading.Thread(target=clean_path).start()
            
            # Restart the tracker without the removed path
            self.tracker.stop()
            self.tracker.watch_paths = self.watch_paths
            self.tracker.start()
    
    def start_processing(self, message="Processing..."):
        """Show processing indicator"""
        self.is_processing = True
        self.status_label.config(text=message)
        self.progress_bar.start(10)
        self.parent.update()
    
    def stop_processing(self, message="Ready"):
        """Hide processing indicator"""
        self.is_processing = False
        self.status_label.config(text=message)
        self.progress_bar.stop()
        self.parent.update()
    
    def on_date_select(self, event=None):
        """Handle date selection event"""
        selected_date = self.cal.get_date()
        self.date_label.config(text=f"Selected Date: {selected_date}")
        
        def scan_folders():
            self.parent.after(0, self.start_processing, "Scanning folders...")
            date_obj = datetime.datetime.strptime(selected_date, '%m/%d/%y')
            date_str = date_obj.strftime('%Y-%m-%d')
            
            success = True
            for path in self.watch_paths:
                if not self.tracker.add_current_files_for_date(date_str, path):
                    success = False
            
            if success:
                self.parent.after(0, self.stop_processing, "Scan complete")
            else:
                self.parent.after(0, self.stop_processing, "Scan completed with errors")
            self.parent.after(100, self.refresh_files)
        
        threading.Thread(target=scan_folders).start()
    
    def refresh_files(self):
        """Refresh the files listbox"""
        try:
            if self.is_processing:
                self.parent.after(100, self.refresh_files)
                return

            selected_date = self.cal.get_date()
            date_obj = datetime.datetime.strptime(selected_date, '%m/%d/%y')
            date_str = date_obj.strftime('%Y-%m-%d')
            
            selected_paths = self.get_selected_paths()
            
            self.files_listbox.delete(0, tk.END)
            files = self.tracker.get_files_for_date(date_str, selected_paths)
            
            if files:
                for file in files:
                    self.files_listbox.insert(tk.END, file)
                self.status_label.config(
                    text=f"Found {len(files)} files for {selected_date} in {len(selected_paths)} selected folders")
            else:
                self.files_listbox.insert(tk.END, "No files found for this date in selected folders")
                self.status_label.config(
                    text=f"No files found for {selected_date} in {len(selected_paths)} selected folders")
            
        except Exception as e:
            self.files_listbox.delete(0, tk.END)
            self.files_listbox.insert(tk.END, f"Error processing date: {str(e)}")
            self.status_label.config(text="Error processing date")
    
    def open_file_location(self, event=None):
        """Open the location of the selected file"""
        selection = self.files_listbox.curselection()
        if selection:
            file_path = self.files_listbox.get(selection[0])
            try:
                # Get the directory path
                dir_path = os.path.dirname(file_path)
                
                # Open the directory in file explorer
                if os.path.exists(dir_path):
                    if os.name == 'nt':  # For Windows
                        os.startfile(dir_path)
                    elif os.name == 'posix':  # For Linux/Unix/Mac
                        try:
                            os.system(f'xdg-open "{dir_path}"')
                        except:
                            os.system(f'open "{dir_path}"')
                    self.status_label.config(text=f"Opened directory: {dir_path}")
                else:
                    self.status_label.config(text="Directory not found")
            except Exception as e:
                self.status_label.config(text=f"Error opening directory: {str(e)}")
