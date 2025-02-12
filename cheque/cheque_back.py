import tkinter as tk
from tkinter import font, ttk
from datetime import datetime
from cheque import cheque_front, chequeWriter_Canon, excel_con, shared, bank_handling
from cheque.shared import field_data_hdfc
from PIL import Image, ImageTk, ImageDraw, ImageFont
import textwrap

root = None
canvas2 = None

class ChequeBack:
    def __init__(self):
        self.current_widget = None

    def set_widget(self, widget):
        self.current_widget = widget

# Instantiate the class to access the `current_widget` attribute
cheque_back = ChequeBack()

# Function to update the default_value
def update_ifsc(new_value, sel_bank):
    ifsc_value = tk.StringVar()
    ifsc_value.set(new_value)
    ifsc_label = tk.Label(root, textvariable=new_value, font=("Arial", 9), bg="lightgray", width=12) #textvariable=default_value, state="readonly", bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10) )
    canvas2.create_window(45, 180, window=ifsc_label, anchor="w") 

    bank_value.set(sel_bank)
    bank_label = tk.Label(root, textvariable=bank_value, font=("Arial", 9), bg="lightgray", width=12) # Create an entry field
    canvas2.create_window(175, 180, window=bank_label, anchor="w")

def update_chq_date(event):
    selected_date = cheque_front.date_entry.get_date()
    new_value = selected_date.strftime("%d.%m.%y")
    chq_date.set(new_value)
    print(f" new value is {new_value}")
    chq_date_label = tk.Label(root, textvariable=chq_date, font=("Arial", 9), bg="lightgray", width=12)
    canvas2.create_window(260, 155, window=chq_date_label, anchor="w") 

def validate_words_limit(new_value):
    word_count = len(new_value.split())
    if word_count > 5:  # Set your word limit here
        return False
    return True

def limit_words(event):
    text_content = narration_entry.get("1.0", "end-1c")  # Get all text without the trailing newline
    words = text_content.split()
    if len(words) > 25:  # Set your word limit here
        # Remove extra words
        limited_text = " ".join(words[:25])
        narration_entry.delete("1.0", "end")
        narration_entry.insert("1.0", limited_text)

def draw_line(text, x_position, y_position, draw):
    # Get the text size to calculate underline position
    # Use textbbox to calculate text size
    text_bbox = draw.textbbox((x_position, y_position), text, font=bank_handling.font_small)
    text_width = text_bbox[2] - text_bbox[0]  # Calculate text width
    text_height = text_bbox[3] - text_bbox[1]  # Calculate text height

    # Draw an underline below the text
    underline_y_position = y_position + text_height + 2  # Slightly below the text
    draw.line(
    [(x_position, underline_y_position), (x_position + text_width, underline_y_position)],
    fill="black",
    width=1
    )
def generate_cheque_back_new():
    print (" New cheque format")
    # Create cheque image
    cheque_image = Image.new('RGB', (792, 612), color='white')
    draw = ImageDraw.Draw(cheque_image)
    chq_num = cheque_entry.get()
    globe_id = "SGP"

    line_height = 15  # Line spacing
    font_10 = bank_handling.font_small10 
    x_position = 60
    y_position = 30

    draw.text((x_position, y_position), f"GlobeID: {globe_id}       Amount: {cheque_front.amount_entry.get()}", font=font_10, fill="black")
    draw_line("Globe",x_position, y_position, draw)
    y_position += 20

    draw.text((x_position, y_position), "Payer Details:", font=font_10, fill="black")
    draw_line("PaeDetails",x_position, y_position, draw)

    x_position = 250
    y_position = 50
    draw.text((x_position, y_position), "Payee Details:", font=font_10, fill="black")
    draw_line("PayDetails",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"Name: {biller_entry.get()}", font=font_10, fill="black")
    y_position += 20

    x_position = 430
    y_position = 50
    draw.text((x_position, y_position), f"Compliance: ", font=font_10, fill="black")
    draw_line("Payee Details",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"Name: {payee.get()}", font=font_10, fill="black")
    y_position += 20

    # Save cheque as image
    cheque_image.save(f"chequeBack_{chq_num}.pdf")
    chequeWriter_Canon.print_cheque(f"chequeBack_{chq_num}.pdf") 



