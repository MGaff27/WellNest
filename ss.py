import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import json
import os
from datetime import datetime

# Dictionary to hold appointments, prescriptions, and tasks
appointments = {}
prescriptions = {}
tasks = {}

# Files to store data
appointments_file = "appointments.json"
prescriptions_file = "prescriptions.json"
tasks_file = "tasks.json"

# Function to get prescriptions from a file
def get_prescriptions():
    global prescriptions
    if os.path.exists(prescriptions_file):
        with open(prescriptions_file, "r") as file:
            prescriptions = json.load(file)

# Function to save prescription to a file
def save_prescription():
    with open(prescriptions_file, "w") as file:
        json.dump(prescriptions, file)

# Function to get appointments from a file
def get_appointments():
    global appointments
    if os.path.exists(appointments_file):
        with open(appointments_file, "r") as file:
            appointments = json.load(file)

# Function to save appointments to a file
def save_appointments():
    with open(appointments_file, "w") as file:
        json.dump(appointments, file)

# Function to get tasks from a file
def get_tasks():
    global tasks
    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as file:
            tasks = json.load(file)

# Function to save tasks to a file
def save_tasks():
    with open(tasks_file, "w") as file:
        json.dump(tasks, file)

# Load data on app start
get_prescriptions()
get_appointments()
get_tasks()

# Function to open the calendar and manage tasks, appointments, and prescriptions
def open_calendar():
    def calendar_menu():
        calendar_window = tk.Toplevel(root)
        calendar_window.title("Calendar")
        calendar_window.minsize(800, 600)

        calendar_frame = tk.Frame(calendar_window)
        calendar_frame.pack(pady=20, fill='both', expand=True)

        # Initialize the Calendar
        cal = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd")
        cal.pack(pady=10, fill='both', expand=True)

        # Display pills, appointments, and tasks on the calendar
        def display_items():
            # Clear existing events
            cal.calevent_remove('all')

            for date, pills in prescriptions.items():
                # Add each pill name as an event on the calendar with smaller text
                pill_event = "\n".join([f"Pill: {pill.split()[0]}" for pill in pills])  # Display only pill name
                cal.calevent_create(datetime.strptime(date, '%Y-%m-%d'), pill_event, 'pill')

            for date, apps in appointments.items():
                app_event = "\n".join([f"Appointment: {app}" for app in apps])
                cal.calevent_create(datetime.strptime(date, '%Y-%m-%d'), app_event, 'appointment')

            for date, task_list in tasks.items():
                task_event = "\n".join([f"Task: {task}" for task in task_list])
                cal.calevent_create(datetime.strptime(date, '%Y-%m-%d'), task_event, 'task')

            cal.tag_config('pill', background='lightgreen', foreground='black')
            cal.tag_config('appointment', background='lightblue', foreground='black')
            cal.tag_config('task', background='lightyellow', foreground='black')

        # Function to add a prescription for the selected date
        def add_prescription(selected_date=None):
            if not selected_date:
                selected_date = cal.get_date()

            pill_name = simpledialog.askstring("Input", "Enter the name of the pill (In all CAPS, e.g., OZEMPIC):")
            dosage = simpledialog.askstring("Input", "Enter the dosage:")
            purpose = simpledialog.askstring("Input", "Brief description of the medication's purpose:")
            instructions = simpledialog.askstring("Input", "Instructions (e.g., on an empty stomach):")
            duration = simpledialog.askstring("Input", "How many days will this pill be taken?")

            if all([pill_name, dosage, purpose, instructions, duration]):
                prescription_info = f"{pill_name} (Dosage: {dosage}, Purpose: {purpose}, Instructions: {instructions}, Duration: {duration} days)"
                if selected_date not in prescriptions:
                    prescriptions[selected_date] = []
                prescriptions[selected_date].append(prescription_info)
                save_prescription()  # Save prescriptions after adding
                messagebox.showinfo("Prescription Added", f"Prescription for {pill_name} added on {selected_date}")
                display_items()  # Update calendar with new pill
            else:
                messagebox.showwarning("Input Error", "All fields must be filled out.")

        # Make calendar clickable to add prescriptions
        def on_date_click(event):
            selected_date = cal.get_date()
            add_prescription(selected_date)

        cal.bind("<<CalendarSelected>>", on_date_click)

        # Function to view all items on the selected date
        def show_items():
            selected_date = cal.get_date()
            items = []
            if selected_date in prescriptions:
                items.append(f"Prescriptions: {', '.join(prescriptions[selected_date])}")
            if selected_date in appointments:
                items.append(f"Appointments: {', '.join(appointments[selected_date])}")
            if selected_date in tasks:
                items.append(f"Tasks: {', '.join(tasks[selected_date])}")
            if items:
                messagebox.showinfo(f"Items for {selected_date}", "\n".join(items))
            else:
                messagebox.showinfo(f"Items for {selected_date}", "No items found for this date.")

        # Buttons to view and add items to the selected date
        tk.Button(calendar_window, text="View Items", command=show_items).pack(pady=5)
        tk.Button(calendar_window, text="Add Prescription", command=add_prescription).pack(pady=5)
        tk.Button(calendar_window, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)

        # Display the existing items on the calendar
        display_items()

    calendar_menu()

