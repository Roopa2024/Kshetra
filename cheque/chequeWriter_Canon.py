import tkinter as tk
from tkinter import ttk
from tkinter import font 
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from cheque import cheque_front, excel_con, cheque_back, bank_handling
import cheque.cheque_front
import cheque.rtgs_handling
import os, sys

import win32api
import win32print
import win32ui
import ctypes
from ctypes import wintypes
    
# Function to print the generated Cheque
def print_cheque(cheque_image_path):
    printer_name = win32print.GetDefaultPrinter()  # Get default printer
    print(f"Default Printer: {printer_name}")
    # Call the Windows Print Dialog
    win32api.ShellExecute(0, "open", cheque_image_path, None, ".", 1) #'/d:"%s"' % printer_name, ".", 0)
    
    #open_native_print_dialog()
    #print("Printer properties dialog opened.")
    #messagebox.showinfo("Printing", "Cheque sent to the printer.")

def open_native_print_dialog():
    class PRINTDLGEX(ctypes.Structure):
        _fields_ = [
            ("lStructSize", wintypes.DWORD),
            ("hwndOwner", wintypes.HWND),
            ("hDevMode", wintypes.HGLOBAL),
            ("hDevNames", wintypes.HGLOBAL),
            ("hDC", wintypes.HDC),
            ("Flags", wintypes.DWORD),
            ("nFromPage", wintypes.WORD),
            ("nToPage", wintypes.WORD),
            ("nMinPage", wintypes.WORD),
            ("nMaxPage", wintypes.WORD),
            ("nCopies", wintypes.WORD),
            ("hInstance", wintypes.HINSTANCE),
            ("lCustData", wintypes.LPARAM),
            ("lpfnPrintHook", wintypes.LPVOID),
            ("lpfnSetupHook", wintypes.LPVOID),
            ("lpPrintTemplateName", wintypes.LPCWSTR),
            ("lpSetupTemplateName", wintypes.LPCWSTR),
            ("hPrintTemplate", wintypes.HGLOBAL),
            ("hSetupTemplate", wintypes.HGLOBAL),
        ]

    pd = PRINTDLGEX()
    pd.lStructSize = ctypes.sizeof(PRINTDLGEX)
    pd.Flags = 0x00000002  # PD_RETURNDC: Return a printer device context
    pd.nMinPage = 1
    pd.nMaxPage = 1
    pd.nCopies = 1

    # Open the print dialog
    result = ctypes.windll.comdlg32.PRINTDLGEX(ctypes.byref(pd))
    if result:
        print("Print dialog opened successfully.")
    else:
        print("Failed to open print dialog.")

# GUI setup
root = tk.Tk()
root.title("Cheque Printing Software")
root.geometry("1000x600")

#cheque_front.root = root 
#####FRONT PAGE
#cheque_front.
bank_handling.set_base_path()
cheque_front.UI_front(root)
#cheque.cheque_front.update_background(event=None)
# Access the IFSC value
print(f"Front page IFSC is {cheque_front.IFSC}")

#BACK PAGE
cheque_back.UI_back(root)

# Run the application
root.mainloop()
