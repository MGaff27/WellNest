#SECTION 1
import threading
from tkinter import Menu
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Checkbutton, IntVar
from tkcalendar import Calendar
import json
import os

import pyttsx3
from plyer import notification
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import datetime
import time
from datetime import datetime, timedelta
from threading import Timer

# Files to store data
appointments_file = "appointments.json"
prescriptions_file = "prescriptions.json"
tasks_file = "tasks.json"
notes_file = "notes.json"

# Global variables
appointments = {}
tasks = {}
notes = {}
prescriptions = {}
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Firebase Initialization
#cred = credentials.Certificate("firebase_credentials.json")
#firebase_admin.initialize_app(cred)
#db = firestore.client()

# Load prescriptions from the JSON file
def load_prescriptions(filename="prescriptions.json"):
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            try:
                return json.load(json_file)
            except json.JSONDecodeError:
                messagebox.showwarning("Notice", "The prescriptions file is empty or invalid. Starting fresh.")
                return {}
    return {}

# Save prescriptions to the JSON file
def save_prescriptions(data, filename="prescriptions.json"):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Load data on app start
def load_data():
    global prescriptions, appointments, tasks, notes
    prescriptions = load_prescriptions()  # Load prescriptions with the new function
    if os.path.exists(appointments_file):
        with open(appointments_file, "r") as file:
            appointments = json.load(file)
    if os.path.exists(tasks_file):
        with open(tasks_file, "r") as file:
            tasks = json.load(file)
    if os.path.exists(notes_file):
        with open(notes_file, "r") as file:
            notes = json.load(file)

# Save data to files
def save_data():
    save_prescriptions(prescriptions)  # Save prescriptions with the new function
    with open(appointments_file, "w") as file:
        json.dump(appointments, file)
    with open(tasks_file, "w") as file:
        json.dump(tasks, file)
    with open(notes_file, "w") as file:
        json.dump(notes, file)



#SECTION 2

# Google Calendar Authentication
def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# Validate future dates
def validate_future_date(selected_date):
    today = datetime.now().strftime('%Y-%m-%d')
    if selected_date < today:
        messagebox.showerror("Date Error", "Cannot add tasks or appointments to a past date.")
        return False
    return True

# Show Splash Screen
def splash_screen():
    splash = tk.Toplevel()
    splash.geometry("600x400")
    splash.overrideredirect(True)
    splash.title("WellNest")

    splash_img = Image.open("wellnest_splash_final.png")
    splash_img = splash_img.resize((600, 400), Image.Resampling.LANCZOS)
    splash_img = ImageTk.PhotoImage(splash_img)

    splash_label = tk.Label(splash, image=splash_img)
    splash_label.image = splash_img
    splash_label.pack()

    splash.after(3000, lambda: close_splash_and_show_main(splash))

# Close splash and show main window
def close_splash_and_show_main(splash):
    splash.destroy()
    root.deiconify()

#SECTION 3

# User login/signup with Firebase
def signup_user():
    email = simpledialog.askstring("Signup", "Enter email:")
    password = simpledialog.askstring("Signup", "Enter password:", show="*")
    if email and password:
        db.collection('users').document(email).set({'password': password})
        messagebox.showinfo("Signup", "Signup successful!")

def login_user():
    email = simpledialog.askstring("Login", "Enter email:")
    password = simpledialog.askstring("Login", "Enter password:", show="*")
    user = db.collection('users').document(email).get()
    if user.exists and user.to_dict()['password'] == password:
        messagebox.showinfo("Login", "Login successful!")
    else:
        messagebox.showerror("Login", "Invalid credentials")

# Medication Schedule and Tracking
def add_medication_schedule():
    selected_date = simpledialog.askstring("Medication Schedule", "Enter the date for medication schedule (yyyy-mm-dd):")
    if not validate_future_date(selected_date):
        return
    med_name = simpledialog.askstring("Medication", "Enter the medication name:")
    if selected_date and med_name:
        prescriptions[selected_date] = {'medication': med_name, 'status': 'scheduled'}
        save_data()

