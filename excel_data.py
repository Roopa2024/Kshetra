#import tkinter as tk
from tkinter import messagebox
import pandas as pd
import openpyxl
from openpyxl import load_workbook, Workbook
import os, configparser, io
from io import BytesIO
import barcode, qrcode
from barcode.writer import ImageWriter
from PIL import Image as PILImage, ImageFont, ImageDraw
from openpyxl.drawing.image import Image
from datetime import datetime
import qrcode

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config", "receipt.ini"))
custom_font_path = os.path.dirname(os.path.abspath(__file__))+r"\config\RobotoMono-Regular.ttf"
print(config_path)
config = configparser.ConfigParser()
config.read(config_path)
xcl_file = config.get('Filenames', 'xcl_file')
xcl_sheet = config.get('Filenames', 'xcl_sheet')
pdf_heading = config['Heading']['pdf_heading']
pdf_headings = pdf_heading.split(',')
entity_xcl = config.get('Filenames', 'input_files')
entity_xcls = entity_xcl.split(',')
try:
    font = ImageFont.truetype(custom_font_path, 20)
except OSError:
    print(f"Font {custom_font_path} not found, using default.")
    font = ImageFont.load_default()
    
def increment_counter(col_number, xcl_path):
    #xcl_path = os.path.join("Images", xcl_path)
    if not os.path.exists(xcl_path):
        print(f"⚠️ File '{xcl_path}' not found. Creating a new one...{col_number}")
        wb = Workbook()  # Create a new workbook
        wb.active.append(["Counter"])  # Add a header row (optional)
        wb.save(xcl_path)  # Save new workbook
        print("✅ New file created successfully!")

    print(f"increment_counter is col # = {xcl_path}")
    df = pd.read_excel(xcl_path, sheet_name="Sheet1") 
    wb = load_workbook(xcl_path)   # Load the workbook and select the sheet
    sheet = wb.active               # Or use wb['SheetName'] if you have a specific sheet
    last_row = sheet.max_row        # Get the last row number
    last_value = sheet.cell(row=last_row, column=col_number).value  # Adjust column index as needed
    last_value1 = df["Id."].dropna().iloc[-1] 
    print(f"Value is {last_value1}")

    if(col_number == 2):
        #match = re.match(r'([a-zA-Z]+)(\d+)', last_value)
        match = last_value[-4:] 

        if match:
            prefix = remaining_text = last_value[:-4]    # Extract the prefix and the number part
            num_part = last_value[-4:] 
        
            # Increment the numeric part and pad it to 4 digits (e.g., 0002)
            num_part = str(int(num_part) + 1).zfill(len(num_part))  # Use zfill to maintain leading zeros
        
            new_value = prefix + num_part # Reassemble the string with the incremented value
        else:
            print("Invalid format")
            return None    
    else:
        new_value = int(last_value1) + 1
        globeid = df.at[last_value1, "GlobeId"]
        text = df.at[last_value1, "TextColumn"]
    print(f"New value: {new_value} and {globeid}")
    return new_value, globeid, text
    
def get_bar_directory(pdf_filename):
    base_dir = os.getcwd()
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_folder = os.path.join(base_dir, "barcodes", pdf_name_without_ext)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

from openpyxl import load_workbook
from openpyxl.drawing.image import Image

