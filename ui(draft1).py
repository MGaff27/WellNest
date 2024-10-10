import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import calendar
from datetime import datetime

# Initialize the root window
root = tk.Tk()
root.title("Well Nest Caregiving App")
root.geometry("800x600")
root.configure(bg="black")

# Define styles
style = ttk.Style()
style.configure("TLabel", background="black", foreground="white", font=("Helvetica", 12))
style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))

# Lists to hold tasks, completed tasks, pills, and calendar notes
tasks = []
completed_tasks = []
pills = []
calendar_notes = {}  # Dictionary to store notes for each date

# Initialize variables for calendar
current_year = datetime.now().year
current_month = datetime.now().month


# Function to generate the calendar grid for a given month and year
def generate_calendar(year, month):
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
                note = calendar_notes.get((year, month, day), "")
                if note:
                    day_button.config(text=f"{day}\n{note}")
                day_button.grid(row=row, column=col, padx=5, pady=5)


# Function called when a day is clicked
def day_clicked(day):
    note = simpledialog.askstring("Add Notes", f"Add notes for {current_month}/{day}/{current_year}:")
    if note:
        # Store the note in the dictionary for the specific date
        calendar_notes[(current_year, current_month, day)] = note
        # Refresh the calendar to display the note
        generate_calendar(current_year, current_month)


# Function to move to the next month
def next_month():
    global current_month, current_year
    if current_month == 12:
        current_month = 1
        current_year += 1
    else:
        current_month += 1
    generate_calendar(current_year, current_month)


# Function to move to the previous month
def previous_month():
    global current_month, current_year
    if current_month == 1:
        current_month = 12
        current_year -= 1
    else:
        current_month -= 1
    generate_calendar(current_year, current_month)


# Function to add a new task with consecutive input prompts
def add_task():
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
                    tasks.append({
                        "Task": task_name,
                        "Description": task_description,
                        "Patient": patient,
                        "Caretaker": caretaker,
                        "Notes": notes
                    })
                    update_task_view()


# Function to mark a task as completed
def complete_task(task_index):
    task = tasks[task_index]
    tasks.pop(task_index)
    completed_tasks.append(task)
    update_task_view()
    update_completed_tasks()


# Function to update the task view
def update_task_view():
    for widget in task_view_frame.winfo_children():
        widget.destroy()

    for i, task in enumerate(tasks):
        task_label = ttk.Label(task_view_frame, text=f"Task {i + 1}: {task['Task']}", style="TLabel")
        task_label.grid(row=i * 5, column=0, padx=5, pady=5, sticky="w")

        description_label = ttk.Label(task_view_frame, text=f"Description: {task['Description']}", style="TLabel")
        description_label.grid(row=i * 5 + 1, column=0, padx=5, pady=5, sticky="w")

        patient_label = ttk.Label(task_view_frame, text=f"Patient: {task['Patient']}", style="TLabel")
        patient_label.grid(row=i * 5 + 2, column=0, padx=5, pady=5, sticky="w")

        caretaker_label = ttk.Label(task_view_frame, text=f"Caretaker: {task['Caretaker']}", style="TLabel")
        caretaker_label.grid(row=i * 5 + 3, column=0, padx=5, pady=5, sticky="w")

        notes_label = ttk.Label(task_view_frame, text=f"Notes: {task['Notes']}", style="TLabel")
        notes_label.grid(row=i * 5 + 4, column=0, padx=5, pady=5, sticky="w")

        complete_button = ttk.Button(task_view_frame, text="Complete", command=lambda idx=i: complete_task(idx))
        complete_button.grid(row=i * 5, column=1, padx=5, pady=5)


# Function to update the completed tasks view
def update_completed_tasks():
    for widget in completed_tasks_frame.winfo_children():
        widget.destroy()

    for i, task in enumerate(completed_tasks):
        task_label = ttk.Label(completed_tasks_frame, text=f"{task['Task']} ✔️", style="TLabel")
        task_label.grid(row=i, column=0, padx=5, pady=5, sticky="w")


# Function to add a new pill
def add_pill():
    pill_name = simpledialog.askstring("New Pill", "Enter pill name:")
    if pill_name:
        remaining = simpledialog.askinteger("Pill Count", f"How many {pill_name} pills are remaining?")
        pills.append({"Pill": pill_name, "Remaining": remaining})
        update_pill_storage()


# Function to update the pill storage view
def update_pill_storage():
    for widget in pill_storage_frame.winfo_children():
        widget.destroy()

    for i, pill in enumerate(pills):
        pill_label = ttk.Label(pill_storage_frame, text=f"{pill['Pill']}: {pill['Remaining']} pills remaining",
                               style="TLabel")
        pill_label.grid(row=i, column=0, padx=5, pady=5)


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

# Pill Storage Frame
pill_storage_frame = ttk.LabelFrame(root, text="Pill Storage", padding=(10, 5), style="Header.TLabel")
pill_storage_frame.grid(row=1, column=0, padx=20, pady=20, sticky="n")

# Button to add new pill
add_pill_button = ttk.Button(pill_storage_frame, text="Add Pill", command=add_pill)
add_pill_button.grid(row=0, column=0, padx=5, pady=5)

# Completed Tasks Frame
completed_tasks_frame = ttk.LabelFrame(root, text="Completed Tasks", padding=(10, 5), style="Header.TLabel")
completed_tasks_frame.grid(row=1, column=1, padx=20, pady=20, sticky="n")

# Generate the initial calendar for the current month and year
generate_calendar(current_year, current_month)

# Run the application
root.mainloop()
