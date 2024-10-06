# Define the Patient class
class Patient:
    def __init__(self, name, age, medical_conditions):
        self.name = name
        self.age = age
        self.medical_conditions = medical_conditions
        self.tasks = []  # List to store daily tasks
    
    def add_task(self, task):
        self.tasks.append(task)
    
    def display_tasks(self):
        print(f"Tasks for {self.name}:")
        for task in self.tasks:
            print(f"- {task.name} (Due: {task.due_date}) - {task.status}")

# Define the Task class
class Task:
    def __init__(self, name, description, assigned_caregiver, due_date, status='Pending'):
        self.name = name
        self.description = description
        self.assigned_caregiver = assigned_caregiver
        self.due_date = due_date
        self.status = status

    def mark_completed(self):
        self.status = 'Completed'

# Define the Caregiver class
class Caregiver:
    def __init__(self, name, contact_info):
        self.name = name
        self.contact_info = contact_info
        self.patients = []  # List to store patients managed by the caregiver

    def add_patient(self, patient):
        self.patients.append(patient)

    def view_patient_tasks(self, patient_name):
        for patient in self.patients:
            if patient.name == patient_name:
                patient.display_tasks()

# Function to create a new patient with user input
def create_patient():
    name = input("Enter the patient's name: ")
    age = int(input(f"Enter {name}'s age: "))
    conditions = input(f"Enter {name}'s medical conditions (comma-separated): ").split(', ')
    return Patient(name, age, conditions)

# Function to create a new caregiver with user input
def create_caregiver():
    name = input("Enter the caregiver's name: ")
    contact_info = input(f"Enter {name}'s contact information: ")
    return Caregiver(name, contact_info)

# Function to create a new task for a patient
def create_task(caregiver_name):
    name = input("Enter the task name: ")
    description = input(f"Enter a description for the task '{name}': ")
    due_date = input(f"Enter the due date for '{name}' (YYYY-MM-DD): ")
    return Task(name, description, caregiver_name, due_date)

# Main function to interactively add caregivers, patients, and tasks
def main():
    print("Welcome to the Caregiver Management System")
    
    # Create a caregiver
    caregiver = create_caregiver()

    # Add a patient to the caregiver's care list
    patient = create_patient()
    caregiver.add_patient(patient)

    # Add tasks for the patient
    add_more_tasks = 'y'
    while add_more_tasks.lower() == 'y':
        task = create_task(caregiver.name)
        patient.add_task(task)
        add_more_tasks = input("Do you want to add another task? (y/n): ")

    # View patient tasks
    caregiver.view_patient_tasks(patient.name)

# Run the main function
main()
