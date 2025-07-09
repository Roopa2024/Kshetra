import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import tkinter.font as tkfont
import os, configparser
import pandas as pd
import UI_support

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
font_settings = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'))
font_settings_bold = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'), "bold")
voucher_entity_xcl = config.get('Filenames', 'voucher_input_files')
voucher_entity_xcls = voucher_entity_xcl.split(',')
voucher_mapping_xcl = config.get('Filenames', 'voucher_mapping_files')
voucher_mapping_xcls = voucher_mapping_xcl.split(',')
invoice_entity_xcl = config.get('Filenames', 'invoice_input_files')
invoice_entity_xcls = invoice_entity_xcl.split(',')
invoice_mapping_xcl = config.get('Filenames', 'invoice_mapping_files')
invoice_mapping_xcls = invoice_mapping_xcl.split(',')
sheet_map= config.get('Filenames', 'mapping_sheet')

selected_option = {}   

def extract_purchase_code(purchase_head, purchase_category):
    purchase_head = str(purchase_head) if purchase_head is not None else ""
    purchase_category = str(purchase_category) if purchase_category is not None else ""
    
    head_caps = ''.join([ch for ch in purchase_head if ch.isupper()])
    cat_caps = ''.join([ch for ch in purchase_category if ch.isupper()])
    combined = f"{head_caps}_{cat_caps}" if head_caps or cat_caps else 'xx' #head_caps + cat_caps
    return combined if combined else 'XX'   #capitals if capitals else 'XX' 

def generate_unique_codes(df):
    code_to_data = {}
    unique_codes = []
    seen_codes = set()

    for _, row in df.iterrows():
        head = str(row['Purchase Head']).strip()
        category = str(row.get('Purchase Category', '')).strip()
        expense = str(row.get('Expense Type', '')).strip()

        base_code = extract_purchase_code(head, category)

        # Avoid duplicates (optional: you can allow duplicates if needed)
        if base_code not in seen_codes:
            unique_codes.append(base_code)
            seen_codes.add(base_code)
            code_to_data[base_code] = {
                "head": head,
                "category": category,
                "expense_type": expense
            }

    #print(f"UNIQUE CODES: {unique_codes}")
    return unique_codes, code_to_data


def load_excel_and_generate_codes(file_path):
    df = pd.read_excel(file_path, sheet_name=sheet_map)
    if 'Purchase Head' not in df.columns:
        raise ValueError("Excel must contain 'Purchase Head' column")
    # Identify all Purchase Category columns
    category_cols = [col for col in df.columns if 'Purchase Category' in col]    
    # Expand the DataFrame: one row per (Head, Category)
    expanded_rows = []
    for _, row in df.iterrows():
        head = row['Purchase Head']
        for cat_col in category_cols:
            category = row[cat_col]
            if pd.notna(category) and str(category).strip():
                expanded_rows.append({
                    'Purchase Head': head,
                    'Purchase Category': category,
                    'Expense Type': row.get('Expense Type', '')
                })

    expanded_df = pd.DataFrame(expanded_rows)

    # Apply code generation
    expanded_df['Purchase Code'] = expanded_df.apply(
        lambda row: extract_purchase_code(row['Purchase Head'], row['Purchase Category']),
        axis=1
    )
    codes, code_to_data = generate_unique_codes(expanded_df)    #df)
    #df['Purchase Code'] = codes     
    return expanded_df, codes, code_to_data

def load_data(file_path):
    df = pd.read_excel(file_path, sheet_name=sheet_map)
    # Assume first column is Purchase Head
    head_col = df.columns[0]
    category_cols = df.columns[1:-1]  # Exclude first (head) and last (expense type)
    expense_type_col = df.columns[-1]

    mapping = {}
    expense_type_mapping = {}

    for _, row in df.iterrows():
        head = row[head_col]
        if pd.isna(head):
            continue
        # Collect all non-empty categories in the row
        categories = [str(row[col]).strip() for col in category_cols if pd.notna(row[col]) and str(row[col]).strip()]
        mapping[head] = categories
        expense_type_mapping[head] = row[expense_type_col]
    return list(mapping.keys()), mapping, expense_type_mapping

