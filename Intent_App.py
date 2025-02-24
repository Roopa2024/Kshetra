import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import subprocess
import configparser
import tkinter.messagebox as messagebox

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\Intent_excel_to_pdf.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
font_name = config.get('FontSettings', 'font_name')
font_size = int(config.get('FontSettings', 'font_size'))
#excel_to_pdf_path = config.get('Filenames', 'script')
global root

# Function to submit the selected file and process it in a script
def submit_file(root, file_path, sheet_name):
    file_path_value = file_path.get()
    sheet = sheet_name.get()  
    if sheet == "":
        sheet = "Please enter the Sheet name"
    print (f"PATH {file_path_value} and sheet is {sheet}")

    # Check if the file path is not empty and if the file exists
    if file_path_value and os.path.isfile(file_path_value):
        print(f"File submitted: {file_path_value}")
        # Call your Python script here, passing the file as input
        process_file(root, file_path_value, sheet)
    else:
        print("Please select a valid file.")
        messagebox.showinfo("Error", "Please select a valid file.")

def get_file_path(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundles the app into a temporary folder, we use _MEIPASS to get the path to bundled files
        return os.path.join(sys._MEIPASS, filename)
    else:
        # For normal Python execution, just return the direct path
        return filename
    
def process_file(root, file_path, sheet_name):
    print(f"Processing the file: {file_path}")
    excel_to_pdf_path = get_file_path('Intent_excel_to_pdf.py')
    print(f"Path to excel_to_pdf.py: {excel_to_pdf_path}")
    command = ["python", excel_to_pdf_path, "--filepath", file_path, "--sheetname", sheet_name]
    print(f"COMMAND {command}")
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Output from script:", result.stdout)
        messagebox.showinfo("Done", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error executing script:", e)
        print("Error output:", e.stderr)

def browse_file(file_path, file_label):
    file = filedialog.askopenfilename(title="Select a file")  # Open file dialog
    if file:  # If a file is selected
        file_path.set(file)  # Store the file path in the StringVar
        file_label.config(text=f"Selected file: {file}")  # Update the label to show the selected file

def create_input_field(root):
    # Create an input field (Entry widget) for user input
    entry_label = tk.Label(root, text="Please enter the Sheet name:")
    entry_label.pack(padx=10, pady=5)

    input_field = tk.Entry(root, width=20)  # Width defines the visible space for text input
    input_field.pack(padx=10, pady=5)

    return input_field

def update_selected_value(event): #(event,dropdown):
    global selected_value, selected_index
    dropdown = event.widget
    selected_value = dropdown.get()  # Update the global variable with the selected value
    selected_index = dropdown.current()
    print(f"Option {selected_value} and {selected_index}") 

def start_gui():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("")

    # Create a label
    label = tk.Label(root, text="Excel to PDF Converter:")
    label.pack(padx=10, pady=5)

    file_path = tk.StringVar()
    # Create a label for the file selection
    file_label = tk.Label(root, text="Select the data file:")
    file_label.pack(padx=10, pady=5)
    # Create a "Browse" button to trigger the file dialog
    browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_path, file_label))
    browse_button.pack(padx=10, pady=5)
    sheet_entry = create_input_field(root)
    
    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_file(root, file_path, sheet_entry))
    submit_button.pack(padx=10, pady=10)

    # Run the Tkinter event loop
    root.mainloop()

# Run the GUI
start_gui()
