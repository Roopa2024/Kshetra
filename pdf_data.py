import tkinter as tk
import os, configparser, io, qrcode, sys
import pandas as pd
import shutil
import canvas_update, canvas_update_voucher, excel_data
import tkinter.messagebox as messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import UI_support

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
copy_font_name = config.get('FontSettings', 'copy_font_name')
#font_name_bold = config.get('FontSettings', 'font_name_bold')
font_size = config.getint('FontSettings', 'font_size')
x_position = config.getint('FontSettings', 'y_position')
y_position = config.getint('FontSettings', 'y_position')
printer_name = config.get('printer', 'printer')

x_top_contributor_name = config.getint('top_dimensions', 'x_contributor_name')
y_top_contributor_name = config.get('top_dimensions', 'y_contributor_name')
x_bottom_contributor_name = config.getint('bottom_dimensions', 'x_contributor_name')
y_bottom_contributor_name = config.get('bottom_dimensions', 'y_contributor_name')

x_top_address = config.getint('top_dimensions', 'x_address')
y_top_address = config.get('top_dimensions', 'y_address')
x_bottom_address = config.getint('bottom_dimensions', 'x_address')
y_bottom_address = config.get('bottom_dimensions', 'y_address')

x_top_pan = config.getint('top_dimensions', 'x_pan')
y_top_pan = config.get('top_dimensions', 'y_pan')
x_bottom_pan = config.getint('bottom_dimensions', 'x_pan')
y_bottom_pan = config.get('bottom_dimensions', 'y_pan')
x_bottom_pan_HP = config.getint('HP_dimensions', 'x_pan')
y_bottom_pan_HP = config.get('HP_dimensions', 'y_pan')

x_top_contributor_type = config.getint('top_dimensions', 'x_contributor_type')
y_top_contributor_type = config.get('top_dimensions', 'y_contributor_type')
x_bottom_contributor_type = config.getint('bottom_dimensions', 'x_contributor_type')
y_bottom_contributor_type = config.get('bottom_dimensions', 'y_contributor_type')
x_top_contributor_intent = config.getint('top_dimensions', 'x_contributor_intent')
y_top_contributor_intent = config.get('top_dimensions', 'y_contributor_intent')
x_bottom_contributor_intent = config.getint('bottom_dimensions', 'x_contributor_intent')
y_bottom_contributor_intent = config.get('bottom_dimensions', 'y_contributor_intent')

x_bank_name = config.getint('top_dimensions', 'x_bank_name')
y_bank_name = config.get('top_dimensions', 'y_bank_name')
x_branch_name = config.getint('top_dimensions', 'x_branch_name')
y_branch_name = config.get('top_dimensions', 'y_branch_name')

y_top_print_date = config.get('top_dimensions', 'y_print_date')
y_bottom_print_date = config.getint('bottom_dimensions', 'y_print_date')

x_authoriser = config.getint('top_dimensions', 'x_receipt_date')
x_top_qrcode = config.getint('top_dimensions', 'x_qrcode')
y_top_qrcode = config.get('top_dimensions', 'y_qrcode')
x_bottom_qrcode = config.getint('bottom_dimensions', 'x_qrcode')
y_bottom_qrcode = config.get('bottom_dimensions', 'y_qrcode')
qrcode_size = config.getint('top_dimensions', 'qrcode_size')

x_barcode = config.getint('top_dimensions', 'x_barcode')
y_barcode = config.getint('top_dimensions', 'y_barcode')
y_top_barcode_receipt = config.getint('top_dimensions', 'y_barcode_receipt')
y_bottom_barcode_receipt = config.getint('bottom_dimensions', 'y_barcode_receipt')
barcode_width = config.getint('top_dimensions', 'barcode_width')
barcode_height = config.getint('top_dimensions', 'barcode_height')