def generate_cheque_back():
    print (f"Generate Back cheque ")
    current_widget = tk.Entry()
    globe_id =excel_con.increment_counter()

    # Create cheque image
    cheque_image = Image.new('RGB', (792, 612), color='white')
    draw = ImageDraw.Draw(cheque_image)
    chq_num = cheque_entry.get()

    print("Data to Save in Excel")
    kwargs = {
        'globe_id' : globe_id,
        'globe_stat' : 'Approved',
        'Payee' : cheque_front.payee_entry.get(),
        'Amount' : cheque_front.amount_entry.get(),
        'Date' : cheque_front.date_entry.get(),
        'Bank' : cheque_front.bank_name_dropdown.get(),
        'Purpose' : purpose_dropdown.get(),
        'Narration' : narration_entry.get('1.0', 'end-1c'),
        'Cheque #' : cheque_entry.get(),
        'IFSC code' : bank_handling.IFSC, #ifsc_value.get(),
        'Biller name' : biller_entry.get(),
        'Invoice #' : invoice_entry.get(),
        'GST/PAN' : gst_pan_entry.get(),
        'Payee Name' : payee.get(),
        'Bank Name' : bank_entry.get(),
        'Branch Name' : branch_entry.get(),
        'Payee IFSC' : ifsc_Payee_entry.get(),
        'Digital Sign' : dig_sign_entry.get()
    }
    shared.field_data_hdfc.update(kwargs)

    # Define the maximum width for text wrapping
    max_width = 300  # Adjust as needed
    line_height = 15  # Line spacing
    font_10 = bank_handling.font_small10 
    nar_text = narration_entry.get('1.0', 'end').strip()
    wrapped_text = textwrap.fill(nar_text, width=40) # Wrap the text to fit within the max_width

    x_position = 60
    y_position = 30
    draw.text((x_position, y_position), "Payment Details", font=font_10, fill=(0, 0, 0))
    draw_line("Payment Details",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position),"Purpose: ",font=font_10, fill="black")
    y_position += 15
    if isinstance(current_widget, tk.Entry):
        draw.text((x_position, y_position),f"{current_widget.get()}",font=font_10, fill="black")
    else:
        draw.text((x_position, y_position),f"{purpose_dropdown.get()}",font=font_10, fill="black")
    y_position += 20
    draw.text((x_position, y_position), "Narration: ", font=font_10, fill="black")
    #draw_line("Narration",x_position, y_position, draw)
    y_position += 15
    for line in wrapped_text.splitlines():
        draw.text((x_position, y_position), line, font=font_10, fill="black")
        y_position += line_height
    #y_position += 10
    draw.text((x_position, y_position), f"Cheque#: {cheque_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Cheque Date: {chq_date.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"IFSC: {bank_handling.IFSC}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Bank: {bank_value.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Branch: {pay_branch_entry.get()}", font=font_10, fill=(0, 0, 0))
    #y_position += 20
    #draw.text((x_position, y_position), f"Cheque# 1: {pay_branch_entry}", font=font_10, fill=(0, 0, 0))
    #y_position += 20 #position of the last line on the cheque back
    #draw.text((x_position, y_position), f"Cheque# 2: {pay_branch_entry}", font=font_10, fill=(0, 0, 0))
    
    x_position = 250
    y_position = 30
    draw.text((x_position, y_position), "Bill Details", font=font_10, fill=(0, 0, 0))
    draw_line("Bill Details",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"Name: {biller_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Invoice#: {invoice_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"GST: {gst_pan_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"PAN: {gst_pan_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), "Digital Signature: ", font=font_10, fill=(0, 0, 0))
    draw_line("Digital Signature:",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"{dig_sign_entry.get()}", font=font_10, fill=(0, 0, 0))

    x_position = 430
    y_position = 30
    draw.text((x_position, y_position), f"Payee Details: ", font=font_10, fill=(0, 0, 0))
    draw_line("Payee Details",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"Name: {payee.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Bank: {bank_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Branch: {branch_entry.get()}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"IFSC: {ifsc_Payee_entry.get()}", font=font_10, fill=(0, 0, 0))

    # Save cheque as image
    cheque_image.save(f"chequeBack_{chq_num}.pdf")
    chequeWriter_Canon.print_cheque(f"chequeBack_{chq_num}.pdf") 
    
    excel_con.save_to_excel(**kwargs)

def limit_characters_text(event, text_widget, char_limit):
    # Get the current content of the Text widget
    current_text = text_widget.get("1.0", "end-1c")  # Get all text except the trailing newline
    
    # Check if the character limit is exceeded
    if len(current_text) > char_limit:
        # Truncate the text to the allowed limit
        truncated_text = current_text[:char_limit]
        
        # Clear the widget and insert truncated text
        text_widget.delete("1.0", "end")
        text_widget.insert("1.0", truncated_text)

def limit_characters(entry_widget, limit):
    current_text = entry_widget.get()
    if len(current_text) > limit:
        entry_widget.delete(limit, "end")  # Truncate extra characters

def switch_to_entry():
    """Replace the checkbox with an Entry widget."""
    global current_widget
    if isinstance(current_widget, tk.Checkbutton) or purpose_dropdown.get() == "Specific purpose":
        print("switch_to_entry ")
        # Remove the checkbox
        current_widget.pack_forget()
        # Create and display the Entry widget
        current_widget = tk.Entry(root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", width=28)
        current_widget.bind("<KeyRelease>", lambda event: limit_characters(current_widget, 25))
        current_widget.pack(pady=10)
        canvas2.create_window(180, 35, window=current_widget, anchor="nw")

def switch_to_checkbox():
    """Replace the Entry widget with a Checkbutton."""
    global current_widget
    if isinstance(current_widget, tk.Entry) or current_widget.cget("state") == "disabled":
        print("switch_to_checkbox")
        # Remove the Entry widget
        current_widget.pack_forget()
        # Create and display the Checkbutton
        checkbox_var = tk.IntVar()
        current_widget = tk.Checkbutton(root, text="Print Corpus Donation Form", variable=checkbox_var)
        current_widget.pack(pady=10)
        canvas2.create_window(180, 35, window=current_widget, anchor="nw")

# Bind the dropdown selection to a callback
def handle_selection(event):
    print(f"Current selection : {purpose_dropdown.get()}")
    if purpose_dropdown.get() == "Revenue":
        print("Revenue") #switch_to_checkbox()
    elif purpose_dropdown.get() == "Capital":
        print("Capital")
        #switch_to_entry()

def create_dropdowns(dropdown_values, x_position, y_position):
    global purpose_dropdown
    #dropdown_values = [arg1, arg2]     # Dropdown values and Combobox setup
    purpose_dropdown = ttk.Combobox(root, values=dropdown_values, state="readonly", font=("Arial", 10), width=10)
    purpose_dropdown.set(dropdown_values[0])  # Set the default selection
    purpose_dropdown.bind("<<ComboboxSelected>>", handle_selection) 
    # Canvas to place the dropdown
    cheque_front.canvas.create_window(x_position, y_position, window=purpose_dropdown, anchor="nw") # Place the dropdown on the canvas

def create_checkbox(x_position, y_position, text, var):
    checkbox = tk.Checkbutton(root, text=text, variable=var, font=("Arial", 10), bg="white", fg="black")
    checkbox.place(x=x_position, y=y_position)
    return checkbox

def UI_back(app_root):
    global root, ifsc_value, bank_value, pay_branch_entry, chq_date, chq_date_label, canvas2 , canvas, IFSC, narration_entry, cheque_entry, biller_entry, invoice_entry, gst_pan_entry, payee, bank_entry,branch_entry, ifsc_Payee_entry, dig_sign_entry, purpose_dropdown, checkbox_var, checkbox, current_widget, handle_selection
    root = app_root
    # Create a white canvas
    canvas2 = tk.Canvas( root, width=800, height=300, bg="white")  # Set the background color to white
    canvas2.place(x=0, y=310)  # Position the canvas further down

    x_payment_details = 5
    y_payment_details = 15
    bold_underline_font = font.Font(family="Arial", size=10, weight="bold", underline=1)
    label = tk.Label(root, text="Payment Details:", font=bold_underline_font, bg="white", fg="black")
    canvas2.create_window(150, y_payment_details, window=label, anchor="w") 
    y_payment_details += 50

    #Check number
    label = tk.Label(root, text="Cheque#:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(5, y_payment_details, window=label, anchor="w")  
    cheque_entry = tk.Entry( root, width=15, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10) )
    canvas2.create_window(65, y_payment_details, window=cheque_entry, anchor="w")  
    print(f" Cheque entry {cheque_entry.get()}")

    #Check date
    selected_date = cheque_front.date_entry.get()
    date_obj = datetime.strptime(selected_date, "%m/%d/%y")
    formatted_date = date_obj.strftime("%d.%m.%y")
    label = tk.Label(root, text="Cheque date:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(180, y_payment_details, window=label, anchor="w")   # Add the label to the canvas
    chq_date = tk.StringVar()                                 # Create a StringVar for the Entry's value
    chq_date.set(formatted_date)
    chq_date_label = tk.Label(root, textvariable=chq_date, font=("Arial", 9), bg="lightgray", width=12) # Create an entry field
    canvas2.create_window(260, y_payment_details, window=chq_date_label, anchor="w")
    y_payment_details += 35

    # Access the IFSC variable  #IFSC Code#
    label = tk.Label(root, text="IFSC:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(5, y_payment_details, window=label, anchor="w")   # Add the label to the canvas
    ifsc_value = tk.StringVar()                                 # Create a StringVar for the Entry's value
    ifsc_value.set(cheque_front.IFSC)
    ifsc_label = tk.Label(root, textvariable=ifsc_value, font=("Arial", 9), bg="lightgray", width=12) # Create an entry field
    canvas2.create_window(60, y_payment_details, window=ifsc_label, anchor="w")

    label = tk.Label(root, text="Bank:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(180, y_payment_details, window=label, anchor="w")   # Add the label to the canvas
    bank_value = tk.StringVar()                                 # Create a StringVar for the Entry's value
    bank_value.set(cheque_front.bank_name_dropdown.get())
    bank_label = tk.Label(root, textvariable=bank_value, font=("Arial", 9), bg="lightgray", width=12) # Create an entry field
    canvas2.create_window(260, y_payment_details, window=bank_label, anchor="w")
    y_payment_details += 30
    
    #Branch name
    label = tk.Label(root, text="Branch:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(5, y_payment_details, window=label, anchor="w")  
    pay_branch_entry = tk.Entry( root, width=10, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10) )
    canvas2.create_window(60, y_payment_details, window=pay_branch_entry, anchor="w")  

    # Digital Sigature # Create a font with bold and underline
    label = tk.Label(root, text="Digital Signature:", font=bold_underline_font, bg="white", fg="black")
    canvas2.create_window(5, 165, window=label, anchor="w")  # Adjusted position
    dig_sign_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=40 )
    canvas2.create_window(5, 190, window=dig_sign_entry, anchor="w")  # Adjusted position

    x_biller = 360
    x_biller_entry = 410
    y_biller = 50
    #Bill Details: 
    label = tk.Label(root, text="Bill Details:", font=bold_underline_font, bg="white", fg="black")
    canvas2.create_window(450, 20, window=label, anchor="w")     

    # Biller Name
    label = tk.Label(root, text="Name:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_biller, y_biller, window=label, anchor="w")  
    biller_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_biller_entry, y_biller, window=biller_entry, anchor="w") 
    y_biller += 30

    # Invoice No. 
    label = tk.Label(root, text="Invoice#:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_biller, y_biller, window=label, anchor="w")  # Adjusted position
    invoice_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23 )
    canvas2.create_window(x_biller_entry, y_biller, window=invoice_entry, anchor="w")  # Adjusted position
    y_biller += 30

    # GST
    label = tk.Label(root, text="GST:", font=("Arial", 8), bg="white", fg="black")
    canvas2.create_window(x_biller, y_biller, window=label, anchor="w")  # Adjusted position
    gst_pan_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_biller_entry, y_biller, window=gst_pan_entry, anchor="w")  # Adjusted position
    y_biller += 30

    # PAN
    label = tk.Label(root, text="PAN:", font=("Arial", 8), bg="white", fg="black")
    canvas2.create_window(x_biller, y_biller, window=label, anchor="w")  # Adjusted position
    gst_pan_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_biller_entry, y_biller, window=gst_pan_entry, anchor="w")  # Adjusted position

    x_payee = 580
    x_payee_entry = 630
    y_payee = 50
    #Payee  Details: 
    label = tk.Label(root, text="Payee Details:", font=bold_underline_font, bg="white", fg="black")
    canvas2.create_window(670, 20, window=label, anchor="w")

    #Payee name
    label = tk.Label(root, text="Name:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_payee, y_payee, window=label, anchor="w") 
    payee = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_payee_entry, y_payee, window=payee, anchor="w") 
    y_payee += 30

    #Bank Name
    label = tk.Label(root, text="Bank:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_payee, y_payee, window=label, anchor="w")  # Adjusted position
    bank_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23 )
    canvas2.create_window(x_payee_entry, y_payee, window=bank_entry, anchor="w") 
    
    y_payee += 30

    # Branch
    label = tk.Label(root, text="Branch:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_payee, y_payee, window=label, anchor="w")  
    branch_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_payee_entry, y_payee, window=branch_entry, anchor="w") 
    y_payee += 30

    #IFSC Code
    # Branch
    label = tk.Label(root, text="IFSC:", font=("Arial", 10), bg="white", fg="black")
    canvas2.create_window(x_payee, y_payee, window=label, anchor="w")  
    ifsc_Payee_entry = tk.Entry( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=23)
    canvas2.create_window(x_payee_entry, y_payee, window=ifsc_Payee_entry, anchor="w")
    #ifsc_Payee_entry.bind("<KeyRelease>", update_field_data)

    x_position = 810
    y_position = 330
    label = tk.Label(root, text="Expense Type:", font=("Arial", 10), bg="white", fg="black")
    cheque_front.canvas.create_window(x_position, y_position, window=label, anchor="w")  
    y_position += 10
    dropdown_values = excel_con.load_column_values_to_dropdown("ExpenseType")
    create_dropdowns(dropdown_values,x_position, y_position)
    y_position += 40

    label = tk.Label(root, text="Classification Code:", font=("Arial", 10), bg="white", fg="black")
    cheque_front.canvas.create_window(x_position, y_position, window=label, anchor="w") 
    y_position += 15
    dropdown_values_cat1 = excel_con.load_column_values_to_dropdown("Payee")
    create_dropdowns(dropdown_values_cat1, x_position, y_position)
    y_position += 30
    dropdown_values_cat2 = excel_con.load_column_values_to_dropdown("Bank")
    create_dropdowns(dropdown_values_cat2, x_position, y_position)
    y_position += 30
    dropdown_values_cat3 = excel_con.load_column_values_to_dropdown("Amount")
    create_dropdowns(dropdown_values_cat3, x_position, y_position)
    y_position += 40

    #Classification Code
    label = tk.Label(root, text="Code:", font=("Arial", 10), bg="white", fg="black")
    cheque_front.canvas.create_window(x_position, y_position, window=label, anchor="w")  
    x_right = x_position + 40
    code_entry = tk.Entry( root, width=10, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10) )
    cheque_front.canvas.create_window(x_right, y_position, window=code_entry, anchor="w")  
    print(f" Classification Code {code_entry.get()}")
    x_right += 90
    y_position -= 15
    checkbox_var = tk.BooleanVar()
    create_checkbox(x_right, y_position, "Print", checkbox_var)
    y_position += 40
    
    label = tk.Label(root, text="Description:", font=("Arial", 10), bg="white", fg="black")
    cheque_front.canvas.create_window(x_position, y_position, window=label, anchor="w") 
    y_position += 30
    narration_entry = tk.Text( root, bd=2, highlightthickness=2, highlightbackground="gray", highlightcolor="blue", font=("Arial", 10), width=15, height=2)
    narration_entry.pack()
    character_limit = 100
    narration_entry.bind("<KeyRelease>", lambda event: limit_characters_text(event, narration_entry, character_limit))
    cheque_front.canvas.create_window(x_position, y_position, window=narration_entry, anchor="w")  # Adjusted position
    checkbox_var = tk.BooleanVar()
    create_checkbox((x_position+130), (y_position-10), "Print", checkbox_var)
    y_position += 40
    x_position += 40
    ### Print Button - Create a button
    generate_back_button = tk.Button(root, text="Print - Back", command=generate_cheque_back) 
    cheque_front.canvas.create_window((x_position+40), y_position, window=generate_back_button, anchor="center") 