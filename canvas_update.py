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
#x_offset = 90
printer_name = config.get('printer', 'printer')

x_top_receipt_date = config.getint('top_dimensions', 'x_receipt_date')
x_top_receipt_date_HP = config.getint('HP_dimensions', 'x_receipt_date')
y_bottom_receipt_date_HP = config.get('HP_dimensions', 'y_bottom_receipt_date')
y_top_receipt_date = config.get('top_dimensions', 'y_receipt_date')
x_top_intent_receipt_date = config.getint('top_dimensions', 'x_intent_receipt_date')
y_top_intent_receipt_date = config.get('top_dimensions', 'y_intent_receipt_date')
x_bottom_receipt_date = config.getint('bottom_dimensions', 'x_receipt_date')
y_bottom_receipt_date = config.get('bottom_dimensions', 'y_receipt_date')

x_top_bank_date = config.getint('top_dimensions', 'x_bank_date')
y_top_bank_date = config.get('top_dimensions', 'y_bank_date')
x_top_intent_bank_date = config.getint('top_dimensions', 'x_intent_bank_date')
y_top_intent_bank_date = config.get('top_dimensions', 'y_intent_bank_date')
x_bottom_bank_date = config.getint('bottom_dimensions', 'x_bank_date')
y_bottom_bank_date = config.get('bottom_dimensions', 'y_bank_date')

x_top_utrn = config.getint('top_dimensions', 'x_utrn')
y_top_utrn = config.get('top_dimensions', 'y_utrn')
x_top_intent_utrn = config.getint('top_dimensions', 'x_intent_utrn')
y_top_intent_utrn = config.get('top_dimensions', 'y_intent_utrn')
x_top_utrn_HP = config.getint('HP_dimensions', 'x_utrn')
x_bottom_utrn = config.getint('bottom_dimensions', 'x_utrn')
y_bottom_utrn = config.get('bottom_dimensions', 'y_utrn')

x_top_amount = config.getint('top_dimensions', 'x_amount')
y_top_amount = config.get('top_dimensions', 'y_amount')
x_top_intent_amount = config.getint('top_dimensions', 'x_intent_amount')
y_top_intent_amount = config.get('top_dimensions', 'y_intent_amount')
x_bottom_amount = config.getint('bottom_dimensions', 'x_amount')
y_bottom_amount = config.get('bottom_dimensions', 'y_amount')
y_bottom_amount_HP = config.get('HP_dimensions', 'y_amount')
x_top_amount_in_words = config.getint('top_dimensions', 'x_amount_in_words')
y_top_amount_in_words = config.get('top_dimensions', 'y_amount_in_words')
x_top_intent_amount_in_words = config.getint('top_dimensions', 'x_intent_amount_in_words')
y_top_intent_amount_in_words = config.get('top_dimensions', 'y_intent_amount_in_words')
x_bottom_amount_in_words = config.getint('bottom_dimensions', 'x_amount_in_words')
y_bottom_amount_in_words = config.get('bottom_dimensions', 'y_amount_in_words')
y_bottom_amount_in_words_HP = config.get('HP_dimensions', 'y_amount_in_words')

x_top_EFT_tick= config.getint('top_dimensions', 'x_EFT_tick')
x_top_cheque_tick = config.getint('top_dimensions', 'x_cheque_tick')
x_top_cash_tick = config.getint('top_dimensions', 'x_cash_tick')
y_top_tick = config.get('top_dimensions', 'y_tick')
x_top_intent_EFT_tick = config.getint('top_dimensions', 'x_intent_EFT_tick')
x_top_intent_cheque_tick = config.getint('top_dimensions', 'x_intent_cheque_tick')
x_top_intent_cash_tick = config.getint('top_dimensions', 'x_intent_cash_tick')
y_top_intent_tick = config.get('top_dimensions', 'y_intent_tick')
x_bottom_EFT_tick = config.getint('bottom_dimensions', 'x_EFT_tick')
x_bottom_cheque_tick = config.getint('bottom_dimensions', 'x_cheque_tick')
x_bottom_cash_tick = config.getint('bottom_dimensions', 'x_cash_tick')
y_bottom_tick = config.get('bottom_dimensions', 'y_tick')

x_top_cheque_date = config.getint('top_dimensions', 'x_cheque_date')
y_top_cheque_date = config.get('top_dimensions', 'y_cheque_date')
x_top_intent_cheque_date = config.getint('top_dimensions', 'x_intent_cheque_date')
y_top_intent_cheque_date = config.get('top_dimensions', 'y_intent_cheque_date')
x_bottom_cheque_date = config.getint('bottom_dimensions', 'x_cheque_date')
y_bottom_cheque_date = config.get('bottom_dimensions', 'y_cheque_date')