# Function to get the pdf directory path for EXE
def get_pdf_directory():
    if hasattr(sys, '_MEIPASS'):    # Running as a bundled .exe
        temp_dir = sys._MEIPASS     # Temporary folder where files are extracted
        pdf_dir = os.path.join(temp_dir, 'pdfs')  # Target pdfs folder in temp dir
    else:
        pdf_dir = 'pdfs'            # Default pdfs directory in current working directory
    return pdf_dir

# Function to get base path for EXE
def get_base_path():
    # Get the base path (different for script vs. executable)
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller .exe
        base_path = sys._MEIPASS  
    else:
        base_path = os.path.dirname(__file__)  
    return base_path

# Function to create pdf contents
def merge_pdf(entity, new_pdf, pdf_name):
    base_path = get_base_path()
    image_path = os.path.join(base_path, "Images", entity)
    existing_pdf = PdfReader(image_path) 
    #print(f"Merge with {image_path}")
    writer = PdfWriter()
    for page in existing_pdf.pages:
        if len(new_pdf.pages) == 0:                             # Merge the new PDF with the old PDF (the original form)
            print("Error: The PDF has no pages!")
        else:
            page.merge_page(new_pdf.pages[0])
        writer.add_page(page)

    pdf_dir = os.path.dirname(pdf_name)  # Extract the folder path
    os.makedirs(pdf_dir, exist_ok=True)
    with open(pdf_name, "wb") as f:                             # Save the final filled PDF
        writer.write(f) 

#Function to generate duplicate pdfs for Accountant and Office copy
def generate_duplicates(pdf_path, entity):
    pdf_name = os.path.basename(pdf_path)
    entity_name = os.path.splitext(entity)[0]
    duplicate_pdf_path_acct = os.path.join("Accountant_copy", entity_name, pdf_name)
    pdf_dir_acct = os.path.dirname(duplicate_pdf_path_acct)  # Extract the folder path
    os.makedirs(pdf_dir_acct, exist_ok=True)
    shutil.copy(pdf_path, duplicate_pdf_path_acct)