def submit(day_entry, month_entry, year_entry, days_entry, weeks_entry,
           prescription_name_entry, medication_description_entry, food_entry, window):
    startDay = day_entry.get()
    startMon = month_entry.get()
    startYr = year_entry.get()
    days = days_entry.get().split(",")  # Comma-separated input for days
    numWeeks = weeks_entry.get()
    prescription_name = prescription_name_entry.get()
    medication_description = medication_description_entry.get().strip()
    taken_with_food = food_entry.get().strip()

    # Validate inputs
    try:
        start_date = datetime(int(startYr), int(startMon), int(startDay))
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid start date.")
        return

    if not prescription_name:
        messagebox.showerror("Input Error", "Please enter a prescription name.")
        return

    if not medication_description:
        messagebox.showerror("Input Error", "Please enter a medication description.")
        return

    try:
        numWeeks = int(numWeeks)
        if numWeeks <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid positive number for weeks.")
        return

    medication_info = {
        "Description": medication_description,
        "Taken with food": taken_with_food
    }

    try:
        # Schedule prescriptions
        prescriptionDays = prescriptionScheduler(startDay, startMon, startYr, days, numWeeks, medication_info)
        prescriptions[prescription_name] = prescriptionDays  # Save to global dictionary
        save_prescriptions(prescriptions)  # Save all prescriptions back to file
        messagebox.showinfo("Success", f"Prescription '{prescription_name}' saved successfully!")
        window.destroy()  # Close the prescription window on success
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Function to open a new window for prescription management
def open_prescription_manager():
    # Create a new top-level window
    prescription_window = tk.Toplevel(root)
    prescription_window.title("Prescription Manager")
    prescription_window.geometry("300x400")  # Adjust the size as needed

    # Add input fields to the new window
    tk.Label(prescription_window, text="Prescription Name:").pack(pady=5)
    prescription_name_entry = tk.Entry(prescription_window)
    prescription_name_entry.pack()

    tk.Label(prescription_window, text="Medication Description:").pack(pady=5)
    medication_description_entry = tk.Entry(prescription_window)
    medication_description_entry.pack()

    tk.Label(prescription_window, text="Taken with food (Yes/No):").pack(pady=5)
    food_entry = tk.Entry(prescription_window)
    food_entry.pack()

    tk.Label(prescription_window, text="Start Day (DD):").pack(pady=5)
    day_entry = tk.Entry(prescription_window)
    day_entry.pack()

    tk.Label(prescription_window, text="Start Month (MM):").pack(pady=5)
    month_entry = tk.Entry(prescription_window)
    month_entry.pack()

    tk.Label(prescription_window, text="Start Year (YYYY):").pack(pady=5)
    year_entry = tk.Entry(prescription_window)
    year_entry.pack()

    tk.Label(prescription_window, text="Days (e.g., Monday, Wednesday):").pack(pady=5)
    days_entry = tk.Entry(prescription_window)
    days_entry.pack()

    tk.Label(prescription_window, text="Number of Weeks:").pack(pady=5)
    weeks_entry = tk.Entry(prescription_window)
    weeks_entry.pack()

    # Add a submit button to the new window
    submit_button = tk.Button(prescription_window, text="Submit Prescription", command=lambda: submit(
        day_entry, month_entry, year_entry, days_entry, weeks_entry,
        prescription_name_entry, medication_description_entry, food_entry, prescription_window
    ))
    submit_button.pack(pady=10)

