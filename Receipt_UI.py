import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import os, configparser
import excel_data, pdf_data
import pandas as pd
import openpyxl
from openpyxl import load_workbook, Workbook
from openpyxl.drawing.image import Image

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
font_settings = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'))
width = config.getint('FontSettings', 'width')
xcl_file = config.get('Filenames', 'xcl_file')
xcl_sheet = config.get('Filenames', 'xcl_sheet')
entity_xcl = config.get('Filenames', 'input_files')
entity_xcls = entity_xcl.split(',')
heading = config['Heading']['heading']
headings = heading.split(',')
pdf_heading = config['Heading']['pdf_heading']
pdf_headings = pdf_heading.split(',')
entity = pdf_heading.split(',')

# Function to limit input length
def limit_chars(var, limit):
    if len(var.get()) > limit:
        var.set(var.get()[:limit])

# Function to limit characters in a Text widget (e.g., Address)
def limit_text_chars(event, text_widget, limit=120):
    current_text = text_widget.get("1.0", "end-1c")  # Get text without newline at the end
    if len(current_text) > limit:
        text_widget.delete("1.0", "end")  # Clear text
        text_widget.insert("1.0", current_text[:limit])

def on_selection(event, selected_heading, pdf_headings):
    index = event.widget.current()
    pdf_file.set(pdf_headings[index])

def selection_changed(*args):
    print(f"Selected option: {var.get()}")

# Tkinter Window
root = tk.Tk()
root.title("Receipt Input")
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")

# Validation functions
validate_number = root.register(lambda char: char.isdigit() or char == "")
validate_alpha = root.register(lambda char: char.isalpha() or char.isspace() or char == "")

# Main Frame (Left)
main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, padx=20, pady=20)

# Payment Selection
selection_var = tk.StringVar(value="Cash")
selected_index = tk.IntVar(value=0)
checkbox_var = tk.IntVar(value=0)
selected_heading = tk.StringVar()
pdf_file = tk.StringVar()
pdf_file.set(pdf_headings[0])

# Create input fields dynamically
fields = [
    ("Select an option:", tk.OptionMenu, {"options": headings}),
    ("Receipt Date:", DateEntry, {}),
    ("Contributor Name:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Address:", tk.Text, {"height": 3}),
    ("PAN:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Contribution Type:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Contribution Intent:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Amount:", tk.Entry, {"validate": "key", "validatecommand": (validate_number, "%S")}),
    ("Bank name:", tk.Entry, {"validate": "key", "validatecommand": (validate_alpha, "%S")}),
    ("Branch:", tk.Entry, {"validate": "key", "validatecommand": (validate_alpha, "%S")}),
]

input_vars = {}  # Store variables for later access

def on_var1_change(var, label, field_options_ref):
    selected_value = var.get()
    options_list = field_options_ref["options"]
    
    # Get the index of the selected value
    try:
        selected_index.set(options_list.index(selected_value))
    except ValueError:
        selected_index.set(-1)  # In case the value is not found

    print(f"Option changed to: {selected_value} (Index: {selected_index.get()}) and {field_options_ref}")

for i, (label, widget, field_options) in enumerate(fields):
    tk.Label(main_frame, text=label, font=font_settings).grid(row=i, column=0, sticky="w", pady=5)
    
    var = field_options.get("textvariable", None)
    if var:  # Apply character limits
        limit=10 if "PAN:" in label else 27 if "UTRN:" in label else 60
        var.trace_add("write", lambda *args, v=var, l=limit: limit_chars(v, l))
        input_vars[label] = var 
    
    if widget == tk.Text:  # Special handling for Text widgets
        entry = widget(main_frame, font=font_settings, width=width, height=3)  
        entry.bind("<KeyRelease>", lambda event, e=entry, l=120: limit_text_chars(event, e, l))  # Bind character limit
    #elif widget == tk.OptionMenu:
    elif label == "Select an option:":
        var1 = tk.StringVar()                   # ✅ Create a StringVar to track selection
        var1.set(field_options["options"][0])         # ✅ Set default option
        print("Options Dictionary:", label, field_options)

        var1.trace_add("write", lambda *args, v=var1, f_opts=field_options: on_var1_change(v, label, f_opts))
        entry = tk.OptionMenu(main_frame, var1, *field_options["options"])  # Create dropdown
        input_vars[label] = var1  # ✅ Store the StringVar, NOT the widget
        entry.grid(row=i, column=1, pady=5)
    else:
        entry = widget(main_frame, font=font_settings, width=width, **field_options)

    entry.grid(row=i, column=1, pady=5)
    input_vars[label] = entry  # Store reference

