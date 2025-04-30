import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from .base_entity_tab import BaseEntityTab

class FlightTab(BaseEntityTab):
    """Tab for managing flights"""
    
    def __init__(self, parent, db_connection, flight_manager, location_manager):
        self.entity_name = "Flight"
        self.flight_manager = flight_manager
        self.location_manager = location_manager
        super().__init__(parent, db_connection)
    
    def _create_form_fields(self):
        """Create form fields for flight"""
        # Create variables
        self.flight_number_var = tk.StringVar()
        self.carrier_var = tk.StringVar()
        self.source_id = None
        self.source_var = tk.StringVar()
        self.destination_id = None
        self.destination_var = tk.StringVar()
        self.class_var = tk.StringVar()
        self.fare_var = tk.StringVar()
        self.departure_time_var = tk.StringVar()
        self.arrival_time_var = tk.StringVar()
        
        # Create form layout
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Flight Number
        ttk.Label(form_grid, text="Flight Number:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.flight_number_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Carrier
        ttk.Label(form_grid, text="Carrier:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.carrier_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Source
        ttk.Label(form_grid, text="Source:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Source selection frame
        source_frame = ttk.Frame(form_grid)
        source_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Source display
        self.source_label = ttk.Label(source_frame, textvariable=self.source_var, width=25)
        self.source_label.pack(side=tk.LEFT, padx=0, pady=0)
        
        # Source selection button
        ttk.Button(source_frame, text="Select", command=lambda: self.select_location("source")).pack(side=tk.LEFT, padx=5, pady=0)
        
        # Destination
        ttk.Label(form_grid, text="Destination:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Destination selection frame
        destination_frame = ttk.Frame(form_grid)
        destination_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Destination display
        self.destination_label = ttk.Label(destination_frame, textvariable=self.destination_var, width=25)
        self.destination_label.pack(side=tk.LEFT, padx=0, pady=0)
        
        # Destination selection button
        ttk.Button(destination_frame, text="Select", command=lambda: self.select_location("destination")).pack(side=tk.LEFT, padx=5, pady=0)
        
        # Class
        ttk.Label(form_grid, text="Class:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.class_combo = ttk.Combobox(form_grid, textvariable=self.class_var, width=28)
        self.class_combo['values'] = ('Economy', 'Premium Economy', 'Business', 'First')
        self.class_combo['state'] = 'readonly'
        self.class_combo.grid(row=4, column=1, padx=5, pady=5)
        
        # Fare
        ttk.Label(form_grid, text="Fare:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.fare_var, width=30).grid(row=5, column=1, padx=5, pady=5)
        
        # Departure Time
        ttk.Label(form_grid, text="Departure Time (YYYY-MM-DD HH:MM):").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.departure_time_var, width=30).grid(row=6, column=1, padx=5, pady=5)
        
        # Arrival Time
        ttk.Label(form_grid, text="Arrival Time (YYYY-MM-DD HH:MM):").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.arrival_time_var, width=30).grid(row=7, column=1, padx=5, pady=5)
    
    def select_location(self, location_type):
        """Open a dialog to select a location"""
        select_window = tk.Toplevel(self.parent)
        select_window.title(f"Select {location_type.capitalize()} Location")
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
            location_text = f"{values[1]}, {values[3]}"
            if values[2]:
                location_text = f"{values[1]}, {values[2]}, {values[3]}"
                
            if location_type == "source":
                self.source_id = values[0]
                self.source_var.set(location_text)
            else:
                self.destination_id = values[0]
                self.destination_var.set(location_text)
            
            # Close window
            select_window.destroy()
        
        ttk.Button(btn_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=select_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _create_treeview(self):
        """Create treeview for listing flights"""
        # Create treeview frame
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('Flight Number', 'Carrier', 'Source', 'Destination', 'Class', 'Fare', 'Departure', 'Arrival')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Define column widths
        self.tree.column('Flight Number', width=100)
        self.tree.column('Carrier', width=150)
        self.tree.column('Source', width=150)
        self.tree.column('Destination', width=150)
        self.tree.column('Class', width=100)
        self.tree.column('Fare', width=80)
        self.tree.column('Departure', width=150)
        self.tree.column('Arrival', width=150)
        
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
        """Load all flights"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all flights
        flights = self.flight_manager.get_all_flights()
        
        # Add to treeview
        for flight in flights:
            source = f"{flight['SourceCity']}, {flight['SourceCountry']}"
            destination = f"{flight['DestinationCity']}, {flight['DestinationCountry']}"
            
            self.tree.insert('', 'end', values=(
                flight['FlightNumber'],
                flight['Carrier'],
                source,
                destination,
                flight['Class'],
                flight['Fare'],
                flight['DepartureTime'],
                flight['ArrivalTime']
            ))
    
    def search_records(self):
        """Search flights"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_records()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search flights
        flights = self.flight_manager.search_flights(search_term)
        
        # Add to treeview
        for flight in flights:
            source = f"{flight['SourceCity']}, {flight['SourceCountry']}"
            destination = f"{flight['DestinationCity']}, {flight['DestinationCountry']}"
            
            self.tree.insert('', 'end', values=(
                flight['FlightNumber'],
                flight['Carrier'],
                source,
                destination,
                flight['Class'],
                flight['Fare'],
                flight['DepartureTime'],
                flight['ArrivalTime']
            ))
    
    def add_record(self):
        """Add a new flight"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.flight_manager.add_flight(data):
            messagebox.showinfo("Success", "Flight added successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to add flight")
    
    def update_record(self):
        """Update selected flight"""
        if not self.flight_number_var.get().strip():
            messagebox.showwarning("Warning", "Please select a flight to update")
            return
        
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.flight_manager.update_flight(self.flight_number_var.get().strip(), data):
            messagebox.showinfo("Success", "Flight updated successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to update flight")
    
    def delete_record(self):
        """Delete selected flight"""
        if not self.flight_number_var.get().strip():
            messagebox.showwarning("Warning", "Please select a flight to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this flight?"):
            if self.flight_manager.delete_flight(self.flight_number_var.get().strip()):
                messagebox.showinfo("Success", "Flight deleted successfully")
                self.clear_form()
                self.load_records()
            else:
                messagebox.showerror("Error", "Failed to delete flight. It may be referenced by bookings.")
    
    def clear_form(self):
        """Clear form fields"""
        self.flight_number_var.set("")
        self.carrier_var.set("")
        self.source_id = None
        self.source_var.set("")
        self.destination_id = None
        self.destination_var.set("")
        self.class_var.set("")
        self.fare_var.set("")
        self.departure_time_var.set("")
        self.arrival_time_var.set("")
    
    def load_selected_record(self, event):
        """Load selected flight into form"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get selected item values
        item = self.tree.item(selected_items[0])
        values = item['values']
        
        # Get full flight data
        flight = self.flight_manager.get_flight_by_number(values[0])
        
        # Set form values
        self.flight_number_var.set(flight['FlightNumber'])
        self.carrier_var.set(flight['Carrier'])
        
        # Set source
        self.source_id = flight['SourceID']
        source_text = f"{flight['SourceCity']}, {flight['SourceCountry']}"
        self.source_var.set(source_text)
        
        # Set destination
        self.destination_id = flight['DestinationID']
        destination_text = f"{flight['DestinationCity']}, {flight['DestinationCountry']}"
        self.destination_var.set(destination_text)
        
        # Set other fields
        self.class_var.set(flight['Class'])
        self.fare_var.set(flight['Fare'])
        self.departure_time_var.set(flight['DepartureTime'])
        self.arrival_time_var.set(flight['ArrivalTime'])
    
    def get_form_data(self):
        """Get data from form"""
        return {
            'flight_number': self.flight_number_var.get().strip(),
            'carrier': self.carrier_var.get().strip(),
            'source_id': self.source_id,
            'destination_id': self.destination_id,
            'class': self.class_var.get(),
            'fare': float(self.fare_var.get().strip()),
            'departure_time': self.departure_time_var.get().strip(),
            'arrival_time': self.arrival_time_var.get().strip()
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.flight_number_var.get().strip():
            messagebox.showerror("Validation Error", "Flight number is required")
            return False
        
        if not self.carrier_var.get().strip():
            messagebox.showerror("Validation Error", "Carrier is required")
            return False
        
        if not self.source_id:
            messagebox.showerror("Validation Error", "Source location is required")
            return False
        
        if not self.destination_id:
            messagebox.showerror("Validation Error", "Destination location is required")
            return False
        
        if self.source_id == self.destination_id:
            messagebox.showerror("Validation Error", "Source and destination cannot be the same")
            return False
        
        if not self.class_var.get():
            messagebox.showerror("Validation Error", "Class is required")
            return False
        
        if not self.fare_var.get().strip():
            messagebox.showerror("Validation Error", "Fare is required")
            return False
        
        try:
            fare = float(self.fare_var.get().strip())
            if fare <= 0:
                messagebox.showerror("Validation Error", "Fare must be greater than zero")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Fare must be a number")
            return False
        
        if not self.departure_time_var.get().strip():
            messagebox.showerror("Validation Error", "Departure time is required")
            return False
        
        if not self.arrival_time_var.get().strip():
            messagebox.showerror("Validation Error", "Arrival time is required")
            return False
        
        # Validate datetime format
        try:
            departure_time = datetime.strptime(self.departure_time_var.get().strip(), '%Y-%m-%d %H:%M')
        except ValueError:
            messagebox.showerror("Validation Error", "Departure time must be in YYYY-MM-DD HH:MM format")
            return False
        
        try:
            arrival_time = datetime.strptime(self.arrival_time_var.get().strip(), '%Y-%m-%d %H:%M')
        except ValueError:
            messagebox.showerror("Validation Error", "Arrival time must be in YYYY-MM-DD HH:MM format")
            return False
        
        if departure_time >= arrival_time:
            messagebox.showerror("Validation Error", "Departure time must be before arrival time")
            return False
        
        return True
