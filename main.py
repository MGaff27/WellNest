import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar
import json
# to help check for files using os
import os
# to help find date in a string
import re

from datetime import datetime

# Dictionary to hold appointments
appointments = {}
# Dictionary to hold prescriptions
prescriptions = {}
# File to store appointments
appointments_file = "appointments.json"
#file to store prescription
prescriptions_file= "prescription.json"

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

#Function to create prescription ID
current_id=123 #initialized
def prescription_id():
    global current_id
    current_id += 1
    return current_id

#Function to create appointment ID
appoint_id=456 #initialized
def appointment_id():
    global appoint_id
    appoint_id += 1
    return appoint_id

# Load prescription when starting the application
get_prescriptions()

# Load appointments when starting the application
get_appointments()


# Function to show calendar options
def open_calendar():
    def calendar_menu():
        calendar_window = tk.Toplevel(root)
        calendar_window.title("Calendar")
        calendar_window.minsize(800,600)
        # calendar frame
        calendar_frame = tk.Frame(calendar_window)
        calendar_frame.pack(pady=20,fill='both', expand=True)

        # Calendar widget
        cal = Calendar(calendar_frame, selectmode='day',
                       date_pattern="yyyy-mm-dd",
                       font="Arial 12",
                       foreground="black",
                       height=800,
                       width=800,
                       background="#87CEFA",  # Light sky blue background for the calendar
                       headersbackground="#4682B4",  # Steel blue for the header
                       headersforeground="white",  # White text for the header
                       selectforeground="white",  # White text for selected dates
                       selectbackground="#1E90FF",  # Dodger blue for selected dates
                       weekendforeground="#FF4500",  # Orange-red for weekends
                       weekendbackground="#87CEFA",  # Light sky blue background for weekends
                       othermonthforeground="#A9A9A9",  # Dark gray for other month dates
                       othermonthbackground="#87CEFA",  # Light sky blue for other month dates
                       disabledforeground="#B0C4DE",  # Light steel blue for disabled dates
                       )
        cal.pack(pady=10, fill='both', expand=True)

        def display_appointments(): # to display the appointments on the calendar visually

            for appoint_id, details in appointments.items():
                for detail in details:
                    # Extract the date from the appointment string
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', detail)
                    if match:
                        appointment_date_str = match.group(1)
                        appointment_date = datetime.strptime(appointment_date_str,
                                                             '%Y-%m-%d').date()  # Convert to date object

                        # Create calendar event
                        cal.calevent_create(appointment_date, detail, 'reminder')

            cal.tag_config('reminder', background='red', foreground='yellow')
        def show_appointment():
            selected_date = cal.get_date()
            appointments_for_date = []

            for appoint_id, details in appointments.items():
                for detail in details:
                    # Using regex to find the date in the appointment string
                    match = re.search(r'(\d{4}-\d{2}-\d{2})', detail)
                    if match and match.group(1) == selected_date:
                        appointments_for_date.append(detail)

            if appointments_for_date:
                events_str = "\n".join(appointments_for_date)
                messagebox.showinfo("Day View", f"Appointments on {selected_date}:\n{events_str}")
            else:
                messagebox.showwarning("No appointments", "A chill day.")
        def show_pills():
            selected_date = cal.get_date()
            messagebox.showinfo("Pill View", f"Showing pills for the day of: {selected_date}")

        def show_task():
            selected_date = cal.get_date()
            messagebox.showinfo("Task View", f"Showing task for the day of: {selected_date}")


        tk.Button(calendar_window, text="View appointment", command=show_appointment).pack(pady=5)
        tk.Button(calendar_window, text="View pills", command=show_pills).pack(pady=5)
        tk.Button(calendar_window, text="View task", command=show_task).pack(pady=5)
        tk.Button(calendar_window, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)
        display_appointments()
    calendar_menu()