def on_head_selected(purchase_head_cb, purchase_category_cb, expense_entry, purchase_code_var):
    selected_head = purchase_head_cb.get().strip()

    for head, categories in head_to_categories.items():
        if head.strip().lower() == selected_head.lower():
            purchase_category_cb['values'] = categories
            if categories:
                first_category = categories[0]
                purchase_category_cb.set(first_category)
                if purchase_code_var is not None:
                    base_code = extract_purchase_code(selected_head, first_category)
                    purchase_code_var.set(base_code)
            else:
                purchase_category_cb.set('')
                if purchase_code_var is not None:
                    purchase_code_var.set('')

            # Update Expense Type Entry
            expense_type = head_to_expense_type.get(head, '')
            expense_entry.config(state="normal")
            expense_entry.delete(0, tk.END)
            expense_entry.insert(0, expense_type)
            expense_entry.config(state="readonly")
            break

def on_code_selected(code_cb, head_cb, category_cb, expense_entry, local_code_to_data):
    selected_code = code_cb.get()
    data = local_code_to_data.get(selected_code, None)

    if data:
        head_cb.set(data['head'])                                           # Update Head
        categories = head_to_categories.get(data['head'], [])               # Update Category list and selection
        category_cb['values'] = categories
        if data['category'] in categories:
            category_cb.set(data['category'])
        else:
            category_cb.set('')

        # Update Expense Type
        #expense_type = head_to_expense_type.get(head, '')
        expense_entry.config(state='normal')
        expense_entry.delete(0, tk.END)
        expense_entry.insert(0, data['expense_type'])
        expense_entry.config(state='readonly')
    else:
        # Reset all fields
        head_cb.set('')
        category_cb.set('')
        expense_entry.config(state='normal')
        expense_entry.delete(0, tk.END)

#Voucher toggle function
def toggle_voucher_mode(index, selected_option, cheque_frame, online_frame, voucher_data):
    print(f"toggle_voucher_mode: Selection1 = {selected_option[index].get()}")
    selected_value = selected_option[index].get()
    voucher_data['payment_mode'].set(selected_value)
    cheque_frame.grid() if selected_value == "Cheque" else cheque_frame.grid_remove()
    online_frame.grid() if selected_value == "EFT" else online_frame.grid_remove()

def add_payment_mode(count, selected_option, group_frames, frame_name_options, cheque_frame, online_frame, voucher_data):
    selected_option[count] = tk.StringVar(value="Cash")

    tk.Label(group_frames[frame_name_options], text="Payment Mode:", font=font_settings_bold, bg="#99ccff").grid(row=1, column=2, sticky="w", pady=5)
    cash = tk.Radiobutton(group_frames[frame_name_options], text="Cash", bg="#99ccff", variable=selected_option[count], value="Cash", font=font_settings, command=lambda c=count: toggle_voucher_mode(c, selected_option, cheque_frame, online_frame, voucher_data))
    cheque = tk.Radiobutton(group_frames[frame_name_options], text="Cheque", bg="#99ccff", variable=selected_option[count], value="Cheque", font=font_settings, command=lambda c=count: toggle_voucher_mode(c, selected_option, cheque_frame, online_frame, voucher_data))
    online = tk.Radiobutton(group_frames[frame_name_options],  text="EFT", bg="#99ccff", variable=selected_option[count], value="EFT", font=font_settings, command=lambda c=count: toggle_voucher_mode(c, selected_option, cheque_frame, online_frame, voucher_data))
    cash.grid(row=2, column=2, sticky="w")
    cheque.grid(row=3, column=2, sticky="w")
    online.grid(row=4, column=2, sticky="w") 

def get_validate_number(root):
    return root.register(lambda char: char.isdigit() or char == "" or len(char) < 10)

