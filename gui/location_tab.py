import tkinter as tk
from tkinter import ttk, messagebox

from .base_entity_tab import BaseEntityTab

class LocationTab(BaseEntityTab):
    """Tab for managing locations"""
    
    def __init__(self, parent, db_connection, location_manager):
        self.entity_name = "Location"
        self.location_manager = location_manager
        super().__init__(parent, db_connection)
    
    def _create_form_fields(self):
        """Create form fields for location"""
        # Create variables
        self.location_id = None
        self.city_var = tk.StringVar()
        self.state_var = tk.StringVar()
        self.country_var = tk.StringVar()
        
        # Create form layout
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # City
        ttk.Label(form_grid, text="City:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.city_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # State
        ttk.Label(form_grid, text="State:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.state_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Country
        ttk.Label(form_grid, text="Country:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.country_var, width=30).grid(row=2, column=1, padx=5, pady=5)
    
    def _create_treeview(self):
        """Create treeview for listing locations"""
        # Create treeview frame
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'City', 'State', 'Country')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Define column widths
        self.tree.column('ID', width=50)
        self.tree.column('City', width=150)
        self.tree.column('State', width=150)
        self.tree.column('Country', width=150)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.load_selected_record)
    
    def load_records(self):
        """Load all locations"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all locations
        locations = self.location_manager.get_all_locations()
        
        # Add to treeview
        for location in locations:
            self.tree.insert('', 'end', values=(
                location['LocationID'],
                location['City'],
                location['State'] or '',
                location['Country']
            ))
    
    def search_records(self):
        """Search locations"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_records()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search locations
        locations = self.location_manager.search_locations(search_term)
        
        # Add to treeview
        for location in locations:
            self.tree.insert('', 'end', values=(
                location['LocationID'],
                location['City'],
                location['State'] or '',
                location['Country']
            ))
    
    def add_record(self):
        """Add a new location"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.location_manager.add_location(data):
            messagebox.showinfo("Success", "Location added successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to add location")
    
    def update_record(self):
        """Update selected location"""
        if not self.location_id:
            messagebox.showwarning("Warning", "Please select a location to update")
            return
        
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.location_manager.update_location(self.location_id, data):
            messagebox.showinfo("Success", "Location updated successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to update location")
    
    def delete_record(self):
        """Delete selected location"""
        if not self.location_id:
            messagebox.showwarning("Warning", "Please select a location to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this location?"):
            if self.location_manager.delete_location(self.location_id):
                messagebox.showinfo("Success", "Location deleted successfully")
                self.clear_form()
                self.load_records()
            else:
                messagebox.showerror("Error", "Failed to delete location. It may be referenced by other records.")
    
    def clear_form(self):
        """Clear form fields"""
        self.location_id = None
        self.city_var.set("")
        self.state_var.set("")
        self.country_var.set("")
    
    def load_selected_record(self, event):
        """Load selected location into form"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get selected item values
        item = self.tree.item(selected_items[0])
        values = item['values']
        
        # Set form values
        self.location_id = values[0]
        self.city_var.set(values[1])
        self.state_var.set(values[2])
        self.country_var.set(values[3])
    
    def get_form_data(self):
        """Get data from form"""
        return {
            'city': self.city_var.get().strip(),
            'state': self.state_var.get().strip() or None,
            'country': self.country_var.get().strip()
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.city_var.get().strip():
            messagebox.showerror("Validation Error", "City is required")
            return False
        
        if not self.country_var.get().strip():
            messagebox.showerror("Validation Error", "Country is required")
            return False
        
        return True
