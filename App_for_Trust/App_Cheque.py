import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import sys
import subprocess
import configparser
import tkinter.messagebox as messagebox

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\excel_to_pdf.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
font_name = config.get('FontSettings', 'font_name')
font_size = int(config.get('FontSettings', 'font_size'))

global root
#names = ['S_C_Print', 'P_C_Print', 'I_C_Print']
pdf_heading = config['Heading']['pdf_heading'] 
heading = config['Heading']['heading']
global val_heading, val_pdf_heading

# Function to submit the selected file and process it in a script
def submit_file(root, file_path, sheet_name, sel_heading, sel_pdf_heading):
    file_path_value = file_path.get()
    sheet = sheet_name.get()  
    #selected_index = dropdown.current()
    print (f"PATH {file_path_value} and sheet is {sheet} and heading = {sel_heading} pdf head = {sel_pdf_heading}")

    # Check if the file path is not empty and if the file exists
    if file_path_value and os.path.isfile(file_path_value):
        print(f"File submitted: {file_path_value}")
        # Call your Python script here, passing the file as input
        process_file(root, file_path_value, sheet, sel_heading, sel_pdf_heading)
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
    
def process_file(root, file_path, sheet_name, idx_heading, idx_pdf_heading):
    print(f"Processing the file: {file_path}")
    excel_to_pdf_path = get_file_path('excel_to_pdf_Cheque.py')
    print(f"Path to excel_to_pdf.py: {excel_to_pdf_path}")
    command = ["python", excel_to_pdf_path, "--filepath", file_path, "--sheetname", sheet_name, "--option1", str(idx_heading), "--option2", str(idx_pdf_heading)]

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

def update_selected_value(event,dropdown):
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
    label = tk.Label(root, text="Choose an option:")
    label.pack(padx=10, pady=5)
    selected_heading = tk.StringVar()
    selected_pdf_heading = tk.StringVar()

    headings = heading.split(',')
    pdf_headings = pdf_heading.split(',')
    print(f"Option before {headings} and {pdf_headings}")

    #selected_heading = tk.StringVar(value=headings[0])  # Set default to first item
    #selected_pdf_heading = tk.StringVar(value=pdf_headings[0])

    # Create First Combobox
    dropdown1 = ttk.Combobox(root, values=headings, textvariable=selected_heading, width=40)
    dropdown1.pack(pady=10)
    dropdown1.current(0)
    dropdown1.tk.eval(f"{dropdown1} configure -justify center")
    # Create Second Combobox
    dropdown2 = ttk.Combobox(root, values=pdf_headings, textvariable=selected_pdf_heading, width=40)
    dropdown2.pack(pady=10)
    dropdown2.current(3)
    dropdown2.tk.eval(f"{dropdown2} configure -justify center")

    def on_selection(event):
        global val_heading, val_pdf_heading
        val_heading = selected_heading.get()
        val_pdf_heading = selected_pdf_heading.get()
        print(f"cval = {val_heading} and {val_pdf_heading}")
        print("Dropdown 1 Selected:", selected_heading.get())
        print("Dropdown 2 Selected:", selected_pdf_heading.get())

    dropdown1.bind("<<ComboboxSelected>>", on_selection)
    dropdown2.bind("<<ComboboxSelected>>", on_selection)

    #val_heading = selected_heading.get()
    #val_pdf_heading = selected_pdf_heading.get()
    #print(f"Option after {val_heading} and {val_pdf_heading}") 
    file_path = tk.StringVar()
    # Create a label for the file selection
    file_label = tk.Label(root, text="Select a file:")
    file_label.pack(padx=10, pady=5)
    # Create a "Browse" button to trigger the file dialog
    browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_path, file_label))
    browse_button.pack(padx=10, pady=5)
    
    sheet_entry = create_input_field(root)
    
    # Create a submit button
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_file(root, file_path, sheet_entry, selected_heading.get(), selected_pdf_heading.get())) # val_heading, val_pdf_heading)) #dropdown)) #selected_index))
    submit_button.pack(padx=10, pady=10)

    # Run the Tkinter event loop
    root.mainloop()

# Run the GUI
start_gui()
