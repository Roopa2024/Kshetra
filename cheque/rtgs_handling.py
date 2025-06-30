from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import textwrap
import io

def draw_hdfc(c, field_data):
    # Position and text to fill based on field names (you may need to adjust the coordinates)
    for field, value in field_data.items():
        # Manually specify the x, y positions of the fields
        if field == 'rtgs':
            c.drawString(45, 785, value)
        if field == 'hdfc_cust_name':
            c.drawString(160, 750, value)
        elif field == 'Others':
            c.drawString(525, 700, value)
        elif field == 'time':
            c.drawString(70, 685, value)
        elif field == 'cust_name':
            c.drawString(130,670, value)    
        elif field == 'acct_num':
            c.drawString(100, 650, value)
        elif field == 'chq_num':
            c.drawString(240,650, value)
        elif field == 'mobile':
            c.drawString(100, 635, value)
        #if field == 'addr_remitter':
        #    c.drawString(330, 565, value)
        elif field == 'email':
            c.drawString(380, 550, value)
        elif field == 'cash_dep':
            c.drawString(120, 520, value)
        elif field == 'ben_name':
            c.drawString(85, 490, value)
        elif field == 'ben_addr':
            c.drawString(80, 475, value)
        elif field == 'ben_acct_num':
            c.drawString(160, 460, value)
        if field == 're-ben_acct_num':
            c.drawString(160, 445, value)
        elif field == 'bank_br':
            c.drawString(150, 425, value)
        elif field == 'ifsc_code':
            c.drawString(400, 425, value)
        elif field == 'acct_type':
            c.drawString(95, 410, value)
        elif field == 'purpose':
            c.drawString(350, 410, value)
        elif field == 'amount':
            c.drawString(200, 330, value)
        elif field == 'in_words':
            #c.drawString(400, 330, value)  
            y = 330 
            wrapper = textwrap.TextWrapper(width=30)
            lines = wrapper.wrap(value)
            # Split into exactly 2 lines
            if len(lines) > 1:
                first_line = lines[0]
                second_line = " ".join(lines[1:])  # Combine remaining lines into one
            else:
                first_line = lines[0]
                second_line = ""
            c.drawString(400, y, first_line)
            c.drawString(60, y - 12, second_line)
        elif field == 'remarks':
            c.drawString(100, 300, value)

def draw_kar(c, field_data):
    # Position and text to fill based on field names (you may need to adjust the coordinates)
    for field, value in field_data.items():
        # Manually specify the x, y positions of the fields
        if field == 'date':
            c.drawString(475, 755, value)
        if field == 'PAN':
            c.drawString(450, 740, value)
        elif field == 'bank_br':
            c.drawString(65, 720, value)
        elif field == 'amount':
            c.drawString(340, 685, value)
        elif field == 'in_words':
            #c.drawString(400, 330, value)  
            y = 685 
            wrapper = textwrap.TextWrapper(width=10)
            lines = wrapper.wrap(value)
            # Split into exactly 2 lines
            if len(lines) > 1:
                first_line = lines[0]
                second_line = " ".join(lines[1:])  # Combine remaining lines into one
            else:
                first_line = lines[0]
                second_line = ""
            c.drawString(480, y, first_line)
            c.drawString(65, y - 15, second_line)
        elif field == 'acct_num':
            c.drawString(165, 600, value)
        elif field == 'chq_num':
            c.drawString(165, 585, value)
        elif field == 'chq_date':
            c.drawString(430, 580, value)
        elif field == 'cust_name':
            c.drawString(170, 570, value)    
        elif field == 'mobile':
            c.drawString(190, 540, value)
        #if field == 'addr_remitter':
        #    c.drawString(330, 565, value)
        elif field == 'ben_name':
            c.drawString(170, 505, value)
        elif field == 'ben_acct_num':
            c.drawString(170, 485, value)
        if field == 'acct_type':
            c.drawString(500, 485, value)
        elif field == 'bank_name':
            c.drawString(140, 472, value)
        elif field == 'ifsc_code':
            c.drawString(430, 470, value)
        elif field == 'ben_bank_br':
            c.drawString(150, 455, value)
        #elif field == 'purpose':
        #    c.drawString(350, 410, value)

