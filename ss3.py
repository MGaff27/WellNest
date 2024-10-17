import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Checkbutton, IntVar
from tkcalendar import Calendar
import json
import os
import datetime
import pyttsx3
from plyer import notification


# Dictionary to hold appointments, prescriptions, tasks, and notes
appointments = {}
prescriptions = {}
tasks = {}
notes = {}

# Files to store data
appointments_file = "appointments.json"
prescriptions_file = "prescriptions.json"
tasks_file = "tasks.json"
notes_file = "notes.json"

# Function to load data from files
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

# Function to save data to files
def save_data():
    with open(prescriptions_file, "w") as file:
        json.dump(prescriptions, file)
    with open(appointments_file, "w") as file:
        json.dump(appointments, file)
    with open(tasks_file, "w") as file:
        json.dump(tasks, file)
    with open(notes_file, "w") as file:
        json.dump(notes, file)

# Load data on app start
load_data()

# Function to get the day of the week
def get_day_of_week():
    today = datetime.datetime.now()
    return today.strftime("%A")  # Returns the day of the week (e.g., Monday)

# Function to display tasks, appointments, and notes on the calendar
def display_items(cal):
    # Clear all previous events
    cal.calevent_remove('all')

    for date, items in tasks.items():
        task_event = "\n".join([task for task in items])  # Display task name
        cal.calevent_create(datetime.datetime.strptime(date, '%Y-%m-%d'), task_event, 'task')

    for date, apps in appointments.items():
        app_event = "\n".join([app for app in apps])
        cal.calevent_create(datetime.datetime.strptime(date, '%Y-%m-%d'), app_event, 'appointment')

    for date, note in notes.items():
        note_event = "\n".join([note])
        cal.calevent_create(datetime.datetime.strptime(date, '%Y-%m-%d'), note_event, 'note')

    cal.tag_config('task', background='lightyellow', foreground='black')
    cal.tag_config('appointment', background='lightblue', foreground='black')
    cal.tag_config('note', background='lightgreen', foreground='black')

# Function to delete tasks or appointments based on user selection
def delete_selected_items(selected_date, task_vars, appointment_vars):
    # Delete selected tasks
    if selected_date in tasks:
        tasks_to_delete = [task for i, task in enumerate(tasks[selected_date]) if task_vars[i].get() == 1]
        for task in tasks_to_delete:
            tasks[selected_date].remove(task)
        if not tasks[selected_date]:  # Remove the date if no tasks remain
            del tasks[selected_date]

    # Delete selected appointments
    if selected_date in appointments:
        apps_to_delete = [app for i, app in enumerate(appointments[selected_date]) if appointment_vars[i].get() == 1]
        for app in apps_to_delete:
            appointments[selected_date].remove(app)
        if not appointments[selected_date]:  # Remove the date if no appointments remain
            del appointments[selected_date]

    save_data()

# Function to view and delete tasks/appointments for a selected date
def view_and_manage_items(cal):
    selected_date = cal.get_date()

    # Retrieve tasks and appointments for the selected date
    tasks_today = tasks.get(selected_date, [])
    appointments_today = appointments.get(selected_date, [])

    if tasks_today or appointments_today:
        # Create a new window to display tasks and appointments
        manage_window = Toplevel(root)
        manage_window.title(f"Manage Items for {selected_date}")
        manage_window.geometry("400x400")

        task_vars = []
        appointment_vars = []

        # Display tasks with checkboxes
        if tasks_today:
            tk.Label(manage_window, text="Tasks:").pack(pady=10)
            for task in tasks_today:
                var = IntVar()
                cb = Checkbutton(manage_window, text=task, variable=var)
                cb.pack(anchor='w')
                task_vars.append(var)  # Keep track of the checkbox variable

        # Display appointments with checkboxes
        if appointments_today:
            tk.Label(manage_window, text="Appointments:").pack(pady=10)
            for app in appointments_today:
                var = IntVar()
                cb = Checkbutton(manage_window, text=app, variable=var)
                cb.pack(anchor='w')
                appointment_vars.append(var)  # Keep track of the checkbox variable

        # Delete button
        tk.Button(manage_window, text="Delete Selected", command=lambda: [delete_selected_items(selected_date, task_vars, appointment_vars), display_items(cal), manage_window.destroy()]).pack(pady=20)

        # Close the window
        tk.Button(manage_window, text="Close", command=manage_window.destroy).pack(pady=10)
    else:
        messagebox.showinfo("No Items", f"No tasks or appointments for {selected_date}")

# Function to add a task for a selected date
def add_task(cal, selected_date=None):
    if not selected_date:
        selected_date = cal.get_date()

    task_name = simpledialog.askstring("Input", "Enter the task name:")
    if task_name:
        if selected_date not in tasks:
            tasks[selected_date] = []
        tasks[selected_date].append(task_name)
        save_data()
        display_items(cal)

