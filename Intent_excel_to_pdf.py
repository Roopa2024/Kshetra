from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import openpyxl
from reportlab.lib import fonts
import tkinter.messagebox as messagebox
import configparser
import argparse
import os
import io
import sys
import textwrap
from num2words import num2words
import locale

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\Intent_excel_to_pdf.ini"
config = configparser.ConfigParser()
config.read(configuration_path)

fonts = {key: config.get('FontSettings', key) for key in ['font_name', 'font_size', 'font_name_bold', 'font_size_bold']}
files = {key: config.get('Filenames', key) for key in ['output_file', 'receipt']}
dims = {key: int(config.get('Values', key)) for key in ['cheque_width', 'neft_width', 'amt_y', 'amt_x', 'amt_words_x', 'cash_rtgs_y', 'cash_x', 'serial_rtgs_x', 'receipt_x', 'cheque_x', 'neft_x', 'cross_y']}

def text_wrapper(c, value, length, x, y):
    wrapper = textwrap.TextWrapper(width=length)
    lines = wrapper.wrap(str(value))
    if len(lines) > 0:
        first_line = lines[0]
    else:
        first_line = ""
    if len(lines) > 1:                                          # Split into exactly 2 lines
        second_line = " ".join(lines[1:])                       # Combine remaining lines into one
    else:
        second_line = ""
    c.drawString(x, y, first_line)
    if length == dims['neft_width']: #28:
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

def draw_receipt(c, row_dict, y):
    c.drawString(45, dims['cross_y'], '✔') 
    x = dims['receipt_x'] 
    value = row_dict['Book No.']
    if pd.notna(value):
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
        c.drawString(x, y, str(spaced_value))
    y = y-20
    value = row_dict['Receipt No.']
    if pd.notna(value):
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
        c.drawString(x, y, str(spaced_value))
    y = y-15
    value = row_dict['Receipt Date']
    if pd.notna(value):
        value = str(int(value)).zfill(8)
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
        c.drawString(x, y, str(spaced_value))
    y = 60
    x = x - 20

def draw_cheque(c, row_dict, y):
    c.drawString(220, dims['cross_y'], '✔') 
    x = dims['cheque_x']  
    y = y + 8
    value = row_dict['Cheque No.']
    if pd.notna(value):
        spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
        c.drawString(x, y, str(spaced_value))
    y = y-15
    value = row_dict['Cheque Date']
    if pd.notna(value):
        value = str(int(value)).zfill(8)
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
        c.drawString(x, y, str(spaced_value))
    y = y-15
    value = row_dict['Cheque IFSC']
    if pd.notna(value):
        spaced_value = " ".join(str(value)) if isinstance(value, (str, int)) else value
        c.drawString(x, y, str(spaced_value))
    y = y-12
    value = row_dict['Cheque ACC No.']
    if pd.notna(value):
        spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
        text_wrapper(c, spaced_value, dims['cheque_width'], 250, y)
    y = y-30          

def draw_neft(c, row_dict, y):
    x = dims['neft_x']
    y = y + 4
    c.drawString(dims['cash_x'], dims['cross_y'], '✔')
    value = row_dict['Transaction ID'] #) if pd.notna(row_dict['Transaction ID']) and row_dict['Transaction ID'] != 'N/A' else ''
    if pd.notna(value):
        spaced_value = "  ".join(str(value)) if isinstance(value, (str, int)) else value
        text_wrapper(c, spaced_value, dims['neft_width'], 450, y)
    y = y-30
    value = row_dict['NEFT Date']
    if pd.notna(value):
        value = str(int(value)).zfill(8)
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value                
        c.drawString(420, y, str(spaced_value))
    y = y-20

def create_filled_pdf(row_dict, pdf_file_name):
    packet = io.BytesIO()                                       # Create a PDF buffer with reportlab
    c = canvas.Canvas(packet, pagesize=A4)                      # Initialize a canvas for the PDF
    c.setFont(fonts['font_name'], int(fonts['font_size']))
    y = 150

    try:
        receipt = row_dict['Receipt']
        cheque = row_dict['Cheque']
        neft = row_dict['NEFT']
        amount = row_dict ['Amount']
        serial_no = row_dict['Serial No.']
        c.drawString(dims['serial_rtgs_x'], 190, str(serial_no))

        if receipt == 'Yes':
            draw_receipt(c, row_dict, y)
        elif receipt == 'No':
            c.drawString(45, dims['cross_y'], 'X') 
        if cheque == 'Yes':
            draw_cheque(c, row_dict, y)
        elif cheque == 'No':
            c.drawString(220, dims['cross_y'], 'X') 
        if neft == 'Yes':
            draw_neft(c, row_dict, y)
        elif neft == 'No':
            c.drawString(dims['cash_x'], dims['cross_y'], 'X')
        if row_dict['Cash'] == 'Yes':
            c.drawString(dims['cash_x'], dims['cash_rtgs_y'], '✔')
        elif row_dict['Cash'] == 'No':
            c.drawString(dims['cash_x'], dims['cash_rtgs_y'], 'X')
        if row_dict['RTGS'] == 'Yes':
            c.drawString(dims['serial_rtgs_x'], dims['cash_rtgs_y'], '✔')
        elif row_dict['RTGS'] == 'No':
            c.drawString(dims['serial_rtgs_x'], dims['cash_rtgs_y'], 'X')
        if pd.notna(amount): 
            c.setFont(fonts['font_name'], int(fonts['font_size_bold']))
            locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
            formatted_amount = locale.format_string("%0.2f", amount, grouping=True)
            c.drawString(dims['amt_x'], dims['amt_y'], str(formatted_amount)) 
            in_words= convert_to_words(amount)
            c.drawString(dims['amt_words_x'], dims['amt_y'], in_words)
    except KeyError as e:
        print(f"Error: {e}. Column not found.")
        return
    
    c.save()                                                # Save the PDF
    
    packet.seek(0)                                          # Merge the new content (generated with reportlab) onto the original PDF form
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    #Blank pdf logic to write on new pdf
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
        pdf_file_name = f"{output_folder}/{row_dict['Serial No.']}.pdf"   
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
        df = pd.read_excel(excel_file, sheet, dtype={'Book No.': str, 'Receipt No.': str, 'Cheque No.': str,'Cheque ACC No.': str, 'Transaction ID': str })
        workbook = openpyxl.load_workbook(excel_file)
        sheet = workbook.active
        pdf_dir = get_pdf_directory()
        os.makedirs(pdf_dir, exist_ok=True)
    except ValueError as e:
        print(f"Error: Worksheet named '{sheet_name}' not found. Please check the sheet name.")
        messagebox.showinfo(f"Error:", f"Worksheet named '{sheet_name}' not found. Please check the sheet name.") 
    except Exception as e:
        print(e)                                            # Catch any other exceptions (optional)

    read_and_generate_pdf(df, files['output_file'], sheet_name)
    print ("PDFs created successfully at ./pdfs/*")

