import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
import openpyxl
from openpyxl.drawing.image import Image
from reportlab.lib.utils import ImageReader
from reportlab.lib import fonts
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import tkinter.messagebox as messagebox
from PIL import ImageFont
import re
import qrcode
import configparser
import argparse
import os
import io
import sys

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\excel_to_pdf.ini"
font_path_kannada = os.path.dirname(os.path.abspath(__file__))+r"\config\Malige-n.ttf" #Nirmalafont.ttf#NotoSansKannada-VariableFont_wdth,wght.ttf"
img_path = os.path.dirname(os.path.abspath(__file__))+r"\config\Logo.jpg"
config = configparser.ConfigParser()
config.read(configuration_path)

heading = config['Heading']['heading'] 
sub_heading = config['Heading']['sub_heading'] 
pdf_heading = config['Heading']['pdf_heading'] 

col_str = config.get('Columns', 'columns')
columns_str = config.get('Columns', 'column_names')
columns_str_kartha = config.get('Columns', 'column_names_kartha')
font_name = config.get('FontSettings', 'font_name')
font_size = int(config.get('FontSettings', 'font_size'))
font_name_bold = config.get('FontSettings', 'font_name_bold')
font_size_bold = int(config.get('FontSettings', 'font_size_bold'))
font_name_kannada = config.get('FontSettings', 'font_name_kannada')
#font_name_kannada = 'KannadaFont'
pdfmetrics.registerFont(TTFont(font_name_kannada, font_path_kannada))
excel_file = config['Filenames']['input_file']
sheet = config['Filenames']['sheet']
qr_y_position = int(config.get('FontSettings', 'qr_y_position'))

# Function to detect if the string contains Kannada text
def is_kannada(text):
    for char in text:
        # Check if the character is within the Kannada Unicode block
        if '\u0C80' <= char <= '\u0CFF':
            return True
    return False

def underline_text(canvas, x_pos, y_pos, text):
    canvas.setLineWidth(0.5)  # Set line thickness
    if text in [heading, sub_heading, pdf_heading] or text in pdf_heading:
        text_width = canvas.stringWidth(text, font_name_bold, font_size_bold)
    else:
        text_width = canvas.stringWidth(text, font_name, font_size)
    canvas.line(x_pos, y_pos - 2, x_pos + (text_width), y_pos - 2)

def center_text(canvas, text, y_pos):
    page_width, page_height = A4
    #print (f"center {text}")
    text_width = canvas.stringWidth(text, font_name_bold, font_size_bold)
    x_pos = (page_width - text_width) / 2  # Center the text horizontally
    canvas.setFont(font_name_bold, font_size_bold)
    canvas.drawString(x_pos, y_pos, text)
    underline_text(canvas, x_pos, y_pos, text)

def print_value(canvas, col, x_position, y_position):
    value = str(row[col]) if pd.notna(row[col]) and row[col] != 'N/A' else ''
    text = f"{value}" 
    if col in ['Department', 'Designation']:
        text = value.split('/')
        if is_kannada(text[0]):
            #print(f"Kannada text {repr(text[0])} and {repr(text[1])}")
            canvas.setFont(font_name_kannada, font_size)
            canvas.drawString(x_position, y_position, f"{text[0]}/")
            text_width_kannada = canvas.stringWidth(text[0], font_name_kannada, font_size)
            x_position_for_english = x_position + text_width_kannada + 2
            canvas.setFont(font_name, font_size)
            canvas.drawString(x_position_for_english, y_position, text[1])
        else:
            if isinstance(text, list):
                text = ''.join(text)
            canvas.setFont(font_name, font_size)
            canvas.drawString(x_position, y_position, text)
    else:
        canvas.setFont(font_name, font_size)
        canvas.drawString(x_position, y_position, text)

def print_QR_code(c, col):
    #row_data = ';'.join([f"{col}={row[col]}" for col in df.columns])
    
    column_value_pairs = []
    for col in df.columns:
        if "Date" in col: # == 'Date':
            if isinstance(row[col], datetime):
                row[col] = row[col].strftime('%Y-%m-%d')
        column_value_pairs.append(f"{col}={row[col]}")

    # After the loop, join the list into a single string separated by semicolons
    row_data = ';'.join(column_value_pairs)

    image_width =100  # in pixels
    image_height = 100  # in pixels

    # Generate the QR code
    qr = qrcode.QRCode(
        version=10, 
        error_correction=qrcode.constants.ERROR_CORRECT_L, 
        box_size=10, 
        border=4
    )
    qr.add_data(row_data)
    qr.make(fit=True)

    # Save the QR code as an image to a BytesIO object (so we can insert it into Excel without saving it as a file)
    img_stream = io.BytesIO()
    img = qr.make_image(fill='black', back_color='white')
    img.save(img_stream)
    image = ImageReader(img_stream)

    if img_stream:
        img_stream.seek(0)
        c.drawImage(image, 410, qr_y_position, width=image_width, height=image_height) 

def get_pdf_directory():
    if hasattr(sys, '_MEIPASS'):
        # Running as a bundled .exe
        temp_dir = sys._MEIPASS  # Temporary folder where files are extracted
        pdf_dir = os.path.join(temp_dir, 'pdfs')  # Target pdfs folder in temp dir
    else:
        # Running from script directly
        pdf_dir = 'pdfs'  # Default pdfs directory in current working directory
    return pdf_dir