def draw_canara(c, field_data):
    # Position and text to fill based on field names (you may need to adjust the coordinates)
    for field, value in field_data.items():
        spaced_value = "    ".join(str(value)) if isinstance(value, (str, int)) else value
        if field == 'date':
            spaced_value = "    ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(422, 760, spaced_value)
        if field == 'PAN':
            spaced_value = "    ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(393, 735, spaced_value)
        elif field == 'bank_br':
            c.drawString(50, 740, value)
        elif field == 'amount':
            c.drawString(235, 710, value)
        elif field == 'in_words':
            #c.drawString(400, 330, value)  
            y = 710
            wrapper = textwrap.TextWrapper(width=30)
            lines = wrapper.wrap(value)
            # Split into exactly 2 lines
            if len(lines) > 1:
                first_line = lines[0]
                second_line = " ".join(lines[1:])  # Combine remaining lines into one
            else:
                first_line = lines[0]
                second_line = ""
            c.drawString(395, y, first_line)
            c.drawString(60, y - 11, second_line)
        elif field == 'acct_num':
            c.drawString(165, 615, spaced_value)
        elif field == 'chq_num':
            c.drawString(160, 595, spaced_value)
        elif field == 'chq_date':
            spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(405, 598, spaced_value)
        elif field == 'cust_name':
            c.drawString(160, 580, spaced_value)    
        elif field == 'addr_remitter':
            c.drawString(160, 560, spaced_value)
        elif field == 'mobile':
            c.drawString(378, 510, spaced_value)
        elif field == 'ben_name':
            c.drawString(160, 465, spaced_value)
        elif field == 'ben_acct_num':
            c.drawString(160, 445, spaced_value)
        if field == 're-ben_acct_num':
            c.drawString(160, 430, spaced_value)
        elif field == 'bank_name':
            c.drawString(160, 410, spaced_value)
        elif field == 'ifsc_code':
            c.drawString(160, 375, spaced_value)
        elif field == 'ben_bank_br':
            c.drawString(160, 355, spaced_value)
        #elif field == 'purpose':
        #    c.drawString(350, 410, value)

def draw_union(c, field_data):
    # Position and text to fill based on field names (you may need to adjust the coordinates)
    for field, value in field_data.items():
        #add space between each letter
        spaced_value = "   ".join(str(value)) if isinstance(value, (str, int)) else value
        # Manually specify the x, y positions of the fields
        #if field == 'rtgs':
        #    c.drawString(45, 785, value)
        if field == 'bank_br':
            c.drawString(210,645, value)
        elif field == 'acct_num':
            spaced_value = "    ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(290, 575, spaced_value)
        elif field == 'cust_name':
            c.drawString(190, 560, spaced_value)
        elif field == 'mobile':
            c.drawString(210,545, spaced_value)    
        elif field == 'PAN':
            spaced_value = "    ".join(str(value)) if isinstance(value, (str, int)) else value
            c.drawString(120, 530, spaced_value)
        elif field == 'amount':
            c.drawString(120,503, spaced_value)
        elif field == 'exchange':
            c.drawString(300, 503, spaced_value)
        if field == 'total':
            c.drawString(420, 503, spaced_value)
        elif field == 'in_words':
            #y = 490 
            #wrapper = textwrap.TextWrapper(width=100)
            #lines = wrapper.wrap(value)
            # Split into exactly 2 lines
            #if len(lines) > 1:
            #    first_line = lines[0]
            #    second_line = " ".join(lines[1:])  # Combine remaining lines into one
            #else:
            #    first_line = lines[0]
            #    second_line = ""
            #c.drawString(210, y, first_line)
            #c.drawString(60, y - 2, second_line)
            c.drawString(210, 490, value)
        elif field == 'chq_num':
            c.drawString(130, 460, spaced_value)
        elif field == 'chq_date':
            c.drawString(230, 460, spaced_value)
        elif field == 'ben_acct_num':
            c.drawString(175, 428, spaced_value)
        elif field == 'ben_name':
            c.drawString(175, 402, spaced_value)
        if field == 'ben_addr':
            c.drawString(155, 390, spaced_value)
        elif field == 'bank_name':
            c.drawString(155, 365, spaced_value)
        elif field == 'ben_bank_br':
            c.drawString(155, 348, spaced_value)
        elif field == 'ifsc_code':
            c.drawString(190, 332, spaced_value)
        elif field == 'date':
            c.drawString(100, 270, value)
        #elif field == 'remarks':
        #    c.drawString(100, 300, value)

    
def create_filled_pdf(input_pdf, output_pdf, field_data):
    print(f"INPUT : {input_pdf} and output : {output_pdf}")
    # Create a PDF buffer with reportlab
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    # Set font and size for writing text
    c.setFont("Helvetica", 10)
    print(field_data)

    if field_data['BANK'] == 'hdfc':
        print("Draw HDFC RTGS")
        draw_hdfc(c, field_data)
    elif field_data['BANK'] == 'kar':
        print("Draw Kar RTGS")
        draw_kar(c, field_data)
    elif field_data['BANK'] == 'canara':
        print("Draw Canara RTGS")
        draw_canara(c, field_data)
    elif field_data['BANK'] == 'union':
        print("Draw Union RTGS")
        draw_union(c, field_data)
    
    c.save()

    # Merge the new content (generated with reportlab) onto the original PDF form
    packet.seek(0)
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in existing_pdf.pages:
        # Merge the new PDF with the old PDF (the original form)
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)

    # Save the final filled PDF
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