# Function to schedule prescription dates based on input parameters
def prescriptionScheduler(startDay, startMon, startYr, days, numWeeks, medication_info):
    # Initialize the starting date
    start_date = datetime(int(startYr), int(startMon), int(startDay))

    # Dictionary to store prescription dates
    prescriptionDays = {
        "Prescription": [],
        "Medication Info": medication_info
    }

    # Mapping of day names to numbers
    day_name_to_number = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 7
    }

    # Convert day names to numbers for easier scheduling
    days_numbers = [day_name_to_number[day.strip()] for day in days if day.strip() in day_name_to_number]

    # Generate prescription dates by week and day
    for week in range(int(numWeeks)):
        for day in days_numbers:
            # Calculate date for each day specified in the week
            prescription_date = start_date + datetime.timedelta(weeks=week)

            # Calculate day offset to target day in the current week
            day_offset = (day - prescription_date.isoweekday()) % 7

            # Adjust date accordingly
            prescription_date += datetime.timedelta(days=day_offset)

            # Store the calculated date
            prescriptionDays["Prescription"].append({
                "Day": prescription_date.day,
                "Month": prescription_date.month,
                "Year": prescription_date.year
            })

    return prescriptionDays

def update_medication_status():
    selected_date = simpledialog.askstring("Medication Status", "Enter the date (yyyy-mm-dd):")
    if selected_date and selected_date in prescriptions:
        status = simpledialog.askstring("Medication Status", "Enter status: (taken on time/missed)")
        if status:
            prescriptions[selected_date]['status'] = status
            save_data()

def display_medication_graph():
    dates = list(prescriptions.keys())
    statuses = [1 if prescriptions[date]['status'] == 'taken on time' else 0 for date in dates]
    plt.plot(dates, statuses, marker='o')
    plt.xticks(rotation=45)
    plt.yticks([0, 1], ['Missed', 'On Time'])
    plt.title("Medication Status Over Time")
    plt.xlabel("Date")
    plt.ylabel("Status")
    plt.tight_layout()
    plt.show()


#SECTION 3 (or near the start of SECTION 4)

# Function to view all prescriptions
def view_prescriptions():
    # Create a new top-level window for viewing prescriptions
    prescriptions_window = tk.Toplevel(root)
    prescriptions_window.title("View Prescriptions")
    prescriptions_window.geometry("400x500")  # Adjust size as needed

    # Display each prescription in the window
    if prescriptions:
        for prescription_name, details in prescriptions.items():
            tk.Label(prescriptions_window, text=f"Prescription Name: {prescription_name}", font=("Arial", 10, "bold")).pack(anchor='w', padx=10, pady=5)

            for entry in details["Prescription"]:
                day, month, year = entry["Day"], entry["Month"], entry["Year"]
                tk.Label(prescriptions_window, text=f"Date: {day}-{month}-{year}").pack(anchor='w', padx=20)

            # Display medication info if available
            if "Medication Info" in details:
                tk.Label(prescriptions_window, text=f"Description: {details['Medication Info']['Description']}").pack(anchor='w', padx=20)
                tk.Label(prescriptions_window, text=f"Taken with food: {details['Medication Info']['Taken with food']}").pack(anchor='w', padx=20)
            tk.Label(prescriptions_window, text="-"*50).pack(anchor='w', padx=10, pady=5)

    else:
        tk.Label(prescriptions_window, text="No prescriptions found.", font=("Arial", 12)).pack(anchor='center', pady=20)

# Function to check for upcoming tasks and notify if due within the next hour
def check_for_upcoming_task_notifications():
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    
    if current_date in tasks:
        for task in tasks[current_date]:
            task_time_str = task.get('time')
            if task_time_str:
                task_datetime = datetime.strptime(f"{current_date} {task_time_str}", '%Y-%m-%d %H:%M')
                time_diff = (task_datetime - now).total_seconds()
                
                # If task is due within the next hour (3600 seconds) and in the future
                if 0 < time_diff <= 3600:
                    notification.notify(
                        title="Upcoming Task",
                        message=f"Task '{task['name']}' is due at {task_time_str}.",
                        app_name="WellNest",
                        timeout=10
                    )

    # Schedule the function to check again in 5 minutes
    Timer(300, check_for_upcoming_task_notifications).start()

