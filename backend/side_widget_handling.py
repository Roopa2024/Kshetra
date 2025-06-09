import os, sys
import configparser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
import win32print, win32api
from backend import shared, format_amount, rtgs_handling, bottom_widget_handling, excel_con
from babel.numbers import format_decimal
from tkinter import messagebox
import json
SAVE_FILE = "saved_data.json"

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(f"PARENT = {parent_dir}")
sys.path.append(parent_dir)
font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'Images','arial.ttf'))
font_small = ImageFont.truetype(font_path, 12)
font_10 = ImageFont.truetype(font_path, 10)
import PyQt_chequeWriter #import BottomWidget

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
global cancel, line1, line2, text
cross= 1

def set_cross():
    global cross
    cross = 1
    return cross

def toggle_button_state(btn, label_name, bottom_widget, top_widget, sel_bank_index):
    print(f"BUTTON name = {label_name} and Values = {btn.text()} Bank = {sel_bank_index}")
    global cross
    #cancel = 0
    ## ON to OFF
    if btn.text() == "ON":                          # Check if the button's text is "Turn ON"
        if label_name == 'Cancel Cheque':
            cancel = 0
            print(f"CANCEL = {cancel} is turned  OFF")
        elif label_name == "A/C Payee":            
            cross = 0
            top_widget.toggle_ac_payee()
            print(f"A/C Payee and cross is turned  OFF")
        elif label_name == "RTGS":
            print(f"RTGS turned OFF")
            top_widget.entries[4].setText('')
            top_widget.entries[4].setEnabled(True)
            top_widget.toggle_ac_payee()
        btn.setText("OFF")
        btn.setStyleSheet("background-color: orange; color: black;")  # Change the button color
    ## OFF to ON
    else:
        if label_name == 'Cancel Cheque':           
            cancel = 1
            print(f"CANCEL = {label_name} is ON")
        elif label_name == "A/C Payee":            
            cross = 1
            top_widget.toggle_ac_payee()
            print(f"A/C Payee and cross is turned  ON")
        elif label_name == "RTGS":
            if not top_widget.entries[7].text():
                messagebox.showerror("Input Error", "Please fill in all required fields.")
                return
            cross = 0
            print(f"RTGS turned ON to open {sel_bank_index}")
            top_widget.toggle_ac_payee()
            
            #def on_text_changed():
            #    print("Roopa Text entered:", bottom_widget.bottom_entries[1][1].text())

            #bottom_widget.bottom_entries[1][1].editingFinished.connect(on_text_changed)
            name = bottom_widget.bottom_entries[1][2].text() 
            #print(f"IFSC = {name}")
            #try:
            #    with open(SAVE_FILE, "r") as f:
            #        data = json.load(f)
            #        #print("Retrieved from JSON:", data.get("Name1_entry", "NA"))
            #        #print("Retrieved Data:", data)
            #except (FileNotFoundError, json.JSONDecodeError):
            #    print("No saved data found.")

            rtgs_handling.update_rtgs_bank(sel_bank_index, top_widget)  #rtgs_path[0]
        btn.setText("ON")
        btn.setStyleSheet("background-color: green; color: black;") 

def cancel_check(cheque_image, draw, font_large):
    text_img = Image.new("RGBA", (400, 180), (255, 255, 255, 0))  # Transparent background for text
    text_draw = ImageDraw.Draw(text_img)
    # First slanting line
    draw.line([0, 200, 600, 0], fill= shared.font_color, width=2)
    text_draw.text((200, 80), text="CANCELLED", font=font_large, fill=shared.font_color)
    # Second slanting line
    draw.line([600, 50, 50, 240], fill=shared.font_color, width=2)
    rotated_text = text_img.rotate(20, expand=True)
    # Get the size of the rotated text image
    rotated_width, rotated_height = rotated_text.size
    # Paste the rotated text back onto the original image
    cheque_image.paste(rotated_text, (0, 0), rotated_text)

# Function to print the generated Cheque
def print_cheque(cheque_image_path):
    printer_name = win32print.GetDefaultPrinter()  # Get default printer
    print(f"Default Printer: {printer_name}")
    # Call the Windows Print Dialog
    win32api.ShellExecute(0, "open", cheque_image_path, None, ".", 1) #'/d:"%s"' % printer_name, ".", 0)

