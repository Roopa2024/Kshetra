from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io, os, sys
from pathlib import Path
from PIL import Image  
import pdf_data

# Get the base path (different for script vs. executable)
if getattr(sys, 'frozen', False):  # Running as a PyInstaller .exe
    base_path = sys._MEIPASS  
else:
    base_path = os.path.dirname(__file__)  

def draw_barcode(c, pdf_filename, filename):
    #print(f"Barcode updated at {pdf_filename}")
    folder_name = os.path.basename(pdf_filename)
    png_file = Path(pdf_filename) / filename #"0.png" 
    image = Image.open(png_file)
    img_width, img_height = image.size 

    #print(f"PNG file is {png_file} size {img_width} x {img_height}")
    match folder_name:
        case 'SGPT_DN' | 'SPK_DNS':
            #print ("DN DNS")
            c.drawImage(png_file, 220, 422, width=150, height=50)
            c.drawImage(png_file, 220, 2, width=150, height=50)
        case 'SGPT' | 'SPT':
            #print("SGPT")
            c.drawImage(png_file, 220, 424, width=150, height=50)
            c.drawImage(png_file, 220, 4, width=150, height=50)
    c.showPage()
    c.save()

def create_filled_pdf(input_folder, filename, with_bg): #, field_data):
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
    #pdf_data.print_QR_code(c)

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