# Start the notification scheduler
check_for_upcoming_task_notifications()
#SECTION 4

# Prompt user to select a date and item to edit or delete
def prompt_select_date_for_action(action, item_type):
    prompt_window = tk.Toplevel(root)
    prompt_window.title(f"Select Date to {action} {item_type.capitalize()}")
    prompt_window.geometry("400x400")

    cal = Calendar(prompt_window, selectmode='day', date_pattern="yyyy-mm-dd")
    cal.pack(pady=20)

    def on_date_selected():
        selected_date = cal.get_date()
        prompt_window.destroy()
        if item_type == "task":
            manage_tasks_for_date(selected_date, action)
        elif item_type == "appointment":
            manage_appointments_for_date(selected_date, action)

    tk.Button(prompt_window, text=f"Select Date to {action} {item_type.capitalize()}", command=on_date_selected).pack(pady=10)

# Manage tasks for the selected date
def manage_tasks_for_date(selected_date, action):
    if selected_date in tasks:
        manage_window = Toplevel(root)
        manage_window.title(f"{action.capitalize()} Tasks for {selected_date}")
        manage_window.geometry("400x400")

        task_vars = []
        for task in tasks[selected_date]:
            var = IntVar()
            cb = Checkbutton(manage_window, text=f"{task['name']} - Assignee: {task['assignee']}", variable=var)
            cb.pack(anchor='w')
            task_vars.append((var, task))

        def apply_action():
            selected_tasks = [task for var, task in task_vars if var.get() == 1]
            if action == "Edit":
                for task in selected_tasks:
                    new_name = simpledialog.askstring("Edit Task", f"Enter new name for task '{task['name']}':")
                    if new_name:
                        task['name'] = new_name
                save_data()
                messagebox.showinfo("Success", "Selected tasks edited successfully.")
            elif action == "Delete":
                for task in selected_tasks:
                    tasks[selected_date].remove(task)
                if not tasks[selected_date]:
                    del tasks[selected_date]
                save_data()
                messagebox.showinfo("Success", "Selected tasks deleted successfully.")
            manage_window.destroy()

        tk.Button(manage_window, text=f"{action.capitalize()} Selected Tasks", command=apply_action).pack(pady=20)
    else:
        messagebox.showinfo("No Tasks", f"No tasks found for {selected_date}.")

# Manage appointments for the selected date
def manage_appointments_for_date(selected_date, action):
    if selected_date in appointments:
        manage_window = Toplevel(root)
        manage_window.title(f"{action.capitalize()} Appointments for {selected_date}")
        manage_window.geometry("400x400")

        app_vars = []
        for app in appointments[selected_date]:
            var = IntVar()
            cb = Checkbutton(manage_window, text=app, variable=var)
            cb.pack(anchor='w')
            app_vars.append((var, app))

        def apply_action():
            selected_apps = [app for var, app in app_vars if var.get() == 1]
            if action == "Edit":
                for app in selected_apps:
                    new_detail = simpledialog.askstring("Edit Appointment", f"Enter new details for appointment '{app}':")
                    if new_detail:
                        appointments[selected_date][appointments[selected_date].index(app)] = new_detail
                save_data()
                messagebox.showinfo("Success", "Selected appointments edited successfully.")
            elif action == "Delete":
                for app in selected_apps:
                    appointments[selected_date].remove(app)
                if not appointments[selected_date]:
                    del appointments[selected_date]
                save_data()
                messagebox.showinfo("Success", "Selected appointments deleted successfully.")
            manage_window.destroy()

        tk.Button(manage_window, text=f"{action.capitalize()} Selected Appointments", command=apply_action).pack(pady=20)
    else:
        messagebox.showinfo("No Appointments", f"No appointments found for {selected_date}.")

# Function to create the "three-dot" menu for tasks
def open_task_options_menu(event):
    task_menu = Menu(root, tearoff=0)
    task_menu.add_command(label="Edit Task", command=edit_task)
    task_menu.add_command(label="Delete Task", command=delete_task)
    task_menu.tk_popup(event.x_root, event.y_root)

