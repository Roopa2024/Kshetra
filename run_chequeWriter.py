from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
import openpyxl
from reportlab.lib import fonts
import tkinter.messagebox as messagebox
import re
import configparser
import argparse
import os
import io
import sys
import textwrap
from num2words import num2words

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\Intent_excel_to_pdf.ini"
config = configparser.ConfigParser()
config.read(configuration_path)

fonts = {key: config.get('FontSettings', key) for key in ['font_name', 'font_size', 'font_name_bold', 'font_size_bold']}
files = {key: config.get('Filenames', key) for key in ['output_file','receipt']}

def check_for_null(value):
    return int(value) if pd.notna(value) and value!= 'N/A' else ''


def test_wrapper(c, value, length, x, y):
    wrapper = textwrap.TextWrapper(width=length)
    lines = wrapper.wrap(value)
    
    if len(lines) > 1:                                          # Split into exactly 2 lines
        first_line = lines[0]
        second_line = " ".join(lines[1:])                       # Combine remaining lines into one
    else:
        first_line = lines[0]
        second_line = ""
    c.drawString(x, y, first_line)
    if length == 28:
        x = x-52
        y = y-15
    else:
        y = y-13
    
    c.drawString(x, y, second_line)

def get_pdf_directory():
    if hasattr(sys, '_MEIPASS'):                                # Running as a bundled .exe
        temp_dir = sys._MEIPASS                                 # Temporary folder where files are extracted
        pdf_dir = os.path.join(temp_dir, 'pdfs')                # Target pdfs folder in temp dir
    else:
        pdf_dir = 'pdfs'                                        # Default pdfs directory in current working directory
    return pdf_dir

def convert_to_words(amount):
    amount = int(amount)
    whole_number = int(amount)                                  # Split the amount into whole and fractional parts
    fraction_part = round((amount - whole_number) * 100)        # Getting the fraction part as Paise
    whole_in_words = num2words(whole_number, lang='en_IN')      # Convert whole number into words in English
    capitalized_number = whole_in_words.title()                 # Capitalize the first letter of each word

    if fraction_part > 0:                                       # Convert fraction part (Paise) into words if it's non-zero
        fraction_in_words = num2words(fraction_part, lang='en_IN')
        capitalized_fractions = fraction_in_words.title()
        result = f"{capitalized_number} Rupees {capitalized_fractions} Paise"
    else:
        result = f"{capitalized_number} Rupees"
    return result

def create_filled_pdf(row_dict, pdf_file_name):
    #print(f"output : {pdf_file_name}")
    packet = io.BytesIO()                                       # Create a PDF buffer with reportlab
    c = canvas.Canvas(packet, pagesize=A4)                      # Initialize a canvas for the PDF
    c.setFont(fonts['font_name'], int(fonts['font_size_bold']))
    y = 150

    try:
        receipt = row_dict['Receipt']
        cheque = row_dict['Cheque']
        neft = row_dict['NEFT']
        amount = row_dict ['Amount']

        serial_no = row_dict['Serial No.']
        c.drawString(480, 190, str(serial_no))

        if receipt == 'Yes':
            c.drawString(45, 170, 'X') 
            x = 100 
            value = check_for_null(row_dict['Book No.']) 
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(x, y, str(spaced_value))
            y = y-20
            value = check_for_null(row_dict['Receipt No.']) 
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
            c.drawString(x, y, str(spaced_value))
            y = y-15
            value = check_for_null(row_dict['Receipt Date'])
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(x, y, str(spaced_value))
            y = 60
            x = x - 20
        if cheque == 'Yes':
            c.drawString(220, 170, 'X') 
            x = 250  
            y = y + 8
            value = int(row_dict['Cheque No.'])
            spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(x, y, str(spaced_value))
            y = y-15
            value = int(row_dict['Cheque Date'])
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
            c.drawString(x, y, str(spaced_value))
            y = y-15
            value = row_dict['Cheque IFSC']
            spaced_value = " ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(x, y, str(spaced_value))
            y = y-12
            value = int(row_dict['Cheque ACC No.'])
            spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
            test_wrapper(c, spaced_value, 34, 250, y)
            y = y-30          
        if neft == 'Yes':
            x = 400
            y = y + 4
            c.drawString(395, 170, 'X')
            value = str(row_dict['Transaction ID']) if pd.notna(row_dict['Transaction ID']) and row_dict['Transaction ID'] != 'N/A' else ''
            if value != '':
                spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
                test_wrapper(c, spaced_value, 28, 450, y)
            y = y-30
            value = check_for_null(row_dict['NEFT Date'])
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
            c.drawString(420, y, str(spaced_value))
            y = y-20
        if row_dict['Cash'] == 'Yes':
            c.drawString(395, y, 'X')
        if row_dict['RTGS'] == 'Yes':
            c.drawString(480, y, 'X')
            
        if pd.notna(amount): 
            y = 60
            x = 80
            c.drawString(x,y, str(amount)) 
            in_words= convert_to_words(amount)
            #in_words = in_words.replace("Rupees", "").strip()
            #in_words = in_words.replace(",", "")
            x = x + 90
            c.drawString(x,y,in_words)
    except KeyError as e:
        print(f"Error: {e}. Column not found.")
        return
    
    c.save()                                                # Save the PDF
    
    packet.seek(0)                                          # Merge the new content (generated with reportlab) onto the original PDF form
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    #Blank pdf logic
    writer = PdfWriter()
    for page in new_pdf.pages:
        writer.add_page(page)
    with open(pdf_file_name, "wb") as f:                     # Save the final filled PDF
        writer.write(f)

    #Merge PDF Logic for writing on existing old pdf
    #existing_pdf = PdfReader(files['receipt'])
    #writer = PdfWriter()
    #for page in existing_pdf.pages:
    #    page.merge_page(new_pdf.pages[0])                   # Merge the new PDF with the old PDF (the original form)
    #    writer.add_page(page)
    #with open(pdf_file_name, "wb") as f: #output_file:      # Save the final filled PDF
    #    writer.write(f) #output_file)

def read_and_generate_pdf(df, output_folder, sheet):
    rows_data = []                                          # List to store row data as key-value pairs
    for index, row in df.iterrows():
        row_dict = {df.columns[i]: row[i] for i in range(len(df.columns))}  # Create a dictionary with col name as key and row value as value
        rows_data.append(row_dict)
        #print(row_dict)
        file_idx = index + 1
        pdf_file_name = f"{output_folder}/{row_dict['Serial No.']}.pdf"     # Generate a unique PDF file name based on row index
        create_filled_pdf(row_dict, pdf_file_name)          # Call the function to create a filled PDF

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Excel to PDF convertor")
    parser.add_argument("--filepath", default="", help="Excel file location/path")
    parser.add_argument("--sheetname", default="", help="Name of the Sheet where we can find data to process")
    args = parser.parse_args()
    filepath = args.filepath
    sheet_name = args.sheetname

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
        print(f"Error: Worksheet named '{sheet_name}' not found. Please check the sheet name.")
        messagebox.showinfo(f"Error:", f"Worksheet named '{sheet_name}' not found. Please check the sheet name.") 
    except Exception as e:
        print(e)                                            # Catch any other exceptions (optional)

    read_and_generate_pdf(df, files['output_file'], sheet_name)
    print ("PDFs created successfully at ./pdfs/*")
