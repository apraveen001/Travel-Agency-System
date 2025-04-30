# main.py
import tkinter as tk
from tkinter import ttk
from database.db_connection import DatabaseConnection

# managers
from modules.accommodation_manager   import AccommodationManager
from modules.admin_employee_manager  import AdminEmployeeManager
from modules.flight_manager          import FlightManager
from modules.location_manager        import LocationManager
from modules.passenger_manager       import PassengerManager

# GUI tabs
from gui.accommodation_tab    import AccommodationTab
from gui.admin_employee_tab   import AdminEmployeeTab
from gui.flight_tab           import FlightTab
from gui.location_tab         import LocationTab
from gui.passenger_tab        import PassengerTab


def main():
    # 1) Database
    db = DatabaseConnection()
    db.connect()

    # 2) Managers
    location_mgr      = LocationManager(db)
    flight_mgr        = FlightManager(db)
    accommodation_mgr = AccommodationManager(db)
    admin_employee_mgr = AdminEmployeeManager(db)
    passenger_mgr     = PassengerManager(db)
    # …add other managers as needed…

    # 3) Tk root + notebook
    root = tk.Tk()
    root.title("Travel Agency Management System")
    root.geometry("1024x768")
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # 4) Tabs (note FlightTab now gets location_mgr too)
    tabs = [
        ("Locations",     LocationTab,      (notebook, db, location_mgr)),
        ("Flights",       FlightTab,        (notebook, db, flight_mgr, location_mgr)),
        ("Accommodation", AccommodationTab, (notebook, db, accommodation_mgr, location_mgr)),
        ("Employees",     AdminEmployeeTab, (notebook, db, admin_employee_mgr)),
        ("Passengers",    PassengerTab,     (notebook, db, passenger_mgr)),
        # …more tabs…
    ]
    for title, TabClass, args in tabs:
        tab = TabClass(*args)
        notebook.add(tab.frame, text=title)

    # 5) Run
    root.mainloop()
    # 6) Cleanup
    db.disconnect()


if __name__ == "__main__":
    main()