# Function to generate pdf content based on the inputs given in the APP UI
def create_pdf_from_kwargs(kwargs, pdf_path, entity, with_bg, top_text, bottom_text, pdf):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    height = height - 56
    
    #x_offset = 90                                               # Set starting position for text
    receipt = int(entity in ('SGPM_DN.pdf', 'SPK_DPS.pdf'))
    
    c.setFont(font_name, font_size)     
    for key, value in kwargs.items():
        if key not in ["Barcode", "QR Code"] and value:         # Exclude image fields
            match key:
                case 'Receipt Date':
                    canvas_update.draw_receipt_date(c, value, receipt, pdf)
                case 'Contributor Name':
                    if receipt: c.drawString(x_top_contributor_name, eval(y_top_contributor_name), f"{value}")          
                    c.drawString(x_bottom_contributor_name, eval(y_bottom_contributor_name), f"{value}")       
                case 'Address':
                    if receipt: canvas_update.wrap_text(c, f"{value}", x_top_address, eval(y_top_address), 500, font_name, font_size, receipt)
                    canvas_update.wrap_text(c, f"{value}", x_bottom_address, eval(y_bottom_address), 500, font_name, font_size, 1)
                case 'PAN':
                    c.setFont(font_name, font_size) 
                    if pdf:
                        x = x_bottom_pan
                        y = eval(y_bottom_pan)
                    else:
                        x = x_bottom_pan_HP
                        y = eval(y_bottom_pan_HP)
                    if receipt: c.drawString(x_top_pan, eval(y_top_pan), "    ".join(str(value).upper()))
                    c.drawString(x, y, "    ".join(str(value).upper()))
                    #c.setFont(font_name, font_size) 
                case 'Contributor Type':
                    if receipt: c.drawString(x_top_contributor_type , eval(y_top_contributor_type), f"{value}")
                    c.drawString(x_bottom_contributor_type, eval(y_bottom_contributor_type), f"{value}")
                case 'Contributor Intent':
                    if receipt: c.drawString(x_top_contributor_intent, eval(y_top_contributor_intent), f"{value}")
                    c.drawString(x_bottom_contributor_intent, eval(y_bottom_contributor_intent), f"{value}")
                case 'Bank Date':
                    canvas_update.draw_bank_date(c, value, receipt)
                case 'UTR No.':
                    canvas_update.draw_utrn(c, value, receipt, pdf)
                case 'Amount':
                    canvas_update.draw_amount(c, value, receipt, pdf)
                case 'Payment Mode':
                    canvas_update.draw_payment_mode_tick(c, value, receipt)
                case 'Cheque Date':
                    canvas_update.draw_cheque_date(c, value, receipt)
                case 'Cheque No.':
                    canvas_update.draw_cheque_no(c, value, receipt)
                case 'IFSC':
                    canvas_update.draw_ifsc(c, value, receipt)
                case 'Account No.':
                    canvas_update.draw_acct_no(c, value, receipt)
                case 'Bank Name':  
                    c.setFont(font_name, font_size)
                    if not receipt: c.drawString(x_bank_name, eval(y_bank_name), f"{value}")
                case 'Branch Name':  
                    if not receipt: c.drawString(x_branch_name, eval(y_branch_name), f"{value}")
                case 'Print Date':
                    c.setFont(copy_font_name, 8)  # Set font and size
                    c.setFillColorRGB(0.5, 0.5, 0.5) 
                    text_width = c.stringWidth(value, copy_font_name, 8)
                    canvas_update.draw_copy_type(c, eval(y_top_print_date) - text_width, value)
                    canvas_update.draw_copy_type(c, y_bottom_print_date, value)
                    c.setFont(font_name, font_size)
                    #c.drawString(475, 5, f"{value}")
                case 'Authoriser':
                    if receipt:
                        c.drawString(x_authoriser, y_top_barcode_receipt, f"{value}")
                    c.drawString(x_authoriser, y_bottom_barcode_receipt, f"{value}")

    # Insert QR Code
    if kwargs.get("QR Code"):
        try:
            qr_image = ImageReader(kwargs["QR Code"])
            if receipt: c.drawImage(qr_image, x_top_qrcode, eval(y_top_qrcode), width=qrcode_size, height=qrcode_size)
            c.drawImage(qr_image, x_bottom_qrcode, eval(y_bottom_qrcode), width=qrcode_size, height=qrcode_size)
        except Exception as e:
            print("Error adding QR Code:", e)

    # Insert Barcode
    if kwargs.get("Barcode"):
        try:
            barcode_image = ImageReader(kwargs["Barcode"])
            name = entity.split(".")[0]
            c.drawImage(barcode_image, x_barcode, y_top_barcode_receipt, width=barcode_width, height=barcode_height)
            c.drawImage(barcode_image, x_barcode, y_bottom_barcode_receipt, width=barcode_width, height=barcode_height)
        except Exception as e:
            print("Error adding Barcode:", e)
   
    canvas_update.create_vertical_watermark(c, top_text, bottom_text)

    # Save PDF
    c.showPage()
    c.save()

    packet.seek(0)
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    if not entity == 0:     
        pdf_name = os.path.basename(pdf_path)
        entity_name = os.path.splitext(entity)[0]  
        if top_text == bottom_text:
            duplicate_pdf_path = os.path.join("Office_copy", entity_name, pdf_name)
            merge_pdf(entity, new_pdf, duplicate_pdf_path)
        #print(f"Entity is {entity}")

        if with_bg == 0: 
            if top_text != bottom_text:                                               #print without bg
                writer = PdfWriter()
                for page in new_pdf.pages:
                    writer.add_page(page)
                
                if pdf:
                    pdf_path = os.path.join("Accountant_copy", entity_name, pdf_name)

                with open(str(pdf_path), "wb") as f:                     # Save the final filled PDF
                    writer.write(f)
                
                if not pdf:
                    absolute_path = os.path.abspath(pdf_path)
                    print(f"Attempting to open: {absolute_path}")

                    if os.path.exists(absolute_path):
                        os.startfile(absolute_path)
                    else:
                        print("File not found on disk!")
                duplicate_pdf_path_acct = os.path.join("Accountant_copy", entity_name, pdf_name)
                merge_pdf(entity, new_pdf, duplicate_pdf_path_acct)
        elif with_bg == 1:                                               # print with background
            if top_text != bottom_text:
                merge_pdf(entity, new_pdf, pdf_path)
                generate_duplicates(pdf_path, entity)
                absolute_path = os.path.abspath(pdf_path)
                print(f"Attempting to open: {absolute_path}")

                if os.path.exists(absolute_path):
                    os.startfile(absolute_path)
                else:
                    print("File not found on disk!")
    print(f"PDF saved: {pdf_path}")

