from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import io, os, sys
from pathlib import Path
from PIL import Image  
import pdf_data, configparser
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

# Function to wrap text
def wrap_text(c, text, x, y, width, font_name, font_size, receipt):
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = font_name
    style.fontSize = font_size
    style.leading = font_size + 7                           #vertical spacing between lines
    
    # To adjust the max 200 chars in Address 
    if receipt:
        style.leftIndent = 0
        style.firstLineIndent = 40
        #style.fontSize = font_size-4

    if "&nbsp;&nbsp;&nbsp;&nbsp;" not in text:              #vertical spacing for 'Amount in words' is different
        style.leading = font_size + 3

    paragraph = Paragraph(text, style)                      # Create a Paragraph object which wraps the text
    _, text_height = paragraph.wrap(width, 550)             # Get actual text height
    paragraph.drawOn(c, x, y - text_height)     

# Custom function to convert number to INR words (Indian Rupees in English)
def convert_to_words(amount):
    try:
        amount = int(amount)
    except ValueError:
        messagebox.showerror("Amount Error", "Please enter a valid amount.")
        return
    
    whole_number = int(amount)                              # Split the amount into whole and fractional parts
    fraction_part = round((amount - whole_number) * 100)    # Getting the fraction part as Paise
    whole_in_words = num2words(whole_number, lang='en_IN')  # Convert whole number into words in English
    capitalized_number = whole_in_words.upper()             # Capitalize the first letter of each word
    if fraction_part > 0:                                   # Convert fraction part (Paise) into words if it's non-zero
        fraction_in_words = num2words(fraction_part, lang='en_IN')
        capitalized_fractions = fraction_in_words.upper()
        result = f"{capitalized_number} RUPEES {capitalized_fractions} PAISE"
    else:
        result = f"{capitalized_number} RUPEES"
    return result

# Function to add tick mark based on the mode of payment
def receipt_check(c, receipt, x1, y1, x2, y2, text):
    if receipt:
        c.drawString(x1, y1, text)
    else:
        c.drawString(x2, y2, text)

#Function to wrap text inside the boxes 
def receipt_cheque_wrap(c, receipt, x1, y1, x2, y2, text1, text2, limit, font_name, font_size):
    if receipt:                                             # SGPM_DN and SPK_DPS
        if limit == 0:                                      #cheque no.
            c.drawString(x1, y1, text1)
        else:
            wrap_text(c, text1, x1, y1, limit, font_name, font_size, 0)
    else:                                                   #SGPT and SPT
        if limit == 380:
            font_size -= 2
        c.setFont(font_name, font_size)
        c.drawString(x2, y2, text2)
    c.setFont(font_name, font_size)

# Function to draw receipt date inside the boxes
def draw_receipt_date(c, value, receipt):
    formatted_date = get_date_format(c, value)
    c.setFont(font_name, font_size) 
    x, y = (433, height - 82) if receipt else (420, height - 66)
    c.drawString(x, y, "    ".join(formatted_date) )
    c.drawString(433, height - 470, "    ".join(formatted_date) )
    c.setFont(font_name, font_size) 

# Function to draw bank date inside the boxes
def draw_bank_date(c, value,receipt):
    formatted_date = get_date_format(c, value)
    c.setFont(font_name, font_size) 
    receipt_check(c, receipt,  422, height - 220, x_offset + 330, height - 170, "    ".join(formatted_date))
    c.drawString(422, height - 608, "    ".join(formatted_date))
    c.setFont(font_name, font_size) 

# Function to draw UTRN
def draw_utrn(c, value, receipt):
    receipt_cheque_wrap(c, receipt, 422, height - 227, x_offset + 70, height - 190, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()),"    ".join(str(value).upper()), 140, copy_font_name, font_size-1)
    wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), 422, height - 617, 140, copy_font_name, font_size-1, 0)

