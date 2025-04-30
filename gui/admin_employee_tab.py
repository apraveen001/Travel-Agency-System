import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from .base_entity_tab import BaseEntityTab

class AdminEmployeeTab(BaseEntityTab):
    """Tab for managing admin employees"""
    
    def __init__(self, parent, db_connection, employee_manager):
        self.entity_name = "Admin Employee"
        self.employee_manager = employee_manager
        super().__init__(parent, db_connection)
    
    def _create_form_fields(self):
        """Create form fields for admin employee"""
        # Create variables
        self.employee_id = None
        self.name_var = tk.StringVar()
        self.role_var = tk.StringVar()
        self.join_date_var = tk.StringVar()
        self.supervisor_id = None
        self.supervisor_var = tk.StringVar()
        
        # Create form layout
        form_grid = ttk.Frame(self.form_frame)
        form_grid.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Name
        ttk.Label(form_grid, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Role
        ttk.Label(form_grid, text="Role:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.role_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Join Date
        ttk.Label(form_grid, text="Join Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(form_grid, textvariable=self.join_date_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        # Supervisor
        ttk.Label(form_grid, text="Supervisor:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Supervisor selection frame
        supervisor_frame = ttk.Frame(form_grid)
        supervisor_frame.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Supervisor display
        self.supervisor_label = ttk.Label(supervisor_frame, textvariable=self.supervisor_var, width=25)
        self.supervisor_label.pack(side=tk.LEFT, padx=0, pady=0)
        
        # Supervisor selection button
        ttk.Button(supervisor_frame, text="Select", command=self.select_supervisor).pack(side=tk.LEFT, padx=5, pady=0)
        ttk.Button(supervisor_frame, text="Clear", command=self.clear_supervisor).pack(side=tk.LEFT, padx=0, pady=0)
    
    def select_supervisor(self):
        """Open a dialog to select a supervisor"""
        select_window = tk.Toplevel(self.parent)
        select_window.title("Select Supervisor")
        select_window.geometry("500x400")
        select_window.transient(self.parent)
        select_window.grab_set()
        
        # Create treeview
        tree_frame = ttk.Frame(select_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Name', 'Role')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            
        # Define column widths
        tree.column('ID', width=50)
        tree.column('Name', width=200)
        tree.column('Role', width=150)
        
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
        
        # Load employees
        employees = self.employee_manager.get_all_employees()
        
        # Add to treeview
        for employee in employees:
            # Skip the current employee if editing
            if self.employee_id and employee['EmployeeID'] == self.employee_id:
                continue
                
            tree.insert('', 'end', values=(
                employee['EmployeeID'],
                employee['Name'],
                employee['Role']
            ))
        
        # Button frame
        btn_frame = ttk.Frame(select_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Select button
        def on_select():
            selected_items = tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "Please select a supervisor", parent=select_window)
                return
                
            # Get selected item values
            item = tree.item(selected_items[0])
            values = item['values']
            
            # Set supervisor
            self.supervisor_id = values[0]
            self.supervisor_var.set(values[1])
            
            # Close window
            select_window.destroy()
        
        ttk.Button(btn_frame, text="Select", command=on_select).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=select_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def clear_supervisor(self):
        """Clear selected supervisor"""
        self.supervisor_id = None
        self.supervisor_var.set("")
    
    def _create_treeview(self):
        """Create treeview for listing admin employees"""
        # Create treeview frame
        tree_frame = ttk.Frame(self.list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview
        columns = ('ID', 'Name', 'Role', 'Join Date', 'Supervisor')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            
        # Define column widths
        self.tree.column('ID', width=50)
        self.tree.column('Name', width=150)
        self.tree.column('Role', width=150)
        self.tree.column('Join Date', width=100)
        self.tree.column('Supervisor', width=150)
        
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
        """Load all admin employees"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all employees
        employees = self.employee_manager.get_all_employees()
        
        # Add to treeview
        for employee in employees:
            self.tree.insert('', 'end', values=(
                employee['EmployeeID'],
                employee['Name'],
                employee['Role'],
                employee['JoinDate'],
                employee.get('SupervisorName', '')
            ))
    
    def search_records(self):
        """Search admin employees"""
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_records()
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Search employees
        employees = self.employee_manager.search_employees(search_term)
        
        # Add to treeview
        for employee in employees:
            self.tree.insert('', 'end', values=(
                employee['EmployeeID'],
                employee['Name'],
                employee['Role'],
                employee['JoinDate'],
                employee.get('SupervisorName', '')
            ))
    
    def add_record(self):
        """Add a new admin employee"""
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.employee_manager.add_employee(data):
            messagebox.showinfo("Success", "Admin employee added successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to add admin employee")
    
    def update_record(self):
        """Update selected admin employee"""
        if not self.employee_id:
            messagebox.showwarning("Warning", "Please select an admin employee to update")
            return
        
        if not self.validate_form():
            return
        
        data = self.get_form_data()
        if self.employee_manager.update_employee(self.employee_id, data):
            messagebox.showinfo("Success", "Admin employee updated successfully")
            self.clear_form()
            self.load_records()
        else:
            messagebox.showerror("Error", "Failed to update admin employee")
    
    def delete_record(self):
        """Delete selected admin employee"""
        if not self.employee_id:
            messagebox.showwarning("Warning", "Please select an admin employee to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this admin employee?"):
            if self.employee_manager.delete_employee(self.employee_id):
                messagebox.showinfo("Success", "Admin employee deleted successfully")
                self.clear_form()
                self.load_records()
            else:
                messagebox.showerror("Error", "Failed to delete admin employee. It may be referenced by other records.")
    
    def clear_form(self):
        """Clear form fields"""
        self.employee_id = None
        self.name_var.set("")
        self.role_var.set("")
        self.join_date_var.set("")
        self.supervisor_id = None
        self.supervisor_var.set("")
    
    def load_selected_record(self, event):
        """Load selected admin employee into form"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get selected item values
        item = self.tree.item(selected_items[0])
        values = item['values']
        
        # Get full employee data
        employee = self.employee_manager.get_employee_by_id(values[0])
        
        # Set form values
        self.employee_id = employee['EmployeeID']
        self.name_var.set(employee['Name'])
        self.role_var.set(employee['Role'])
        self.join_date_var.set(employee['JoinDate'])
        
        # Set supervisor
        if employee['SupervisorID']:
            self.supervisor_id = employee['SupervisorID']
            self.supervisor_var.set(employee.get('SupervisorName', ''))
        else:
            self.supervisor_id = None
            self.supervisor_var.set("")
    
    def get_form_data(self):
        """Get data from form"""
        return {
            'name': self.name_var.get().strip(),
            'role': self.role_var.get().strip(),
            'join_date': self.join_date_var.get().strip(),
            'supervisor_id': self.supervisor_id
        }
    
    def validate_form(self):
        """Validate form data"""
        if not self.name_var.get().strip():
            messagebox.showerror("Validation Error", "Name is required")
            return False
        
        if not self.role_var.get().strip():
            messagebox.showerror("Validation Error", "Role is required")
            return False
        
        if not self.join_date_var.get().strip():
            messagebox.showerror("Validation Error", "Join date is required")
            return False
        
        # Validate date format
        try:
            datetime.strptime(self.join_date_var.get().strip(), '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Validation Error", "Join date must be in YYYY-MM-DD format")
            return False
        
        return True