def cross_check(bank_name, cheque_image, draw, top_widget):
    #global line1, line2, text
    if bank_name == "HDFC Bank":
        print("HDFC")
        x1_y2 = 130
        x3_y4 = 100
        x_AC = 65
        text_img = Image.new("RGBA", (150, 280), (255, 255, 255, 0))  # Transparent background for text
    elif bank_name in ("Karnataka Bank", "Canara Bank"):
        print(" KAR CANARA")
        x1_y2 = 160
        x3_y4 = 130
        x_AC = 92
        text_img = Image.new("RGBA", (190, 290), (255, 255, 255, 0))  # Transparent background for text
    else:
        print("Union")
        x1_y2 = 160
        x3_y4 = 130 
        x_AC = 80
        text_img = Image.new("RGBA", (190, 290), (255, 255, 255, 0))  # Transparent background for text
        #y_position = 70
        y_date = 40
    if bank_name == "Canara Bank":
        y_date = 43

    # Define the coordinates for the slanting lines
    x1, y1 = x1_y2, 0  # Starting point of first line
    x2, y2 = 0, x1_y2  # Ending point of first line
    x3, y3 = x3_y4, 0   # Starting point of second line
    x4, x3 = 0, x3_y4  # Ending point of second line

    # Set the color for the lines (Red in RGB)
    line_color = (0, 0, 0)  # Red color
    # Draw the two slanting lines
    top_widget.line1 = draw.line([x1_y2, y1, x2, x1_y2], fill=line_color, width=1)  # First slanting line
    top_widget.line2 = draw.line([x3_y4, y3, x4, x3_y4], fill=line_color, width=1)  # Second slanting line
    try:
        # Use a specific TTF font and specify the font size (e.g., 20)
        font = ImageFont.truetype("arial.ttf", size=40)  # Make sure to specify the correct path to the font
    except IOError:
        font = ImageFont.load_default()  # Fallback to default if the font is not found
    # Optionally add slanted text
    #text_color = (0, 0, 0)  # Black color for text
    font = ImageFont.load_default()  # Use a default font (you can also use a custom font)
    
    text_draw = ImageDraw.Draw(text_img)
    # Draw the text on the new image
    top_widget.text = text_draw.text((x_AC, 0), "A/C Payee", font=font, fill=shared.font_color)  

    # Rotate the text image to make it slanted (e.g., 45 degrees)
    rotated_text = text_img.rotate(45, expand=True)
    # Get the size of the rotated text image
    rotated_width, rotated_height = rotated_text.size
    # Paste the rotated text back onto the original image
    cheque_image.paste(rotated_text, (0, 0), rotated_text)  # Position it at (100, 50)

