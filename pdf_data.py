import os, configparser, io, qrcode, sys
from datetime import datetime
import pandas as pd
import openpyxl
from num2words import num2words
import locale

#from openpyxl import load_workbook, Workbook
import canvas_update, excel_data
import tkinter.messagebox as messagebox
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

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

def wrap_text(c, text, x, y, width, font_name, font_size):
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = font_name
    style.fontSize = font_size
    style.leading = font_size + 7
    print (f"WRAP text {text}")
    if "&nbsp;&nbsp;&nbsp;&nbsp;" not in text:
        style.leading = font_size + 2

    paragraph = Paragraph(text, style)  # Create a Paragraph object which wraps the text
    #paragraph.wrapOn(c, width, 500)     # 500 is the height of the text box
    _, text_height = paragraph.wrap(width, 550)  # Get actual text height
    paragraph.drawOn(c, x, y - text_height)     

def create_vertical_watermark(c, top_text, bottom_text): #, watermark_pdf):
    """Create a watermark PDF with vertical text on the right top corner."""
    width, height = A4  # A4 size in points (595x842)
    
    #c = canvas.Canvas(watermark_pdf, pagesize=A4)
    c.setFont("Helvetica", 8)  # Set font and size
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Darker gray
    text_width = c.stringWidth(top_text, "Helvetica", 8) 

    c.saveState()
    c.translate(width - 15, (height - 220) - text_width)  # Move to top half center
    #c.translate(width - 15, (height - 235) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, top_text)  # Draw the text
    c.restoreState()

    # Position 2: Center of the bottom half
    c.saveState()
    c.translate(width - 15, (height - 610) - text_width)  # Move to bottom half center
    #c.translate(width - 15, (height - 620) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, bottom_text)  # Draw the text
    c.restoreState()

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

def generate_pdf():
    bar_dir = excel_data.get_bar_directory(pdf_headings[0]) 
    print(f"generating pdf for each row {bar_dir}")
    for file in os.listdir(bar_dir):
        if file.lower().endswith(".png"):  # Check for PNG extension
            #print(os.path.join(bar_dir, file))
            canvas_update.create_filled_pdf(bar_dir, file, 1) #with_bg)
    #canvas_update.create_filled_pdf(bar_dir, 1)
    print(f"PDFs generated successfully at {bar_dir}")
    messagebox.showinfo("Success", f"PDFs generated successfully at {bar_dir}")

# Custom function to convert number to INR words (Indian Rupees in English)
def convert_to_words(amount):
    try:
        amount = int(amount)
    except ValueError:
        messagebox.showerror("Amount Error", "Please enter a valid amount.")
        return
    # Split the amount into whole and fractional parts
    whole_number = int(amount)
    fraction_part = round((amount - whole_number) * 100)  # Getting the fraction part as Paise
    # Convert whole number into words in English
    whole_in_words = num2words(whole_number, lang='en_IN')
    # Capitalize the first letter of each word
    capitalized_number = whole_in_words.upper()
    # Convert fraction part (Paise) into words if it's non-zero
    if fraction_part > 0:
        fraction_in_words = num2words(fraction_part, lang='en_IN')
        capitalized_fractions = fraction_in_words.upper()
        result = f"{capitalized_number} RUPEES {capitalized_fractions} PAISE"
    else:
        result = f"{capitalized_number} RUPEES"

    return result

def get_date_format(c, value):
    date_obj = datetime.strptime(value, "%m/%d/%y") 
    formatted_date = date_obj.strftime("%d%b%Y").upper()
    c.setFont(font_name_bold, font_size) 
    return formatted_date

