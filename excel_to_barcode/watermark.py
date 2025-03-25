from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import black

def create_vertical_watermark(text, watermark_pdf):
    """Create a watermark PDF with vertical text on the right top corner."""
    width, height = A4  # A4 size in points (595x842)
    
    c = canvas.Canvas(watermark_pdf, pagesize=A4)
    c.setFont("Helvetica", 8)  # Set font and size
    #c.setFillColorRGB(0.6, 0.6, 0.6, 0.5)  # Light gray color with transparency
    c.setFillColorRGB(0.5, 0.5, 0.5)  # Darker gray
    text_width = c.stringWidth(text, "Helvetica", 8) 

    print(f" Text width is {text_width}")
    c.saveState()
    #c.translate(width - 15, (height - 220) - text_width)   # Move to top half center
    c.translate(width - 15, (height - 235) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, text)  # Draw the text
    c.restoreState()

    # Position 2: Center of the bottom half
    c.saveState()
    #c.translate(width - 15, (height - 610) - text_width)   # Move to bottom half center
    c.translate(width - 15, (height - 620) - text_width)    # Office copy dims
    c.rotate(90)  # Rotate vertically
    c.drawString(0, 0, text)  # Draw the text
    c.restoreState()

    c.save()

def add_watermark_to_pdf(input_pdf, output_pdf, watermark_text="CONFIDENTIAL"):
    """Add the watermark to an existing PDF."""
    watermark_pdf = "temp_watermark.pdf"
    create_vertical_watermark(watermark_text, watermark_pdf)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    watermark = PdfReader(watermark_pdf).pages[0]

    for page in reader.pages:
        page.merge_page(watermark)  # Merge the watermark onto each page
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

    print(f"Watermarked PDF saved as {output_pdf}")

# Example usage
add_watermark_to_pdf("Images/SPK_DPS.pdf", "output.pdf", "OFFICE COPY")
