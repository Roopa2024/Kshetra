import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import os, configparser, sys
import UI_support

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
font_settings = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'))
font_settings_bold = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'), "bold")
mapping = config.get('Filenames', 'mapping_sheet')

def add_group_4and5(frame, group_frames):

    # Payment Mode Selection
    tk.Label(group_frames["group4_frame"], text="Payment Mode:", font=font_settings_bold, bg="#99ccff").grid(row=3, column=0, sticky="w", pady=5)
    cash = tk.Radiobutton(group_frames["group4_frame"], text="Cash", bg="#99ccff", variable=selection_var, value="Cash", font=font_settings, command=lambda: toggle_cheque_fields())
    cheque = tk.Radiobutton(group_frames["group4_frame"], text="Cheque", bg="#99ccff", variable=selection_var, value="Cheque", font=font_settings, command=lambda: toggle_cheque_fields())
    online = tk.Radiobutton(group_frames["group4_frame"],  text="EFT", bg="#99ccff", variable=selection_var, value="EFT", font=font_settings, command=lambda: toggle_cheque_fields())
    cash.grid(row=4, column=0, sticky="w")
    cheque.grid(row=4, column=1, sticky="w")
    online.grid(row=4, column=2, sticky="w")

    # Cheque Frame (Right)
    cheque_frame = tk.Frame(group_frames["group6_frame"], borderwidth=2, relief="groove", bg="#99ccff")
    cheque_frame.grid(row=2, column=1, padx=50, pady=20, sticky="nsew")
    cheque_frame.grid_remove()  # Hide initially

    # Online Frame (Right)
    online_frame = tk.Frame(group_frames["group6_frame"], borderwidth=2, relief="groove", bg="#99ccff")
    online_frame.grid(row=2, column=1, padx=50, pady=20, sticky="nsew")
    online_frame.grid_remove()                                                          # Hide initially

    tk.Label(cheque_frame, text="Cheque Details", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0, columnspan=2, pady=10)
    cheque_fields = [
        ("Cheque Date:", DateEntry, {"date_pattern": "dd/mm/yyyy"}),
        ("Cheque No.:", tk.Entry, {"textvariable": tk.StringVar(), "validate": "key", "validatecommand": (validate_number, "%P")}),
        ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Account No.:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Bank name:", tk.Entry, {"validate": "key", "validatecommand": vcmd}),
        ("Branch:", tk.Entry, {"validate": "key", "validatecommand": vcmd_branch}),
    ]
    #underline_font = tkFont.Font(family=(config.get('FontSettings', 'font_name')), size=config.getint('FontSettings', 'font_size'), weight="bold", underline=1)
    tk.Label(online_frame, text="EFT", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0,columnspan=2, pady=10)
    online_fields = [
        ("Bank Date:", DateEntry, {"date_pattern": "dd/mm/yyyy"}),
        ("UTRN:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Bank name:", tk.Entry, {"validate": "key", "validatecommand": vcmd}),
        ("Branch:", tk.Entry, {"validate": "key", "validatecommand": vcmd_branch}),
    ]

    cheque_vars = {}                                                                    # Store variables for later access
    for i, (label, widget, options) in enumerate(cheque_fields):
        tk.Label(cheque_frame, text=label, font=font_settings, bg="#99ccff").grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
    
        var = options.get("textvariable", None)
        if var:                                                                         # Apply character limits
            limit = 6 if "Cheque No" in label else 11 if "IFSC Code" in label else 12
            var.trace_add("write", lambda *args, v=var, l=limit: UI_support.limit_chars(v, l))
            cheque_vars[label] = var                                                    
    
        entry = widget(cheque_frame, font=font_settings, width=13, **options)
        entry.grid(row=i + 1, column=1, padx=5, pady=5)
        cheque_vars[label] = entry                                                      
    cheque_frame.grid(row=2, column=1, rowspan=2, padx=50, pady=20, sticky="nsew")

    online_vars = {}
    for i, (label, widget, options) in enumerate(online_fields):
        tk.Label(online_frame, text=label, font=font_settings, bg="#99ccff").grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")
    
        var = options.get("textvariable", None)
        if var:                                                                         # Apply character limits
            if "UTRN:" in label:
                limit = 27 
            var.trace_add("write", lambda *args, v=var, l=limit: UI_support.limit_chars(v, l))
            online_vars[label] = var                                                    # Store for later
    
        entry = widget(online_frame, font=font_settings, width=28, **options)
        entry.grid(row=i + 1, column=1, padx=5, pady=5)
        online_vars[label] = entry                                                      # Store reference
    online_frame.grid(row=2, column=1, rowspan=2, padx=50, pady=20, sticky="nsew")

    include_bg(group_frames["group5_frame"], checkbox_var)
    submit_button = tk.Button(group_frames["group5_frame"], text="Print", font=font_settings, command=lambda: UI_support.submit(selection_var, cheque_vars, online_vars, selected_indx, checkbox_var))   # Submit Button
    submit_button.grid(row=2, column=2, padx=10, pady=10) 
    cancel_button = tk.Button(group_frames["group5_frame"], text="Cancel Receipt", font=font_settings, command=lambda: UI_support.cancel(selected_indx))   # Cancel Button
    cancel_button.grid(row=3, column=2, padx=10, pady=10)    

    def toggle_cheque_fields():
        #print(f"Selection is {selection_var.get()}")
        cheque_frame.grid() if selection_var.get() == "Cheque" else cheque_frame.grid_remove()
        online_frame.grid() if selection_var.get() == "EFT" else online_frame.grid_remove()
    toggle_cheque_fields()   