def update_purchase_code(receipt_frame,mapping_voucher_path):
        global head_to_categories, head_to_expense_type, code_to_data
        purchase_code_var = tk.StringVar()
        purchase_head_var = tk.StringVar()
        purchase_category_var = tk.StringVar()
        expense_type_var = tk.StringVar()

        tk.Label(receipt_frame, text="Exp. Type:", font=font_settings, bg="#99ccff").grid(row=6, column=2, sticky="w")
        expense_entry = tk.Entry(receipt_frame, textvariable=expense_type_var, state="readonly", width=15, font=font_settings)
        expense_entry.grid(row=6, column=3)
        expense_type_var.set('') 

        # UI Layout
        df, codes, code_to_data = load_excel_and_generate_codes(mapping_voucher_path)
        #print(f"CODES {codes}")
        tk.Label(receipt_frame, text="Purchase Code:", font=font_settings,  bg="#99ccff").grid(row=5, column=0, sticky="w")
        code_cb = ttk.Combobox(receipt_frame, textvariable=purchase_code_var, values=codes, width=15)
        code_cb.grid(row=5, column=1)

        tk.Label(receipt_frame, text="Purchase Category:", font=font_settings, bg="#99ccff").grid(row=6, column=0, sticky="w")
        category_cb = ttk.Combobox(receipt_frame, textvariable=purchase_category_var, width=15)
        category_cb.grid(row=6, column=1)

        tk.Label(receipt_frame, text="Purchase Head:", font=font_settings, bg="#99ccff").grid(row=5, column=2, sticky="w")
        head_cb = ttk.Combobox(receipt_frame, textvariable=purchase_head_var, width=15)
        head_cb.grid(row=5, column=3)

        try:
            heads, mapping, expense_types = load_data(mapping_voucher_path)
            head_to_categories = mapping
            head_to_expense_type = expense_types
            head_cb['values'] = [''] + heads  # Add an empty string at the beginning to set blank as default
            head_cb.set('') 
            head_cb.bind('<Configure>', adjust_dropdown_width)
            on_head_selected(head_cb, category_cb, expense_entry, purchase_code_var)
            head_cb.bind("<<ComboboxSelected>>", lambda e, hcb=head_cb, ccb=category_cb, eentry=expense_entry, pcode=purchase_code_var: 
                         on_head_selected(hcb, ccb, eentry, pcode))
        except Exception as e:
            print(f"Error: {e}")
    
        code_cb.bind("<<ComboboxSelected>>", lambda e, ccb=code_cb, hcb=head_cb, catcb=category_cb, eentry=expense_entry, c2d=code_to_data:
                on_code_selected(ccb, hcb, catcb, eentry, c2d))
        category_cb.bind("<<ComboboxSelected>>", lambda e, catcb=category_cb, hcb=head_cb, codecb=code_cb: on_category_selected(catcb, hcb, codecb))

        return code_cb, head_cb, category_cb, expense_entry

