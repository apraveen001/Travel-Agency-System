import tkinter as tk
from tkinter import ttk, messagebox
import json

from .base_entity_tab import BaseEntityTab

class AccommodationTab(BaseEntityTab):
    """Tab for managing accommodations"""
    
    def __init__(self, parent, db_connection, accommodation_manager, location_manager):
        self.entity_name = "Accommodation"
        self.accommodation_manager = accommodation_manager
        self.location_manager = location_manager
        super().__init__(parent, db_connection)
    
    def _create_form_fields(self):
        """Create form fields for accommodation"""
        # Create variables
        self.accommodation_id = None
        self.name_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.rate_var = tk.StringVar()
        self.location_id = None
        self.location_var = tk.StringVar()
        self.facilities_var = tk.StringVar()
        self.discount_var = tk.StringVar()
        
        # Create form layout
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name
        ttk.Label(form_grid, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Type
        ttk.Label(form_grid, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.type_combo = ttk.Combobox(form_grid, textvariable=self.type_var, width=28)
        self.type_combo['values'] = ('Hotel', 'Resort', 'Villa', 'Hostel')
        self.type_combo['state'] = 'readonly'
        self.type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Rate
        ttk.Label(form_grid, text="Rate:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.rate_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Location
        ttk.Label(form_grid, text="Location:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Location selection frame
        location_frame = ttk.Frame(form_grid)
        location_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Location display
        self.location_label = ttk.Label(location_frame, textvariable=self.location_var, width=25)
        self.location_label.pack(side=tk.LEFT, padx=0, pady=0)
        
        # Location selection button
        ttk.Button(location_frame, text="Select", command=self.select_location).pack(side=tk.LEFT, padx=5, pady=0)
        
        # Facilities
        ttk.Label(form_grid, text="Facilities (JSON):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        facilities_frame = ttk.Frame(form_grid)
        facilities_frame.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.facilities_text = tk.Text(facilities_frame, width=30, height=5)
        self.facilities_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        facilities_scroll = ttk.Scrollbar(facilities_frame, command=self.facilities_text.yview)
        facilities_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.facilities_text.config(yscrollcommand=facilities_scroll.set)
        
        # Discount
        ttk.Label(form_grid, text="Discount (%):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.discount_var, width=30).grid(row=5, column=1, padx=5, pady=5)
    
    def select_location(self):
        """Open a dialog to select a location"""
        select_window = tk.Toplevel(self.parent)
        select_window.title("Select Location")
        select_window.geometry("600x400")
        select_window.transient(self.parent)
        select_window.grab_set()
        
        # Create treeview
        tree_frame = ttk.Frame(select_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'City', 'State', 'Country')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            
        # Define column widths
        tree.column('ID', width=50)
        tree.column('City', width=150)
        tree.column('State', width=150)
        tree.column('Country', width=150)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        # Load locations
        locations = self.location_manager.get_all_locations()
        
        # Add to treeview
        for location in locations:
            tree.insert('', 'end', values=(
                location['LocationID'],
                location['City'],
                location['State'] or '',
                location['Country']
            ))
        
        # Search frame
        search_frame = ttk.Frame(select_window)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        def search_locations():
            search_term = search_var.get().strip()
            if not search_term:
                return
                
            # Clear existing items
            for item in tree.get_children():
                tree.delete(item)
            
            # Search locations
            locations = self.location_manager.search_locations(search_term)
            
            # Add to treeview
            for location in locations:
                tree.insert('', 'end', values=(
                    location['LocationID'],
                    location['City'],
                    location['State'] or '',
                    location['Country']
                ))
        
        ttk.Button(search_frame, text="Search", command=search_locations).pack(side=tk.LEFT, padx=5)
        
        # Button frame
        btn_frame = ttk.Frame(select_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Select button
        def on_select():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "Please select a location", parent=select_window)
                return
                
            # Get selected item values
            item = tree.item(selected_items[0])
            values = item['values']
            
            # Set location
            self.location_id = values[0]
            location_text = f"{values[1]}, {values[3]}"
            if values[2]:
                location_text = f"{values[1]}, {values[2]}, {values[3]}"
            self.location_var.set(location_text)
            
            # Close window
            select_window.destroy()
        
        ttk.Button(btn_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=select_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _create_treeview(self):
        """Create treeview for listing accommodations"""
        # Create treeview frame
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'Name', 'Type', 'Rate', 'Location', 'Discount')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Define column widths
        self.tree.column('ID', width=50)
        self.tree.column('Name', width=150)
        self.tree.column('Type', width=100)
        self.tree.column('Rate', width=80)
        self.tree.column('Location', width=200)
        self.tree.column('Discount', width=80)
        
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
        """Load all accommodations"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all accommodations
        accommodations = self.accommodation_manager.get_all_accommodations()
        
        # Add to treeview
        for accommodation in accommodations:
            location = f"{accommodation['City']}, {accommodation['Country']}"
            self.tree.insert('', 'end', values=(
                accommodation['AccommodationID'],
                accommodation['Name'],
                accommodation['Type'],
                accommodation['Rate'],
                location,
                accommodation['Discount']
            ))
    
    def search_records(self):
        """Search accommodations"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_records()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search accommodations
        accommodations = self.accommodation_manager.search_accommodations(search_term)
        
        # Add to treeview
        for accommodation in accommodations:
            location = f"{accommodation['City']}, {accommodation['Country']}"
            self.tree.insert('', 'end', values=(
                accommodation['AccommodationID'],
                accommodation['Name'],
                accommodation['Type'],
                accommodation['Rate'],
                location,
                accommodation['Discount']
            ))
    
    def add_record(self):
        """Add a new accommodation"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.accommodation_manager.add_accommodation(data):
            messagebox.showinfo("Success", "Accommodation added successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to add accommodation")
    
    def update_record(self):
        """Update selected accommodation"""
        if not self.accommodation_id:
            messagebox.showwarning("Warning", "Please select an accommodation to update")
            return
        
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.accommodation_manager.update_accommodation(self.accommodation_id, data):
            messagebox.showinfo("Success", "Accommodation updated successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to update accommodation")
    
    def delete_record(self):
        """Delete selected accommodation"""
        if not self.accommodation_id:
            messagebox.showwarning("Warning", "Please select an accommodation to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this accommodation?"):
            if self.accommodation_manager.delete_accommodation(self.accommodation_id):
                messagebox.showinfo("Success", "Accommodation deleted successfully")
                self.clear_form()
                self.load_records()
            else:
                messagebox.showerror("Error", "Failed to delete accommodation. It may be referenced by bookings.")
    
    def clear_form(self):
        """Clear form fields"""
        self.accommodation_id = None
        self.name_var.set("")
        self.type_var.set("")
        self.rate_var.set("")
        self.location_id = None
        self.location_var.set("")
        self.facilities_text.delete('1.0', tk.END)
        self.discount_var.set("")
    
    def load_selected_record(self, event):
        """Load selected accommodation into form"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get selected item values
        item = self.tree.item(selected_items[0])
        values = item['values']
        
        # Get full accommodation data
        accommodation = self.accommodation_manager.get_accommodation_by_id(values[0])
        
        # Set form values
        self.accommodation_id = accommodation['AccommodationID']
        self.name_var.set(accommodation['Name'])
        self.type_var.set(accommodation['Type'])
        self.rate_var.set(accommodation['Rate'])
        
        # Set location
        self.location_id = accommodation['LocationID']
        location_text = f"{accommodation['City']}, {accommodation['Country']}"
        self.location_var.set(location_text)
        
        # Set facilities
        self.facilities_text.delete('1.0', tk.END)
        if accommodation['Facilities']:
            if isinstance(accommodation['Facilities'], str):
                self.facilities_text.insert('1.0', accommodation['Facilities'])
            else:
                self.facilities_text.insert('1.0', json.dumps(accommodation['Facilities'], indent=2))
        
        # Set discount
        self.discount_var.set(accommodation['Discount'])
    
    def get_form_data(self):
        """Get data from form"""
        # Parse facilities JSON
        facilities_json = self.facilities_text.get('1.0', tk.END).strip()
        if facilities_json:
            try:
                facilities = json.loads(facilities_json)
            except json.JSONDecodeError:
                facilities = facilities_json
        else:
            facilities = None
        
        # Parse discount
        discount = self.discount_var.get().strip()
        if discount:
            try:
                discount = float(discount)
            except ValueError:
                discount = 0.0
        else:
            discount = 0.0
        
        return {
            'name': self.name_var.get().strip(),
            'type': self.type_var.get(),
            'rate': float(self.rate_var.get().strip()),
            'location_id': self.location_id,
            'facilities': facilities,
            'discount': discount
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False
        
        if not self.type_var.get():
            messagebox.showerror("Validation Error", "Type is required")
            return False
        
        if not self.rate_var.get().strip():
            messagebox.showerror("Validation Error", "Rate is required")
            return False
        
        try:
            rate = float(self.rate_var.get().strip())
            if rate <= 0:
                messagebox.showerror("Validation Error", "Rate must be greater than zero")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Rate must be a number")
            return False
        
        if not self.location_id:
            messagebox.showerror("Validation Error", "Location is required")
            return False
        
        # Validate facilities JSON
        facilities_json = self.facilities_text.get('1.0', tk.END).strip()
        if facilities_json:
            try:
                json.loads(facilities_json)
            except json.JSONDecodeError:
                messagebox.showerror("Validation Error", "Facilities must be valid JSON")
                return False
        
        # Validate discount
        discount = self.discount_var.get().strip()
        if discount:
            try:
                discount_val = float(discount)
                if discount_val < 0 or discount_val > 100:
                    messagebox.showerror("Validation Error", "Discount must be between 0 and 100")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Discount must be a number")
                return False
        
        return True
