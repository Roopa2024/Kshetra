import os, configparser, io, qrcode, sys
import pandas as pd
import openpyxl

import canvas_update, excel_data
import tkinter.messagebox as messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
xcl_file = config.get('Filenames', 'xcl_file')
xcl_sheet = config.get('Filenames', 'xcl_sheet')
pdf_heading = config['Heading']['pdf_heading']
pdf_headings = pdf_heading.split(',')
copy_type = config['Heading']['copy_type']
copy_types = copy_type.split(',')
font_name = config.get('FontSettings', 'font_name')
font_name_bold = config.get('FontSettings', 'font_name_bold')
font_size = config.getint('FontSettings', 'font_size')
x_position = config.getint('FontSettings', 'y_position')
y_position = config.getint('FontSettings', 'y_position')

def get_pdf_directory():
    if hasattr(sys, '_MEIPASS'):    # Running as a bundled .exe
        temp_dir = sys._MEIPASS     # Temporary folder where files are extracted
        pdf_dir = os.path.join(temp_dir, 'pdfs')  # Target pdfs folder in temp dir
    else:
        pdf_dir = 'pdfs'            # Default pdfs directory in current working directory
    return pdf_dir

def get_base_path():
    # Get the base path (different for script vs. executable)
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller .exe
        base_path = sys._MEIPASS  
    else:
        base_path = os.path.dirname(__file__)  
    return base_path

def merge_pdf(entity, new_pdf, pdf_name):
    base_path = get_base_path()

    image_path = os.path.join(base_path, "Images", entity)
    existing_pdf = PdfReader(image_path) #f"Images/{folder_name}.pdf")
    print(f"Merge with {existing_pdf}")
    writer = PdfWriter()
    for page in existing_pdf.pages:
    # Merge the new PDF with the old PDF (the original form)
        if len(new_pdf.pages) == 0:
            print("Error: The PDF has no pages!")
        else:
            page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
    with open(pdf_name, "wb") as f: #output_file:      # Save the final filled PDF
        writer.write(f) #output_file)

def create_pdf_from_kwargs(kwargs, pdf_path, entity, with_bg):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    print(f"BG and entity = {with_bg} and {entity}")
    height = height - 56
    x_offset = 90                                               # Set starting position for text
    receipt = int(entity in ('SGPM_DN.pdf', 'SPK_DPS.pdf'))

    # Draw data (excluding images)
    c.setFont(font_name, font_size)     
    for key, value in kwargs.items():
        if key not in ["Barcode", "QR Code"] and value:  # Exclude image fields
            match key:
                case 'Receipt Date':
                    canvas_update.draw_receipt_date(c, value, receipt)
                case 'Contributor Name':
                    if receipt: c.drawString(x_offset, height - 105, f"{value}")          
                    c.drawString(x_offset, height - 495, f"{value}")       
                case 'Address':
                    if receipt: canvas_update.wrap_text(c, f"{value}", x_offset, height - 115, 455, font_name, font_size)
                    canvas_update.wrap_text(c, f"{value}", x_offset, height - 505, 455, font_name, font_size)
                case 'PAN':
                    c.setFont(font_name, font_size-1) 
                    if receipt: c.drawString(402, height - 148, "    ".join(str(value).upper()))
                    c.drawString(402, height - 538, "    ".join(str(value).upper()))
                    c.setFont(font_name, font_size) 
                case 'Contribution Type':
                    if receipt: c.drawString(x_offset + 70 , height - 170, f"{value}")
                    c.drawString(x_offset + 70, height - 560, f"{value}")
                case 'Contribution Intent':
                    if receipt: c.drawString(x_offset + 70, height - 187, f"{value}")
                    c.drawString(x_offset + 70, height - 575, f"{value}")
                case 'Bank Date':
                    canvas_update.draw_bank_date(c, value, receipt)
                case 'UTRN':
                    canvas_update.draw_utrn(c, value, receipt)
                case 'Amount':
                    canvas_update.draw_amount(c, value, receipt)
                case 'Payment Mode':
                    canvas_update.draw_payment_mode_tick(c, value, receipt)
                case 'Cheque Date':
                    canvas_update.draw_cheque_date(c, value, receipt)
                case 'Cheque No.':
                    canvas_update.draw_cheque_no(c, value, receipt)
                case 'IFSC Code':
                    canvas_update.draw_ifsc(c, value, receipt)
                case 'A/C No.':
                    canvas_update.draw_acct_no(c, value, receipt)
                case 'Bank Name':  
                    if not receipt: c.drawString(x_offset, height - 215, f"{value}")
                case 'Branch Name':  
                    if not receipt: c.drawString(x_offset + 180, height - 215, f"{value}")

    # Insert QR Code
    if kwargs.get("QR Code"):
        print("QR Code found")
        try:
            qr_image = ImageReader(kwargs["QR Code"])
            if receipt: c.drawImage(qr_image, 480, height - 65, width=60, height=60)
            c.drawImage(qr_image, 480, height - 457, width=60, height=60)
        except Exception as e:
            print("Error adding QR Code:", e)

    # Insert Barcode
    if kwargs.get("Barcode"):
        try:
            barcode_image = ImageReader(kwargs["Barcode"])
            name = entity.split(".")[0]
            c.drawImage(barcode_image, 220, 395, width=150, height=50)
            c.drawImage(barcode_image, 220, 5, width=150, height=50)
        except Exception as e:
            print("Error adding Barcode:", e)
   
    canvas_update.create_vertical_watermark(c, copy_types[1], copy_types[2]) #, watermark_pdf)

    # Save PDF
    c.showPage()
    c.save()

    packet.seek(0)
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    if not entity == 0:       
        print(f"Entity is {entity}")
        if with_bg == 0:
            writer = PdfWriter()
            for page in new_pdf.pages:
                writer.add_page(page)
            with open(str(pdf_path), "wb") as f:                     # Save the final filled PDF
                writer.write(f)
        elif with_bg == 1:
            merge_pdf(entity, new_pdf, pdf_path)
    print(f"PDF saved: {pdf_path}")
