from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
#from reportlab.lib.colors import black
import io, os, sys
from pathlib import Path
from PIL import Image  

# Get the base path (different for script vs. executable)
if getattr(sys, 'frozen', False):  # Running as a PyInstaller .exe
    base_path = sys._MEIPASS  
else:
    base_path = os.path.dirname(__file__)  

def create_vertical_watermark(c, text): #, watermark_pdf):
    """Create a watermark PDF with vertical text on the right top corner."""
    width, height = A4  # A4 size in points (595x842)
    
    #c = canvas.Canvas(watermark_pdf, pagesize=A4)
    c.setFont("Helvetica", 8)  # Set font and size
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Darker gray
    text_width = c.stringWidth(text, "Helvetica", 8) 

    c.saveState()
    c.translate(width - 15, (height - 220) - text_width)  # Move to top half center
    #c.translate(width - 15, (height - 235) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, text)  # Draw the text
    c.restoreState()

    # Position 2: Center of the bottom half
    c.saveState()
    c.translate(width - 15, (height - 610) - text_width)  # Move to bottom half center
    #c.translate(width - 15, (height - 620) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, text)  # Draw the text
    c.restoreState()

    #c.translate(width - 110, height - 75)   # Position at the right-top corner
    #c.drawString(0, 0, text)  # Draw the watermark text

    #c.save()

def add_watermark_to_pdf(c, input_pdf, output_pdf, watermark_text="CONFIDENTIAL"):
    """Add the watermark to an existing PDF."""
    watermark_pdf = "temp_watermark.pdf"
    create_vertical_watermark(c, watermark_text) #, watermark_pdf)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    #watermark = PdfReader(watermark_pdf).pages[0]

    for page in reader.pages:
        #page.merge_page(watermark)  # Merge the watermark onto each page
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    print(f"Watermarked PDF saved as {output_pdf}")

def draw_barcode(c, pdf_filename, filename):
    #print(f"Barcode updated at {pdf_filename}")
    folder_name = os.path.basename(pdf_filename)
    png_file = Path(pdf_filename) / filename #"0.png" 
    image = Image.open(png_file)
    img_width, img_height = image.size 

    number_part = int(filename.split('.')[0])  # Get the number (0)
    sec_filename = f"{number_part + 1}.png"  # Increment and format
    png_file2 = Path(pdf_filename) / sec_filename

    c.drawImage(png_file, 220, 395, width=150, height=50)
    #c.drawImage(png_file, 220, 5, width=150, height=50)
    
    print(f"PNG files are {png_file} {png_file2} size {img_width} x {img_height}")
    match folder_name:
        case 'SGPM_DN' | 'SPK_DPS':
            #print ("DN DPS")
    #        c.drawImage(png_file, 220, 395, width=150, height=50)
             c.drawImage(png_file2, 220, 5, width=150, height=50)
        case 'SGPT' | 'SPT':
            #print("SGPT")
    #        c.drawImage(png_file, 220, 395, width=150, height=50)
            c.drawImage(png_file, 220, 5, width=150, height=50)
    #c.showPage()
    #c.save()

def create_filled_pdf(input_folder, filename, copy_type, with_bg): #, field_data):
    print(f"create_filled_pdf INPUT : {input_folder} = {with_bg}")
    folder_name = os.path.basename(input_folder)
    image_path = os.path.join(base_path, "Images", f"{folder_name}.pdf")
    name = filename.split(".")[0]
    output_pdf = Path(input_folder) / ( name + ".pdf" )

    # Create a PDF buffer with reportlab
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)

    # Set font and size for writing text
    #c.setFont("Helvetica", 10)
    #print(field_data)

    #print("Draw barcode")
    draw_barcode(c,input_folder, filename) #, field_data)
    # OFFICE COPY , ACCOUNTANT COPY, RECIPIENT COPY
    add_watermark_to_pdf(c, image_path, output_pdf, copy_type)  #"RECIPIENT COPY")
    #pdf_data.print_QR_code(c)
    c.showPage()
    c.save()

    packet.seek(0)
    if packet.getbuffer().nbytes > 0:
        new_pdf = PdfReader(packet)
    else:
        print("The file is empty. Please check the PDF generation process.")

    if with_bg == 0:
        #print("No BG")
        #Blank pdf logic to write on new pdf
        writer = PdfWriter()
        for page in new_pdf.pages:
            writer.add_page(page)
        with open(str(output_pdf), "wb") as f:                     # Save the final filled PDF
            writer.write(f)
    else:
        #print("With BG")
        # Code below this ... is to merge with existing pdf
        existing_pdf = PdfReader(image_path) #f"Images/{folder_name}.pdf")
        writer = PdfWriter()
        for page in existing_pdf.pages:
        # Merge the new PDF with the old PDF (the original form)
            page.merge_page(new_pdf.pages[0])
            writer.add_page(page)

        # Save the final filled PDF
        #print(f"OUTPUT pdf is {output_pdf}")
        try:
            with open(str(output_pdf), "wb") as output_file:
                writer.write(output_file)
            #print("PDF file saved successfully.")
        except PermissionError:
            print("Error: Permission denied. Close the file if it's open and try again.")
        except IOError as e:
            print(f"IO Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
