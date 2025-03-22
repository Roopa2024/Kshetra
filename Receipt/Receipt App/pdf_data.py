import os, configparser, io, qrcode, sys
from reportlab.lib.utils import ImageReader
from datetime import datetime
import pandas as pd
import openpyxl
from openpyxl import load_workbook, Workbook
import canvas_update, excel_data
import tkinter.messagebox as messagebox

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
xcl_file = config.get('Filenames', 'xcl_file')
xcl_sheet = config.get('Filenames', 'xcl_sheet')
pdf_heading = config['Heading']['pdf_heading']
pdf_headings = pdf_heading.split(',')

def get_pdf_directory():
    if hasattr(sys, '_MEIPASS'):    # Running as a bundled .exe
        temp_dir = sys._MEIPASS     # Temporary folder where files are extracted
        pdf_dir = os.path.join(temp_dir, 'pdfs')  # Target pdfs folder in temp dir
    else:
        pdf_dir = 'pdfs'            # Default pdfs directory in current working directory
    return pdf_dir

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


# Function to create a PDF for each row
def create_pdf_for_row(row, pdf_file_name, pdf_type):
    narration_value = ""
    c = canvas.Canvas(pdf_file_name, pagesize=A4)
    y_position = int(fonts['y_position']) # int(config.get('FontSettings', 'y_position'))
    font_size = int(fonts['font_size'])

    text = headings['heading']
    center_text(c, text, y_position, fonts)
    c.setLineWidth(3)   # Set line thickness (3 is a thick line, you can adjust it)
    c.line(50, y_position - 5, 550, y_position - 5)
    y_position -= 20
    center_text(c, str(headings['sub_heading']), y_position, fonts)
    y_position -= 20
    pdf_headings = headings['pdf_heading'].split(',')
    center_text(c, pdf_headings[pdf_type], y_position, fonts)
    y_position -= 20

    # Calculate the maximum width of column names
    max_col_width = max([c.stringWidth(col, fonts['font_name'], font_size) for col in df.columns])
    x_position_colname = 50
    x_position_narration = None
    c.setFont(fonts['font_name'], font_size)       # Set font for the PDF

    for col in df.columns:
        if re.match(r"Unnamed: \d+", col) or col in columns['columns']: 
            if (col == 'PAN' or col == 'Description') and pdf_type == 0:
                pass
            else:
                continue
        if col in columns['column_names']:
            if col == 'Kartha Code':
                c.drawString(x_position_colname, y_position, "Narration:")
                underline_text(c, x_position_colname, y_position, "Narration:")
                x_position_colname = x_position_colval
                x_position_narration = x_position_colname
                c.drawString(x_position_colname, y_position, col)
                underline_text(c, x_position_colname, y_position, col)
                y_position -= 15
                print_value(c, col, x_position_colval, y_position)
            elif col in ['Department', 'Designation']:
                y_position -= 20
                if x_position_narration:
                    x_position_colname = x_position_narration
                c.drawString(x_position_colname, y_position, col)
                underline_text(c, x_position_colname, y_position, col)
                x_position_colval = x_position_colname + max_col_width + 10  # Leave some space after the column names
                #print_value(c, col, x_position_colval, y_position)
                value = str(row[col]) if pd.notna(row[col]) and row[col] != 'N/A' else ''
                text = f"{value}" 
                text = value.split('/')
                if is_kannada(text[0]):
                    #print(f"Kannada text {repr(text[0].encode('utf-8'))} and {repr(text[1].encode('utf-8'))}")
                    c.setFont(fonts['font_name_kannada'], font_size)
                    c.drawString(x_position_colval, y_position, f"{text[0]}/")
                    text_width_kannada = c.stringWidth(text[0], fonts['font_name_kannada'], font_size)
                    x_position_for_english = x_position_colval + text_width_kannada + 2
                    c.setFont(fonts['font_name'], font_size)
                    c.drawString(x_position_for_english, y_position, text[1])
                else:
                    if isinstance(text, list):
                        text = ''.join(text)
                c.setFont(fonts['font_name'], font_size)
                text = str(text)
                y_position -= 15
        elif col in columns['column_names_kartha']:
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
            if col == 'Narration' and pdf_type == 0: #For SC, Narration needs special handling
                continue
            elif col == 'Narration':
                value = str(row[col])
                narration_value = f"{value}"
                continue
            x_position_colname = 50
            c.drawString(x_position_colname, y_position, col)
            underline_text(c, x_position_colname, y_position, col)
            x_position_colval = x_position_colname + max_col_width + 10  # Leave some space after the column names
            print_value(c, col, x_position_colval, y_position)
            y_position -= 15

        if y_position < 50: # Add a new page if we reach the bottom
            c.showPage()  # Start a new page
            c.setFont(fonts['font_name'], font_size)  # Re-set the font on the new page
            y_position = 750  # Reset Y position
    
    if not pdf_type == 0:       #function to wrap text for Narration, for PC and IC
        c.drawString(x_position_colname, y_position, "Narration:")
        underline_text(c, x_position_colname, y_position, "Narration:")
        x_position_colval = x_position_colname + max_col_width + 10
        y_position -= 15
        wrap_text(c, narration_value, x_position_colval, y_position, 400, fonts['font_name'], font_size)

    c.drawImage(img_path, 50, qr_y_position, width=100, height=100, mask=None)
    
    # Save the PDF
    c.save()
