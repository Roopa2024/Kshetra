import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from tkinter import messagebox
from datetime import datetime
from cheque import cheque_front, chequeWriter_Canon, format_amount, rtgs_handling, shared, cheque_back, shared
from cheque.shared import field_data_hdfc
import os, sys
IFSC = "HDFC0004012"

#global base_path
#image_path = os.path.join(base_path, 'Images','HDFC.png')

def set_base_path():
    global base_path, image_path, hdfc_path, karnataka_path, canara_path, union_path, font_small, font_small10, font_small11, rtgs_path, rtgs_filled
    if getattr(sys, 'frozen', False):
        # If frozen (running as an executable), use _MEIPASS to get the temp directory where PyInstaller extracts files
        base_path = sys._MEIPASS
    else:
        # If not frozen (running as a script), use the current script's directory
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Accessing an external file 
    hdfc_path = os.path.join(base_path, 'Images','HDFC.jpg')
    image_path = hdfc_path
    karnataka_path = os.path.join(base_path, 'Images','Karnataka.jpg')
    canara_path = os.path.join(base_path, 'Images','Canara.jpg')
    union_path = os.path.join(base_path, 'Images','Union.jpg')
    rtgs_path = os.path.join(base_path, 'Images','RTGS_HDFC.pdf')
    rtgs_filled = os.path.join(base_path, 'Images','RTGS_HDFC_filled.pdf')
    #print(f"Image path {hdfc_path}")

    # Load fonts
    try:
        font_path = os.path.join(base_path, 'Images','arial.ttf')
        font_large = ImageFont.truetype(font_path, 20)
        font_small = ImageFont.truetype(font_path, 12)
        font_small11 = ImageFont.truetype(font_path, 11)
        font_small10 = ImageFont.truetype(font_path, 10)
    except:
        messagebox.showerror("Font Error", "Font file not found. Ensure Arial is installed.")
        return

# Function to update the background based on the dropdown selection
def update_background(event, canvas):
    global IFSC, ifsc_value, cross, rtgs_path, rtgs_filled, image_path
    ifsc_value = tk.StringVar()
    selected_bank = cheque_front.bank_name_dropdown.get()
    print(f" background is {selected_bank}")
    if selected_bank == "HDFC Bank":
        hdfc_path = os.path.join(base_path, 'Images','HDFC.jpg')
        image_path = hdfc_path
        IFSC = "HDFC0004012"
        rtgs_path = os.path.join(base_path, 'Images','RTGS_HDFC.pdf')
        rtgs_filled = os.path.join(base_path, 'Images','RTGS_HDFC_filled.pdf')
    elif selected_bank == "Karnataka Bank":
        karnataka_path = os.path.join(base_path, 'Images','Karnataka.jpg')
        rtgs_filled = os.path.join(base_path, 'Images','RTGS_KAR_filled.pdf')
        rtgs_path = os.path.join(base_path, 'Images','RTGS_KAR.pdf')
        image_path = karnataka_path
        IFSC = "KARB0000605"
    elif selected_bank == "Canara Bank":
        rtgs_path = os.path.join(base_path, 'Images','RTGS_Canara.pdf')
        rtgs_filled = os.path.join(base_path, 'Images','RTGS_Canara_filled.pdf')
        image_path = canara_path
        IFSC = "CNRB0000640"
    elif selected_bank == "Union Bank":
        rtgs_path = os.path.join(base_path, 'Images','RTGS_Union.pdf')
        rtgs_filled = os.path.join(base_path, 'Images','RTGS_Union_filled.pdf')
        image_path = union_path
        IFSC = "UBIN0907111"
        #entry_window = canvas.create_window(300, 60, window=payee_entry, anchor="center")
    else:
        return  # Do nothing if no valid selection
    
    print(f" background should change to  {image_path}")

    ifsc_value.set(IFSC)
    cheque_back.update_ifsc(ifsc_value, selected_bank)

    # Update the canvas background
    new_image = Image.open(image_path).resize((800, 300), Image.Resampling.LANCZOS)
    new_photo = ImageTk.PhotoImage(new_image)
    canvas.image = new_photo  # Keep a reference to avoid garbage collection
    bg_image_id = canvas.create_image(0, 0, anchor="nw", image=new_photo)
    canvas.lower(bg_image_id)

    return

def get_updated_field_data(field_data):
    field_data.update({'chq_num': cheque_back.cheque_entry.get()})
    field_data.update({'ben_name': cheque_back.payee.get()})
    field_data.update({'ifsc_code': cheque_back.ifsc_Payee_entry.get()})
    if isinstance(cheque_back.current_widget, tk.Entry):
        field_data.update({'purpose': cheque_back.current_widget.get()})
    else:
        field_data.update({'purpose': cheque_back.purpose_dropdown.get()})
    amt = cheque_front.amount_entry.get()
    field_data.update({'amount': amt})
    in_words = format_amount.convert_to_words(amt)
    #wrapped_amount_words = format_amount.wrap_text(in_words, font_small, 100)
    print(f"WRAP = {in_words}")
    field_data.update({'in_words': in_words})

    #Bank specific RTGS Data handling
    if field_data['BANK'] == 'hdfc':
        field_data.update({'bank_br': cheque_back.bank_entry.get()+ " " + cheque_back.branch_entry.get()})
    else:
        selected_date = cheque_front.date_entry.get()
        date_obj = datetime.strptime(selected_date, "%m/%d/%y")  # Parse the input date
        if 'total' in field_data and field_data['total'] == '':
            field_data.update({'total': amt})
            formatted_date = date_obj.strftime("%d.%m.%y")
            formatted_date = formatted_date.replace(".", "")
        else:
            formatted_date = date_obj.strftime("%d.%m.%Y")

        field_data.update({'chq_date': formatted_date})
        #PAN is commented out temporarily 29-06-2025
        #field_data.update({'PAN': cheque_back.gst_pan_entry.get()})
        field_data.update({'bank_name': cheque_back.bank_entry.get()})
        field_data.update({'ben_bank_br': cheque_back.branch_entry.get()})

    return field_data
