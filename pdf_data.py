import os, configparser, io, qrcode, sys
from datetime import datetime
import pandas as pd
import openpyxl
from num2words import num2words

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
font_name = config.get('FontSettings', 'font_name')
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

    paragraph = Paragraph(text, style)  # Create a Paragraph object which wraps the text
    #paragraph.wrapOn(c, width, 500)     # 500 is the height of the text box
    _, text_height = paragraph.wrap(width, 550)  # Get actual text height
    paragraph.drawOn(c, x, y - text_height)     
    
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

def print_QR_code(c):
    #row_data = ';'.join([f"{col}={row[col]}" for col in df.columns])
    print ("QR Code logic")
    df = pd.read_excel(xcl_file, xcl_sheet)
    
    for index, row in df.iterrows():  # Iterate over each row
        column_value_pairs = []
        for col in df.columns:
            if "Date" in col:
                if isinstance(row[col], datetime):
                    row[col] = row[col].strftime('%Y-%m-%d')
            column_value_pairs.append(f"{col}={row[col]}")

        row_data = ';'.join(column_value_pairs)  # After the loop, join the list into a single string separated by semicolons

        image_width = 100  # in pixels
        image_height = 100  # in pixels
        print("QR Data Length:", len(str(row_data)))
        print("QR Data:", row_data)
        
        # Generate the QR code
        qr = qrcode.QRCode(
            version=40, 
            error_correction=qrcode.constants.ERROR_CORRECT_L, 
            box_size=10, 
            border=4
        )
        qr.add_data(row_data)
        qr.make() #fit=True)

        # Save the QR code as an image to a BytesIO object (so we can insert it into Excel without saving it as a file)
        img_stream = io.BytesIO()
        img = qr.make_image(fill='black', back_color='white')
        img.save(img_stream)
        image = ImageReader(img_stream)

        if img_stream:
            img_stream.seek(0)
            c.drawImage(image, 410, 50, width=image_width, height=image_height) 
    return

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
    capitalized_number = whole_in_words.title()
    # Convert fraction part (Paise) into words if it's non-zero
    if fraction_part > 0:
        fraction_in_words = num2words(fraction_part, lang='en_IN')
        capitalized_fractions = fraction_in_words.title()
        result = f"{capitalized_number} Rupees {capitalized_fractions} Paise"
    else:
        result = f"{capitalized_number} Rupees"

    return result

def get_date_format(c, value):
    date_obj = datetime.strptime(value, "%m/%d/%y") 
    formatted_date = date_obj.strftime("%d%b%Y").upper()
    c.setFont(font_name, font_size) 
    return formatted_date