# Function to manage prescriptions
def open_prescription():
    def prescription_menu():
        prescription_window = tk.Toplevel(root)
        prescription_window.title("Prescription Menu")
        prescription_window.minsize(400, 600)

        # Function to view current prescriptions
        def current_prescriptions():
            if prescriptions:
                prescription_list = []
                for date, details in prescriptions.items():
                    for prescription in details:
                        prescription_list.append(f"Date: {date}, Details: {prescription}")
                prescriptions_str = "\n".join(prescription_list)
                messagebox.showinfo("Current Prescriptions", f"Medications:\n{prescriptions_str}")
            else:
                messagebox.showwarning("Prescriptions", "No current prescriptions.")

        # Function to remove a prescription
        def remove_prescription():
            selected_date = simpledialog.askstring("Input", "Enter the date of the prescription (e.g., 2024-10-01):")
            pill_name = simpledialog.askstring("Input", "Enter the name of the pill to remove:")
            if selected_date in prescriptions:
                for prescription in prescriptions[selected_date]:
                    if pill_name in prescription:
                        prescriptions[selected_date].remove(prescription)
                        save_prescription()  # Save prescriptions after removing
                        messagebox.showinfo("Prescription Removed", f"Prescription for {pill_name} removed.")
                        break
                else:
                    messagebox.showwarning("Remove Error", f"No prescription found for {pill_name} on {selected_date}.")
            else:
                messagebox.showwarning("Remove Error", "No prescriptions found for the selected date.")

        def close_prescription():
            prescription_window.destroy()

        tk.Label(prescription_window, text="Prescription Menu:").pack(pady=5)
        tk.Button(prescription_window, text="View Current Prescriptions", command=current_prescriptions).pack(pady=20)
        tk.Button(prescription_window, text="Remove Prescription", command=remove_prescription).pack(pady=20)
        tk.Button(prescription_window, text="Close Menu", command=close_prescription).pack(pady=20)

    prescription_menu()

# Function to manage appointments
def open_appointments():
    def appointment_menu():
        appointment_window = tk.Toplevel(root)
        appointment_window.title("Appointment Menu")
        appointment_window.minsize(400, 600)

        # Function to add an appointment
        def add_appointment():
            appointment_date = simpledialog.askstring("Input", "Enter the date of your appointment (e.g., 2024-10-01):")
            time = simpledialog.askstring("Input", "Enter the time:")
            doctor_name = simpledialog.askstring("Input", "Your doctor's name:")
            location = simpledialog.askstring("Input", "Location:")
            reason = simpledialog.askstring("Input", "Brief description for your visit:")

            if all([appointment_date, time, doctor_name, location, reason]):
                appointment_info = f"Appointment with Dr. {doctor_name} at {time} in {location}. Reason: {reason}"
                if appointment_date not in appointments:
                    appointments[appointment_date] = []
                appointments[appointment_date].append(appointment_info)
                save_appointments()
                messagebox.showinfo("Appointment Added", f"Appointment added on {appointment_date}")
            else:
                messagebox.showwarning("Input Error", "All fields must be filled out.")

        # Function to remove an appointment
        def remove_appointment():
            appointment_date = simpledialog.askstring("Input", "Enter the date of the appointment to remove (e.g., 2024-10-01):")
            if appointment_date in appointments:
                del appointments[appointment_date]
                save_appointments()
                messagebox.showinfo("Appointment Removed", f"Removed appointment on {appointment_date}.")
            else:
                messagebox.showwarning("Remove Error", f"No appointments found on {appointment_date}.")

        def close_appointment():
            appointment_window.destroy()

        tk.Label(appointment_window, text="Appointment Menu:").pack(pady=5)
        tk.Button(appointment_window, text="Add Appointment", command=add_appointment).pack(pady=20)
        tk.Button(appointment_window, text="Remove Appointment", command=remove_appointment).pack(pady=20)
        tk.Button(appointment_window, text="Close Menu", command=close_appointment).pack(pady=20)

    appointment_menu()

# Function to close the application
def close_app():
    root.quit()

# Main window
root = tk.Tk()
root.title("WellNest")
root.geometry("400x600")  # Size of window for main menu

# Buttons for each function
calendar_button = tk.Button(root, text="Calendar", command=open_calendar)
calendar_button.pack(pady=30)

prescription_button = tk.Button(root, text="Prescription", command=open_prescription)
prescription_button.pack(pady=30)

appointments_button = tk.Button(root, text="Appointments", command=open_appointments)
appointments_button.pack(pady=30)

close_button = tk.Button(root, text="Close", command=close_app)
close_button.pack(pady=30)

# Run the application
root.mainloop()
