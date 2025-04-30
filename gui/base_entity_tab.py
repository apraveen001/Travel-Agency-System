import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

class BaseEntityTab:
    """Base class for entity tabs with common functionality"""
    
    def __init__(self, parent, db_connection):
        self.parent = parent
        self.db = db_connection
        self.frame = ttk.Frame(parent)
        
        # Create split layout
        self.paned_window = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel for form
        self.form_frame = ttk.LabelFrame(self.paned_window, text=f"{self.entity_name} Details")
        
        # Right panel for list
        self.list_frame = ttk.Frame(self.paned_window)
        
        self.paned_window.add(self.form_frame, weight=40)
        self.paned_window.add(self.list_frame, weight=60)
        
        # Search frame above the list
        self.search_frame = ttk.Frame(self.list_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Search", command=self.search_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Create form fields
        self._create_form_fields()
        
        # Create action buttons
        self._create_action_buttons()
        
        # Create treeview for list
        self._create_treeview()
        
        # Load initial data
        self.load_records()
    
    def _create_form_fields(self):
        """Create form fields - to be implemented by subclasses"""
        pass
    
    def _create_action_buttons(self):
        """Create action buttons for CRUD operations"""
        btn_frame = ttk.Frame(self.form_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Update", command=self.update_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
    
    def _create_treeview(self):
        """Create treeview for listing records - to be implemented by subclasses"""
        pass
    
    def load_records(self):
        """Load all records - to be implemented by subclasses"""
        pass
    
    def search_records(self):
        """Search records - to be implemented by subclasses"""
        pass
    
    def clear_search(self):
        """Clear search and reload all records"""
        self.search_var.set("")
        self.load_records()
    
    def add_record(self):
        """Add a new record - to be implemented by subclasses"""
        pass
    
    def update_record(self):
        """Update selected record - to be implemented by subclasses"""
        pass
    
    def delete_record(self):
        """Delete selected record - to be implemented by subclasses"""
        pass
    
    def clear_form(self):
        """Clear form fields - to be implemented by subclasses"""
        pass
    
    def load_selected_record(self, event):
        """Load selected record into form - to be implemented by subclasses"""
        pass
    
    def get_form_data(self):
        """Get data from form - to be implemented by subclasses"""
        pass
    
    def validate_form(self):
        """Validate form data - to be implemented by subclasses"""
        return True