# Function to draw amount in numbers and amount in words
def draw_amount(c, value, receipt):
    locale.setlocale(locale.LC_ALL, 'en_IN')
    locale_value = locale.format_string("%d", int(value), grouping=True)
    x, y = (x_offset - 30, height - 310) if receipt else (x_offset, height - 150)
    c.drawString(x, y, f"{locale_value}")
    c.drawString(x_offset - 30, height - 700,f"{locale_value}")
    in_words = convert_to_words(value)
    c.setFont(font_name, font_size-2)
    receipt_cheque_wrap(c, receipt, x_offset + 70, height - 294, x_offset + 120, height - 150, f"{in_words}", f"{in_words}", 380, font_name, font_size-2)
    wrap_text(c, f"{in_words}", x_offset + 70, height - 684, 380, font_name, font_size-2, 0)
    c.setFont(font_name, font_size)

# Function to draw tick for EFT/Cheque or Cash
def draw_payment_mode_tick(c, value, receipt):
    y = height - 210
    y_intent = height - 170
    y_bottom = height - 600

    match value:
        case 'EFT':
            receipt_check(c, receipt, 343, y, x_offset + 190, y_intent, '✔')
            c.drawString(343, y_bottom, '✔')
        case 'Cheque':
            receipt_check(c, receipt, x_offset-20, y, x_offset + 110, y_intent, '✔')
            c.drawString(x_offset-25, y_bottom, '✔')
        case 'Cash':
            receipt_check(c, receipt, x_offset-60, y, x_offset + 40, y_intent, '✔')
            c.drawString(x_offset-60, y_bottom, '✔')

# Function to draw cheque date in boxes
def draw_cheque_date(c, value, receipt):
    if value != '': 
        formatted_date = get_date_format(c, value)
        c.setFont(font_name, font_size)
        receipt_check(c, receipt, x_offset + 45, height - 215, x_offset + 330, height - 170, "    ".join(formatted_date))
        c.drawString(x_offset + 45, height - 604, "    ".join(formatted_date))
        c.setFont(font_name, font_size)

# Function to draw cheque number in boxes
def draw_cheque_no(c, value, receipt):
    if value != '':
        receipt_cheque_wrap(c, receipt, x_offset + 45, height - 230, x_offset + 70, height - 190, "    ".join(value), "    ".join(value), 0, font_name, font_size)
    c.drawString(x_offset + 45, height - 622, "    ".join(value))

# Function to draw IFSC in boxes
def draw_ifsc(c, value, receipt):
    if value !='':
        c.setFont(font_name, font_size)
        receipt_check(c, receipt, x_offset + 45, height - 248, x_offset + 300, height - 215, "    ".join(value).upper())
        c.drawString(x_offset + 45, height - 642, "    ".join(value).upper())
        c.setFont(font_name, font_size) 

# Function to draw acct no. in boxes
def draw_acct_no(c, value, receipt):
    if value != '':
        c.setFont(font_name, font_size)
        if receipt: c.drawString(x_offset + 47, height - 268, "    ".join(value).upper())
        c.drawString(x_offset + 47, height - 660, "    ".join(value).upper())
        c.setFont(font_name, font_size)

# Function to draw Copy Type vertically on the RHS of receipt 
def draw_copy_type(c, y, text):
    c.saveState()
    c.translate(width - 15, y)                          # Move to top half center
    c.rotate(90)                                        # Rotate vertically
    c.drawString(0, 0, text)                       
    c.restoreState()

# Function to generate copy type based on the copy type
def create_vertical_watermark(c, top_text, bottom_text): 
    """Create a watermark PDF with vertical text on the right top corner."""
    width, height = A4  # A4 size in points (595x842)
    
    c.setFont(copy_font_name, 8)                             # Set font and size
    c.setFillColorRGB(0.5, 0.5, 0.5)                    # Darker gray
    text_width = c.stringWidth(top_text, font_name, 8) 

    draw_copy_type(c, (height - 220) - text_width, top_text)
    draw_copy_type(c, (height - 610) - text_width, bottom_text)

# Function to draw barcode
def draw_barcode(c, pdf_filename, filename):
    folder_name = os.path.basename(pdf_filename)
    png_file = Path(pdf_filename) / filename 
    image = Image.open(png_file)

    match folder_name:
        case 'SGPM_DN' | 'SPK_DPS':
            c.drawImage(png_file, 220, 422, width=150, height=50)
            c.drawImage(png_file, 220, 2, width=150, height=50)
        case 'SGPT' | 'SPT':
            c.drawImage(png_file, 220, 424, width=150, height=50)
            c.drawImage(png_file, 220, 4, width=150, height=50)
    c.showPage()
    c.save()