def include_bg(group_name, checkbox_var):
    checkbox = tk.Checkbutton(group_name, text="Include background", bg="#99ccff", variable=checkbox_var, font=font_settings)
    checkbox.grid(row=1, column=2, sticky="w")
     

def draw_receipt(frame):
    dest_excel_path = UI_support.get_excel_file(selected_indx)
    contribution_types = UI_support.get_dropdown_values(dest_excel_path, mapping, "Contribution Type")         # Load from "ContributionType" sheet
    contribution_intents = UI_support.get_dropdown_values(dest_excel_path, mapping, "Contribution Intent")     # Load from "ContributionIntent" sheet

    # Define variables to store selected values
    contribution_type_var = tk.StringVar(value=contribution_types[0] if contribution_types else "")
    contribution_intent_var = tk.StringVar(value=contribution_intents[0] if contribution_intents else "")

    frame_positions = [(1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (5, 0, 1), (2, 3, 1), (2, 2, 2)]                
    group_frames = {}

    for i, (row, col, span) in enumerate(frame_positions): #, start=1):
        frame_name = f"group{i}_frame"
        if frame_name == 'group6_frame':
            grp_frame = tk.Frame(frame,  bg="white")
        else:
            grp_frame = tk.Frame(frame, borderwidth=2, relief="groove", bg="#99ccff")
        grp_frame.grid(row=row, column=col, rowspan=span, padx=20, pady=20, sticky="nsew")
        group_frames[frame_name] = grp_frame

    # Grouped Fields (you can adjust as needed)
    fields_group_0 = [("Receipt Date:", DateEntry, {"date_pattern": "dd/mm/yyyy"})]

    fields_group_1 = [
        ("Contributor Name:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Address:", tk.Text, {"height": 3}),
        ("PAN:", tk.Entry, {"textvariable": tk.StringVar()}),
    ]

    fields_group_2 = [
        ("__HEADER__", "Contribution:", {"font": font_settings_bold}),  #(font_settings[0], font_settings[1], "bold")
        ("Contribution Type:", ttk.Combobox, {"values": contribution_types, "textvariable": contribution_type_var}),
        ("Contribution Intent:", ttk.Combobox, {"values": contribution_intents, "textvariable": contribution_intent_var}),
    ]

    fields_group_3 = [
        ("Amount:", tk.Entry, {"validate": "key", "validatecommand": (validate_number, "%S")}),
    ]

    fields_group_4 = []
    fields_group_5 = []
    fields_group_6 = []

    # Add widgets to the frames for each group of fields
    field_groups = {
        "group0_frame": fields_group_0, "group1_frame": fields_group_1, "group2_frame": fields_group_2, 
        "group3_frame": fields_group_3, "group4_frame": fields_group_4, "group5_frame": fields_group_5, 
        "group6_frame": fields_group_6,
    }
    for group_name, frame in group_frames.items():
        fields = field_groups.get(group_name)
        if fields:
            UI_support.add_widgets_to_group(frame, fields)
     
    add_group_4and5(frame, group_frames)

def draw_debit_voucher(frame):
    dv_entries = []
    group_frames = {}

    for i in range(3): 
        row_offset = i * 6
        receipt_frame = tk.LabelFrame(frame,  text=f"Voucher {i+1}", bg="#99ccff", font=font_settings_bold,
        bd=2,                                               # Border width
        relief="groove",                                    # Can be 'groove', 'ridge', 'sunken', 'raised', etc.
        padx=5, pady=5
        )
        receipt_frame.grid(row=row_offset+1 , column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        tk.Label(receipt_frame, text="Receipt Date:", font=font_settings, bg="#99ccff").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        date_entry = DateEntry(receipt_frame, date_pattern="dd/mm/yyyy", width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=2, column=1, padx=5, pady=5)

        name_var = tk.StringVar()
        tk.Label(receipt_frame, text="Pay to:", font=font_settings, bg="#99ccff").grid(row=3, column=0, sticky="e", padx=5, pady=5) 
        name_entry = tk.Entry(receipt_frame, font=font_settings, textvariable=name_var)
        limit = 200
        name_var.trace_add("write", lambda *args, v=name_var, l=limit: UI_support.limit_chars(v, l))
        name_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(receipt_frame, text="Amount:", font=font_settings, bg="#99ccff").grid(row=4, column=0, sticky="e", padx=5, pady=5) 
        amt_entry = tk.Entry(receipt_frame, font=font_settings, validate="key", validatecommand=(validate_number, "%S"))
        amt_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(receipt_frame, text="Purpose:", font=font_settings, bg="#99ccff").grid(row=5, column=0,sticky="e", padx=5, pady=5) 
        purpose_entry = tk.Text(receipt_frame, font=font_settings, height=3, width=40)
        purpose_entry.bind("<KeyRelease>", lambda event, e=purpose_entry: UI_support.limit_text_chars(event, e, 200))
        purpose_entry.grid(row=5, column=1, padx=5, pady=5)

        # Store all widget references in a dictionary
        dv_data = {
            'date': date_entry,
            'pay_to': name_entry,
            'amount': amt_entry,
            'purpose': purpose_entry
        }
        dv_entries.append(dv_data)

    print_frame = tk.LabelFrame(frame,  font=font_settings_bold, bg="#99ccff", bd=2, relief="groove", padx=10, pady=10 )
    print_frame.grid(row=1 , column=2, columnspan=1, padx=15, pady=10, sticky="ew")
    
    include_bg(print_frame, checkbox_var)
    submit_button = tk.Button(print_frame, text="Print", font=font_settings, command=lambda: UI_support.dv_print(dv_entries, selected_indx, checkbox_var))   # Submit Button
    submit_button.grid(row=2, column=2, padx=10, pady=10) 

    add_group_4and5(frame, group_frames)

def draw_inv_voucher(frame):
    for i in range(3):
        # Create a LabelFrame for each receipt
        receipt_frame = tk.LabelFrame(
        frame,
        text=f"Voucher {i + 1}",  # Title of the LabelFrame
        font=font_settings_bold,
        bg="#99ccff",
        bd=2,             # Border width
        relief="groove",  # Border style ('groove', 'sunken', etc.)
        padx=10,          # Padding inside the frame (left and right)
        pady=10           # Padding inside the frame (top and bottom)
        )

        # Place the LabelFrame in a unique row (using i * 7 to create a gap between each receipt)
        receipt_frame.grid(row=i * 7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Inside the LabelFrame, create widgets for the receipt details
        tk.Label(receipt_frame, text="Receipt Date:", font=font_settings, bg="#99ccff").grid(row=0, column=0, sticky="e", pady=5)
        date_entry = DateEntry(receipt_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        date_entry.grid(row=0, column=1, pady=5)

        tk.Label(receipt_frame, text="Pay to:", font=font_settings, bg="#99ccff").grid(row=1, column=0, sticky="e", pady=5)
        name_entry = tk.Entry(receipt_frame)
        name_entry.grid(row=1, column=1, pady=5)

        tk.Label(receipt_frame, text="Amount:", font=font_settings, bg="white") \
            .grid(row=2, column=0, sticky="e", pady=5)
        amount_entry = tk.Entry(receipt_frame)
        amount_entry.grid(row=2, column=1, pady=5)

        tk.Label(receipt_frame, text="Purpose:", font=font_settings, bg="white") \
            .grid(row=3, column=0, sticky="e", pady=5)
        purpose_entry = tk.Entry(receipt_frame)
        purpose_entry.grid(row=3, column=1, pady=5)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Receipt App")
        self.frames = {}
        self.current_frame = None

        # Navigation buttons
        nav_frame = tk.Frame(self.root)
        nav_frame.grid(row=0, column=0, sticky="ew")

        buttons = [
            ("Receipt", "Receipt"),
            ("Debit Voucher", "Debit Voucher"),
        ]

        # Step 1: Configure nav_frame columns to expand equally
        for i in range(len(buttons)):
            nav_frame.grid_columnconfigure(i, weight=1)  # Each button gets equal width 
        for i, (label, name) in enumerate(buttons):
            tk.Button(nav_frame, text=label, command=lambda name=name: self.show_frame(name)).grid(row=0, column=i, sticky="ew")

        # Build pages
        self.build_page1()
        self.build_page2()

        # Show first
        self.show_frame("Receipt")

    def show_frame(self, name):
        if self.current_frame:
            self.frames[self.current_frame].grid_forget()
        self.frames[name].grid(row=1, column=0, sticky="nsew")
        self.current_frame = name

    def build_page1(self):
        frame = tk.Frame(self.root,  bg="white")
        draw_receipt(frame)      
        self.frames["Receipt"] = frame

    def build_page2(self):
        frame = tk.Frame(self.root,  bg="white")
        draw_debit_voucher(frame)
        self.frames["Debit Voucher"] = frame

# Run the app
root = tk.Tk()

root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")        #set the App to window size

# Validation functions
validate_number = root.register(lambda char: char.isdigit() or char == "")
vcmd = (root.register(UI_support.validate_alpha), "%S", "%P")
vcmd_branch =(root.register(UI_support.validate_alpha_branch), "%S", "%P")

        
selection_var = tk.StringVar(value="Cash")
checkbox_var = tk.IntVar(value=0)
selected_indx = int(sys.argv[2])

app = App(root)
root.mainloop()