# Function to generate cheque
def generate_cheque_front(bank_idx, date, top_widget):
    
    #Input validation
    if not top_widget.entries[4].text() or not top_widget.entries[7].text(): #or not cheque_number or not bank_name:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return
    
    payee = top_widget.entries[4].text()            
    amount = float(top_widget.entries[7].text())    
    date = top_widget.entries[2].date() 
    date = date.toPyDate() 
    print (f"Generate Front cheque {bank_idx}, {payee} {amount} and {date}")

    #font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'Images','arial.ttf'))
    #font_small = ImageFont.truetype(font_path, 12)

    # Create cheque image
    cheque_image = Image.new('RGB', (792, 612), color='white')
    draw = ImageDraw.Draw(cheque_image)
    
    if 'cancel' in globals() and cancel == 1:
        print("Cancel")
        current_time = datetime.now().strftime("%H%M%S")
        cancel_check(cheque_image, draw, shared.font_large)
        # Save cheque as image
        cheque_image.save(f"Cancelcheque_{current_time}.pdf")
        print_cheque(f"Cancelcheque_{current_time}.pdf") 
        return

    bank_name = shared.banks[bank_idx] #bank_name_entry.get()
    print(f"Bank name is {bank_name}")
    y_position = 80
    y_date = 42

    if 'cross' in globals() and cross == 1:
        print("cross")
        cross_check(bank_name, cheque_image, draw, top_widget)
        draw.text((535, y_position), "XXXXXXX", font=font_small, fill=(0, 0, 0))

    # Add payee details
    payee_with_star = " **" + payee + "**"
    print (f" PAYEE = {payee_with_star} and {font_small}")
    draw.text((90, y_position), f" {payee_with_star}", font=font_small, fill=(0, 0, 0))

    y_position += 22
    # Add cheque date
    #selected_date = date_entry.get()
    print(f"DATE is {date}")
    #if isinstance(date, str):
    #    date_obj = datetime.strptime(date, "%m/%d/%y")
    #    print(f"DATE is {date_obj}")
    #else:
    #    print("Error: Expected a string for date, but got", type(date))
    day = str(date.day).zfill(2)  # Get the day, month, and year as strings (without leading zeros)
    month = str(date.month).zfill(2)
    year = str(date.year)
    
    formatted_date = '   '.join(list(day + month + year))               # Break each part of the date into individual digits
    print(f"Formatted DATe = {formatted_date}")
    if bank_name == "Union Bank":
        draw.text((480, y_date), f"{formatted_date}", font=font_small, fill=(0, 0, 0))
    elif bank_name == "HDFC Bank":
        draw.text((480, y_date), f"{formatted_date}", font=font_small, fill=(0, 0, 0))
    else:
        draw.text((480, y_date), f"{formatted_date}", font=font_small, fill=(0, 0, 0))

    amount_words = format_amount.convert_to_words(amount)               # Add amount in words (converted to INR)
    amount_words = amount_words.replace("Rupees", "").strip()
    amount_words_with_only = " **" + amount_words + " Only**"
    wrapped_amount_words = format_amount.wrap_text(amount_words_with_only, font_small, 500)  # 700px width for wrapping

    for line in wrapped_amount_words:
        draw.text((130, y_position), line, font=font_small, fill=(0, 0, 0))
        y_position += 25  # Move to next line

    # Ensure 'amount' is a string before filtering digits
    amount_str = str(amount)                                            # Convert the integer 'amount' to a string

    if amount:
        formatted_amount = format_decimal(amount, locale='en_IN')       # Format the integer part in the Indian numbering system
    else:
        formatted_amount = ""
    print(f" FORMAT = {formatted_amount}")

    if bank_name in ("Union Bank"):
        draw.text((500, 125), f" {formatted_amount} /-", font=shared.font12, fill=(0, 0, 0))
    else:
        draw.text((490, 120), f" {formatted_amount} /-", font=font_small, fill=(0, 0, 0))

    # Save cheque as image
    cheque_image.save(f"cheque_{payee}.pdf")
    print_cheque(f"cheque_{payee}.pdf") 

def draw_line(text, x_position, y_position, draw):
    # Get the text size to calculate underline position
    # Use textbbox to calculate text size
    text_bbox = draw.textbbox((x_position, y_position), text, font=font_small)
    text_width = text_bbox[2] - text_bbox[0]  # Calculate text width
    text_height = text_bbox[3] - text_bbox[1]  # Calculate text height

    # Draw an underline below the text
    underline_y_position = y_position + text_height + 2  # Slightly below the text
    draw.line(
    [(x_position, underline_y_position), (x_position + text_width, underline_y_position)],
    fill="black",
    width=1
    )

