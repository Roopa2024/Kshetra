from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import pandas as pd
from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
import io, os, sys
from io import BytesIO
from pathlib import Path
from PIL import Image  
import pdf_data, configparser, canvas_update
from datetime import datetime
import tkinter.messagebox as messagebox
from num2words import num2words
import locale

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
font_name = config.get('FontSettings', 'font_name')
copy_font_name = config.get('FontSettings', 'copy_font_name')
#font_name_bold = config.get('FontSettings', 'font_name_bold')
font_size = config.getint('FontSettings', 'font_size')
width, height = A4
height = height - 56
x_offset = 90

# Converting date to the desired format
def get_date_format(c, value):
    date_obj = datetime.strptime(value, "%d/%m/%Y") 
    formatted_date = date_obj.strftime("%d%b%Y").upper()
    c.setFont(font_name, font_size) 
    return formatted_date

# Function to draw receipt date inside the boxes
def draw_receipt_date(c, i, value):
    formatted_date = get_date_format(c, value)
    c.setFont(font_name, font_size) 
    x, y = (435, height - 10)
    if i == 0:
        c.drawString(x, y, "    ".join(formatted_date) )
    elif i == 1:
        c.drawString(x, height - 290, "    ".join(formatted_date) )
    elif i == 2:
        c.drawString(x, height - 570, "    ".join(formatted_date) )
    #c.setFont(font_name, font_size) 

def print_amount(c, locale_value, x1, x2, y1, y2, in_words, line_width):
    if locale_value != "":
            c.drawString(x1, y1, f"{locale_value} /-")
            canvas_update.wrap_text(c, f"{in_words} ONLY", x2, y2, line_width, font_name, font_size, 0)

# Function to draw amount in numbers and amount in words
def draw_voucher(c, i, value, pay_to, purpose, dest_excel_path, pdf_path):
    c.setFont(font_name, font_size)
    locale.setlocale(locale.LC_ALL, 'en_IN')
    if value:
        locale_value = locale.format_string("%d", int(value), grouping=True)
    else:
        locale_value = ""
    x1 = x_offset - 15
    x2 = x_offset + 70
    x3 = x_offset + 20
    line_width = 420
    in_words = canvas_update.convert_to_words(value)
    if i == 0:
        print_amount(c, locale_value, x1, x2, height - 190, height - 70, in_words, line_width)
        canvas_update.wrap_text(c, f"{pay_to}", x3, height - 30, line_width, font_name, font_size, 0)
        canvas_update.wrap_text(c, f"{purpose}", x3, height - 110, line_width, font_name, font_size, 0)
    elif i == 1:
        print_amount(c, locale_value, x1, x2, height - 470, height - 350, in_words, line_width)
        canvas_update.wrap_text(c, f"{pay_to}", x3, height - 310, line_width, font_name, font_size, 0)
        canvas_update.wrap_text(c, f"{purpose}", x3, height - 390, line_width, font_name, font_size, 0)
    elif i == 2:
        print_amount(c, locale_value, x1, x2, height - 750, height - 632, in_words, line_width)
        canvas_update.wrap_text(c, f"{pay_to}", x3, height - 590, line_width, font_name, font_size, 0)
        canvas_update.wrap_text(c, f"{purpose}", x3, height - 672, line_width, font_name, font_size, 0)
    
    draw_code(c, dest_excel_path)

def draw_code(c, dest_excel_path):
    wb = load_workbook(dest_excel_path)
    ws = wb.active

    # Get header row to find correct columns
    header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    col_map = {name.strip().lower(): idx for idx, name in enumerate(header_row) if name is not None}

    # Ensure columns exist
    barcode_col_idx = header_row.index("Barcode")
    qrcode_col_idx = header_row.index("QR Code")
    if barcode_col_idx is None or qrcode_col_idx is None:
        raise ValueError("Required columns 'barcode' and/or 'QRCode' not found.")

    barcode_col_letter = get_column_letter(barcode_col_idx + 1)
    qrcode_col_letter = get_column_letter(qrcode_col_idx + 1)

    # Separate images by column and row
    barcode_images = {}
    qrcode_images = {}

    for img in ws._images:
        if hasattr(img.anchor, "_from"):
            col = img.anchor._from.col
            row = img.anchor._from.row
            col_letter = get_column_letter(col + 1)

            if col_letter == barcode_col_letter:
                barcode_images[row] = img
            elif col_letter == qrcode_col_letter:
                qrcode_images[row] = img

    # Find all rows where at least a barcode or QR code exists
    all_rows = sorted(set(barcode_images.keys()) | set(qrcode_images.keys()))
    last_rows = all_rows[-3:]  # Get last 3 rows with image(s)
    x_barcode, x_qrcode = 430, 379 #350
    if 'SGPM_DN' in dest_excel_path or 'SPK_DPS' in dest_excel_path:
        x_qrcode = 350
    elif 'SGPT' in dest_excel_path:
        x_qrcode = 365
    start_y_barcode, start_y_qrcode, y_offset = height+5, height-15, 282
    
    # Draw images row-wise
    for i, row in enumerate(last_rows):
        y_barcode = start_y_barcode - i * y_offset
        y_qrcode = start_y_qrcode - i * y_offset

        # Barcode
        if row in barcode_images:
            img_data = barcode_images[row]._data()
            pil_img = Image.open(BytesIO(img_data))
            pil_img.save(f"temp_barcode_{row}.png")
            c.drawImage(f"temp_barcode_{row}.png", x_barcode, y_barcode, width=150, height=40)
            os.remove(f"temp_barcode_{row}.png")
        # QRCode
        if row in qrcode_images:
            img_data = qrcode_images[row]._data()
            pil_img = Image.open(BytesIO(img_data))
            pil_img.save(f"temp_qrcode_{row}.png")
            c.drawImage(f"temp_qrcode_{row}.png", x_qrcode, y_qrcode, width=55, height=65) #width=70, height=70)
            os.remove(f"temp_qrcode_{row}.png")