# Function to manage prescriptions
def open_prescription():
    def prescription_menu():
        prescription_window = tk.Toplevel(root)
        prescription_window.title("Prescription Menu")
        prescription_window.minsize(400,600)

        def current_prescriptions():
            if prescriptions:
                # list of id and name pairs
                prescription_list = []
                for current_id, details in prescriptions.items():
                    pill_name = details[0].split('.')[1].strip()  # This splits string to get 'ID: {id} & {name}. ...'
                    prescription_list.append(f"ID: {current_id}, Name: {pill_name}")

                # Join all prescription details into a single string for display
                prescriptions_str = "\n".join(prescription_list)

                # Show the prescriptions in a message box
                messagebox.showinfo("Current Prescriptions", f"Medications:\n{prescriptions_str}")
            else:
                messagebox.showwarning("Prescriptions", "No current prescriptions.")
        def add_prescription():
            pill_name = simpledialog.askstring("Input", "Enter the name of the pill ( In all CAPS.eg... OZEMPIC:")
            dosage = simpledialog.askstring("Input", "Enter the dosage:")
            purpose = simpledialog.askstring("Input", "Give a brief description of the purpose of the medication:")
            instructions = simpledialog.askstring("Input", "State if medication is taken on an empty stomach or not:")
            duration = simpledialog.askstring("Input", "How many days will this pill be taken for?")

            if all([pill_name, dosage, purpose, instructions, duration]):
                    current_id= prescription_id()
                    prescription_info = f"ID: {current_id}. {pill_name}. Dosage: {dosage}.Purpose: {purpose}. Instructions: {instructions}. Duration (days): {duration}"
                    prescriptions[current_id] = [prescription_info]
                    save_prescription()  # Save prescription after adding
                    messagebox.showinfo("Prescription Information",f"Prescription added {prescription_info}")

            else:
                      messagebox.showwarning("Input Error", "All fields must be filled out.")



        def remove_prescription():
            pill_name = simpledialog.askstring("Input", "Enter the name of the pill to remove:")
            current_id= simpledialog.askstring("Input","Enter pill ID")
            if pill_name and current_id in prescriptions:
                del prescriptions[current_id]
                save_prescription()  # Save prescription after removing
                messagebox.showinfo("Removed Prescription", f"{pill_name} was removed.")

            else:
                messagebox.showwarning("Remove Error", "No prescription found with that name, Ensure name is in ALL CAPS.")


        def close_prescription():
            prescription_window.destroy()

        tk.Label(prescription_window, text="My Pharmacy:").pack(pady=5)
        tk.Button(prescription_window, text="Current Prescriptions", command=current_prescriptions).pack(pady=20)
        tk.Button(prescription_window, text="Add Prescription", command=add_prescription).pack(pady=20)
        tk.Button(prescription_window, text="Remove Prescription", command=remove_prescription).pack(pady=20)
        tk.Button(prescription_window, text="Back to Main Menu", command=close_prescription).pack(pady=20)

    prescription_menu()


# Function to manage appointments
def open_appointments():
    def appointment_menu():
        appointment_window = tk.Toplevel(root)
        appointment_window.title("Appointment Menu")
        appointment_window.minsize(400, 600)
        def add_appointment():
            appointment_date = simpledialog.askstring("Input", "Enter the date of your appointment (e.g., 2024-10-01):")
            time = simpledialog.askstring("Input", "Enter the time:")
            doctor_name = simpledialog.askstring("Input", "Your doctor's name (e.g. , Dr. .....:")
            location = simpledialog.askstring("Input", "Location:")
            reason = simpledialog.askstring("Input", "Give a brief description for your visit:")

            if all([appointment_date, time, doctor_name, location, reason]):
                appoint_id= appointment_id()
                appointment_info = f"ID: {appoint_id}. Your appointment is on {appointment_date} at {time} with {doctor_name} in {location}. Reason: {reason}"
                appointments[appoint_id] = [appointment_info]
                save_appointments()  # Save appointments after adding
                messagebox.showinfo("Appointment Information",f"Appointment added for {appointment_info}")
            else:

                messagebox.showwarning("Input Error", "All fields must be filled out.")

        def remove_appointment():

                 appointment_date = simpledialog.askstring("Input", "Enter the date of the appointment to remove:..eg. 2024-11-29")
                 appoint_id= simpledialog.askstring("Input", "Enter appointment ID:")
                 if appointment_date and appoint_id in appointments:
                   del appointments [appoint_id]
                   save_appointments()  # Save appointments after removing
                   messagebox.showinfo("Remove Appointment", f"Removed appointment on {appointment_date}.")

                 else:
                  messagebox.showwarning("Remove Error", "No appointments found on that date.")

        def close_appointment():
            appointment_window.destroy()

        tk.Label(appointment_window, text="Appointment Menu:").pack(pady=5)
        tk.Button(appointment_window, text="Add Appointment", command=add_appointment).pack(pady=20)
        tk.Button(appointment_window, text="Remove Appointment", command=remove_appointment).pack(pady=20)
        tk.Button(appointment_window, text="Back to Main Menu", command=close_appointment).pack(pady=20)

    appointment_menu()


# Function to close the application
def close_app():
    root.quit()


# the main window
root = tk.Tk()
root.title("WellNest")
root.geometry("400x600") # size of window for main

# buttons for each function
calendar_button = tk.Button(root, text="Calendar", command=open_calendar)
calendar_button.pack(pady=30) #space between buttons

prescription_button = tk.Button(root, text="Prescription", command=open_prescription)
prescription_button.pack(pady=30)

appointments_button = tk.Button(root, text="Appointments", command=open_appointments)
appointments_button.pack(pady=30)

close_button = tk.Button(root, text="Close", command=close_app)
close_button.pack(pady=30)

# Run the application
root.mainloop()
