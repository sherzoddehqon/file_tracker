import os
import threading
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from core.duplicate_finder import DuplicateFinder
from utils.file_utils import format_file_size, open_file_location, safe_delete_file

class DuplicateFinderTab:
    """UI component for the duplicate finder tab"""
    
    def __init__(self, parent_frame):
        """Initialize the duplicate finder tab"""
        self.parent = parent_frame
        self.duplicate_finder = DuplicateFinder()
        self.scan_directories = []
        
        # Create UI elements
        self.create_widgets()
    
    def create_widgets(self):
        """Create UI widgets for the duplicate finder tab"""
        # Create main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top status frame with progress bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=2)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, pady=2)
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Folders selection
        folder_frame = ttk.LabelFrame(main_frame, text="Folders to Scan")
        folder_frame.pack(fill=tk.X, pady=5)
        
        folder_list_frame = ttk.Frame(folder_frame)
        folder_list_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create scrollbar for the directory listbox
        folder_scroll = ttk.Scrollbar(folder_list_frame)
        folder_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.scan_listbox = tk.Listbox(folder_list_frame, height=5, yscrollcommand=folder_scroll.set)
        self.scan_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        folder_scroll.config(command=self.scan_listbox.yview)
        
        folder_btn_frame = ttk.Frame(folder_list_frame)
        folder_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        ttk.Button(folder_btn_frame, text="Add", command=self.add_scan_directory).pack(pady=2)
        ttk.Button(folder_btn_frame, text="Remove", command=self.remove_scan_directory).pack(pady=2)
        
        # Function buttons - grouped into Frame 1 (Content-based methods)
        method_frame1 = ttk.LabelFrame(main_frame, text="Content-Based Detection")
        method_frame1.pack(fill=tk.X, pady=5)
        
        ttk.Button(method_frame1, text="Find Duplicates by Hash (Most Accurate)", 
                 command=self.find_duplicates_by_hash,
                 width=40).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(method_frame1, text="Find Duplicates by Name & Size (Faster)", 
                 command=self.find_duplicates_by_name_size,
                 width=40).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Function buttons - Frame 2 (Advanced methods)
        method_frame2 = ttk.LabelFrame(main_frame, text="Advanced Methods")
        method_frame2.pack(fill=tk.X, pady=5)
        
        ttk.Button(method_frame2, text="Find Similar Files (Fuzzy Matching)", 
                 command=self.find_similar_files,
                 width=40).pack(side=tk.LEFT, padx=5, pady=5)
        
        ttk.Button(method_frame2, text="Scan Directories (Statistics)", 
                 command=self.scan_directory_stats,
                 width=40).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Stop button
        ttk.Button(main_frame, text="Stop Current Scan", 
                 command=self.stop_current_scan).pack(pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Results")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create a treeview for results
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_tree = ttk.Treeview(tree_frame, 
                                       yscrollcommand=tree_scroll_y.set,
                                       xscrollcommand=tree_scroll_x.set)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        tree_scroll_y.config(command=self.results_tree.yview)
        tree_scroll_x.config(command=self.results_tree.xview)
        
        # Configure treeview columns
        self.results_tree["columns"] = ("path", "size", "modified")
        self.results_tree.column("#0", width=50, minwidth=50)
        self.results_tree.column("path", width=400, minwidth=200)
        self.results_tree.column("size", width=100, minwidth=100)
        self.results_tree.column("modified", width=150, minwidth=150)
        
        self.results_tree.heading("#0", text="Group")
        self.results_tree.heading("path", text="File Path")
        self.results_tree.heading("size", text="Size")
        self.results_tree.heading("modified", text="Modified Date")
        
        # Buttons for actions
        action_frame = ttk.Frame(results_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Open Selected", 
                 command=self.open_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Delete Selected", 
                 command=self.delete_selected_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Keep Newest", 
                 command=self.keep_newest_duplicates).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Keep Oldest", 
                 command=self.keep_oldest_duplicates).pack(side=tk.LEFT, padx=5)
    
    def add_scan_directory(self):
        """Add a directory to scan for duplicates"""
        path = filedialog.askdirectory(title="Select Directory to Scan")
        if path:
            abs_path = os.path.abspath(path)
            if abs_path not in self.scan_directories:
                self.scan_directories.append(abs_path)
                self.scan_listbox.insert(tk.END, abs_path)
                self.status_label.config(text=f"Added directory: {abs_path}")
    
    def remove_scan_directory(self):
        """Remove a directory from scan list"""
        selection = self.scan_listbox.curselection()
        if selection:
            index = selection[0]
            path = self.scan_listbox.get(index)
            self.scan_directories.remove(path)
            self.scan_listbox.delete(index)
            self.status_label.config(text=f"Removed directory: {path}")
    
    def update_scan_progress(self, progress, message):
        """Update progress bar and status during scan"""
        # Use after() to update UI from a non-main thread
        self.parent.after(0, lambda: self.progress_bar.config(value=progress))
        self.parent.after(0, lambda: self.status_label.config(text=message))
    
    def clear_results_tree(self):
        """Clear the results treeview"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
    
    def find_duplicates_by_hash(self):
        """Find duplicates using content hash comparison"""
        if not self.scan_directories:
            messagebox.showinfo("No Directories", "Please add at least one directory to scan.")
            return
        
        self.clear_results_tree()
        self.progress_bar["value"] = 0
        
        def run_scan():
            try:
                self.update_scan_progress(0, "Starting hash-based duplicate scan...")
                duplicates = self.duplicate_finder.find_duplicates_by_hash(
                    self.scan_directories, self.update_scan_progress)
                
                self.parent.after(0, lambda: self.display_duplicate_results(duplicates))
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def find_duplicates_by_name_size(self):
        """Find duplicates using name and size comparison"""
        if not self.scan_directories:
            messagebox.showinfo("No Directories", "Please add at least one directory to scan.")
            return
        
        self.clear_results_tree()
        self.progress_bar["value"] = 0
        
        def run_scan():
            try:
                self.update_scan_progress(0, "Starting name/size-based duplicate scan...")
                duplicates = self.duplicate_finder.find_duplicates_by_name_size(
                    self.scan_directories, self.update_scan_progress)
                
                self.parent.after(0, lambda: self.display_duplicate_results(duplicates))
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def find_similar_files(self):
        """Find similar files using fuzzy matching"""
        if not self.scan_directories:
            messagebox.showinfo("No Directories", "Please add at least one directory to scan.")
            return
        
        # Ask user for similarity threshold
        threshold_dialog = tk.Toplevel(self.parent)
        threshold_dialog.title("Similarity Threshold")
        threshold_dialog.geometry("300x150")
        threshold_dialog.resizable(False, False)
        threshold_dialog.transient(self.parent)
        threshold_dialog.grab_set()
        
        ttk.Label(threshold_dialog, 
                text="Enter similarity threshold (0.1-1.0):").pack(pady=10)
        
        threshold_var = tk.StringVar(value="0.8")
        threshold_entry = ttk.Entry(threshold_dialog, textvariable=threshold_var)
        threshold_entry.pack(pady=5)
        
        def start_scan():
            try:
                threshold = float(threshold_var.get())
                if 0.1 <= threshold <= 1.0:
                    threshold_dialog.destroy()
                    
                    self.clear_results_tree()
                    self.progress_bar["value"] = 0
                    
                    def run_scan():
                        try:
                            self.update_scan_progress(0, f"Starting similarity scan (threshold: {threshold})...")
                            similar_files = self.duplicate_finder.find_similar_files(
                                self.scan_directories, threshold, self.update_scan_progress)
                            
                            self.parent.after(0, lambda: self.display_duplicate_results(similar_files))
                        except Exception as e:
                            self.parent.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
                    
                    threading.Thread(target=run_scan, daemon=True).start()
                else:
                    messagebox.showerror("Invalid Input", "Threshold must be between 0.1 and 1.0")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")
        
        button_frame = ttk.Frame(threshold_dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Start Scan", command=start_scan).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", 
                 command=threshold_dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def scan_directory_stats(self):
        """Scan directories for file statistics"""
        if not self.scan_directories:
            messagebox.showinfo("No Directories", "Please add at least one directory to scan.")
            return
        
        self.clear_results_tree()
        self.progress_bar["value"] = 0
        
        def run_scan():
            try:
                self.update_scan_progress(0, "Scanning directories for statistics...")
                stats = self.duplicate_finder.scan_directories(
                    self.scan_directories, self.update_scan_progress)
                
                self.parent.after(0, lambda: self.display_directory_stats(stats))
            except Exception as e:
                self.parent.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        
        threading.Thread(target=run_scan, daemon=True).start()
    
    def stop_current_scan(self):
        """Stop the current scanning operation"""
        if hasattr(self, 'duplicate_finder'):
            self.duplicate_finder.stop_scan()
            self.status_label.config(text="Scan stopped by user")
    
    def display_duplicate_results(self, duplicates):
        """Display duplicate/similar file results in the treeview"""
        self.clear_results_tree()
        
        if not duplicates:
            self.status_label.config(text="No duplicates or similar files found")
            return
        
        total_groups = len(duplicates)
        total_files = sum(len(files) for files in duplicates.values())
        wasted_space = 0
        
        group_num = 1
        for group_id, file_list in duplicates.items():
            # Calculate potential wasted space
            if file_list:
                try:
                    file_size = os.path.getsize(file_list[0])
                    wasted_space += file_size * (len(file_list) - 1)
                except Exception:
                    pass
            
            # Create group node
            group_node = self.results_tree.insert("", "end", text=f"Group {group_num}", 
                                              values=("", "", ""))
            
            # Add files to group
            for file_path in file_list:
                try:
                    size = os.path.getsize(file_path)
                    modified = datetime.datetime.fromtimestamp(
                        os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    
                    size_str = format_file_size(size)
                    
                    self.results_tree.insert(group_node, "end", text="", 
                                          values=(file_path, size_str, modified))
                except Exception as e:
                    self.results_tree.insert(group_node, "end", text="", 
                                          values=(file_path, "Error", str(e)))
            
            group_num += 1
        
        # Expand all groups for better visibility
        for item in self.results_tree.get_children():
            self.results_tree.item(item, open=True)
        
        # Update status
        wasted_space_str = format_file_size(wasted_space)
        self.status_label.config(
            text=f"Found {total_groups} groups ({total_files} files). Potential wasted space: {wasted_space_str}")
        self.progress_bar["value"] = 100
    
    def display_directory_stats(self, stats):
        """Display directory statistics in the treeview"""
        self.clear_results_tree()
        
        # Add summary node
        summary_node = self.results_tree.insert("", "end", text="Summary", 
                                             values=("", "", ""))
        
        total_size_str = format_file_size(stats['total_size'])
        
        self.results_tree.insert(summary_node, "end", text="", 
                              values=(f"Total Files: {stats['total_files']}", 
                                      f"Total Size: {total_size_str}", ""))
        
        # Add extensions node
        if stats['extensions']:
            extensions_node = self.results_tree.insert("", "end", text="Extensions", 
                                                    values=("", "", ""))
            
            for ext, ext_stats in sorted(stats['extensions'].items(), 
                                       key=lambda x: x[1]['size'], reverse=True):
                ext_size_str = format_file_size(ext_stats['size'])
                self.results_tree.insert(extensions_node, "end", text="", 
                                      values=(f"Extension: {ext or '(no extension)'}", 
                                              f"Count: {ext_stats['count']}", 
                                              f"Size: {ext_size_str}"))
        
        # Add largest files node
        if stats['largest_files']:
            largest_node = self.results_tree.insert("", "end", text="Largest Files", 
                                                 values=("", "", ""))
            
            for filepath, size in stats['largest_files']:
                size_str = format_file_size(size)
                modified = datetime.datetime.fromtimestamp(
                    os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                
                self.results_tree.insert(largest_node, "end", text="", 
                                      values=(filepath, size_str, modified))
        
        # Expand all nodes
        for item in self.results_tree.get_children():
            self.results_tree.item(item, open=True)
        
        # Update status
        self.status_label.config(
            text=f"Scanned {stats['total_files']} files, total size: {total_size_str}")
        self.progress_bar["value"] = 100
    
    def open_selected_file(self):
        """Open the directory of the selected file"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            values = self.results_tree.item(item, "values")
            
            # Check if this is a file entry (not a group)
            if values and values[0] and not values[0].startswith("Total") and not values[0].startswith("Extension"):
                file_path = values[0]
                try:
                    if open_file_location(file_path):
                        self.status_label.config(text=f"Opened location of: {file_path}")
                    else:
                        self.status_label.config(text=f"Could not open location: {file_path}")
                except Exception as e:
                    self.status_label.config(text=f"Error: {str(e)}")
    
    def delete_selected_file(self):
        """Delete the selected file"""
        selection = self.results_tree.selection()
        if selection:
            item = selection[0]
            values = self.results_tree.item(item, "values")
            
            # Check if this is a file entry (not a group)
            if values and values[0] and not values[0].startswith("Total") and not values[0].startswith("Extension"):
                file_path = values[0]
                
                confirm = messagebox.askyesno("Confirm Delete", 
                                           f"Are you sure you want to delete:\n{file_path}?")
                if confirm:
                    if safe_delete_file(file_path):
                        self.status_label.config(text=f"Deleted: {file_path}")
                        self.results_tree.delete(item)
                    else:
                        self.status_label.config(text=f"Failed to delete: {file_path}")
    
    def keep_newest_duplicates(self):
        """Keep newest file in each duplicate group and delete others"""
        # Get all groups
        groups = self.results_tree.get_children()
        if not groups:
            return
        
        # Confirm action
        confirm = messagebox.askyesno("Confirm Action", 
                                   "This will keep only the newest file in each group and delete all others. Continue?")
        if not confirm:
            return
        
        total_deleted = 0
        total_failed = 0
        
        for group_id in groups:
            # Skip non-duplicate groups (Summary, Extensions, etc.)
            group_text = self.results_tree.item(group_id, "text")
            if not group_text.startswith("Group"):
                continue
            
            # Get all files in the group
            files = self.results_tree.get_children(group_id)
            if len(files) <= 1:
                continue
                
            # Find newest file
            newest_item = None
            newest_time = datetime.datetime.min
            
            for item in files:
                values = self.results_tree.item(item, "values")
                file_path = values[0]
                try:
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time > newest_time:
                        newest_time = mod_time
                        newest_item = item
                except Exception:
                    continue
            
            # Delete all except newest
            if newest_item:
                for item in files:
                    if item != newest_item:
                        values = self.results_tree.item(item, "values")
                        file_path = values[0]
                        if safe_delete_file(file_path):
                            self.results_tree.delete(item)
                            total_deleted += 1
                        else:
                            total_failed += 1
        
        self.status_label.config(text=f"Deleted {total_deleted} files, {total_failed} failed")
    
    def keep_oldest_duplicates(self):
        """Keep oldest file in each duplicate group and delete others"""
        # Get all groups
        groups = self.results_tree.get_children()
        if not groups:
            return
        
        # Confirm action
        confirm = messagebox.askyesno("Confirm Action", 
                                   "This will keep only the oldest file in each group and delete all others. Continue?")
        if not confirm:
            return
        
        total_deleted = 0
        total_failed = 0
        
        for group_id in groups:
            # Skip non-duplicate groups (Summary, Extensions, etc.)
            group_text = self.results_tree.item(group_id, "text")
            if not group_text.startswith("Group"):
                continue
            
            # Get all files in the group
            files = self.results_tree.get_children(group_id)
            if len(files) <= 1:
                continue
                
            # Find oldest file
            oldest_item = None
            oldest_time = datetime.datetime.max
            
            for item in files:
                values = self.results_tree.item(item, "values")
                file_path = values[0]
                try:
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mod_time < oldest_time:
                        oldest_time = mod_time
                        oldest_item = item
                except Exception:
                    continue
            
            # Delete all except oldest
            if oldest_item:
                for item in files:
                    if item != oldest_item:
                        values = self.results_tree.item(item, "values")
                        file_path = values[0]
                        if safe_delete_file(file_path):
                            self.results_tree.delete(item)
                            total_deleted += 1
                        else:
                            total_failed += 1
        
        self.status_label.config(text=f"Deleted {total_deleted} files, {total_failed} failed")