# Function to add a note for the selected date
def add_note_for_date(cal):
    selected_date = cal.get_date()
    note = simpledialog.askstring("Add Note", f"Add a note for {selected_date}:")
    if note:
        notes[selected_date] = note
        save_data()
        display_items(cal)

# Function to view items for a selected date
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

# Function to add an appointment with cancelable prompts
def add_appointment(cal):
    selected_date = cal.get_date()
    time = simpledialog.askstring("Time", "Enter the appointment time:")
    if not time:
        return

    doctor_name = simpledialog.askstring("Doctor", "Enter the doctor's name:")
    if not doctor_name:
        return

    location = simpledialog.askstring("Location", "Enter the appointment location:")
    if not location:
        return

    reason = simpledialog.askstring("Reason", "Enter the reason for the appointment:")
    if not reason:
        return

    appointment_info = f"{time} with Dr. {doctor_name} at {location} - {reason}"
    if selected_date not in appointments:
        appointments[selected_date] = []
    appointments[selected_date].append(appointment_info)
    save_data()
    display_items(cal)

# Function to push notifications for tasks and appointments
def push_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="WellNest",
        timeout=10  # Duration of notification
    )

# Function to check for upcoming tasks or appointments
def check_for_upcoming_events():
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Check appointments for today
    if today in appointments:
        for app in appointments[today]:
            push_notification("Upcoming Appointment", app)

    # Check tasks for today
    if today in tasks:
        for task in tasks[today]:
            push_notification("Reminder: Task", task)

    # Check notes for today (optional)
    if today in notes:
        push_notification("Today's Note", notes[today])

# Function to read out and display tasks for today
def view_and_read_out_tasks():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    tasks_today = tasks.get(today, [])
    if tasks_today:
        # Display tasks
        tasks_str = "\n".join(tasks_today)
        day_of_week = get_day_of_week()
        messagebox.showinfo("Today's Tasks", f"Today is {day_of_week}. Your tasks are:\n{tasks_str}")

        # Read out tasks
        engine.say(f"Today is {day_of_week}. Your tasks for today are:")
        for task in tasks_today:
            engine.say(task)
        engine.runAndWait()
    else:
        day_of_week = get_day_of_week()
        engine.say(f"Today is {day_of_week}. You have no tasks for today.")
        engine.runAndWait()
        messagebox.showinfo("No Tasks", f"Today is {day_of_week}. You have no tasks for today.")

# Function to read out and display appointments for today
def view_and_read_out_appointments():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    engine = pyttsx3.init()

    appointments_today = appointments.get(today, [])
    if appointments_today:
        # Display appointments
        appointments_str = "\n".join(appointments_today)
        day_of_week = get_day_of_week()
        messagebox.showinfo("Today's Appointments", f"Today is {day_of_week}. Your appointments are:\n{appointments_str}")

        # Read out appointments
        engine.say(f"Today is {day_of_week}. Your appointments for today are:")
        for app in appointments_today:
            engine.say(app)
        engine.runAndWait()
    else:
        day_of_week = get_day_of_week()
        engine.say(f"Today is {day_of_week}. You have no appointments for today.")
        engine.runAndWait()
        messagebox.showinfo("No Appointments", f"Today is {day_of_week}. You have no appointments for today.")

# Function to open the main calendar UI
def open_calendar():
    calendar_window = tk.Toplevel(root)
    calendar_window.title("Calendar")
    calendar_window.minsize(800, 600)

    calendar_frame = tk.Frame(calendar_window)
    calendar_frame.pack(pady=20, fill='both', expand=True)

    # Initialize the Calendar
    cal = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd")
    cal.pack(pady=10, fill='both', expand=True)

    # Display existing items on the calendar
    display_items(cal)

    # Buttons to interact with the calendar
    tk.Button(calendar_window, text="Add Task", command=lambda: add_task(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Add Note", command=lambda: add_note_for_date(cal)).pack(pady=5)
    tk.Button(calendar_window, text="View Items", command=lambda: view_items(cal)).pack(pady=5)
    tk.Button(calendar_window, text="View and Manage Items", command=lambda: view_and_manage_items(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Add Appointment", command=lambda: add_appointment(cal)).pack(pady=5)
    tk.Button(calendar_window, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)

# Main window setup
root = tk.Tk()
root.title("WellNest")
root.geometry("400x600")

# Main menu buttons
tk.Button(root, text="Calendar", command=open_calendar).pack(pady=30)
tk.Button(root, text="View and Read Out Today's Tasks", command=view_and_read_out_tasks).pack(pady=30)
tk.Button(root, text="View and Read Out Today's Appointments", command=view_and_read_out_appointments).pack(pady=30)
tk.Button(root, text="Check Upcoming Events", command=check_for_upcoming_events).pack(pady=30)
tk.Button(root, text="Close", command=root.quit).pack(pady=30)

# Run the main loop
root.mainloop()