def create_pdf_from_kwargs_voucher(kwargs, v_entries, pdf_path, entity, with_bg, dest_excel_path):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    height = height - 56
    cheque_date, cheque_no_val, cheque_IFSC, cheque_AC_no, eft_date, utrn_val = '', '','','','',''
    user = UI_support.get_user()

    c.setFont(font_name, font_size)  
    print_date = kwargs.get('Print Date', '')
    user = kwargs.get('Authoriser', '')

    for i, voucher in enumerate(v_entries):
        voucher_date = voucher['date'].get()
        pay_to = voucher['pay_to'].get()
        amount = voucher['amount'].get()
        pan = voucher['pan'].get()
        addr = voucher['addr'].get()
        pur_code = voucher['pur_code'].get()
        pur_head = voucher['pur_head'].get()
        pur_cat = voucher['pur_cat'].get()
        exp_type = voucher['exp_type'].get()
        mode = voucher['payment_mode'].get()
        
        canvas_update_voucher.draw_voucher_date(c, i, voucher_date)

        if mode == "Cheque":
            cheque_date, cheque_no_val, cheque_IFSC, cheque_AC_no = UI_support.get_cheque_data(voucher)
        elif mode == "EFT":
            eft_date, utrn_val = UI_support.get_eft_data(voucher)
        
        canvas_update_voucher.draw_voucher(c, i, amount, pay_to, pan, addr, pur_code, pur_head, pur_cat, exp_type, mode, cheque_date, cheque_no_val, cheque_IFSC, cheque_AC_no, eft_date, utrn_val, dest_excel_path, pdf_path, user, print_date)

    # Save PDF
    c.showPage()
    c.save()

    packet.seek(0)
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    if not entity == 0:     
        pdf_name = os.path.basename(pdf_path)
        entity_name = os.path.splitext(entity)[0]  
        if with_bg == 0:                                            #print without bg
            writer = PdfWriter()
            for page in new_pdf.pages:
                writer.add_page(page)
            with open(str(pdf_path), "wb") as f:                     # Save the final filled PDF
                writer.write(f)
            absolute_path = os.path.abspath(pdf_path)
            print(f"Attempting to open: {absolute_path}")

            if os.path.exists(absolute_path):
                os.startfile(absolute_path)
            else:
                print("File not found on disk!")
            duplicate_pdf_path_acct = os.path.join("Accountant_copy", entity_name, pdf_name)
            merge_pdf(entity, new_pdf, duplicate_pdf_path_acct)
        elif with_bg == 1:                                               # print without background
            merge_pdf(entity, new_pdf, pdf_path)
            generate_duplicates(pdf_path, entity)
            absolute_path = os.path.abspath(pdf_path)
            print(f"Attempting to open: {absolute_path}")

            if os.path.exists(absolute_path):
                os.startfile(absolute_path)
            else:
                print("File not found on disk!")
    print(f"PDF saved: {pdf_path}")
