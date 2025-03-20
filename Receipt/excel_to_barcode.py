import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os
import configparser
import tkinter.messagebox as messagebox
import pandas as pd
import barcode
from barcode.writer import ImageWriter
import openpyxl
from PIL import Image, ImageFont, ImageDraw
import canvas_update
global root

root = tk.Tk()
root.title("")

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\\receipt.ini"
custom_font_path = os.path.dirname(os.path.abspath(__file__))+"\config\RobotoMono-Regular.ttf"
config = configparser.ConfigParser()
config.read(configuration_path)
font_name = config.get('FontSettings', 'font_name')
font_size = int(config.get('FontSettings', 'font_size'))
heading = config['Heading']['heading']
pdf_heading = config['Heading']['pdf_heading']
pdf_file = tk.StringVar()

try:
    font = ImageFont.truetype(custom_font_path, 20)
except OSError:
    print(f"Font {custom_font_path} not found, using default.")
    font = ImageFont.load_default()

def submit_file(root, file_path, sheet_name):
    file_path_value = file_path.get()
    sheet = sheet_name.get()  
    print (f"PATH {file_path_value} and sheet is {sheet} ")

    if file_path_value and os.path.isfile(file_path_value):
        process_file(root, file_path_value, sheet)
    else:
        print("Please select a valid file.")
        messagebox.showinfo("Error", "Please select a valid file.")

def get_bar_directory(pdf_filename):
    base_dir = os.getcwd()
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_folder = os.path.join(base_dir, "barcodes", pdf_name_without_ext)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder

def draw_text(barcode_path, text_label):
    barcode_image = Image.open(barcode_path)                # Open the barcode image and get dimensions
    img_width, img_height = barcode_image.size
    new_height = img_height + 40                            # Create a new image with extra space ABOVE the barcode
    new_image = Image.new("RGB", (img_width, new_height), "white")
    draw = ImageDraw.Draw(new_image)
    bbox = draw.textbbox((0, 0), text_label, font=font)     # Get text bounding box
    text_width = bbox[2] - bbox[0]                          # Calculate width
    text_height = bbox[3] - bbox[1] 
    text_x = img_width - (text_width + 35)
    text_y = 20                                             # Place text at the top
    draw.text((text_x, text_y), text_label, fill="black", font=font)
    new_image.paste(barcode_image, (0, 45))                 # Paste barcode BELOW the text
    new_image.save(barcode_path)
  
def process_file(root, file_path, sheet_name):
    pdf_filename = pdf_file.get()
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        workbook = openpyxl.load_workbook(file_path)
        sheet_name = workbook.active
        #file_names = df.iloc[:, 0]
        bar_dir = get_bar_directory(pdf_filename)
        os.makedirs(bar_dir, exist_ok=True)
    except ValueError:
        print("Error: Sheet not found!")
        messagebox.showinfo("Error", f"Sheet '{sheet_name}' not found in the file.")
        return

    column_name = df.columns[0]                             #barcodes are stored in the first column
    for index, row in df.iterrows():
        barcode_data = str(row[column_name])                # Convert to string
        text_label = str(row['TextColumn'])
        code128 = barcode.get_barcode_class('code128')      # Select barcode type
        barcode_obj = code128(barcode_data, writer=ImageWriter())
        options = {                                         # Define barcode settings
            "module_height": 7,                             # ⬅ Reduce barcode height (default: ~50)
            "font_size": 10,                                # Adjust text size below barcode
            "font_path": custom_font_path                   #"C:/Users/RoopaHegde/Downloads/RobotoMono-Regular.ttf",
        }
        file_name = os.path.join(bar_dir, f"{index}")
        file_name_png = os.path.join(bar_dir, f"{index}.png")
        barcode_obj.save(file_name, options=options) 
        draw_text(file_name_png, text_label)

    #pdf_filename = pdf_file.get()
    #print(f"Submit for {pdf_filename}")
    for file in os.listdir(bar_dir):
        if file.lower().endswith(".png"):  # Check for PNG extension
            #print(os.path.join(bar_dir, file))
            canvas_update.create_filled_pdf(bar_dir, file)

    print(f"Barcodes generated and placed successfully at {bar_dir}!")
    messagebox.showinfo("Success", f"PDFs and Barcodes generated successfully at {bar_dir}")

def browse_file(file_path, file_label):
    file = filedialog.askopenfilename(title="Select a file")    # Open file dialog
    if file:                                                    # If a file is selected
        file_path.set(file)                                     # Store the file path in the StringVar
        file_label.config(text=f"Selected file: {file}")        # Update the label to show the selected file

def create_input_field(root):
    entry_label = tk.Label(root, text="Please enter the Sheet name:")
    entry_label.pack(padx=10, pady=5)
    input_field = tk.Entry(root, width=20)                      # Width defines the visible space for text input
    input_field.pack(padx=10, pady=5)
    return input_field

def on_selection(event, selected_heading, pdf_headings):
    index = event.widget.current()
    pdf_file.set(pdf_headings[index])
    #print(f"cval index = {index} and pdf is {pdf_headings[index]}")
    #print("Dropdown 1 Selected:", selected_heading.get())

def start_gui(): 
    # Create a label
    label = tk.Label(root, text="Choose an option:")
    label.pack(padx=10, pady=5)
    selected_heading = tk.StringVar()
    headings = heading.split(',')
    pdf_headings = pdf_heading.split(',')
    #pdf_filename = pdf_headings[0]
    pdf_file.set(pdf_headings[0])

    # Create First Combobox
    dropdown1 = ttk.Combobox(root, values=headings, textvariable=selected_heading, width=40)
    dropdown1.pack(pady=10)
    dropdown1.current(0)
    dropdown1.tk.eval(f"{dropdown1} configure -justify center")
    dropdown1.bind("<<ComboboxSelected>>", lambda event: on_selection(event, selected_heading, pdf_headings))

    file_path = tk.StringVar()
    file_label = tk.Label(root, text="Select a file:")
    file_label.pack(padx=10, pady=5)
    browse_button = tk.Button(root, text="Browse", command=lambda: browse_file(file_path, file_label))
    browse_button.pack(padx=10, pady=5)
    sheet_entry = create_input_field(root)
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_file(root, file_path, sheet_entry)) 
    submit_button.pack(padx=10, pady=10)

    root.mainloop()

start_gui()