# Function to create the "three-dot" menu for appointments
def open_appointment_options_menu(event):
    appointment_menu = Menu(root, tearoff=0)
    appointment_menu.add_command(label="Edit Appointment", command=edit_appointment)
    appointment_menu.add_command(label="Delete Appointment", command=delete_appointment)
    appointment_menu.tk_popup(event.x_root, event.y_root)

def open_calendar():
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Calendar")
    calendar_window.minsize(800, 600)

    # Create frames for left, right, and center sections
    left_frame = tk.Frame(calendar_window)
    left_frame.pack(side="left", padx=10, pady=10)

    right_frame = tk.Frame(calendar_window)
    right_frame.pack(side="right", padx=10, pady=10)

    center_frame = tk.Frame(calendar_window)
    center_frame.pack(side="top", pady=10)

    # Initialize the Calendar with increased size
    cal = Calendar(center_frame, selectmode='day', date_pattern="yyyy-mm-dd", width=400, height=350)
    cal.pack(pady=10, fill='both', expand=True)

    # Left frame: Add Task and View/Read Out Tasks
    task_button_frame = tk.Frame(left_frame)
    task_button_frame.pack(pady=5)

    add_task_button = tk.Button(task_button_frame, text="Add Task", command=lambda: add_task(cal))
    add_task_button.pack(side="left")

    options_task_button = tk.Button(task_button_frame, text="⋮", command=lambda: None)
    options_task_button.pack(side="left", padx=5)
    options_task_button.bind("<Button-1>", open_task_options_menu)

    view_tasks_button = tk.Button(left_frame, text="View and Read Out Tasks", command=view_and_read_out_tasks)
    view_tasks_button.pack(pady=5)

    # Right frame: Add Appointment and View/Read Out Appointments
    appointment_button_frame = tk.Frame(right_frame)
    appointment_button_frame.pack(pady=5)

    add_appointment_button = tk.Button(appointment_button_frame, text="Add Appointment", command=lambda: add_appointment(cal))
    add_appointment_button.pack(side="left")

    options_appointment_button = tk.Button(appointment_button_frame, text="⋮", command=lambda: None)
    options_appointment_button.pack(side="left", padx=5)
    options_appointment_button.bind("<Button-1>", open_appointment_options_menu)

    view_appointments_button = tk.Button(right_frame, text="View and Read Out Appointments", command=view_and_read_out_appointments)
    view_appointments_button.pack(pady=5)

    # Center frame: Add other buttons
    tk.Button(center_frame, text="Add Note", command=lambda: add_note_for_date(cal)).pack(pady=5)
    tk.Button(center_frame, text="View Medication Status Graph", command=display_medication_graph).pack(pady=5)
    tk.Button(center_frame, text="Check Upcoming Events", command=check_upcoming_events).pack(pady=5)
    tk.Button(center_frame, text="Send Email Notifications", command=send_email_notifications).pack(pady=5)
    tk.Button(center_frame, text="Manage Task Status", command=manage_task_status).pack(pady=5)
    tk.Button(center_frame, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)

def check_upcoming_events():
    today = datetime.now().strftime('%Y-%m-%d')
    tasks_today = tasks.get(today, [])
    appointments_today = appointments.get(today, [])

    if not tasks_today and not appointments_today:
        notification.notify(
            title="No Events Today",
            message="There are no upcoming events scheduled for today.",
            app_name="WellNest",
            timeout=10
        )
    else:
        message = ""
        if tasks_today:
            message += "Tasks:\n" + "\n".join([task['name'] for task in tasks_today]) + "\n"
        if appointments_today:
            message += "Appointments:\n" + "\n".join(appointments_today) + "\n"

        notification.notify(
            title="Today's Events",
            message=message,
            app_name="WellNest",
            timeout=10
        )


