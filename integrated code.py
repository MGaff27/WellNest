import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import calendar
from datetime import datetime
from tkcalendar import Calendar  # Ensure you install tkcalendar via 'pip install tkcalendar'

# Define a Task class
class Task:
    def __init__(self, name, description, patient, caretaker, notes):
        self.name = name
        self.description = description
        self.patient = patient
        self.caretaker = caretaker
        self.notes = notes

# Define a User class to store user information, tasks, and notes
class User:
    def __init__(self, username):
        self.username = username
        self.tasks = []
        self.calendar_notes = {}
        self.pills = []
        self.appointments = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_calendar_note(self, year, month, day, note):
        self.calendar_notes[(year, month, day)] = note

    def add_pill(self, pill_name, remaining):
        self.pills.append({"Pill": pill_name, "Remaining": remaining})

    def add_appointment(self, date, time, doctor, location, reason):
        self.appointments.append({"Date": date, "Time": time, "Doctor": doctor, "Location": location, "Reason": reason})

# Global user directory
users = {}
current_user = None

# Initialize the main window
root = tk.Tk()
root.title("Well Nest Caregiving App")
root.geometry("800x600")
root.configure(bg="black")

# Define styles
style = ttk.Style()
style.configure("TLabel", background="black", foreground="white", font=("Helvetica", 12))
style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

# Calendar Management Functions
current_year = datetime.now().year
current_month = datetime.now().month

def generate_calendar(year, month):
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    for widget in calendar_frame.winfo_children():
        widget.destroy()

    month_name = calendar.month_name[month]
    year_label = ttk.Label(calendar_frame, text=f"{month_name} {year}", style="Header.TLabel")
    year_label.grid(row=0, column=0, columnspan=7)

    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    for col, day in enumerate(days):
        ttk.Label(calendar_frame, text=day, style="Header.TLabel").grid(row=1, column=col)

    cal = calendar.monthcalendar(year, month)
    for row, week in enumerate(cal, start=2):
        for col, day in enumerate(week):
            if day == 0:
                ttk.Label(calendar_frame, text=" ", style="TLabel").grid(row=row, column=col)
            else:
                day_button = tk.Button(
                    calendar_frame, text=str(day), height=3, width=10,
                    command=lambda d=day: day_clicked(d), wraplength=80, justify="left"
                )
                note = current_user.calendar_notes.get((year, month, day), "")
                if note:
                    day_button.config(text=f"{day}\n{note}")
                day_button.grid(row=row, column=col, padx=5, pady=5)

def day_clicked(day):
    note = simpledialog.askstring("Add Notes", f"Add notes for {current_month}/{day}/{current_year}:")
    if note:
        current_user.add_calendar_note(current_year, current_month, day, note)
        generate_calendar(current_year, current_month)

def next_month():
    global current_month, current_year
    current_month = 1 if current_month == 12 else current_month + 1
    current_year += 1 if current_month == 1 else 0
    generate_calendar(current_year, current_month)

def previous_month():
    global current_month, current_year
    current_month = 12 if current_month == 1 else current_month - 1
    current_year -= 1 if current_month == 12 else 0
    generate_calendar(current_year, current_month)

# User Management Functions
def create_user():
    global current_user
    username = simpledialog.askstring("New User", "Enter username:")
    if username and username not in users:
        users[username] = User(username)
        current_user = users[username]
        messagebox.showinfo("User Created", f"User '{username}' created successfully.")
        generate_calendar(current_year, current_month)
    elif username in users:
        messagebox.showwarning("User Exists", "Username already exists.")

def select_user():
    global current_user
    if users:
        username = simpledialog.askstring("Select User", f"Enter username ({', '.join(users.keys())}):")
        if username in users:
            current_user = users[username]
            messagebox.showinfo("User Selected", f"User '{username}' selected.")
            generate_calendar(current_year, current_month)
        else:
            messagebox.showwarning("User Not Found", f"User '{username}' not found.")
    else:
        messagebox.showwarning("No Users", "No users available. Please create a new user.")

# Appointment Management Functions
def open_appointments():
    def add_appointment():
        date = simpledialog.askstring("Date", "Enter the appointment date (YYYY-MM-DD):")
        time = simpledialog.askstring("Time", "Enter the appointment time:")
        doctor = simpledialog.askstring("Doctor", "Enter the doctor's name:")
        location = simpledialog.askstring("Location", "Enter the appointment location:")
        reason = simpledialog.askstring("Reason", "Enter the reason for the appointment:")
        if all([date, time, doctor, location, reason]):
            current_user.add_appointment(date, time, doctor, location, reason)
            messagebox.showinfo("Appointment Added", f"Appointment on {date} with Dr. {doctor} added.")
        else:
            messagebox.showwarning("Input Error", "All fields must be filled.")

    appointment_window = tk.Toplevel(root)
    appointment_window.title("Manage Appointments")
    tk.Button(appointment_window, text="Add Appointment", command=add_appointment).pack(pady=5)
    tk.Button(appointment_window, text="Close", command=appointment_window.destroy).pack(pady=5)

# UI Setup
calendar_frame = ttk.LabelFrame(root, text="Calendar", style="Header.TLabel")
calendar_frame.grid(row=0, column=0, padx=20, pady=20)

task_view_frame = ttk.LabelFrame(root, text="Task View", style="Header.TLabel")
task_view_frame.grid(row=0, column=1, padx=20, pady=20)

user_button_frame = ttk.LabelFrame(root, text="User Management", style="Header.TLabel")
user_button_frame.grid(row=1, column=1, padx=20, pady=20)

tk.Button(user_button_frame, text="Create User", command=create_user).pack(pady=5)
tk.Button(user_button_frame, text="Select User", command=select_user).pack(pady=5)

tk.Button(root, text="Appointments", command=open_appointments).pack(pady=5)
tk.Button(root, text="Close", command=root.quit).pack(pady=5)

# Run the application
generate_calendar(current_year, current_month)
root.mainloop()
