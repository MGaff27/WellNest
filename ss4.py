import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Checkbutton, IntVar
from tkcalendar import Calendar
import json
import os
import datetime
import pyttsx3
from plyer import notification
from PIL import Image, ImageTk
import time
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import firebase_admin
from firebase_admin import credentials, firestore

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
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Load data on app start
def load_data():
    global prescriptions, appointments, tasks, notes
    if os.path.exists(prescriptions_file):
        with open(prescriptions_file, "r") as file:
            prescriptions = json.load(file)
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
    with open(prescriptions_file, "w") as file:
        json.dump(prescriptions, file)
    with open(appointments_file, "w") as file:
        json.dump(appointments, file)
    with open(tasks_file, "w") as file:
        json.dump(tasks, file)
    with open(notes_file, "w") as file:
        json.dump(notes, file)


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


# Show Splash Screen
def splash_screen():
    splash = tk.Toplevel()
    splash.geometry("600x400")
    splash.overrideredirect(True)
    splash.title("WellNest")

    splash_img = Image.open("wellnest_splash.png")
    splash_img = splash_img.resize((600, 400), Image.Resampling.LANCZOS)
    splash_img = ImageTk.PhotoImage(splash_img)

    splash_label = tk.Label(splash, image=splash_img)
    splash_label.image = splash_img
    splash_label.pack()

    splash.after(3000, lambda: close_splash_and_show_main(splash))


# Close splash and show main window
def close_splash_and_show_main(splash):
    splash.destroy()
    root.deiconify()  # Show the main window


# Main window setup
root = tk.Tk()
root.title("WellNest")
root.geometry("400x600")
root.withdraw()  # Hide the main window until splash screen closes

# Load data
load_data()


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


# Buttons to interact with the calendar
def open_calendar():
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Calendar")
    calendar_window.minsize(800, 600)

    calendar_frame = tk.Frame(calendar_window)
    calendar_frame.pack(pady=20, fill='both', expand=True)

    # Initialize the Calendar
    cal = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd")
    cal.pack(pady=10, fill='both', expand=True)

    # Add buttons
    tk.Button(calendar_window, text="Add Task", command=lambda: add_task(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Add Note", command=lambda: add_note_for_date(cal)).pack(pady=5)
    tk.Button(calendar_window, text="View Items", command=lambda: view_items(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Add Appointment", command=lambda: add_appointment(cal)).pack(pady=5)
    tk.Button(calendar_window, text="View and Manage Items", command=lambda: view_and_manage_items(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)


# Add task
def add_task(cal):
    selected_date = cal.get_date()
    task_name = simpledialog.askstring("Task", "Enter the task name:")
    if task_name:
        if selected_date not in tasks:
            tasks[selected_date] = []
        tasks[selected_date].append(task_name)
        save_data()


# Add note
def add_note_for_date(cal):
    selected_date = cal.get_date()
    note = simpledialog.askstring("Note", f"Add a note for {selected_date}:")
    if note:
        notes[selected_date] = note
        save_data()


# View tasks, notes, and appointments
def view_items(cal):
    selected_date = cal.get_date()
    items = []
    if selected_date in tasks:
        items.append(f"Tasks: {', '.join(tasks[selected_date])}")
    if selected_date in appointments:
        items.append(f"Appointments: {', '.join(appointments[selected_date])}")
    if selected_date in notes:
        items.append(f"Note: {notes[selected_date]}")
    if items:
        messagebox.showinfo(f"Items for {selected_date}", "\n".join(items))
    else:
        messagebox.showinfo(f"Items for {selected_date}", "No items found for this date.")


# Add appointment
def add_appointment(cal):
    selected_date = cal.get_date()
    time = simpledialog.askstring("Time", "Enter appointment time:")
    doctor = simpledialog.askstring("Doctor", "Enter doctor's name:")
    location = simpledialog.askstring("Location", "Enter location:")
    if all([time, doctor, location]):
        appointment = f"Appointment at {time} with {doctor} at {location}"
        if selected_date not in appointments:
            appointments[selected_date] = []
        appointments[selected_date].append(appointment)
        save_data()


# Delete tasks and appointments
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
                cb = Checkbutton(manage_window, text=task, variable=var)
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


# Delete items based on selection
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


# Function to read out tasks and appointments for today
def view_and_read_out_tasks():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    tasks_today = tasks.get(today, [])
    if tasks_today:
        tasks_str = "\n".join(tasks_today)
        engine.say(f"Today is {datetime.datetime.now().strftime('%A')}. Your tasks for today are: {tasks_str}")
        messagebox.showinfo("Today's Tasks", f"Tasks:\n{tasks_str}")
    else:
        engine.say(f"Today is {datetime.datetime.now().strftime('%A')}. You have no tasks for today.")
    engine.runAndWait()


# Function to read out appointments for today
def view_and_read_out_appointments():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    appointments_today = appointments.get(today, [])
    if appointments_today:
        appointments_str = "\n".join(appointments_today)
        engine.say(
            f"Today is {datetime.datetime.now().strftime('%A')}. Your appointments for today are: {appointments_str}")
        messagebox.showinfo("Today's Appointments", f"Appointments:\n{appointments_str}")
    else:
        engine.say(f"Today is {datetime.datetime.now().strftime('%A')}. You have no appointments for today.")
    engine.runAndWait()


# Buttons for main menu
tk.Button(root, text="Calendar", command=open_calendar).pack(pady=30)
tk.Button(root, text="View and Read Out Today's Tasks", command=view_and_read_out_tasks).pack(pady=30)
tk.Button(root, text="View and Read Out Today's Appointments", command=view_and_read_out_appointments).pack(pady=30)
tk.Button(root, text="Signup", command=signup_user).pack(pady=30)
tk.Button(root, text="Login", command=login_user).pack(pady=30)
tk.Button(root, text="Close", command=root.quit).pack(pady=30)

# Run splash screen
splash_screen()

# Run the main loop
root.mainloop()
