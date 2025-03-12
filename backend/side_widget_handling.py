import os, sys
import configparser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from datetime import datetime
import win32print, win32api
from backend import shared, format_amount, rtgs_handling
from babel.numbers import format_decimal
from tkinter import messagebox

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
print(f"PARENT = {parent_dir}")
sys.path.append(parent_dir)
#import PyQt_chequeWriter
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
            gvalues = bottom_widget.get_all_entries()
            print("Retrieved Values:", gvalues)
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

    font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'Images','arial.ttf'))
    font_small = ImageFont.truetype(font_path, 12)

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