# Payment Mode Selection
tk.Label(main_frame, text="Select Payment Method:", font=font_settings).grid(row=len(fields), column=0, sticky="w", pady=5)
cash = tk.Radiobutton(main_frame, text="Cash", variable=selection_var, value="Cash", font=font_settings, command=lambda: toggle_cheque_fields())
cheque = tk.Radiobutton(main_frame, text="Cheque", variable=selection_var, value="Cheque", font=font_settings, command=lambda: toggle_cheque_fields())
online = tk.Radiobutton(main_frame, text="EFT", variable=selection_var, value="EFT", font=font_settings, command=lambda: toggle_cheque_fields())
cash.grid(row=len(fields), column=1, sticky="w")
cheque.grid(row=len(fields) + 1, column=1, sticky="w")
online.grid(row=len(fields) + 2, column=1, sticky="w")

checkbox = tk.Checkbutton(main_frame, text="Include background", variable=checkbox_var)  #, command=on_checkbox_toggle)
checkbox.grid(row=len(fields) + 3, column=0, sticky="w")

print(f" Checkbox = {checkbox} var = {checkbox_var.get()}")

# Cheque Frame (Right)
cheque_frame = tk.Frame(root, borderwidth=2, relief="groove")
cheque_frame.grid(row=0, column=1, padx=50, pady=20, sticky="n")
cheque_frame.grid_remove()  # Hide initially

# Online Frame (Right)
online_frame = tk.Frame(root, borderwidth=2, relief="groove")
online_frame.grid(row=0, column=1, padx=50, pady=20, sticky="n")
online_frame.grid_remove()  # Hide initially

tk.Label(cheque_frame, text="Cheque Details", font=(font_settings[0], font_settings[1], "bold")).grid(row=0, column=0, columnspan=2, pady=10)

cheque_fields = [
    ("Cheque Date:", DateEntry, {}),
    ("Cheque No.:", tk.Entry, {"textvariable": tk.StringVar(), "validate": "key", "validatecommand": (validate_number, "%P")}),
    ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Account No.:", tk.Entry, {"textvariable": tk.StringVar()})
]

online_fields = [
    ("Bank Date:", DateEntry, {}),
    ("UTRN:", tk.Entry, {"textvariable": tk.StringVar()}),
]

cheque_vars = {}  # Store variables for later access
for i, (label, widget, options) in enumerate(cheque_fields):
    tk.Label(cheque_frame, text=label, font=font_settings).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
    
    var = options.get("textvariable", None)
    if var:  # Apply character limits
        limit = 6 if "Cheque No" in label else 11 if "IFSC Code" in label else 12
        var.trace_add("write", lambda *args, v=var, l=limit: limit_chars(v, l))
        cheque_vars[label] = var  # Store for later
    
    entry = widget(cheque_frame, font=font_settings, width=30, **options)
    entry.grid(row=i + 1, column=1, padx=5, pady=5)
    cheque_vars[label] = entry  # Store reference

online_vars = {}
for i, (label, widget, options) in enumerate(online_fields):
    tk.Label(online_frame, text=label, font=font_settings).grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
    
    var = options.get("textvariable", None)
    if var:  # Apply character limits
        if "UTRN:" in label:
            limit = 27 
        var.trace_add("write", lambda *args, v=var, l=limit: limit_chars(v, l))
        online_vars[label] = var  # Store for later
    
    entry = widget(online_frame, font=font_settings, width=30, **options)
    entry.grid(row=i + 1, column=1, padx=5, pady=5)
    online_vars[label] = entry  # Store reference

# Toggle Cheque Fields
def toggle_cheque_fields():
    cheque_frame.grid() if selection_var.get() == "Cheque" else cheque_frame.grid_remove()
    online_frame.grid() if selection_var.get() == "EFT" else online_frame.grid_remove()