def save_to_excel(file_path, id, **kwargs):
    # Load the existing Excel file or create a new one
    try:
        wb = load_workbook(file_path)
        ws = wb.active
    except FileNotFoundError:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        # Create headers if file doesn't exist
        ws.append(list(kwargs.keys()))  

    # Determine the next available row
    next_row = id + 1 #ws.max_row + 1  

    # Generate QR Code before inserting data
    qr_code_path = generate_qr_code(kwargs)

    # Insert data into the correct columns
    print(list(kwargs.items())) 
    for col_num, (key, value) in enumerate(kwargs.items(), start=1):
        if key not in ["GlobeId", "TextColumn", "Barcode", "QR Code"]:   #!= "Barcode":  # Barcode needs to be inserted as an image
            print(f"Key = {key} col = {col_num} and value = {value}")
            ws.cell(row=next_row, column=col_num, value=value)

    # Insert barcode into the "Barcode" column (if exists)
    if "Barcode" in kwargs and kwargs["Barcode"]:
        barcode_img = kwargs["Barcode"]  
        img = Image(barcode_img)
        barcode_col = list(kwargs.keys()).index("Barcode") + 1   # Find the column index for "Barcode"
        ws.add_image(img, ws.cell(row=next_row, column=barcode_col).coordinate)

        # Insert QR Code image
    if "QR Code" in kwargs:
        img = Image(qr_code_path)
        qr_col = list(kwargs.keys()).index("QR Code") + 1
        ws.add_image(img, ws.cell(row=next_row, column=qr_col).coordinate)

    # Save the workbook
    wb.save(file_path)
    print(f"Data saved to {file_path} successfully!")
    messagebox.showinfo("Success", "Data saved successfully to Excel!")

def draw_text(barcode_path, text_label):
    barcode_image = PILImage.open(barcode_path)                # Open the barcode image and get dimensions
    img_width, img_height = barcode_image.size
    new_height = img_height + 40                            # Create a new image with extra space ABOVE the barcode
    new_image = PILImage.new("RGB", (img_width, new_height), "white")
    draw = ImageDraw.Draw(new_image)
    bbox = draw.textbbox((0, 0), text_label, font=font)     # Get text bounding box
    text_width = bbox[2] - bbox[0]                          # Calculate width
    text_height = bbox[3] - bbox[1] 
    text_x = img_width - (text_width + 35)
    text_y = 20                                             # Place text at the top
    draw.text((text_x, text_y), text_label, fill="black", font=font)
    new_image.paste(barcode_image, (0, 45))                 # Paste barcode BELOW the text
    new_image.save(barcode_path)
  
def generate_barcode(data, temp_path="temp_barcode"):
    data = str(data) 
    barcode_class = barcode.get_barcode_class("code128")
    barcode_obj = barcode_class(data, writer=ImageWriter())
    options = {                                         # Define barcode settings
            "module_height": 7,                             # ⬅ Reduce barcode height (default: ~50)
            "font_size": 10,                                # Adjust text size below barcode
            "font_path": custom_font_path                   #"C:/Users/RoopaHegde/Downloads/RobotoMono-Regular.ttf",
        }
    #img_bytes = BytesIO()
    #barcode_obj.write(img_bytes, options)  # Save barcode to memory
    #img_bytes.seek(0)  # Reset file pointer
    #return img_bytes

    barcode_obj.save(temp_path, options)
    return temp_path

def generate_qr_code(row_data, qr_path="temp_qr.png"):
    """
    Generates a QR Code containing row data (except Barcode) and saves it as an image.
    
    :param row_data: Dictionary of row values (excluding Barcode)
    :param qr_path: File path to save the QR code
    :return: Path of the saved QR code image
    """
    # Create a copy of row_data to prevent modifying the original dictionary
    qr_data = {key: value for key, value in row_data.items() if key != "Barcode" and value}

    # Convert row data to a readable string
    qr_content = ";".join([f"{key} = {value}" for key, value in qr_data.items()]) #row_data.items() if value])
    print("QR Code Content:\n", qr_content)
    

    # Generate QR Code with error correction and force UTF-8 encoding
    qr = qrcode.QRCode(
        version=5,  # Controls the size of the QR Code (1 is the smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Allows for small errors in reading
        box_size=10,  # Size of each box in the QR Code
        border=4,  # Border around the QR Code
    )
    qr.add_data(qr_content)
    qr.make(fit=True)

    # Create an image from the QR Code
    img = qr.make_image(fill="black", back_color="white")

    # Save QR Code
    img.save(qr_path)

    return qr_path