def generate_cheque_back(bank_idx, date, top_widget, code_print, desc_print):
    #Input validation
    if not top_widget.entries[4].text() or not top_widget.entries[7].text(): #or not cheque_number or not bank_name:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return
    
     # Create cheque image
    #cheque_image = Image.new('RGB', (792, 612), color='white')
    cheque_image = Image.new('RGB', (600, 595), color='white')      #A5 height, but width slightly more

    draw = ImageDraw.Draw(cheque_image)
    chq_num = bottom_widget_handling.get_value('Cheque_entry')
    if not chq_num:
        messagebox.showerror("Input Error", "Please fill in the Cheque Number.")
        return

    amt_entry = float(top_widget.entries[7].text())
    date_entry = top_widget.entries[2].text()
    biller_name = bottom_widget_handling.get_value('Name_entry')
    payee_name = bottom_widget_handling.get_value('Name1_entry')
    globe_id = "SGP"

    globe_id = excel_con.increment_counter()
    print("Data to Save in Excel")
    kwargs = {
        'globe_id' : globe_id,
        'globe_stat' : 'Approved',
        'Payee' : payee_name,
        'Amount' : amt_entry,
        'Date' : date_entry,
        'Bank' : bottom_widget_handling.get_value('Bank_entry'),
        'Cheque #' : bottom_widget_handling.get_value('Cheque_entry'),
        'IFSC code' : bottom_widget_handling.get_value('IFSC1_entry'),
        'Biller name' : biller_name,
        'Invoice #' : bottom_widget_handling.get_value('Invoice_entry'),
        'GST/PAN' : bottom_widget_handling.get_value('GST_entry'),
        'Payee Name' : payee_name,
        'Bank Name' : bottom_widget_handling.get_value('Bank1_entry'),
        'Branch Name' : bottom_widget_handling.get_value('Branch_entry'),
        'Payee IFSC' : bottom_widget_handling.get_value('IFSC_entry'),
        'Digital Sign' : bottom_widget_handling.get_value('Dig_entry'),
        'Expense Type' : bottom_widget_handling.get_value('Expense Type:'),
        'Department' : bottom_widget_handling.get_value('Department'),
        'Designation' : bottom_widget_handling.get_value('Designation'),
        'Service Code' : bottom_widget_handling.get_value('Service Code'),
        'Code' : bottom_widget_handling.get_value('Code:'),
        'Description' : bottom_widget_handling.get_value('Description:')
    }
    shared.field_data_hdfc.update(kwargs)

    line_height = 15  # Line spacing
    #font_10 = bank_handling.font_small_10 
    x_position = 60
    y_position = 30

    draw.text((x_position, y_position), f"GlobeID: {globe_id}       Amount: {amt_entry}", font=font_10, fill="black")
    draw_line("Globe",x_position, y_position, draw)
    y_position += 20

    draw.text((x_position, y_position), "Bill Details:", font=font_10, fill="black")
    draw_line("Bill Details",x_position, y_position, draw)

    x_position = 250
    #y_position = 50
    draw.text((x_position, y_position), "Payee Details:", font=font_10, fill="black")
    draw_line("Payee Details",x_position, y_position, draw)
    x_position = 430
    draw.text((x_position, y_position), "Payment Details", font=font_10, fill=(0, 0, 0))
    draw_line("Payment Details",x_position, y_position, draw)

    #Bill Details
    x_position = 430
    y_position += 20
    draw.text((x_position, y_position), f"Name: {biller_name}", font=font_10, fill="black")
    y_position += 20
    draw.text((x_position, y_position), f"Invoice#: {bottom_widget_handling.get_value('Invoice_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"GST: {bottom_widget_handling.get_value('GST_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"PAN: {bottom_widget_handling.get_value('PAN_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20

    #Payee Details
    x_position = 250
    y_position = 70
    draw.text((x_position, y_position), f"Name: {payee_name}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Bank: {bottom_widget_handling.get_value('Bank_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Branch: {bottom_widget_handling.get_value('Branch_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"IFSC: {bottom_widget_handling.get_value('IFSC_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), "Digital Signature: ", font=font_10, fill=(0, 0, 0))
    draw_line("Digital Signature:",x_position, y_position, draw)
    y_position += 20
    draw.text((x_position, y_position), f"{bottom_widget_handling.get_value('Dig_entry')}", font=font_10, fill=(0, 0, 0))

    #Payment Details
    x_position = 60
    y_position = 70
    draw.text((x_position, y_position), f"Cheque#: {bottom_widget_handling.get_value('Cheque_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"IFSC: {bottom_widget_handling.get_value('IFSC1_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Branch: {bottom_widget_handling.get_value('Branch1_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20 
    draw.text((x_position, y_position), f"Cheque Date: {bottom_widget_handling.get_value('ChequeDate_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Bank: {bottom_widget_handling.get_value('Bank1_entry')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Compliance: ", font=font_10, fill="black")
    draw_line("Compliance:",x_position, y_position, draw)
    y_position += 20 
    draw.text((x_position, y_position), f"Expense Type: {bottom_widget_handling.get_value('Expense Type:')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    draw.text((x_position, y_position), f"Department: {bottom_widget_handling.get_value('Department')}", font=font_10, fill=(0, 0, 0))
    y_position += 10
    draw.text((x_position, y_position), f"Designation: {bottom_widget_handling.get_value('Designation')}", font=font_10, fill=(0, 0, 0))
    y_position += 10
    draw.text((x_position, y_position), f"Service Code: {bottom_widget_handling.get_value('Service Code')}", font=font_10, fill=(0, 0, 0))
    y_position += 20
    print (f"Print code = {code_print} and desc = {desc_print}")
    if code_print == 1:
        draw.text((x_position, y_position), f"Code: {bottom_widget_handling.get_value('Code:')}", font=font_10, fill=(0, 0, 0))
        y_position += 20
    if desc_print == 1:
        draw.text((x_position, y_position), f"Description: {bottom_widget_handling.get_value('Description:')}", font=font_10, fill=(0, 0, 0))
        y_position += 20

    # Save cheque as image
    cheque_image.save(f"chequeBack_{chq_num}.pdf")
    print_cheque(f"chequeBack_{chq_num}.pdf") 
    
    excel_con.save_to_excel(**kwargs)