import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import messagebox
from cheque import chequeWriter_Canon, format_amount, cheque_back, rtgs_handling, shared, bank_handling
import cheque.cheque_back
from cheque.shared import field_data_hdfc
#from cheque.bank_handling import update_background, image_path
import os
import sys

root = None

def cancel_check(cheque_image, draw, font_large):
    text_img = Image.new("RGBA", (400, 180), (255, 255, 255, 0))  # Transparent background for text
    text_draw = ImageDraw.Draw(text_img)
    # First slanting line
    draw.line([0, 200, 600, 0], fill="black", width=2)
    #draw.text((90, y_position), f" {payee_with_star}", font=font_small, fill=(0, 0, 0))
    text_draw.text((200, 80), text="CANCELLED", font=font_large, fill="black")
    # Second slanting line
    draw.line([600, 50, 50, 240], fill="black", width=2)
    rotated_text = text_img.rotate(20, expand=True)
    # Get the size of the rotated text image
    rotated_width, rotated_height = rotated_text.size
    # Paste the rotated text back onto the original image
    cheque_image.paste(rotated_text, (0, 0), rotated_text)

def cross_check(bank_name, cheque_image, draw):
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
    draw.line([x1_y2, y1, x2, x1_y2], fill=line_color, width=1)  # First slanting line
    draw.line([x3_y4, y3, x4, x3_y4], fill=line_color, width=1)  # Second slanting line
    try:
        # Use a specific TTF font and specify the font size (e.g., 20)
        font = ImageFont.truetype("arial.ttf", size=40)  # Make sure to specify the correct path to the font
    except IOError:
        font = ImageFont.load_default()  # Fallback to default if the font is not found
    # Optionally add slanted text
    text_color = (0, 0, 0)  # Black color for text
    font = ImageFont.load_default()  # Use a default font (you can also use a custom font)
    
    text_draw = ImageDraw.Draw(text_img)
    # Draw the text on the new image
    text_draw.text((x_AC, 0), "A/C Payee", font=font, fill=text_color)  

    # Rotate the text image to make it slanted (e.g., 45 degrees)
    rotated_text = text_img.rotate(45, expand=True)
    # Get the size of the rotated text image
    rotated_width, rotated_height = rotated_text.size
    # Paste the rotated text back onto the original image
    cheque_image.paste(rotated_text, (0, 0), rotated_text)  # Position it at (100, 50)