x_top_cheque_no = config.getint('top_dimensions', 'x_cheque_no')
y_top_cheque_no = config.get('top_dimensions', 'y_cheque_no')
x_top_intent_cheque_no = config.getint('top_dimensions', 'x_intent_cheque_no')
y_top_intent_cheque_no = config.get('top_dimensions', 'y_intent_cheque_no')
x_bottom_cheque_no = config.getint('bottom_dimensions', 'x_cheque_no')
y_bottom_cheque_no = config.get('bottom_dimensions', 'y_cheque_no')

x_top_ifsc = config.getint('top_dimensions', 'x_ifsc')
y_top_ifsc = config.get('top_dimensions', 'y_ifsc')
x_top_intent_ifsc = config.getint('top_dimensions', 'x_intent_ifsc')
y_top_intent_ifsc = config.get('top_dimensions', 'y_intent_ifsc')
x_bottom_ifsc = config.getint('bottom_dimensions', 'x_ifsc')
y_bottom_ifsc = config.get('bottom_dimensions', 'y_ifsc')

x_top_acct_no = config.getint('top_dimensions', 'x_acct_no')
y_top_acct_no = config.get('top_dimensions', 'y_acct_no')
x_bottom_acct_no = config.getint('bottom_dimensions', 'x_acct_no')
y_bottom_acct_no = config.get('bottom_dimensions', 'y_acct_no')

x_barcode = config.getint('top_dimensions', 'x_barcode')
y_top_barcode = config.getint('top_dimensions', 'y_barcode')
y_top_barcode_intent = config.getint('top_dimensions', 'y_barcode_intent')
y_bottom_barcode = config.getint('bottom_dimensions', 'y_barcode')
y_bottom_barcode_intent = config.getint('bottom_dimensions', 'y_barcode_intent')
barcode_width = config.getint('top_dimensions', 'barcode_width')
barcode_height = config.getint('top_dimensions', 'barcode_height')

y_top_copy_type = config.get('top_dimensions', 'y_copy_type')
y_bottom_copy_type = config.get('bottom_dimensions', 'y_copy_type')

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
def draw_receipt_date(c, value, receipt, pdf):
    formatted_date = get_date_format(c, value)
    c.setFont(font_name, font_size) 
    if pdf:
        x_update = x_bottom_receipt_date = x_top_receipt_date
        y_update = eval(y_bottom_receipt_date)
    else:
        x_update = x_bottom_receipt_date = x_top_receipt_date_HP
        y_update = eval(y_bottom_receipt_date_HP)
    x, y = (x_update, eval(y_top_receipt_date)) if receipt else (x_top_intent_receipt_date, eval(y_top_intent_receipt_date))
    c.drawString(x, y, "    ".join(formatted_date) )
    c.drawString(x_bottom_receipt_date, y_update, "    ".join(formatted_date) )
    c.setFont(font_name, font_size) 

# Function to draw bank date inside the boxes
def draw_bank_date(c, value,receipt):
    formatted_date = get_date_format(c, value)
    c.setFont(font_name, font_size) 
    receipt_check(c, receipt,  x_top_bank_date, eval(y_top_bank_date), x_top_intent_bank_date, eval(y_top_intent_bank_date), "    ".join(formatted_date))
    c.drawString(x_bottom_bank_date, eval(y_bottom_bank_date), "    ".join(formatted_date))
    c.setFont(font_name, font_size) 

