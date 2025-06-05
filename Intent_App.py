import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import subprocess
import configparser
import tkinter.messagebox as messagebox

configuration_path = os.path.dirname(os.path.abspath(__file__))+r"\config\Intent_excel_to_pdf.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
font_name = config.get('FontSettings', 'font_name')
font_size = int(config.get('FontSettings', 'font_size'))
global root

def submit_file(root, file_path, sheet_name):
    file_path_value = file_path.get()
    sheet = sheet_name.get()  
    if sheet == "":
        sheet = "Please enter the Sheet name"
    print (f"PATH {file_path_value} and sheet is {sheet}")

    if file_path_value and os.path.isfile(file_path_value):                 # Check if the file path is not empty and if the file exists
        process_file(root, file_path_value, sheet)                          # Call your Python script here, passing the file as input
    else:
        print("Please select a valid file.")
        messagebox.showinfo("Error", "Please select a valid file.")

def get_file_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)                         # PyInstaller bundles the app into a temporary folder, we use _MEIPASS to get the path to bundled files
    else:
        return filename                                                     # For normal Python execution, just return the direct path
    
def process_file(root, file_path, sheet_name):
    excel_to_pdf_path = get_file_path('Intent_excel_to_pdf.py')
    command = ["python", excel_to_pdf_path, "--filepath", file_path, "--sheetname", sheet_name]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print("Output from script:", result.stdout)
        messagebox.showinfo("Done", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error executing script:", e , e.stderr)

def browse_file(file_path, file_label):
    file = filedialog.askopenfilename(title="Select a file")            # Open file dialog
    if file:                                                            # If a file is selected
        file_path.set(file)                                             # Store the file path in the StringVar
        file_label.config(text=f"Selected file: {file}")                # Update the label to show the selected file

def create_input_field(root):
    entry_label = tk.Label(root, text="Please enter the Sheet name:")
    entry_label.pack(padx=10, pady=5)
    input_field = tk.Entry(root, width=20)  
    input_field.pack(padx=10, pady=5)
    return input_field

def update_selected_value(event):
    global selected_value, selected_index
    dropdown = event.widget
    selected_value = dropdown.get()                                         # Update the global variable with the selected value
    selected_index = dropdown.current()
    print(f"Option {selected_value} and {selected_index}") 

def start_gui():
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("")

    label = tk.Label(root, text="Excel to PDF Converter:")
    label.pack(padx=10, pady=5)

    file_path = tk.StringVar()
    file_label = tk.Label(root, text="Select the data file:")
    file_label.pack(padx=10, pady=5)
    browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_path, file_label)) # Create a "Browse" button to trigger the file dialog
    browse_button.pack(padx=10, pady=5)
    sheet_entry = create_input_field(root)
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_file(root, file_path, sheet_entry))
    submit_button.pack(padx=10, pady=10)

    root.mainloop()                                                     # Run the Tkinter event loop

start_gui()                                                             # Run the GUI
