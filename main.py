import tkinter as tk
from tkinter import messagebox, simpledialog
from tkcalendar import Calendar


# Function to show calendar options
def open_calendar():
    def calendar_menu():
        calendar_window = tk.Toplevel(root)
        calendar_window.title("Calendar Menu")

        # calendar frame
        calendar_frame = tk.Frame(calendar_window)
        calendar_frame.pack(pady=10)

        def show_day_view():
            selected_date = cal.get_date()
            messagebox.showinfo("Day View", f"Showing events for: {selected_date}")

        def show_week_view():
            selected_date = cal.get_date()
            messagebox.showinfo("Week View", f"Showing events for the week of: {selected_date}")

        def show_month_view():
            selected_date = cal.get_date()
            messagebox.showinfo("Month View", f"Showing events for the month of: {selected_date}")

        # Calendar widget
        cal = Calendar(calendar_frame, selectmode='day')
        cal.pack()

        tk.Button(calendar_window, text="View Day", command=show_day_view).pack(pady=5)
        tk.Button(calendar_window, text="View Week", command=show_week_view).pack(pady=5)
        tk.Button(calendar_window, text="View Month", command=show_month_view).pack(pady=5)
        tk.Button(calendar_window, text="Back to Main Menu", command=calendar_window.destroy).pack(pady=5)

    calendar_menu()


# Function to manage prescriptions
def open_prescription():
    def prescription_menu():
        prescription_window = tk.Toplevel(root)
        prescription_window.title("Prescription Menu")

        def current_prescriptions():
            messagebox.showinfo("Current Prescriptions", "Current Prescription Selected")

        def add_prescription():
            pill_name = simpledialog.askstring("Input", "Enter the name of the pill:")
            dosage = simpledialog.askstring("Input", "Enter the dosage:")
            purpose = simpledialog.askstring("Input", "Give a brief description of the purpose of the medication:")
            instructions = simpledialog.askstring("Input", "State if medication is taken on an empty stomach or not:")
            duration = simpledialog.askstring("Input", "How many days will this pill be taken for?")

            if all([pill_name, dosage, purpose, instructions, duration]):
                messagebox.showinfo("Pill Information",
                                    f"Name: {pill_name}\nDosage: {dosage}\nPurpose: {purpose}\n"
                                    f"Instructions: {instructions}\nDuration: {duration}")
            else:
                messagebox.showwarning("Input Error", "All fields must be filled out.")

        def remove_prescription():
            pill_name = simpledialog.askstring("Input", "Enter the name of the pill to remove:")
            # Implement remove logic here
            messagebox.showinfo("Remove Prescription", f"Removed prescription for {pill_name}")

        def close_prescription():
            prescription_window.destroy()

        tk.Label(prescription_window, text="My Pharmacy:").pack()
        tk.Button(prescription_window, text="Current Prescriptions", command=current_prescriptions).pack(pady=5)
        tk.Button(prescription_window, text="Add Prescription", command=add_prescription).pack(pady=5)
        tk.Button(prescription_window, text="Remove Prescription", command=remove_prescription).pack(pady=5)
        tk.Button(prescription_window, text="Back to Main Menu", command=close_prescription).pack(pady=5)

    prescription_menu()


# Function to manage appointments
def open_appointments():
    def appointment_menu():
        appointment_window = tk.Toplevel(root)
        appointment_window.title("Appointment Menu")

        def add_appointment():
            appointment_date = simpledialog.askstring("Input", "Enter the date of your appointment (e.g., 2024-10-01):")
            time = simpledialog.askstring("Input", "Enter the time:")
            doctor_name = simpledialog.askstring("Input", "Your doctor's name:")
            location = simpledialog.askstring("Input", "Location:")
            reason = simpledialog.askstring("Input", "Give a brief description for your visit:")

            if all([appointment_date, time, doctor_name, location, reason]):
                messagebox.showinfo("Appointment Information",
                                    f"Date: {appointment_date}\nTime: {time}\nDoctor: {doctor_name}\n"
                                    f"Location: {location}\nReason for visit: {reason}")
            else:
                messagebox.showwarning("Input Error", "All fields must be filled out.")

        def remove_appointment():
            appointment_date = simpledialog.askstring("Input", "Enter the date of the appointment to remove:")
            # Implement remove logic here
            messagebox.showinfo("Remove Appointment", f"Removed appointment on {appointment_date}")

        def close_appointment():
            appointment_window.destroy()

        tk.Label(appointment_window, text="Appointment Menu:").pack()
        tk.Button(appointment_window, text="Add Appointment", command=add_appointment).pack(pady=5)
        tk.Button(appointment_window, text="Remove Appointment", command=remove_appointment).pack(pady=5)
        tk.Button(appointment_window, text="Back to Main Menu", command=close_appointment).pack(pady=5)

    appointment_menu()


# Function to close the application
def close_app():
    root.quit()


# the main window
root = tk.Tk()
root.title("Main Menu")

# buttons for each function
calendar_button = tk.Button(root, text="Calendar", command=open_calendar)
calendar_button.pack(pady=10)

prescription_button = tk.Button(root, text="Prescription", command=open_prescription)
prescription_button.pack(pady=10)

appointments_button = tk.Button(root, text="Appointments", command=open_appointments)
appointments_button.pack(pady=10)

close_button = tk.Button(root, text="Close", command=close_app)
close_button.pack(pady=10)

# Run the application
root.mainloop()
