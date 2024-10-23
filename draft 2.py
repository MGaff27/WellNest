import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import calendar
from datetime import datetime


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

    def add_task(self, task):
        self.tasks.append(task)

    def add_calendar_note(self, year, month, day, note):
        self.calendar_notes[(year, month, day)] = note

    def add_pill(self, pill_name, remaining):
        self.pills.append({"Pill": pill_name, "Remaining": remaining})


# Global user directory
users = {}
current_user = None  # Active user

# Initialize the root window
root = tk.Tk()
root.title("Well Nest Caregiving App")
root.geometry("800x600")
root.configure(bg="black")

# Define styles
style = ttk.Style()
style.configure("TLabel", background="black", foreground="white", font=("Helvetica", 12))
style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

# Initialize variables for calendar
current_year = datetime.now().year
current_month = datetime.now().month


# Function to generate the calendar grid for a given month and year
def generate_calendar(year, month):
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    for widget in calendar_frame.winfo_children():
        widget.destroy()

    # Display month and year
    month_name = calendar.month_name[month]
    year_label = ttk.Label(calendar_frame, text=f"{month_name} {year}", style="Header.TLabel")
    year_label.grid(row=0, column=0, columnspan=7)

    # Display days of the week
    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    for col, day in enumerate(days):
        ttk.Label(calendar_frame, text=day, style="Header.TLabel").grid(row=1, column=col)

    # Get the days of the month
    cal = calendar.monthcalendar(year, month)
    for row, week in enumerate(cal, start=2):
        for col, day in enumerate(week):
            if day == 0:
                ttk.Label(calendar_frame, text=" ", style="TLabel").grid(row=row, column=col)
            else:
                day_button = tk.Button(
                    calendar_frame, text=str(day), height=3, width=10,  # Adjust size for notes
                    command=lambda d=day: day_clicked(d), wraplength=80, justify="left"
                )
                # If there is a note for this day, display it on the button
                note = current_user.calendar_notes.get((year, month, day), "")
                if note:
                    day_button.config(text=f"{day}\n{note}")
                day_button.grid(row=row, column=col, padx=5, pady=5)


# Function called when a day is clicked
def day_clicked(day):
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    note = simpledialog.askstring("Add Notes", f"Add notes for {current_month}/{day}/{current_year}:")
    if note:
        # Store the note in the current user's calendar notes
        current_user.add_calendar_note(current_year, current_month, day, note)
        # Refresh the calendar to display the note
        generate_calendar(current_year, current_month)


# Function to move to the next month
def next_month():
    global current_month, current_year
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    if current_month == 12:
        current_month = 1
        current_year += 1
    else:
        current_month += 1
    generate_calendar(current_year, current_month)


# Function to move to the previous month
def previous_month():
    global current_month, current_year
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    if current_month == 1:
        current_month = 12
        current_year -= 1
    else:
        current_month -= 1
    generate_calendar(current_year, current_month)


# Function to create a new user
def create_user():
    global current_user
    username = simpledialog.askstring("New User", "Enter username:")
    if username and username not in users:
        users[username] = User(username)
        current_user = users[username]
        messagebox.showinfo("User Created", f"User '{username}' created successfully.")
    elif username in users:
        messagebox.showwarning("User Exists", "Username already exists.")
    generate_calendar(current_year, current_month)


# Function to select an existing user
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


# Function to add a new task
def add_task():
    if current_user is None:
        messagebox.showwarning("No User Selected", "Please select or create a user first.")
        return

    task_name = simpledialog.askstring("Task Name", "Enter task name:")
    if task_name:
        task_description = simpledialog.askstring("Task Description", "Enter task description:")
        if task_description:
            patient = simpledialog.askstring("Patient Name", "Enter patient's name:")
            if patient:
                caretaker = simpledialog.askstring("Caretaker Name", "Enter caretaker's name:")
                if caretaker:
                    notes = simpledialog.askstring("Additional Notes", "Enter additional notes (optional):",
                                                   initialvalue="No additional notes")
                    task = Task(task_name, task_description, patient, caretaker, notes)
                    current_user.add_task(task)
                    update_task_view()


# Function to update the task view
def update_task_view():
    if current_user is None:
        return

    for widget in task_view_frame.winfo_children():
        widget.destroy()

    for i, task in enumerate(current_user.tasks):
        task_label = ttk.Label(task_view_frame, text=f"Task {i + 1}: {task.name}", style="TLabel")
        task_label.grid(row=i * 5, column=0, padx=5, pady=5, sticky="w")

        description_label = ttk.Label(task_view_frame, text=f"Description: {task.description}", style="TLabel")
        description_label.grid(row=i * 5 + 1, column=0, padx=5, pady=5, sticky="w")

        patient_label = ttk.Label(task_view_frame, text=f"Patient: {task.patient}", style="TLabel")
        patient_label.grid(row=i * 5 + 2, column=0, padx=5, pady=5, sticky="w")

        caretaker_label = ttk.Label(task_view_frame, text=f"Caretaker: {task.caretaker}", style="TLabel")
        caretaker_label.grid(row=i * 5 + 3, column=0, padx=5, pady=5, sticky="w")

        notes_label = ttk.Label(task_view_frame, text=f"Notes: {task.notes}", style="TLabel")
        notes_label.grid(row=i * 5 + 4, column=0, padx=5, pady=5, sticky="w")


# Calendar Frame
calendar_frame = ttk.LabelFrame(root, text="Calendar", padding=(10, 5), style="Header.TLabel")
calendar_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")

# Navigation buttons for the calendar
prev_button = ttk.Button(root, text="<< Prev", command=previous_month)
prev_button.grid(row=0, column=0, sticky="w")

next_button = ttk.Button(root, text="Next >>", command=next_month)
next_button.grid(row=0, column=0, sticky="e")

# Task View Frame
task_view_frame = ttk.LabelFrame(root, text="Task View", padding=(10, 5), style="Header.TLabel")
task_view_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")

# Button to add new task
add_task_button = ttk.Button(task_view_frame, text="Add Task", command=add_task)
add_task_button.grid(row=0, column=0, padx=5, pady=5)

# User management buttons
user_button_frame = ttk.LabelFrame(root, text="User Management", padding=(10, 5), style="Header.TLabel")
user_button_frame.grid(row=1, column=1, padx=20, pady=20, sticky="n")

create_user_button = ttk.Button(user_button_frame, text="Create User", command=create_user)
create_user_button.grid(row=0, column=0, padx=5, pady=5)

select_user_button = ttk.Button(user_button_frame, text="Select User", command=select_user)
select_user_button.grid(row=1, column=0, padx=5, pady=5)

# Run the application
generate_calendar(current_year, current_month)
root.mainloop()