def create_pdf_from_kwargs(kwargs, pdf_path, entity, with_bg):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    print(f"BG and entity = {with_bg} and {entity}")
    height = height - 56

    if entity in ('SGPM_DN.pdf', 'SPK_DPS.pdf'):
        receipt = 1
    else:
        receipt = 0
    print(f"Receipt = {receipt}")

    # Set starting position for text
    x_offset = 90
    y_offset = height - 110
    line_height = 20

    # Draw title
    c.setFont("Helvetica-Bold", 14)
    #c.drawString(x_offset, y_offset, "Contribution Receipt")
    #y_offset -= 40

    # Draw data (excluding images)
    c.setFont(font_name, font_size)     #"Helvetica", 12)
    for key, value in kwargs.items():
        if key not in ["Barcode", "QR Code"] and value:  # Exclude image fields
            match key:
                case 'Receipt Date':
                    formatted_date = get_date_format(c, value)
                    c.setFont(font_name_bold, font_size-1) 
                    if receipt:
                        x = 433
                        y = height - 82
                    else:
                        x = 420
                        y = height - 66
                    c.drawString(x, y, "    ".join(formatted_date) )
                    c.drawString(433, height - 470, "    ".join(formatted_date) )
                    c.setFont(font_name, font_size) 
                case 'Contributor Name':
                    if receipt:
                        c.drawString(x_offset, height - 105, f"{value}")          
                    c.drawString(x_offset, height - 495, f"{value}")       
                case 'Address':
                    if receipt:
                        wrap_text(c, f"{value}", x_offset, height - 115, 455, font_name, font_size)
                    wrap_text(c, f"{value}", x_offset, height - 505, 455, font_name, font_size)
                case 'PAN':
                    c.setFont(font_name, font_size-1) 
                    if receipt:
                        c.drawString(402, height - 148, "    ".join(str(value).upper()))
                    c.drawString(402, height - 538, "    ".join(str(value).upper()))
                    c.setFont(font_name, font_size) 
                case 'Contribution Type':
                    if receipt:
                        c.drawString(x_offset + 70 , height - 170, f"{value}")
                    c.drawString(x_offset + 70, height - 560, f"{value}")
                case 'Contribution Intent':
                    if receipt:
                        c.drawString(x_offset + 70, height - 187, f"{value}")
                    c.drawString(x_offset + 70, height - 575, f"{value}")
                case 'Bank Date':
                    formatted_date = get_date_format(c, value)
                    c.setFont(font_name_bold, font_size-1) 
                    if receipt:
                        c.drawString(422, height - 220, "    ".join(formatted_date))
                    else:
                        c.drawString(x_offset + 330, height - 170, "    ".join(formatted_date))
                    c.drawString(422, height - 608, "    ".join(formatted_date))
                    c.setFont(font_name, font_size) 
                case 'UTRN':
                    if receipt:
                        wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), 422, height - 227, 140, font_name, font_size-1)
                    else:
                        c.setFont(font_name, font_size-1) 
                        c.drawString(x_offset + 75, height - 190, "    ".join(value))
                        c.setFont(font_name, font_size) 
                    wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), 422, height - 617, 140, font_name, font_size-1)
                case 'Amount':
                    locale.setlocale(locale.LC_ALL, 'en_IN')
                    locale_value = locale.format_string("%d", int(value), grouping=True)
                    if receipt:
                        x = x_offset - 30
                        y = height - 310
                    else:
                        x = x_offset 
                        y = height - 150
                    c.drawString(x, y, f"{locale_value}")
                    c.drawString(x_offset - 30, height - 700,f"{locale_value}")
                    in_words = convert_to_words(value)
                    c.setFont(font_name, font_size-2)
                    if receipt:
                        wrap_text(c, f"{in_words}", x_offset + 70, height - 294, 380, font_name, font_size-2)
                    else:
                        c.setFont(font_name, font_size-4) 
                        c.drawString(x_offset + 120, height - 150, f"{in_words}")
                        c.setFont(font_name, font_size-2) 
                    wrap_text(c, f"{in_words}", x_offset + 70, height - 684, 380, font_name, font_size-2)
                    c.setFont(font_name, font_size)
                case 'Payment Mode':
                    y = height - 210
                    y_intent = height - 170
                    y_bottom = height - 600
                    if value == 'Online':
                        if receipt:
                            c.drawString(343, y, '✔')
                        else:
                            c.drawString(x_offset + 190, y_intent, '✔')
                        c.drawString(343, y_bottom, '✔')
                    elif value == 'Cheque':
                        if receipt:
                            c.drawString(x_offset-20, y, '✔')
                        else:
                            c.drawString(x_offset + 110, y_intent, '✔')
                        c.drawString(x_offset-25, y_bottom, '✔')
                    elif value == 'Cash':
                        if receipt:
                            c.drawString(x_offset-60, y, '✔')
                        else:
                            c.drawString(x_offset + 40, y_intent, '✔')
                        c.drawString(x_offset-60, y_bottom, '✔')
                case 'Cheque Date':
                    if value != '': 
                        formatted_date = get_date_format(c, value)
                        c.setFont(font_name_bold, font_size-1)
                        if receipt:
                            c.drawString(x_offset + 45, height - 215, "    ".join(formatted_date))
                        else:
                            c.drawString(x_offset + 330, height - 170, "    ".join(formatted_date))
                        c.drawString(x_offset + 45, height - 604, "    ".join(formatted_date))
                        c.setFont(font_name, font_size)
                case 'Cheque No.':
                    if value != '':
                        if receipt:
                            c.drawString(x_offset + 45, height - 230, "    ".join(value))
                        else:
                            c.setFont(font_name, font_size-1)
                            c.drawString(x_offset + 70, height - 190, "    ".join(value))
                            c.setFont(font_name, font_size)
                        c.drawString(x_offset + 45, height - 622, "    ".join(value))
                        #c.setFont(font_name, font_size)
                case 'IFSC Code':
                    if value !='':
                        c.setFont(font_name, font_size-1)
                        if receipt:
                            c.drawString(x_offset + 45, height - 248, "    ".join(value).upper())
                        else:
                            c.drawString(x_offset + 300, height - 215,  "    ".join(value).upper())
                        c.drawString(x_offset + 45, height - 642, "    ".join(value).upper())
                        c.setFont(font_name, font_size) 
                case 'A/C No.':
                    if value != '':
                        c.setFont(font_name, font_size-1)
                        if receipt:
                            c.drawString(x_offset + 47, height - 268, "    ".join(value).upper())
                        c.drawString(x_offset + 47, height - 660, "    ".join(value).upper())
                        c.setFont(font_name, font_size)
                case 'Bank Name':  
                    if not receipt:                  
                        c.drawString(x_offset, height - 215, f"{value}")
                case 'Branch Name':  
                    if not receipt:                  
                        c.drawString(x_offset + 180, height - 215, f"{value}")

    # Insert QR Code
    if kwargs.get("QR Code"):
        print("QR Code found")
        try:
            qr_image = ImageReader(kwargs["QR Code"])
            if receipt:
                c.drawImage(qr_image, 480, height - 65, width=60, height=60)
            c.drawImage(qr_image, 480, height - 457, width=60, height=60)
            #c.drawString(x_offset, y_offset - 70, "QR Code:")
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
   
    create_vertical_watermark(c, copy_types[1], copy_types[2]) #, watermark_pdf)

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
