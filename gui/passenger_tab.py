import tkinter as tk
from tkinter import ttk, messagebox

from .base_entity_tab import BaseEntityTab

class PassengerTab(BaseEntityTab):
    """Tab for managing passengers"""
    
    def __init__(self, parent, db_connection, passenger_manager):
        self.entity_name = "Passenger"
        self.passenger_manager = passenger_manager
        super().__init__(parent, db_connection)
    
    def _create_form_fields(self):
        """Create form fields for passenger"""
        # Create variables
        self.passenger_id = None
        self.name_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        
        # Create form layout
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name
        ttk.Label(form_grid, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Gender
        ttk.Label(form_grid, text="Gender:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gender_combo = ttk.Combobox(form_grid, textvariable=self.gender_var, width=28)
        self.gender_combo['values'] = ('Male', 'Female', 'Other')
        self.gender_combo['state'] = 'readonly'
        self.gender_combo.grid(row=1, column=1, padx=5, pady=5)
        
        # Age
        ttk.Label(form_grid, text="Age:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.age_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Email
        ttk.Label(form_grid, text="Email:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.email_var, width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Phone
        ttk.Label(form_grid, text="Phone:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.phone_var, width=30).grid(row=4, column=1, padx=5, pady=5)
    
    def _create_treeview(self):
        """Create treeview for listing passengers"""
        # Create treeview frame
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'Name', 'Gender', 'Age', 'Email', 'Phone')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Define column widths
        self.tree.column('ID', width=50)
        self.tree.column('Name', width=150)
        self.tree.column('Gender', width=80)
        self.tree.column('Age', width=50)
        self.tree.column('Email', width=200)
        self.tree.column('Phone', width=120)
        
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
        """Load all passengers"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all passengers
        passengers = self.passenger_manager.get_all_passengers()
        
        # Add to treeview
        for passenger in passengers:
            self.tree.insert('', 'end', values=(
                passenger['PassengerID'],
                passenger['Name'],
                passenger['Gender'] or '',
                passenger['Age'],
                passenger['Email'] or '',
                passenger['Phone'] or ''
            ))
    
    def search_records(self):
        """Search passengers"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_records()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search passengers
        passengers = self.passenger_manager.search_passengers(search_term)
        
        # Add to treeview
        for passenger in passengers:
            self.tree.insert('', 'end', values=(
                passenger['PassengerID'],
                passenger['Name'],
                passenger['Gender'] or '',
                passenger['Age'],
                passenger['Email'] or '',
                passenger['Phone'] or ''
            ))
    
    def add_record(self):
        """Add a new passenger"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.passenger_manager.add_passenger(data):
            messagebox.showinfo("Success", "Passenger added successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to add passenger")
    
    def update_record(self):
        """Update selected passenger"""
        if not self.passenger_id:
            messagebox.showwarning("Warning", "Please select a passenger to update")
            return
        
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.passenger_manager.update_passenger(self.passenger_id, data):
            messagebox.showinfo("Success", "Passenger updated successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to update passenger")
    
    def delete_record(self):
        """Delete selected passenger"""
        if not self.passenger_id:
            messagebox.showwarning("Warning", "Please select a passenger to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this passenger?"):
            if self.passenger_manager.delete_passenger(self.passenger_id):
                messagebox.showinfo("Success", "Passenger deleted successfully")
                self.clear_form()
                self.load_records()
            else:
                messagebox.showerror("Error", "Failed to delete passenger. It may be referenced by bookings or travel groups.")
    
    def clear_form(self):
        """Clear form fields"""
        self.passenger_id = None
        self.name_var.set("")
        self.gender_var.set("")
        self.age_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
    
    def load_selected_record(self, event):
        """Load selected passenger into form"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get selected item values
        item = self.tree.item(selected_items[0])
        values = item['values']
        
        # Set form values
        self.passenger_id = values[0]
        self.name_var.set(values[1])
        self.gender_var.set(values[2])
        self.age_var.set(values[3])
        self.email_var.set(values[4])
        self.phone_var.set(values[5])
    
    def get_form_data(self):
        """Get data from form"""
        return {
            'name': self.name_var.get().strip(),
            'gender': self.gender_var.get() or None,
            'age': int(self.age_var.get().strip()) if self.age_var.get().strip() else None,
            'email': self.email_var.get().strip() or None,
            'phone': self.phone_var.get().strip() or None
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False
        
        if self.age_var.get().strip():
            try:
                age = int(self.age_var.get().strip())
                if age < 0 or age > 120:
                    messagebox.showerror("Validation Error", "Age must be between 0 and 120")
                    return False
            except ValueError:
                messagebox.showerror("Validation Error", "Age must be a number")
                return False
        
        return True