def add_group_voucher(frame, group_frames, frame_name_options, frame_name_hidden, count, selected_option, voucher_data, validate_number):
    vcmd = (frame.register(UI_support.validate_alpha), "%S", "%P")
    vcmd_branch =(frame.register(UI_support.validate_alpha_branch), "%S", "%P")
    selected_option[count] = tk.StringVar(value="Cash")

    # Cheque Frame (Right)
    cheque_frame = tk.Frame(group_frames[frame_name_hidden], borderwidth=2, relief="groove", bg="#99ccff")
    cheque_frame.grid(row=2, column=2, rowspan=1, padx=50, pady=20, sticky="nsew")
    cheque_frame.grid_remove()  # Hide initially

    # Online Frame (Right)
    online_frame = tk.Frame(group_frames[frame_name_hidden], borderwidth=2, relief="groove", bg="#99ccff")
    online_frame.grid(row=2, column=2, rowspan=1, padx=50, pady=20, sticky="nsew")
    online_frame.grid_remove()    
    
    add_payment_mode(count, selected_option, group_frames, frame_name_options, cheque_frame, online_frame, voucher_data)
   
    tk.Label(cheque_frame, text="Cheque Details", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0, columnspan=2, pady=5)
    cheque_fields = [
        ("Cheque Date:", DateEntry, {"date_pattern": "dd/mm/yyyy", "state": "readonly"}),
        ("Cheque No.:", tk.Entry, {"textvariable": tk.StringVar(), "validate": "key", "validatecommand": (validate_number, "%P")}),
        ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Account No.:", tk.Entry, {"textvariable": tk.StringVar()}),
    ]
    #underline_font = tkFont.Font(family=(config.get('FontSettings', 'font_name')), size=config.getint('FontSettings', 'font_size'), weight="bold", underline=1)
    tk.Label(online_frame, text="EFT", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0,columnspan=2, pady=5)
    online_fields = [
        ("Bank Date:", DateEntry, {"date_pattern": "dd/mm/yyyy", "state": "readonly"}),
        ("UTRN:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Bank Name:", tk.Entry, {"validate": "key", "validatecommand": vcmd}),
        ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Bank Branch:", tk.Entry, {"validate": "key", "validatecommand": vcmd_branch}),
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
        if var:                                                                       # Apply character limits
            if "UTRN:" in label:
                limit = 27
            elif "IFSC Code:" in label:
                limit = 11
            var.trace_add("write", lambda *args, v=var, l=limit: UI_support.limit_chars(v, l))
        entry = widget(online_frame, font=font_settings, width=25, **options)
        online_vars[label] = var                                                         # Store for later
        
        if "Bank Date:" in label:
            entry = widget(online_frame, font=font_settings, width=12, **options)
        entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)
        online_vars[label] = entry                                                      # Store reference
    online_frame.grid(row=2, column=1, rowspan=2, padx=50, pady=20, sticky="nsew")
    voucher_data['cheque'] = cheque_vars
    voucher_data['eft'] = online_vars
    #print(f" Voucher entries are {voucher_entries}")

    toggle_voucher_mode(count, selected_option, cheque_frame, online_frame, voucher_data)

    return cheque_frame, online_frame