def wrap_text(c, text, x, y, width, font_name, font_size):
    # Set up a style for the text
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = font_name
    style.fontSize = font_size
    style.leading = font_size + 2 
    # Create a Paragraph object which wraps the text
    paragraph = Paragraph(text, style)
    
    # Draw the wrapped text on the canvas at (x, y)
    paragraph.wrapOn(c, width, 500)  # 500 is the height of the text box
    paragraph.drawOn(c, x, y) 

# Function to create a PDF for each row
def create_pdf_for_row(row, pdf_file_name, pdf_type):
    narration_value = ""
    c = canvas.Canvas(pdf_file_name, pagesize=A4)
    y_position = int(config.get('FontSettings', 'y_position'))

    center_text(c, heading, y_position)
    c.setLineWidth(3)  # Set line thickness (3 is a thick line, you can adjust it)
    c.line(50, y_position - 5, 550, y_position - 5)
    y_position -= 20
    center_text(c, sub_heading, y_position)
    y_position -= 20
    pdf_headings = pdf_heading.split(',')
    center_text(c, pdf_headings[pdf_type], y_position)
    y_position -= 20

    # Calculate the maximum width of column names
    max_col_width = max([c.stringWidth(col, font_name, font_size) for col in df.columns])
    x_position_colname = 50
    x_position_narration = None
    # Set font for the PDF
    c.setFont(font_name, font_size)

    # Write the column names and row values to the PDF
    for col in df.columns:
        if re.match(r"Unnamed: \d+", col) or col in col_str: 
            if (col == 'PAN' or col == 'Description') and pdf_type == 0:
                pass
            else:
                continue
        if col in columns_str:
            if col == 'Kartha Code':
                c.drawString(x_position_colname, y_position, "Narration:")
                underline_text(c, x_position_colname, y_position, "Narration:")
                x_position_colname = x_position_colval
                x_position_narration = x_position_colname
                c.drawString(x_position_colname, y_position, col)
                underline_text(c, x_position_colname, y_position, col)
                y_position -= 15
                print_value(c, col, x_position_colval, y_position)
            else:
                y_position -= 20
                if x_position_narration:
                    x_position_colname = x_position_narration
                c.drawString(x_position_colname, y_position, col)
                underline_text(c, x_position_colname, y_position, col)
                x_position_colval = x_position_colname + max_col_width + 10  # Leave some space after the column names
                print_value(c, col, x_position_colval, y_position)
                y_position -= 15
        elif col in columns_str_kartha:
                y_position += 15
                x_position_colname = x_position_colname + max_col_width + 10 #200
                x_position_colval = x_position_colname
                c.drawString(x_position_colname, y_position, col)
                underline_text(c, x_position_colname, y_position, col)
                y_position -= 15
                print_value(c, col, x_position_colval, y_position)
        elif col == 'QR Code':
                print_QR_code(c,col)
        else:
            if col == 'Narration' and pdf_type == 0:
                continue
            elif col == 'Narration':
                value = str(row[col])
                narration_value = f"{value}"
                continue
            x_position_colname = 50
            #c.setLineWidth(2)
            c.drawString(x_position_colname, y_position, col)
            underline_text(c, x_position_colname, y_position, col)
            x_position_colval = x_position_colname + max_col_width + 10  # Leave some space after the column names
            print_value(c, col, x_position_colval, y_position)
            y_position -= 15

        # Add a new page if we reach the bottom
        if y_position < 50:
            c.showPage()  # Start a new page
            c.setFont(font_name, font_size)  # Re-set the font on the new page
            y_position = 750  # Reset Y position
    
    if not pdf_type == 0:
        c.drawString(x_position_colname, y_position, "Narration:")
        underline_text(c, x_position_colname, y_position, "Narration:")
        x_position_colval = x_position_colname + max_col_width + 10
        y_position -= 15
        wrap_text(c, narration_value, x_position_colval, y_position, 400, font_name, font_size)

    c.drawImage(img_path, 50, qr_y_position, width=100, height=100, mask=None)
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Excel to PDF convertor")
    parser.add_argument("--filepath", default="", help="Excel file location/path")
    parser.add_argument("--sheetname", default="", help="Name of the Sheet where we can find data to process")
    parser.add_argument("--option", default="", help="Helps select the type of print")
    args = parser.parse_args()
    filepath = args.filepath
    sheet_name = args.sheetname
    pdf_type = args.option

    if(filepath):
        excel_file = filepath
    if(sheet_name):
        sheet = sheet_name
    
    try:
        df = pd.read_excel(excel_file, sheet)
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        file_names = df.iloc[:, 0]
        pdf_dir = get_pdf_directory()
        os.makedirs(pdf_dir, exist_ok=True)
    except ValueError as e:
        # Catch the error if sheet name is not found
        print(f"Error: Worksheet named '{sheet_name}' not found. Please check the sheet name.")
        messagebox.showinfo(f"Error:", f"Worksheet named '{sheet_name}' not found. Please check the sheet name.") 
    except Exception as e:
        # Catch any other exceptions (optional)
        print(e)

# Loop through each row in the DataFrame and create a separate PDF
for index, row in df.iterrows():
    type = "SC" if int(pdf_type) == 0 else type
    type = "PC" if int(pdf_type) == 1 else type
    type = "IC" if int(pdf_type) == 2 else type

    pdf_file_name = f"pdfs/{file_names[index]}.pdf"
    create_pdf_for_row(row, pdf_file_name, int(pdf_type))

print(f"PDFs have been successfully created at {pdf_dir}")