# Submit Function
def submit():   
    details = {}
    for label, var in input_vars.items():
        if isinstance(var, tk.StringVar):                       # Dropdown (OptionMenu) and Entry (StringVar)
            details[label] = var.get()
        elif isinstance(var, tk.Entry):                         # Normal Entry widget
            details[label] = var.get()
        elif isinstance(var, tk.Text):                          # Multiline Text widget
            details[label] = var.get("1.0", "end-1c").strip()   # Remove extra newlines
        elif isinstance(var, tk.OptionMenu):
            details[label] = var1.get()
        else:
            details[label] = ""                                 # Handle unexpected types safely
    print("Details:", details)
    
    print(f"Pay mode1 = {selection_var.get()}")
    if selection_var.get() == "Cheque":
        cheque_details = {
            label: var.get() if isinstance(var, tk.StringVar) 
            else var.get("1.0", "end-1c") if isinstance(var, tk.Text)
            else var.get()
            for label, var in cheque_vars.items()}
        print("Cheque Details:", cheque_details)
        payment_mode = 'Cheque'
        cheque_date = cheque_details.get('Cheque Date:')
        cheque_no = cheque_details.get('Cheque No.:')
        IFSC = cheque_details.get('IFSC Code:')
        ac_no =  cheque_details.get('Account No.:')
        bank_date, utrn = '', ''
    elif selection_var.get() in ("Cash", "EFT"):
        print(f"Pay mode = {selection_var.get()}")
        payment_mode = selection_var.get()
        cheque_date, cheque_no, IFSC, ac_no = '', '', '', ''
        if payment_mode == "EFT":
            online_details = {
                label: var.get() if isinstance(var, tk.StringVar) 
                else var.get("1.0", "end-1c") if isinstance(var, tk.Text)
                else var.get()
                for label, var in online_vars.items()}
            bank_date = online_details.get('Bank Date:')
            utrn = online_details.get('UTRN:')
        elif payment_mode == 'Cash':
            bank_date, utrn = '', ''
    
    index = selected_index.get()
    id, globe_id, bar_text = excel_data.increment_counter(1, entity_xcls[index])
    #globe_id = excel_data.increment_counter(2)
    
    print(f" id = {id} and globeid = {globe_id}")
    barcode_path = excel_data.generate_barcode(str(globe_id))   #barcode is temporarily saved in the current dir
    excel_data.draw_text(f"{barcode_path}.png", bar_text)       #adding TextColumn to the barcode
    print("Barcode inserted into Excel successfully!")

    print("Data to Save in Excel", id)
    kwargs = {
        'Id.' : id,
        'GlobeId' : '',
        'TextColumn' : '',
        'QR Code' : '',
        'Receipt Date' : details.get("Receipt Date:"),
        'Contributor Name' : details.get("Contributor Name:"),
        'Address' : details.get("Address:"),
        'PAN' : details.get("PAN:"),
        'Contribution Type' : details.get("Contribution Type:"),
        'Contribution Intent' : details.get("Contribution Intent:"),
        'Payment Mode' : payment_mode,
        'Cheque Date' : cheque_date,
        'Cheque No.' : cheque_no,
        'IFSC Code' : IFSC,
        'A/C No.' : ac_no,
        'Bank Date' : bank_date,
        'UTRN' : utrn,
        'Amount' : details.get("Amount:"),
        'Barcode' : f"{barcode_path}.png",
        'Bank Name' : details.get("Bank name:"),
        'Branch Name' : details.get("Branch:"),
    }
    index = selected_index.get()
    excel_data.save_to_excel(entity_xcls[index], id, **kwargs)

    qr_code_path = excel_data.generate_qr_code(kwargs)
    kwargs["QR Code"] = qr_code_path                        # Update kwargs with QR Code path
    pdf_path = f"pdfs/{kwargs['Id.']}.pdf"
    os.makedirs("pdfs", exist_ok=True)
    selected_entity = var1.get()                            # Generate PDF directly from kwargs
    print(f"Entity is {selected_entity}")
    index = selected_index.get()
    pdf_data.create_pdf_from_kwargs(kwargs, pdf_path, entity[index], checkbox_var.get())

    try:
        df = pd.read_excel(entity_xcls[index], xcl_sheet)
        workbook = openpyxl.load_workbook(entity_xcls[index])
        sheet = workbook.active
        pdf_dir = pdf_data.get_pdf_directory()
        os.makedirs(pdf_dir, exist_ok=True)
    except ValueError as e:
        print(f"Error: Worksheet named '{xcl_sheet}' not found. Please check the sheet name.")
        messagebox.showinfo(f"Error:", f"Worksheet named '{xcl_sheet}' not found. Please check the sheet name.") 
    except Exception as e:
        print(e)

    rows_data = []                                          # Loop through each row in the DataFrame and create a separate PDF

    for index, row in df.iterrows():
        row_dict = {df.columns[i]: row.iloc[i] for i in range(len(df.columns))}
        rows_data.insert(id, row_dict) 
        pdf_name = f"pdfs/{index}.pdf"
    idx = selected_index.get()
    workbook.save(entity_xcls[idx])

submit_button = tk.Button(root, text="Print", font=font_settings, command=submit)   # Submit Button
submit_button.grid(row=1, column=0, columnspan=2, pady=20)

toggle_cheque_fields()                                                              # Ensure correct visibility
root.mainloop()