def send_email_notifications():
    email = simpledialog.askstring("Email", "Enter your email to receive today's event notifications:")
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    tasks_today = tasks.get(today, [])
    appointments_today = appointments.get(today, [])

    if not tasks_today and not appointments_today:
        messagebox.showinfo("No Events", "No upcoming events for today.")
    else:
        body = ""
        if tasks_today:
            body += "Tasks for Today:\n" + "\n".join([task['name'] for task in tasks_today]) + "\n"
        if appointments_today:
            body += "Appointments for Today:\n" + "\n".join(appointments_today) + "\n"

        send_email_notification(email, "Today's Events", body)

def send_email_notification(email, subject, body):
    EMAIL_ADDRESS = "your_email@gmail.com"  # Replace with your App Gmail email address
    EMAIL_PASSWORD = "your_app_password"    # Replace with the App Password generated by Google

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


def add_task(cal):
    selected_date = cal.get_date()
    print("Add Task function triggered")  # Debugging line
    if not validate_future_date(selected_date):
        return
    task_name = simpledialog.askstring("Task", "Enter the task name:")
    assignee = simpledialog.askstring("Assign Task", "Assign this task to someone:")
    task_time = simpledialog.askstring("Task Time", "Enter the task time (HH:MM):")
    if task_name and assignee and task_time:
        if selected_date not in tasks:
            tasks[selected_date] = []
        task = {'name': task_name, 'assignee': assignee, 'status': 'in-progress', 'time': task_time}
        tasks[selected_date].append(task)
        save_data()


def update_task_status(date, task_name, status):
    for task in tasks[date]:
        if task['name'] == task_name:
            task['status'] = status

def manage_task_status():
    selected_date = simpledialog.askstring("Manage Task", "Enter the date (yyyy-mm-dd):")
    if selected_date and selected_date in tasks:
        manage_window = Toplevel(root)
        manage_window.title(f"Manage Tasks for {selected_date}")
        manage_window.geometry("400x400")

        for task in tasks[selected_date]:
            var = tk.StringVar(value=task['status'])
            label = tk.Label(manage_window, text=f"{task['name']} - Assignee: {task['assignee']}")
            label.pack()
            dropdown = tk.OptionMenu(manage_window, var, "in-progress", "completed")
            dropdown.pack()

            var.trace('w', lambda *args, name=task['name']: update_task_status(selected_date, name, var.get()))

        tk.Button(manage_window, text="Save Changes", command=lambda: [save_data(), manage_window.destroy()]).pack(pady=10)
    else:
        messagebox.showinfo("No Tasks", f"No tasks found for {selected_date}.")

def add_note_for_date(cal):
    selected_date = cal.get_date()
    note = simpledialog.askstring("Note", f"Add a note for {selected_date}:")
    if note:
        notes[selected_date] = note
        save_data()

def add_appointment(cal):
    selected_date = cal.get_date()
    if not validate_future_date(selected_date):
        return
    time = simpledialog.askstring("Time", "Enter appointment time:")
    doctor = simpledialog.askstring("Doctor", "Enter doctor's name:")
    location = simpledialog.askstring("Location", "Enter location:")
    if all([time, doctor, location]):
        appointment = f"Appointment at {time} with {doctor} at {location}"
        if selected_date not in appointments:
            appointments[selected_date] = []
        appointments[selected_date].append(appointment)
        save_data()

