#!/usr/bin/env python3
"""
search_packhum_gui.py - GUI interface for searching iphi.json using tkinter
"""

import json
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from tkinter import BooleanVar, StringVar, IntVar
from collections import defaultdict
import threading
from pathlib import Path

class PackhumSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Packhum Greek Inscriptions Search")
        self.root.geometry("1400x900")
        
        # Data storage
        self.data = None
        self.current_results = []
        
        # Create GUI
        self.create_menu()
        self.create_search_frame()
        self.create_results_frame()
        self.create_status_bar()
        
        # Load data
        self.load_data()
    
    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load JSON...", command=self.load_data_dialog)
        file_menu.add_command(label="Export Results to CSV...", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_search_frame(self):
        """Create search filters frame"""
        search_frame = ttk.LabelFrame(self.root, text="Search Filters", padding=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(search_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Basic Search
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Search")
        self.create_basic_tab(basic_frame)
        
        # Tab 2: Region Search
        region_frame = ttk.Frame(notebook)
        notebook.add(region_frame, text="Region Search")
        self.create_region_tab(region_frame)
        
        # Tab 3: Date Search
        date_frame = ttk.Frame(notebook)
        notebook.add(date_frame, text="Date Search")
        self.create_date_tab(date_frame)
        
        # Search button frame
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.search_button = ttk.Button(button_frame, text="🔍 Search", command=self.search, width=20)
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🗑 Clear All", command=self.clear_filters, width=20)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(button_frame, text="")
        self.status_label.pack(side=tk.RIGHT, padx=5)
    
    def create_basic_tab(self, parent):
        """Create basic search tab"""
        # Text search
        ttk.Label(parent, text="Text (Greek inscription):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.text_var = StringVar()
        self.text_entry = ttk.Entry(parent, textvariable=self.text_var, width=60)
        self.text_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Metadata search
        ttk.Label(parent, text="Metadata:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.metadata_var = StringVar()
        self.metadata_entry = ttk.Entry(parent, textvariable=self.metadata_var, width=60)
        self.metadata_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # ID search
        ttk.Label(parent, text="ID (exact):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.id_var = StringVar()
        self.id_entry = ttk.Entry(parent, textvariable=self.id_var, width=20)
        self.id_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
    
    def create_region_tab(self, parent):
        """Create region search tab"""
        # Region Main ID
        ttk.Label(parent, text="Region Main ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.region_main_id_var = StringVar()
        self.region_main_id_entry = ttk.Entry(parent, textvariable=self.region_main_id_var, width=20)
        self.region_main_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Region Main Name
        ttk.Label(parent, text="Region Main Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.region_main_var = StringVar()
        self.region_main_entry = ttk.Entry(parent, textvariable=self.region_main_var, width=40)
        self.region_main_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Region Sub ID
        ttk.Label(parent, text="Region Sub ID:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.region_sub_id_var = StringVar()
        self.region_sub_id_entry = ttk.Entry(parent, textvariable=self.region_sub_id_var, width=20)
        self.region_sub_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Region Sub Name
        ttk.Label(parent, text="Region Sub Name:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.region_sub_var = StringVar()
        self.region_sub_entry = ttk.Entry(parent, textvariable=self.region_sub_var, width=40)
        self.region_sub_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Precedence info
        info_label = ttk.Label(parent, text="Note: If both ID and name are provided, ID takes precedence", 
                               foreground="gray")
        info_label.grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_date_tab(self, parent):
        """Create date search tab"""
        # Date string
        ttk.Label(parent, text="Date String:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_str_var = StringVar()
        self.date_str_entry = ttk.Entry(parent, textvariable=self.date_str_var, width=40)
        self.date_str_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Date min
        ttk.Label(parent, text="Date Min (year):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_min_var = StringVar()
        self.date_min_entry = ttk.Entry(parent, textvariable=self.date_min_var, width=15)
        self.date_min_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Date max
        ttk.Label(parent, text="Date Max (year):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_max_var = StringVar()
        self.date_max_entry = ttk.Entry(parent, textvariable=self.date_max_var, width=15)
        self.date_max_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Date circa
        self.date_circa_var = BooleanVar()
        self.date_circa_check = ttk.Checkbutton(parent, text="Circa Dating", variable=self.date_circa_var)
        self.date_circa_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
    
    def create_results_frame(self):
        """Create results display frame with all columns"""
        results_frame = ttk.LabelFrame(self.root, text="Search Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Results count label
        self.results_count_label = ttk.Label(results_frame, text="No results", font=("Arial", 10, "bold"))
        self.results_count_label.pack(anchor=tk.W, pady=5)
        
        # Create a frame for treeview and scrollbars
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Define all columns matching CSV export
        columns = ("ID", "Text", "Metadata", "Region Main", "Region Main ID", 
                   "Region Sub", "Region Sub ID", "Date String", "Date Min", 
                   "Date Max", "Date Circa")
        
        # Create Treeview for results
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Define headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Text", text="Text")
        self.tree.heading("Metadata", text="Metadata")
        self.tree.heading("Region Main", text="Region Main")
        self.tree.heading("Region Main ID", text="Region Main ID")
        self.tree.heading("Region Sub", text="Region Sub")
        self.tree.heading("Region Sub ID", text="Region Sub ID")
        self.tree.heading("Date String", text="Date String")
        self.tree.heading("Date Min", text="Date Min")
        self.tree.heading("Date Max", text="Date Max")
        self.tree.heading("Date Circa", text="Date Circa")
        
        # Define column widths
        self.tree.column("ID", width=80)
        self.tree.column("Text", width=300)
        self.tree.column("Metadata", width=250)
        self.tree.column("Region Main", width=150)
        self.tree.column("Region Main ID", width=100)
        self.tree.column("Region Sub", width=150)
        self.tree.column("Region Sub ID", width=100)
        self.tree.column("Date String", width=120)
        self.tree.column("Date Min", width=80)
        self.tree.column("Date Max", width=80)
        self.tree.column("Date Circa", width=80)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Use grid for tree_frame children only
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights for tree_frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_result_select)
        
        # Details text area
        details_frame = ttk.LabelFrame(results_frame, text="Entry Details", padding=5)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_data(self, filename="iphi.json"):
        """Load JSON data in background thread"""
        self.status_bar.config(text=f"Loading {filename}...")
        self.search_button.config(state=tk.DISABLED)
        
        def load():
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                self.root.after(0, self.on_data_loaded, filename)
            except Exception as e:
                self.root.after(0, self.on_load_error, str(e))
        
        thread = threading.Thread(target=load)
        thread.daemon = True
        thread.start()
    
    def on_data_loaded(self, filename):
        """Callback when data is loaded"""
        self.status_bar.config(text=f"Loaded {len(self.data):,} entries from {filename}")
        self.search_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Loaded {len(self.data):,} entries from {filename}")
    
    def on_load_error(self, error):
        """Callback when load fails"""
        self.status_bar.config(text=f"Error loading file")
        self.search_button.config(state=tk.NORMAL)
        messagebox.showerror("Error", f"Failed to load JSON file:\n{error}")
    
    def load_data_dialog(self):
        """Open file dialog to load JSON"""
        filename = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.load_data(filename)
    
    def search(self):
        """Perform search based on filters"""
        if not self.data:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.details_text.delete(1.0, tk.END)
        
        # Build filters
        filters = {}
        
        # Basic filters
        if self.text_var.get().strip():
            filters['text'] = self.text_var.get().strip()
        if self.metadata_var.get().strip():
            filters['metadata'] = self.metadata_var.get().strip()
        if self.id_var.get().strip():
            try:
                filters['id'] = int(self.id_var.get().strip())
            except ValueError:
                messagebox.showwarning("Warning", "ID must be a number")
                return
        
        # Region filters (ID takes precedence)
        if self.region_main_id_var.get().strip():
            filters['region_main_id'] = self.region_main_id_var.get().strip()
        elif self.region_main_var.get().strip():
            filters['region_main'] = self.region_main_var.get().strip()
        
        if self.region_sub_id_var.get().strip():
            filters['region_sub_id'] = self.region_sub_id_var.get().strip()
        elif self.region_sub_var.get().strip():
            filters['region_sub'] = self.region_sub_var.get().strip()
        
        # Date filters
        if self.date_str_var.get().strip():
            filters['date_str'] = self.date_str_var.get().strip()
        if self.date_min_var.get().strip():
            filters['date_min'] = self.date_min_var.get().strip()
        if self.date_max_var.get().strip():
            filters['date_max'] = self.date_max_var.get().strip()
        if self.date_circa_var.get():
            filters['date_circa'] = True
        
        if not filters:
            messagebox.showwarning("Warning", "Please enter at least one search filter")
            return
        
        # Perform search
        self.status_bar.config(text="Searching...")
        self.search_button.config(state=tk.DISABLED)
        
        def search_thread():
            results = self.search_entries(filters)
            self.root.after(0, self.display_results, results)
        
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def search_entries(self, filters):
        """Search entries based on filters"""
        results = []
        
        for entry in self.data:
            match = True
            for field, search_value in filters.items():
                field_value = entry.get(field, '')
                
                # Special handling for ID (exact match)
                if field == 'id':
                    if field_value != search_value:
                        match = False
                        break
                # Special handling for date_circa (boolean)
                elif field == 'date_circa':
                    if field_value != search_value:
                        match = False
                        break
                # For other fields, substring match (case-insensitive)
                else:
                    if search_value.lower() not in str(field_value).lower():
                        match = False
                        break
            
            if match:
                results.append(entry)
        
        return results
    
    def display_results(self, results):
        """Display search results in treeview with all columns"""
        self.current_results = results
        
        # Update count label
        self.results_count_label.config(text=f"Found {len(results):,} matching entries")
        self.status_bar.config(text=f"Search complete - {len(results):,} results")
        self.search_button.config(state=tk.NORMAL)
        
        # Populate tree with all columns
        for result in results[:2000]:  # Limit to 2000 for performance
            self.tree.insert("", tk.END, values=(
                result.get('id', 'N/A'),
                result.get('text', 'N/A')[:200] + "..." if len(result.get('text', '')) > 200 else result.get('text', 'N/A'),
                result.get('metadata', 'N/A')[:150] + "..." if len(result.get('metadata', '')) > 150 else result.get('metadata', 'N/A'),
                result.get('region_main', 'N/A'),
                result.get('region_main_id', 'N/A'),
                result.get('region_sub', 'N/A'),
                result.get('region_sub_id', 'N/A'),
                result.get('date_str', 'N/A'),
                result.get('date_min', 'N/A'),
                result.get('date_max', 'N/A'),
                result.get('date_circa', 'N/A')
            ), tags=(result.get('id', ''),))
        
        if len(results) > 2000:
            self.status_bar.config(text=f"Showing first 2000 of {len(results):,} results")
    
    def on_result_select(self, event):
        """Handle result selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get the ID from the selected item
        item = self.tree.item(selection[0])
        values = item['values']
        if not values:
            return
        
        # Find the full entry
        selected_id = values[0]
        full_entry = None
        
        for result in self.current_results:
            if result.get('id') == selected_id:
                full_entry = result
                break
        
        if full_entry:
            self.display_entry_details(full_entry)
    
    def display_entry_details(self, entry):
        """Display full entry details in text area"""
        self.details_text.delete(1.0, tk.END)
        
        details = f"""
{'='*70}
ID: {entry.get('id', 'N/A')}
{'='*70}

TEXT:
{entry.get('text', 'N/A')}

METADATA:
{entry.get('metadata', 'N/A')}

REGION:
  Main: {entry.get('region_main', 'N/A')} (ID: {entry.get('region_main_id', 'N/A')})
  Sub: {entry.get('region_sub', 'N/A')} (ID: {entry.get('region_sub_id', 'N/A')})

DATE:
  String: {entry.get('date_str', 'N/A')}
  Min: {entry.get('date_min', 'N/A')}
  Max: {entry.get('date_max', 'N/A')}
  Circa: {entry.get('date_circa', 'N/A')}
"""
        self.details_text.insert(1.0, details)
    
    def export_results(self):
        """Export current results to CSV with all columns"""
        if not self.current_results:
            messagebox.showwarning("Warning", "No results to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save CSV file",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Complete field list matching the CSV from command line version
                fieldnames = ['id', 'text', 'metadata', 'region_main', 'region_main_id',
                             'region_sub', 'region_sub_id', 'date_str', 'date_min', 
                             'date_max', 'date_circa']
                
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(self.current_results)
                
                messagebox.showinfo("Success", f"Exported {len(self.current_results):,} results to {filename}")
                self.status_bar.config(text=f"Exported {len(self.current_results):,} results")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def clear_filters(self):
        """Clear all filter fields"""
        self.text_var.set("")
        self.metadata_var.set("")
        self.id_var.set("")
        self.region_main_id_var.set("")
        self.region_main_var.set("")
        self.region_sub_id_var.set("")
        self.region_sub_var.set("")
        self.date_str_var.set("")
        self.date_min_var.set("")
        self.date_max_var.set("")
        self.date_circa_var.set(False)
        
        # Clear results
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.details_text.delete(1.0, tk.END)
        self.results_count_label.config(text="No results")
        self.current_results = []
        self.status_bar.config(text="Filters cleared")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Packhum Greek Inscriptions Search

A graphical interface for searching the iphi.json database of Greek inscriptions.

Features:
- Search by text, metadata, ID
- Search by region (name or ID)
- Search by date criteria
- Export results to CSV with all fields
- View full entry details
- All columns from CSV export displayed

Data source: Packhum Greek Inscriptions (iphi.json)
Version: 1.0
"""
        messagebox.showinfo("About", about_text)

def main():
    root = tk.Tk()
    app = PackhumSearchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()