# Function to draw UTRN
def draw_utrn(c, value, receipt, pdf):
    if pdf:
        x = x_top_utrn
    else:
        x = x_top_utrn_HP
    receipt_cheque_wrap(c, receipt, x, eval(y_top_utrn), x_top_intent_utrn, eval(y_top_intent_utrn) , "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()),"    ".join(str(value).upper()), 140, copy_font_name, font_size-1)
    wrap_text(c, "&nbsp;&nbsp;&nbsp;&nbsp;".join(str(value).upper()), x_bottom_utrn, eval(y_bottom_utrn), 140, copy_font_name, font_size-1, 0)

# Function to draw amount in numbers and amount in words
def draw_amount(c, value, receipt, pdf):
    locale.setlocale(locale.LC_ALL, 'en_IN')
    locale_value = locale.format_string("%d", int(value), grouping=True)
    x, y = (x_top_amount, eval(y_top_amount)) if receipt else (x_top_intent_amount, eval(y_top_intent_amount))
    c.drawString(x, y, f"{locale_value}")
    if pdf:
        y = eval(y_bottom_amount)
        y_words = eval(y_bottom_amount_in_words)
    else:
        y = eval(y_bottom_amount_HP)
        y_words = eval(y_bottom_amount_in_words_HP)
    c.drawString(x_bottom_amount, y,f"{locale_value}")
    in_words = convert_to_words(value)
    c.setFont(font_name, font_size-2)
    receipt_cheque_wrap(c, receipt, x_top_amount_in_words, eval(y_top_amount_in_words), x_top_intent_amount_in_words, eval(y_top_intent_amount_in_words), f"{in_words}", f"{in_words}", 380, font_name, font_size-2)
    wrap_text(c, f"{in_words}", x_bottom_amount_in_words, y_words, 380, font_name, font_size-2, 0)
    c.setFont(font_name, font_size)

# Function to draw tick for EFT/Cheque or Cash
def draw_payment_mode_tick(c, value, receipt):
    #y = height - 210
    #y_intent = height - 170
    #y_bottom = height - 600

    match value:
        case 'EFT':
            receipt_check(c, receipt, x_top_EFT_tick, eval(y_top_tick), x_top_intent_EFT_tick, eval(y_top_intent_tick), '✔')
            c.drawString(x_bottom_EFT_tick, eval(y_bottom_tick), '✔')
        case 'Cheque':
            receipt_check(c, receipt, x_top_cheque_tick, eval(y_top_tick), x_top_intent_cheque_tick, eval(y_top_intent_tick), '✔')
            c.drawString(x_bottom_cheque_tick, eval(y_bottom_tick), '✔')
        case 'Cash':
            receipt_check(c, receipt, x_top_cash_tick, eval(y_top_tick), x_top_intent_cash_tick, eval(y_top_intent_tick), '✔')
            c.drawString(x_bottom_cash_tick, eval(y_bottom_tick), '✔')

# Function to draw cheque date in boxes
def draw_cheque_date(c, value, receipt):
    if value != '': 
        formatted_date = get_date_format(c, value)
        c.setFont(font_name, font_size)
        receipt_check(c, receipt, x_top_cheque_date, eval(y_top_cheque_date), x_top_intent_cheque_date, eval(y_top_intent_cheque_date), "    ".join(formatted_date))
        c.drawString(x_bottom_cheque_date, eval(y_bottom_cheque_date), "    ".join(formatted_date))
        c.setFont(font_name, font_size)

# Function to draw cheque number in boxes
def draw_cheque_no(c, value, receipt):
    if value != '':
        receipt_cheque_wrap(c, receipt, x_top_cheque_no, eval(y_top_cheque_no), x_top_intent_cheque_no, eval(y_top_intent_cheque_no), "    ".join(value), "    ".join(value), 0, font_name, font_size)
    c.drawString(x_bottom_cheque_no, eval(y_bottom_cheque_no), "    ".join(value))

# Function to draw IFSC in boxes
def draw_ifsc(c, value, receipt):
    if value !='':
        c.setFont(font_name, font_size)
        receipt_check(c, receipt, x_top_ifsc, eval(y_top_ifsc), x_top_intent_ifsc, eval(y_top_intent_ifsc), "    ".join(value).upper())
        c.drawString(x_bottom_ifsc, eval(y_bottom_ifsc), "    ".join(value).upper())
        c.setFont(font_name, font_size) 

# Function to draw acct no. in boxes
def draw_acct_no(c, value, receipt):
    if value != '':
        c.setFont(font_name, font_size)
        if receipt: c.drawString(x_top_acct_no, eval(y_top_acct_no), "    ".join(value).upper())
        c.drawString(x_bottom_acct_no, eval(y_bottom_acct_no), "    ".join(value).upper())
        c.setFont(font_name, font_size)

# Function to draw Copy Type vertically on the RHS of receipt 
def draw_copy_type(c, y, text):
    c.saveState()
    c.translate(width - 14, y)                          # Move to top half center
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

    draw_copy_type(c, eval(y_top_copy_type) - text_width, top_text)
    draw_copy_type(c, eval(y_bottom_copy_type) - text_width, bottom_text)

# Function to draw barcode
def draw_barcode(c, pdf_filename, filename):
    folder_name = os.path.basename(pdf_filename)
    png_file = Path(pdf_filename) / filename 
    image = Image.open(png_file)

    match folder_name:
        case 'SGPM_DN' | 'SPK_DPS':
            c.drawImage(png_file, x_barcode, y_top_barcode, width=barcode_width, height=barcode_height)
            c.drawImage(png_file, x_barcode, y_bottom_barcode, width=barcode_width, height=barcode_height)
        case 'SGPT' | 'SPT':
            c.drawImage(png_file, x_barcode, y_top_barcode_intent, width=barcode_width, height=barcode_height)
            c.drawImage(png_file, x_barcode, y_bottom_barcode_intent, width=barcode_width, height=barcode_height)
    c.showPage()
    c.save()