def view_and_manage_items(cal):
    selected_date = cal.get_date()
    tasks_today = tasks.get(selected_date, [])
    appointments_today = appointments.get(selected_date, [])

    if tasks_today or appointments_today:
        manage_window = Toplevel(root)
        manage_window.title(f"Manage Items for {selected_date}")
        manage_window.geometry("400x400")

        task_vars = []
        appointment_vars = []

        if tasks_today:
            tk.Label(manage_window, text="Tasks:").pack(pady=10)
            for task in tasks_today:
                var = IntVar()
                cb = Checkbutton(manage_window, text=f"{task['name']} - Assignee: {task['assignee']}", variable=var)
                cb.pack(anchor='w')
                task_vars.append(var)

        if appointments_today:
            tk.Label(manage_window, text="Appointments:").pack(pady=10)
            for app in appointments_today:
                var = IntVar()
                cb = Checkbutton(manage_window, text=app, variable=var)
                cb.pack(anchor='w')
                appointment_vars.append(var)

        tk.Button(manage_window, text="Delete Selected",
                  command=lambda: [delete_selected_items(selected_date, task_vars, appointment_vars),
                                   manage_window.destroy()]).pack(pady=20)

# Delete selected tasks/appointments
def delete_selected_items(selected_date, task_vars, appointment_vars):
    if selected_date in tasks:
        tasks_to_delete = [task for i, task in enumerate(tasks[selected_date]) if task_vars[i].get() == 1]
        for task in tasks_to_delete:
            tasks[selected_date].remove(task)
        if not tasks[selected_date]:
            del tasks[selected_date]

    if selected_date in appointments:
        apps_to_delete = [app for i, app in enumerate(appointments[selected_date]) if appointment_vars[i].get() == 1]
        for app in apps_to_delete:
            appointments[selected_date].remove(app)
        if not appointments[selected_date]:
            del appointments[selected_date]

    save_data()

# Read out today's tasks
def view_and_read_out_tasks():
    today = datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    tasks_today = tasks.get(today, [])
    if tasks_today:
        tasks_str = "\n".join([task['name'] for task in tasks_today])
        engine.say(f"Today is {datetime.now().strftime('%A')}. Your tasks for today are: {tasks_str}")
        messagebox.showinfo("Today's Tasks", f"Tasks:\n{tasks_str}")
    else:
        engine.say(f"Today is {datetime.now().strftime('%A')}. You have no tasks for today.")
    engine.runAndWait()

# Read out today's appointments
def view_and_read_out_appointments():
    today =datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    appointments_today = appointments.get(today, [])
    if appointments_today:
        appointments_str = "\n".join(appointments_today)
        engine.say(f"Today is {datetime.now().strftime('%A')}. Your appointments for today are: {appointments_str}")
        messagebox.showinfo("Today's Appointments", f"Appointments:\n{appointments_str}")
    else:
        engine.say(f"Today is {datetime.now().strftime('%A')}. You have no appointments for today.")
    engine.runAndWait()

#SECTION 5

# Define functions to initiate edit or delete actions for tasks and appointments
def edit_task():
    edit_task_or_appointment("task")

def edit_appointment():
    edit_task_or_appointment("appointment")

def delete_task():
    delete_task_or_appointment("task")

def delete_appointment():
    delete_task_or_appointment("appointment")

# Initiate edit/delete for tasks or appointments
def edit_task_or_appointment(item_type):
    prompt_select_date_for_action("Edit", item_type)

def delete_task_or_appointment(item_type):
    prompt_select_date_for_action("Delete", item_type)

# Initialize the main window
root = tk.Tk()
root.title("WellNest")
root.geometry("400x600")
root.withdraw()

# Buttons for main menu
tk.Button(root, text="Calendar", command=open_calendar).pack(pady=20)
tk.Button(root, text="Signup", command=signup_user).pack(pady=10)
tk.Button(root, text="Login", command=login_user).pack(pady=10)
tk.Button(root, text="View Medication Status Graph", command=display_medication_graph).pack(pady=5)

prescription_manager_button = tk.Button(root, text="Prescription Manager", command=open_prescription_manager)
prescription_manager_button.pack(pady=10)

view_prescriptions_button = tk.Button(root, text="View Prescriptions", command=view_prescriptions)
view_prescriptions_button.pack(pady=10)
tk.Button(root, text="Close", command=root.quit).pack(pady=20)



# Load data and run splash screen
load_data()
splash_screen()

# Run the main loop
root.mainloop()
