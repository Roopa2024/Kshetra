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

def submit_file(root, folder_path, with_bg):
    folder_path = folder_path.get()
    #print (f"PATH {folder_path} ")
    process_file(root, folder_path, with_bg)

def get_bar_directory(pdf_filename):
    base_dir = os.getcwd()
    pdf_name_without_ext = os.path.splitext(pdf_filename)[0]
    output_folder = os.path.join(base_dir, "barcodes", pdf_name_without_ext)
    os.makedirs(output_folder, exist_ok=True)
    return output_folder
  
def process_file(root, bar_dir, with_bg):
    pdf_filename = pdf_file.get()

    for file in os.listdir(bar_dir):
        if file.lower().endswith(".png"):  # Check for PNG extension
            #print(os.path.join(bar_dir, file))
            canvas_update.create_filled_pdf(bar_dir, file, with_bg)

    print(f"PDFs generated successfully at {bar_dir}")
    messagebox.showinfo("Success", f"PDFs generated successfully at {bar_dir}")

def browse_folder(folder_path, folder_label):
    selected_folder  = filedialog.askdirectory()                            # Open folder selection dialog
    if selected_folder :                                                    # If a file is selected
        folder_path.set(selected_folder)                                     # Store the file path in the StringVar
        folder_label.config(text=selected_folder)        # Update the label to show the selected file

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
    checkbox_var = tk.IntVar()
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

    folder_path = tk.StringVar()
    folder_label = tk.Label(root, text="Select the folder with barcodes:")
    folder_label.pack(padx=10, pady=5)
    browse_button = tk.Button(root, text="Browse Folder", command=lambda: browse_folder(folder_path, folder_label))
    browse_button.pack(padx=10, pady=5)
    # Create a Checkbox
    checkbox = tk.Checkbutton(root, text="Include background", variable=checkbox_var)  #, command=on_checkbox_toggle)
    checkbox.pack(pady=10)
    submit_button = tk.Button(root, text="Submit", command=lambda: submit_file(root, folder_path,checkbox_var.get())) 
    submit_button.pack(padx=10, pady=10)

    root.mainloop()

start_gui()