def create_pdf_from_kwargs(kwargs, pdf_path, entity):
    """
    Creates a PDF using the provided kwargs dictionary, including text, QR Code, and Barcode.
    
    :param kwargs: Dictionary containing the row's data.
    :param pdf_path: Path to save the generated PDF.
    """
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    print(f"Width and height = {width} and {height}")
    
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
                    c.setFont(font_name, font_size-1) 
                    c.drawString(437, height - 82, "    ".join(formatted_date) )
                    c.drawString(437, height - 500, "    ".join(formatted_date) )
                    c.setFont(font_name, font_size) 
                case 'Contributor Name':
                    c.drawString(x_offset, height - 105, f"{value}")          
                    c.drawString(x_offset, height - 525, f"{value}")       
                case 'Address':
                    wrap_text(c, f"{value}", x_offset, height - 115, 455, font_name, font_size)
                    wrap_text(c, f"{value}", x_offset, height - 535, 450, font_name, font_size)
                case 'PAN':
                    c.setFont(font_name, font_size-1) 
                    c.drawString(410, height - 150, "    ".join(str(value).upper()))
                    c.drawString(410, height - 570, "    ".join(str(value).upper()))
                    c.setFont(font_name, font_size) 
                case 'Contribution Type':
                    c.drawString(x_offset + 70 , height - 180, f"{value}")
                    c.drawString(x_offset + 70, height - 595, f"{value}")
                case 'Contribution Intent':
                    c.drawString(x_offset + 70, height - 198, f"{value}")
                    c.drawString(x_offset + 70, height - 615, f"{value}")
                case 'Bank Date':
                    formatted_date = get_date_format(c, value)
                    c.setFont(font_name, font_size-1) 
                    c.drawString(428, height - 230, "    ".join(formatted_date))
                    c.drawString(428, height - 653, "    ".join(formatted_date))
                    c.setFont(font_name, font_size) 
                case 'UTRN':
                    wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), 432, height - 244, 140, font_name, font_size-1)
                    wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), 432, height - 663, 140, font_name, font_size-1)
                case 'Amount':
                    c.drawString(x_offset - 50, height - 340, f"{value}")
                    c.drawString(x_offset - 50, height - 760,f"{value}")
                    in_words = convert_to_words(value)
                    c.drawString(x_offset + 70, height - 340, f"{in_words}")
                    c.drawString(x_offset + 70, height - 760, f"{in_words}")
                case 'Payment Mode':
                    if value == 'Online':
                        c.drawString(350, height - 223, '✔')
                        c.drawString(350, height - 643, '✔')
                    elif value == 'Cheque':
                        c.drawString(x_offset-30, height - 223, '✔')
                        c.drawString(x_offset-30, height - 643, '✔')
                    elif value == 'Cash':
                        c.drawString(x_offset-68, height - 223, '✔')
                        c.drawString(x_offset-65, height - 643, '✔')
                case 'Cheque Date':
                    if value != '': 
                        formatted_date = get_date_format(c, value)
                        c.setFont(font_name, font_size-1)
                        c.drawString(x_offset + 40, height - 230, "    ".join(formatted_date))
                        c.drawString(x_offset + 40, height - 652, "    ".join(formatted_date))
                        c.setFont(font_name, font_size)
                case 'Cheque No.':
                    if value != '':
                        #c.setFont(font_name, font_size-1)
                        c.drawString(x_offset + 40, height - 250, "    ".join(value))
                        c.drawString(x_offset + 40, height - 670, "    ".join(value))
                        #c.setFont(font_name, font_size)
                case 'IFSC Code':
                    if value !='':
                        #c.setFont(font_name, font_size-1)
                        c.drawString(x_offset + 40, height - 268, "    ".join(value))
                        c.drawString(x_offset + 40, height - 688, "    ".join(value))
                        #c.setFont(font_name, font_size) 
                case 'A/C No.':
                    if value != '':
                        #c.setFont(font_name, font_size-1)
                        c.drawString(x_offset + 40, height - 288, "    ".join(value))
                        c.drawString(x_offset + 40, height - 706, "    ".join(value))
                        #c.setFont(font_name, font_size)

    # Insert QR Code
    if kwargs.get("QR Code"):
        print("QR Code found")
        try:
            qr_image = ImageReader(kwargs["QR Code"])
            c.drawImage(qr_image, 480, height - 68.5, width=65, height=65)
            c.drawImage(qr_image, 480, height - 487.85, width=65, height=65)
            #c.drawString(x_offset, y_offset - 70, "QR Code:")
        except Exception as e:
            print("Error adding QR Code:", e)

    # Insert Barcode
    if kwargs.get("Barcode"):
        try:
            barcode_image = ImageReader(kwargs["Barcode"])
            name = entity.split(".")[0]
            match name:
                case 'SGPM_DN' | 'SPK_DPS':
                    #print ("DN DNS")
                    c.drawImage(barcode_image, 220, 422, width=150, height=50)
                    c.drawImage(barcode_image, 220, 2, width=150, height=50)
                case 'SGPT' | 'SPT':
                    #print("SGPT")
                    c.drawImage(barcode_image, 220, 424, width=150, height=50)
                    c.drawImage(barcode_image, 220, 4, width=150, height=50)
            #c.drawImage(barcode_image, x_offset + 150, y_offset - 60, width=200, height=50)
            #c.drawString(x_offset + 150, y_offset - 70, "Barcode:")
        except Exception as e:
            print("Error adding Barcode:", e)

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
        with_bg = 1 #tmp, need to read it from UI options
        if with_bg == 1:
            merge_pdf(entity, new_pdf, pdf_path)
    print(f"PDF saved: {pdf_path}")