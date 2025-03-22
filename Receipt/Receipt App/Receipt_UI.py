import tkinter as tk
from tkcalendar import DateEntry
import os, configparser
import excel_data, pdf_data

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)

font_settings = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'))
width = config.getint('FontSettings', 'width')

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

# Create input fields dynamically
fields = [
    ("Select Date:", DateEntry, {}),
    ("Contributor Name:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Address:", tk.Text, {"height": 3}),
    ("PAN:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Contribution Type:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Contribution Intent:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Bank Date:", DateEntry, {}),
    ("UTRN:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Amount:", tk.Entry, {"validate": "key", "validatecommand": (validate_number, "%S")}),
    ("Bank name:", tk.Entry, {"validate": "key", "validatecommand": (validate_alpha, "%S")}),
    ("Branch:", tk.Entry, {"validate": "key", "validatecommand": (validate_alpha, "%S")}),
]

input_vars = {}  # Store variables for later access

for i, (label, widget, options) in enumerate(fields):
    tk.Label(main_frame, text=label, font=font_settings).grid(row=i, column=0, sticky="w", pady=5)
    
    var = options.get("textvariable", None)
    if var:  # Apply character limits
        limit=10 if "PAN:" in label else 27 if "UTRN:" in label else 60
        var.trace_add("write", lambda *args, v=var, l=limit: limit_chars(v, l))
        input_vars[label] = var 
    
    if widget == tk.Text:  # Special handling for Text widgets
        entry = widget(main_frame, font=font_settings, width=width, height=3)  
        entry.bind("<KeyRelease>", lambda event, e=entry, l=120: limit_text_chars(event, e, l))  # Bind character limit
    else:
        entry = widget(main_frame, font=font_settings, width=width, **options)

    entry.grid(row=i, column=1, pady=5)
    input_vars[label] = entry  # Store reference

# Payment Mode Selection
tk.Label(main_frame, text="Select Payment Method:", font=font_settings).grid(row=len(fields), column=0, sticky="w", pady=5)
cash = tk.Radiobutton(main_frame, text="Cash", variable=selection_var, value="Cash", font=font_settings, command=lambda: toggle_cheque_fields())
cheque = tk.Radiobutton(main_frame, text="Cheque", variable=selection_var, value="Cheque", font=font_settings, command=lambda: toggle_cheque_fields())
cash.grid(row=len(fields), column=1, sticky="w")
cheque.grid(row=len(fields) + 1, column=1, sticky="w")

# Cheque Frame (Right)
cheque_frame = tk.Frame(root, borderwidth=2, relief="groove")
cheque_frame.grid(row=0, column=1, padx=50, pady=20, sticky="n")
cheque_frame.grid_remove()  # Hide initially

tk.Label(cheque_frame, text="Cheque Details", font=(font_settings[0], font_settings[1], "bold")).grid(row=0, column=0, columnspan=2, pady=10)

cheque_fields = [
    ("Cheque Date:", DateEntry, {}),
    ("Cheque No.:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
    ("Account No.:", tk.Entry, {"textvariable": tk.StringVar()}),
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

# Toggle Cheque Fields
def toggle_cheque_fields():
    cheque_frame.grid() if selection_var.get() == "Cheque" else cheque_frame.grid_remove()

# Submit Function
def submit():
    details = {
        label: var.get() if isinstance(var, tk.StringVar) 
        else var.get("1.0", "end-1c") if isinstance(var, tk.Text)
        else var.get()
        for label, var in input_vars.items()}
    print("Details:", details)
    
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
    elif selection_var.get() == "Cash":
        payment_mode = 'Cash'
        cheque_date = ''
        cheque_no = ''
        IFSC = ''
        ac_no = ''
    else:
        payment_mode = 'Online'
    
    id = excel_data.increment_counter(1)
    globe_id = excel_data.increment_counter(2)
    print("Data to Save in Excel", globe_id)
    kwargs = {
        'Id.' : id,
        'Globe Id' : globe_id,
        'QR Code' : '',
        'Receipt Date' : details.get("Select Date:"),
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
        'Bank Date' : details.get("Bank Date:"),
        'UTRN' : details.get("UTRN:"),
        'Amount' : details.get("Amount:"),
        'Barcode' : '',
        'Bank Name' : details.get("Bank name:"),
        'Branch Name' : details.get("Branch:"),
    }
    excel_data.save_to_excel(**kwargs)
    excel_data.generate_barcode()
    pdf_data.generate_pdf()

# Submit Button
submit_button = tk.Button(root, text="Print", font=font_settings, command=submit)
submit_button.grid(row=1, column=0, columnspan=2, pady=20)

toggle_cheque_fields()  # Ensure correct visibility
root.mainloop()