# Function to generate cheque
def generate_cheque_front():

    print (f"Generate Front cheque cancel is {cancel} and {cross}")
    
    # Create cheque image
    cheque_image = Image.new('RGB', (792, 612), color='white')
    draw = ImageDraw.Draw(cheque_image)

    # Load fonts
    #try:
        #font_path = "C:/Windows/Fonts/arial.ttf"  # Path to Arial font on Windows
        #font_large = ImageFont.truetype(font_path, 20)
        #font_small = ImageFont.truetype(font_path, 12)
        #font_small11 = ImageFont.truetype(font_path, 11)
        #font_small10 = ImageFont.truetype(font_path, 10)
    #except:
        #messagebox.showerror("Font Error", "Font file not found. Ensure Arial is installed.")
        #return
    
    if 'cancel' in globals() and cancel == 1:
        print("Cancel")
        current_time = datetime.now().strftime("%H%M%S")
        cancel_check(cheque_image, draw, bank_handling.font_large)
        # Save cheque as image
        cheque_image.save(f"Cancelcheque_{current_time}.pdf")
        chequeWriter_Canon.print_cheque(f"Cancelcheque_{current_time}.pdf") 
        return

    payee = payee_entry.get()
    amount = amount_entry.get()
    #cheque_number = cheque_number_entry.get()
    bank_name = bank_name_dropdown.get() #bank_name_entry.get()
    print(f"Bank name is {bank_name}")
    y_position = 80
    y_date = 42

    # Input validation
    if not payee or not amount: #or not cheque_number or not bank_name:
        messagebox.showerror("Input Error", "Please fill in all required fields.")
        return

    #try:
    #    amount = int(amount)
    #except ValueError:
    #    messagebox.showerror("Amount Error", "Please enter a valid amount.")
    #    return
    
    if 'cross' in globals() and cross == 1:
        print("cross")
        cross_check(bank_name, cheque_image, draw)
        draw.text((535, y_position), "XXXXXXX", font=bank_handling.font_small, fill=(0, 0, 0))

    # Add payee details
    payee_with_star = " **" + payee + "**"
    draw.text((90, y_position), f" {payee_with_star}", font=bank_handling.font_small, fill=(0, 0, 0))

    y_position += 22
    # Add cheque date
    selected_date = date_entry.get()
    date_obj = datetime.strptime(selected_date, "%m/%d/%y")
    day = str(date_obj.day).zfill(2)  # Get the day, month, and year as strings (without leading zeros)
    month = str(date_obj.month).zfill(2)
    year = str(date_obj.year)
    # Break each part of the date into individual digits
    formatted_date = '   '.join(list(day + month + year))
    if bank_name == "Union Bank":
        draw.text((480, y_date), f"{formatted_date}", font=bank_handling.font_small11, fill=(0, 0, 0))
    elif bank_name == "HDFC Bank":
        draw.text((480, y_date), f"{formatted_date}", font=bank_handling.font_small10, fill=(0, 0, 0))
    else:
        draw.text((480, y_date), f"{formatted_date}", font=bank_handling.font_small10, fill=(0, 0, 0))

    # Add amount in words (converted to INR)
    amount_words = format_amount.convert_to_words(amount)
    amount_words = amount_words.replace("Rupees", "").strip()
    amount_words_with_only = " **" + amount_words + " Only**"
    # Wrap text in "Amount in Words" field (avoid overwriting)
    wrapped_amount_words = format_amount.wrap_text(amount_words_with_only, bank_handling.font_small, 500)  # 700px width for wrapping
    #field_data['in_words'] = wrapped_amount_words.get()

    for line in wrapped_amount_words:
        draw.text((130, y_position), line, font=bank_handling.font_small, fill=(0, 0, 0))
        y_position += 25  # Move to next line

    # Add amount in figures
    # Ensure 'amount' is a string before filtering digits
    amount_str = str(amount)  # Convert the integer 'amount' to a string
    # Remove any non-digit characters (this could include existing commas)
    amount = ''.join(filter(str.isdigit, amount_str))    
    # Format the number in the Indian numbering system
    if amount:
        # Format the integer part in the Indian numbering system
        formatted_amount = format_amount.format_number(amount)
    else:
        formatted_amount = ""
    if bank_name in ("Union Bank"):
        draw.text((500, 125), f" {formatted_amount} /-", font=bank_handling.font_small, fill=(0, 0, 0))
    else:
        draw.text((490, 120), f" {formatted_amount} /-", font=bank_handling.font_small, fill=(0, 0, 0))

    # Save cheque as image
    cheque_image.save(f"cheque_{payee}.pdf")
    chequeWriter_Canon.print_cheque(f"cheque_{payee}.pdf") 
    #messagebox.showinfo("Cheque Generated", f"Cheque generated successfully! Saved as cheque_{payee}.pdf")