def add_group_inv_voucher(frame, group_frames, frame_name_options, frame_name_hidden, voucher_data, validate_number):
    selection_var = tk.StringVar(value="Cash")
    vcmd = (frame.register(UI_support.validate_alpha), "%S", "%P")
    vcmd_branch =(frame.register(UI_support.validate_alpha_branch), "%S", "%P")
    # Payment Mode Selection
    tk.Label(group_frames[frame_name_options], text="Payment Mode:", font=font_settings_bold, bg="#99ccff").grid(row=3, column=2, sticky="w", pady=5)
    cash = tk.Radiobutton(group_frames[frame_name_options], text="Cash", bg="#99ccff", variable=selection_var, value="Cash", font=font_settings, command=lambda: toggle_cheque_fields())
    cheque = tk.Radiobutton(group_frames[frame_name_options], text="Cheque", bg="#99ccff", variable=selection_var, value="Cheque", font=font_settings, command=lambda: toggle_cheque_fields())
    online = tk.Radiobutton(group_frames[frame_name_options],  text="EFT", bg="#99ccff", variable=selection_var, value="EFT", font=font_settings, command=lambda: toggle_cheque_fields())
    cash.grid(row=4, column=2, sticky="w")
    cheque.grid(row=5, column=2, sticky="w")
    online.grid(row=6, column=2, sticky="w")

    # Cheque Frame (Right)
    cheque_frame = tk.Frame(group_frames[frame_name_hidden], borderwidth=2, relief="groove", bg="#99ccff")
    cheque_frame.grid(row=2, column=2, rowspan=1, padx=50, pady=20, sticky="nsew")
    cheque_frame.grid_remove()  # Hide initially

    # Online Frame (Right)
    online_frame = tk.Frame(group_frames[frame_name_hidden], borderwidth=2, relief="groove", bg="#99ccff")
    online_frame.grid(row=2, column=2, rowspan=1, padx=50, pady=20, sticky="nsew")
    online_frame.grid_remove()
    tk.Label(cheque_frame, text="Cheque Details", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0, columnspan=2, pady=5)
    cheque_fields = [
        ("Cheque Date:", DateEntry, {"date_pattern": "dd/mm/yyyy", "state": "readonly"}),
        ("Cheque No.:", tk.Entry, {"textvariable": tk.StringVar(), "validate": "key", "validatecommand": (validate_number, "%P")}),
        ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Account No.:", tk.Entry, {"textvariable": tk.StringVar()}),
    ]
    #underline_font = tkFont.Font(family=(config.get('FontSettings', 'font_name')), size=config.getint('FontSettings', 'font_size'), weight="bold", underline=1)
    tk.Label(online_frame, text="EFT", font=font_settings_bold, bg="#99ccff").grid(row=0, column=0,columnspan=2, pady=10)
    online_fields = [
        ("Bank Date:", DateEntry, {"date_pattern": "dd/mm/yyyy", "state": "readonly"}),
        ("UTRN:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("IFSC Code:", tk.Entry, {"textvariable": tk.StringVar()}),
        ("Bank Name:", tk.Entry, {"validate": "key", "validatecommand": vcmd}),
        ("Bank Branch:", tk.Entry, {"validate": "key", "validatecommand": vcmd_branch}),
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
        if var:                                                                       # Apply character limits
            if "UTRN:" in label:
                limit = 27
            elif "IFSC Code" in label:
                limit = 11
            var.trace_add("write", lambda *args, v=var, l=limit: UI_support.limit_chars(v, l))
        entry = widget(online_frame, font=font_settings, width=25, **options)
        online_vars[label] = var                                                         # Store for later
        
        if "Bank Date:" in label:
            entry = widget(online_frame, font=font_settings, width=12, **options)
        entry.grid(row=i + 1, column=1, sticky="w", padx=5, pady=5)
        online_vars[label] = entry                                                      # Store reference
    online_frame.grid(row=2, column=1, rowspan=2, padx=50, pady=20, sticky="nsew")
    voucher_data['cheque'] = cheque_vars
    voucher_data['eft'] = online_vars

    def toggle_cheque_fields():
        print(f"Invoice Selection is {selection_var.get()}")
        selected_value = selection_var.get()
        voucher_data['payment_mode'] = selected_value
        cheque_frame.grid() if selection_var.get() == "Cheque" else cheque_frame.grid_remove()
        online_frame.grid() if selection_var.get() == "EFT" else online_frame.grid_remove()
    toggle_cheque_fields()  

    return cheque_frame, online_frame, selection_var

def on_category_selected(category_cb, head_cb, code_cb):
    selected_category = category_cb.get().strip()
    selected_head = head_cb.get().strip()

    # Ensure both head and category are selected
    if not selected_head or not selected_category:
        return

    # Get matching code from code_to_data
    for code, data in code_to_data.items():
        if data['head'].strip() == selected_head and data['category'].strip() == selected_category:
            code_cb.set(code)
            break


def include_bg(group_name, checkbox_var):
    checkbox = tk.Checkbutton(group_name, text="Include background", bg="#99ccff", variable=checkbox_var, font=font_settings)
    checkbox.grid(row=1, column=2, sticky="w")

def validate_number_with_button(char, new_value, submit_btn):
    if not char.isdigit() or len(new_value) > 11:
        submit_btn.config(state="disabled")
        return False
    # Enable button if there's a valid number
    submit_btn.config(state="normal" if new_value else "disabled")
    return True

def adjust_dropdown_width(event):
    combo = event.widget
    style = ttk.Style()

    # Get the longest item in the combobox values
    longest_item = max(combo['values'], key=len)

    # Calculate the width of the longest item
    font = tkfont.nametofont(str(combo.cget('font')))
    width = font.measure(longest_item + " ")

    # Configure the style to set the dropdown width
    style.configure('TCombobox', postoffset=(0, 0, width, 0))
    combo.configure(style='TCombobox')

import tkinter as tk
from tkinter import ttk
from tktooltip import ToolTip

def draw_voucher(frame, selected_indx, root, checkbox_var):
    voucher_entries = []
    group_frames = {}
    group_frames_hidden = {}
    #global head_to_categories, head_to_expense_type, code_to_data
    dest_excel_path = UI_support.generate_excel_file(voucher_entity_xcls[selected_indx])
    mapping_voucher_path = voucher_mapping_xcls[selected_indx]
    print(f"EXCEL VOUCHER {dest_excel_path} and {mapping_voucher_path}")

    validate_number = get_validate_number(root)

    for i in range(3): 
        row_offset = i * 6
        receipt_frame = tk.LabelFrame(frame,  text=f"Voucher {i+1}", bg="#99ccff", font=font_settings_bold, bd=2,
            relief="groove", padx=5, pady=5 )                                   # Can be 'groove', 'ridge', 'sunken', 'raised', etc.  
        receipt_frame.grid(row=row_offset+1 , column=0, padx=10, pady=10, sticky="ew")
    
        limit = 200
        name_var = tk.StringVar()
        tk.Label(receipt_frame, text="Payee Name:", font=font_settings, bg="#99ccff").grid(row=2, column=0, sticky="w", padx=5, pady=5) 
        name_entry = tk.Entry(receipt_frame, font=font_settings, textvariable=name_var)
        name_var.trace_add("write", lambda *args, v=name_var, l=limit: UI_support.limit_chars(v, l))
        name_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(receipt_frame, text="Voucher Date:", font=font_settings, bg="#99ccff").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        date_entry = DateEntry(receipt_frame, date_pattern="dd/mm/yyyy", width=10, background='darkblue', foreground='white', borderwidth=2, state="readonly")
        date_entry.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        tk.Label(receipt_frame, text="Amount:", font=font_settings, bg="#99ccff").grid(row=3, column=0, sticky="w", padx=5, pady=5) 
        #amt_entry = tk.Entry(receipt_frame, font=font_settings, width= 10, validate="key", validatecommand=(validate_number, "%S", "%P"))
        vcmd = root.register(lambda char, new_value: validate_number_with_button(char, new_value, submit_button))
        amt_entry = tk.Entry(receipt_frame, font=font_settings, width=10, validate="key", validatecommand=(vcmd, "%S", "%P"))
        amt_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        pan_var = tk.StringVar()
        tk.Label(receipt_frame, text="PAN:", font=font_settings, bg="#99ccff").grid(row=3, column=2,  sticky="w", padx=5, pady=5) 
        pan_entry = tk.Entry(receipt_frame, font=font_settings, textvariable=pan_var, width=10)
        pan_var.trace_add("write", lambda *args, v=pan_var, l=limit: UI_support.limit_chars(v, 10))
        pan_entry.grid(row=3, column=3, sticky="w", padx=5, pady=5)
        
        addr_var = tk.StringVar()
        tk.Label(receipt_frame, text="Address:", font=font_settings, bg="#99ccff").grid(row=4, column=0, sticky="w", padx=5, pady=5) 
        addr_entry = tk.Entry(receipt_frame, font=font_settings, textvariable=addr_var, width=40)
        addr_var.trace_add("write", lambda *args, v=addr_var, l=limit: UI_support.limit_chars(v, l))
        addr_entry.grid(row=4, column=1, columnspan=4, sticky="w", padx=5, pady=5)

        code_cb, head_cb, category_cb, expense_entry = update_purchase_code(receipt_frame, mapping_voucher_path)

        frame_name_options = f"group{row_offset+7}_frame"
        grp_frame = tk.Frame(frame, borderwidth=2, relief="groove", bg="#99ccff")
        grp_frame.grid(row=row_offset+1, column=3, rowspan=1, padx=20, pady=20, sticky="nsew")
        group_frames[frame_name_options] = grp_frame

        frame_name_hidden = f"group{row_offset+8}_frame"
        grp_frame = tk.Frame(frame,  bg="white")
        grp_frame.grid(row=row_offset+1, column=4, padx=10, pady=10, sticky="nsew")
        group_frames[frame_name_hidden] = grp_frame
        #print(f"frame names are  {frame_name_options} and {frame_name_hidden}")
        selected_option[i] = tk.StringVar(value="Cash")
        voucher_data = {
            'date': date_entry,
            'pay_to': name_entry,
            'amount': amt_entry,
            'pan': pan_entry,
            'addr': addr_entry,
            'pur_code': code_cb,
            'pur_head': head_cb,
            'pur_cat': category_cb,
            'exp_type': expense_entry,
            'payment_mode': selected_option[i],                     # store the selected mode
            'cheque': {},                                           # will be populated later
            'eft': {}
        }
        voucher_entries.append(voucher_data)
        print(f"PAYMENT MODE in voucher data = {voucher_data['payment_mode'].get()}")
        cheque_frame, online_frame = add_group_voucher(frame, group_frames, frame_name_options, frame_name_hidden, i, selected_option, voucher_data, validate_number)
        
    print_frame = tk.LabelFrame(frame,  font=font_settings_bold, bg="#99ccff", bd=2, relief="groove", padx=10, pady=10 )
    print_frame.grid(row=1, column=5, rowspan=1, padx=15, pady=10, sticky="ew")
    
    include_bg(print_frame, checkbox_var)
    submit_button = tk.Button(print_frame, text="Print", font=font_settings, command=lambda: UI_support.voucher_print(voucher_entity_xcls[selected_indx], mapping_voucher_path, voucher_entries, selected_indx, checkbox_var, selected_option, cheque_frame, online_frame))   # Submit Button
    submit_button.grid(row=2, column=2, padx=10, pady=10) 
    submit_button.config(state="disabled")

def draw_inv_voucher(frame, selected_indx, root, checkbox_var):
    limit = 200
    name_var = tk.StringVar()
    selection_var = tk.StringVar()
    voucher_entries = []
    group_frames = {}
    group_frames_hidden = {}
    invoice_excel_path = UI_support.generate_excel_file(invoice_entity_xcls[selected_indx])
    mapping_inv_path = invoice_mapping_xcls[selected_indx]
    print(f"EXCEL INVOICE {invoice_excel_path} and {mapping_inv_path}")

    validate_number = get_validate_number(root)
    
    # Create a LabelFrame for each receipt
    invoice_frame = tk.LabelFrame(frame, text=f"Invoice Voucher", font=font_settings_bold, bg="#99ccff", bd=2, relief="groove", padx=10, pady=10)
    invoice_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # Inside the LabelFrame, create widgets for the receipt details
    tk.Label(invoice_frame, text="Invoice Date:", font=font_settings, bg="#99ccff").grid(row=0, column=2, sticky="w", pady=5)
    date_entry = DateEntry(invoice_frame, date_pattern="dd/mm/yyyy", width=15, background='darkblue', foreground='white', borderwidth=2, state="readonly")
    date_entry.grid(row=0, column=3, pady=10, sticky="ew")

    tk.Label(invoice_frame, text="Invoice # :", font=font_settings, bg="#99ccff").grid(row=0, column=0, sticky="w", pady=5)
    invoice_entry = tk.Entry(invoice_frame, font=font_settings, width=15)
    invoice_entry.grid(row=0, column=1, pady=10, sticky="ew")

    tk.Label(invoice_frame, text="Payee Name:", font=font_settings, bg="#99ccff").grid(row=1, column=0, sticky="w", pady=5)
    name_entry = tk.Entry(invoice_frame, font=font_settings, textvariable=name_var, width=25)
    name_var.trace_add("write", lambda *args, v=name_var, l=limit: UI_support.limit_chars(v, l))
    name_entry.grid(row=1, column=1, pady=10, sticky="ew")

    vcmd = root.register(lambda char, new_value: validate_number_with_button(char, new_value, submit_button))
    tk.Label(invoice_frame, text="Amount:", font=font_settings, bg="#99ccff").grid(row=2, column=0, sticky="w", pady=5)
    amount_entry = tk.Entry(invoice_frame, font=font_settings, width=25, validate="key", validatecommand=(vcmd, "%S", "%P"))
    amount_entry.grid(row=2, column=1, pady=10, sticky="ew")

    amount_in_words_text = UI_support.UI_amount_in_words(invoice_frame, amount_entry, 3, 30)

    tk.Label(invoice_frame, text="Address:", font=font_settings, bg="#99ccff").grid(row=4, column=0, sticky="w", pady=5)
    addr_entry = tk.Text(invoice_frame, font=font_settings, wrap="word", width=30, height=3)
    #addr_entry.config(wrap="word")  # Set wrap here
    addr_entry.bind("<KeyRelease>", lambda event, e=addr_entry: UI_support.limit_text_chars(event, e, 200))
    addr_entry.grid(row=4, column=1, pady=10, sticky="ew")

    code_cb, head_cb, category_cb, expense_entry = update_purchase_code(invoice_frame, mapping_inv_path)

    challan_var = tk.StringVar()
    tk.Label(invoice_frame, text="Challan #:", font=font_settings, bg="#99ccff").grid(row=8, column=0,  sticky="w", pady=5) 
    challan_entry = tk.Entry(invoice_frame, font=font_settings, textvariable=challan_var, width=15)
    challan_var.trace_add("write", lambda *args, v=challan_var, l=limit: UI_support.limit_chars(v, 10))
    challan_entry.grid(row=8, column=1, padx=5, pady=5)

    cert_var = tk.StringVar()
    tk.Label(invoice_frame, text="Certificate #:", font=font_settings, bg="#99ccff").grid(row=8, column=2,  sticky="w", pady=5) 
    cert_entry = tk.Entry(invoice_frame, font=font_settings, textvariable=cert_var, width=15)
    cert_var.trace_add("write", lambda *args, v=cert_var, l=limit: UI_support.limit_chars(v, 10))
    cert_entry.grid(row=8, column=3, sticky="w", padx=5, pady=5)
    
    frame_name_options = f"group_frame"
    grp_frame = tk.Frame(frame, borderwidth=2, relief="groove", bg="#99ccff")
    grp_frame.grid(row=1, column=3, rowspan=1, padx=20, pady=20, sticky="nsew")
    group_frames[frame_name_options] = grp_frame

    frame_name_hidden = f"group_frame_hidden"
    grp_frame = tk.Frame(frame,  bg="white")
    grp_frame.grid(row=1, column=4, padx=10, pady=10, sticky="nsew")
    group_frames[frame_name_hidden] = grp_frame
    
    selected_option = tk.StringVar(value="Cash")

    voucher_data = {
            'inv_no': invoice_entry,
            'date': date_entry,
            'pay_to': name_entry,
            'amount': amount_entry,
            'addr': addr_entry,
            'pur_code': code_cb,
            'pur_head': head_cb,
            'pur_cat': category_cb,
            'exp_type': expense_entry,
            'payment_mode': selected_option,                     
            'challan': challan_entry,
            'cert': cert_entry,
            'amount_in_words': amount_in_words_text,
            'cheque': {},                                           # will be populated later
            'eft': {}
        }
    voucher_entries.append(voucher_data)
    cheque_frame, online_frame, selection_var = add_group_inv_voucher(frame, group_frames, frame_name_options, frame_name_hidden, voucher_data, validate_number)
        
    print_frame = tk.LabelFrame(frame,  font=font_settings_bold, bg="#99ccff", bd=2, relief="groove", padx=10, pady=10 )
    print_frame.grid(row=1, column=5, rowspan=1, padx=15, pady=10, sticky="ew")
    submit_button = tk.Button(print_frame, text="Print", font=font_settings, command=lambda: UI_support.voucher_print(invoice_entity_xcls[selected_indx], mapping_inv_path, voucher_entries, selected_indx, checkbox_var, selection_var, cheque_frame, online_frame))   # Submit Button
    submit_button.grid(row=2, column=2, padx=10, pady=10) 
    submit_button.config(state="disabled")