def toggle_action(selected_button, all_buttons):
    global canvas, line1, text, line2, line1_cancel, text_cancel, line2_cancel, cross, cancel, bearer
    """Toggle the state of the selected button and gray out others."""
    if selected_button["text"] == "OFF":
        # Turn the selected button ON and disable the rest
        selected_button.config(text="ON", bg="green")
        for button in all_buttons:
            if (button != selected_button):
                #var.set(False)
                print(f"Button is {selected_button}")
                if str(selected_button) == ".!button" and str(button) not in [".!button3", ".!button4", ".!button5"]:
                    button.config(state=tk.DISABLED, bg="lightgray", text="OFF")
                elif str(selected_button) == ".!button2":
                    button.config(state=tk.DISABLED, bg="lightgray", text="OFF")  
                elif str(selected_button) in [".!button3", ".!button4", ".!button5"] and str(button) != ".!button2":
                    button.config(state=tk.DISABLED, bg="lightgray", text="OFF")
                elif str(selected_button) in [".!button6", ".!button7"] and str(button) in [".!button",".!button6", ".!button7"]:
                    button.config(state=tk.DISABLED, bg="lightgray", text="OFF")
            else:
                print(f"Button OFF --> ON is {selected_button}")
                if str(selected_button) == ".!button":
                    print("Cross cheque is ON and Cancel is OFF")
                    cross = 1
                    cancel = 0
                    # First slanting line
                    line1 = canvas.create_line(0, 50, 50, 0, fill="black", width=1)
                    text = canvas.create_text(30, 30, text="A/C Payee", font=("Helvetica", 8), fill="black", angle=45)
                    # Second slanting line
                    line2 = canvas.create_line(0, 70, 70, 0, fill="black", width=1)
                    #Bearer
                    #bearer = canvas.create_text(730, 76, text="XXXXXXXXXX", font=("Helvetica", 10), fill="black")
                    bearer = canvas.create_text(730, 90, text="XXXXXXXXXX", font=("Helvetica", 10), fill="black")

                    if 'text_cancel' in globals():
                        canvas.delete(line1_cancel, text_cancel, line2_cancel)
                    print(f"cross is set to {cross}")
                elif str(selected_button) == ".!button2":
                    print("Cancel check is ON, Cross check is OFF")
                    cancel = 1
                    cross = 0
                    # First slanting line
                    line1_cancel = canvas.create_line(0, 250, 750, 0, fill="black", width=2)
                    text_cancel = canvas.create_text(400, 150, text="CANCELLED", font=("Helvetica", 16), fill="black", angle=20)
                    # Second slanting line
                    line2_cancel = canvas.create_line(800, 50, 50, 300, fill="black", width=2)
                    if 'text' in globals():
                        canvas.delete(line1, text, line2, bearer)
                    payee_entry.delete(0, tk.END)
                    payee_entry.config(state=tk.DISABLED)  
                    amount_entry.delete(0, tk.END)
                    amount_entry.config(state=tk.DISABLED)  
                elif str(selected_button) == ".!button3" :
                    print(f"open file {bank_handling.rtgs_path}")
                    if ("HDFC" in bank_handling.rtgs_path):
                        print ("HDFC data")
                        bank_handling.get_updated_field_data(shared.field_data_hdfc)
                        field_data = shared.field_data_hdfc
                    elif("KAR" in bank_handling.rtgs_path):
                        print("KAR bank data")
                        bank_handling.get_updated_field_data(shared.field_data_kar)
                        field_data = shared.field_data_kar
                    elif("Canara" in bank_handling.rtgs_path):
                        print("Canara bank data")
                        bank_handling.get_updated_field_data(shared.field_data_canara)
                        field_data = shared.field_data_canara
                    elif("Union" in bank_handling.rtgs_path):
                        print("Union Bank data")
                        bank_handling.get_updated_field_data(shared.field_data_union)
                        field_data = shared.field_data_union

                    rtgs_handling.create_filled_pdf(bank_handling.rtgs_path, bank_handling.rtgs_filled, field_data) #shared.field_data_hdfc)
                    os.startfile(bank_handling.rtgs_filled)
                    cross=0
                    canvas.delete(line1, text, line2, bearer)
                    payee_entry.delete(0, tk.END)
                    payee_entry.insert(0, "Yourself") 
                    payee_entry.config(state=tk.DISABLED)   
                elif str(selected_button) == ".!button4":
                    print("NEFT selected")
                elif str(selected_button) == ".!button5":
                    print("Cheque selected")
                elif str(selected_button) == ".!button6":
                        payee_entry.delete(0, tk.END)
                        payee_entry.insert(0, "Self")
                        payee_entry.config(state=tk.DISABLED)
                elif str(selected_button) == ".!button7":
                        payee_entry.delete(0, tk.END)
                        payee_entry.insert(0, "Yourself") 
                        payee_entry.config(state=tk.DISABLED)
    else:
        # Turn the selected button OFF and enable the rest
        selected_button.config(text="OFF", bg="orange")
        for button in all_buttons:
            button.config(state=tk.NORMAL, bg="orange")
            if str(selected_button) == ".!button":
                print("A/C cross turned off now")
                cross = 0
                canvas.delete(line1, text, line2, bearer)
            if str(selected_button) == ".!button2":
                print("Cancel cheque turned off now")
                cancel = 0
                canvas.delete(line1_cancel, text_cancel, line2_cancel)
                payee_entry.config(state=tk.NORMAL)
                amount_entry.config(state=tk.NORMAL)  
            if str(selected_button) in [".!button3", ".!button6", ".!button7"]:
                payee_entry.delete(0, tk.END)
                payee_entry.config(state=tk.NORMAL) 

def create_label_and_button(canvas, x, y, text, all_buttons):
    global root
    """Create a label and a toggle button dynamically."""
    # Create the label
    if root is not None:
        label = tk.Label(root, text=text, font=("Arial", 10), bg="white", fg="black")
        canvas.create_window(x, y, window=label, anchor="center")
        # Create the toggle button
        toggle_button = tk.Button( root, text="OFF", bg="orange", fg="white", width=3, height=1,
        command=lambda: toggle_action(toggle_button, all_buttons))
        canvas.create_window(x + 60, y, window=toggle_button, anchor="center")
        all_buttons.append(toggle_button)
        if text == "A/C Payee":
            toggle_action(toggle_button, all_buttons)
    else:
        print("create_label_and_button: Root is not initialized.")

def UI_front(app_root):
    global root, canvas, IFSC, payee_entry, amount_entry, bank_name_dropdown, date_entry#, c_image_path
    root = app_root
    # Load the HDFC Bank background image by default
    IFSC = "HDFC0004012"
    bg_image = Image.open(bank_handling.hdfc_path).resize((800, 300), Image.Resampling.LANCZOS)
    #bg_image = Image.open(image_path).resize((800, 300), Image.Resampling.LANCZOS)

    # Create a canvas to hold the background image
    canvas = tk.Canvas(root, width=bg_image.width, height=bg_image.height)
    canvas.pack(fill="both", expand=True)
    new_photo = ImageTk.PhotoImage(bg_image)
    canvas.image = new_photo  # Keep a reference to avoid garbage collection
    canvas.create_image(0, 0, anchor="nw", image=new_photo)

    # Create an Entry widget and place it over the canvas
    #Pay
    payee_entry = tk.Entry(root, font=("Arial", 10), width=50)
    entry_window = canvas.create_window(300, 76, window=payee_entry, anchor="center")

    #Amount
    amount_entry = tk.Entry(root, font=("Arial", 10), width=10)
    #entry_window = canvas.create_window(680, 124, window=amount_entry, anchor="center")
    entry_window = canvas.create_window(680, 140, window=amount_entry, anchor="center")
    #field_data.update({'amount': amount_entry.get()})

    # Create a DateEntry widget using tkcalendar
    date_entry = DateEntry(root, width=20, font=("Arial", 10))
    date_entry.bind("<<DateEntrySelected>>", cheque_back.update_chq_date)
    #canvas.create_window(680, 25, window=date_entry, anchor="center")
    canvas.create_window(680, 30, window=date_entry, anchor="center")

    # Create a dropdown list (Combobox)
    dropdown_values = ["HDFC Bank", "Karnataka Bank", "Canara Bank", "Union Bank"]
    bank_name_dropdown = ttk.Combobox(root, values=dropdown_values, state="readonly", font=("Arial", 10))
    bank_name_dropdown.set("HDFC Bank")  # Set a placeholder
    bank_name_dropdown.bind("<<ComboboxSelected>>", lambda event: bank_handling.update_background(event, canvas))

    # Place the dropdown on the canvas
    canvas.create_window(900, 15, window=bank_name_dropdown, anchor="center")  

    all_buttons = []    # List to hold references to all buttons
    items = [("A/C Payee", 860, 100), ("Cancel cheque", 860, 130), ("RTGS", 860, 160), ("NEFT", 860, 190), ("Cheque", 860, 220), ("Self", 810, 60), ("Yourself", 920, 60)]
    for item in items:
        create_label_and_button(canvas, item[1], item[2], item[0], all_buttons)

    # Print Button
    # Create a button
    generate_button = tk.Button(root, text="Print - Front", command=generate_cheque_front) #lambda: print("Button clicked!"))
    # Add the button to the canvas
    canvas.create_window(900, 250, window=generate_button, anchor="center") 


