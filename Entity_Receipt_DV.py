import tkinter as tk
from tkinter import messagebox
import os, configparser, getpass, sys, subprocess

# Load configurations
config_path = os.path.join(os.path.dirname(__file__), "config", "receipt.ini")
config = configparser.ConfigParser()
config.read(config_path)
option = config['Heading']['options']
options = option.split(',')
heading = config['Heading']['heading']
button_names = heading.split(',')
font_settings = (config.get('FontSettings', 'font_name'), config.getint('FontSettings', 'font_size'))

# Configuration to limit Access based on Login 
allowed_user = config['Access']['user']
allowed_users = allowed_user.split(',')
current_user = getpass.getuser()
sgpm_dn = config['Access']['SGPM_DN']
spk_dps = config['Access']['SPK_DPS']
all = config['Access']['ALL']
all_access = all.split(',')

def get_screen_size():
    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    return screen_width, screen_height

def toggle_maximize_restore(window, event=None): #event=None
    # Check if the window is maximized
    if window.state() == 'normal':
        # Maximize the window
        window.state('zoomed')
    else:
        # Restore the window to its normal state
        window.state('normal')
        screen_width, screen_height = get_screen_size()
        window.geometry("800x400")  # Set the size of the normal window to 1200x800

def open_second_window(entity, index):
    #os.system(f"python Receipt_DV.py {entity} {index}")
    os.system(f".\App_receipt\Receipt_DV.exe {entity} {index}")
    print(f"Entity = {entity} and idx = {str(index)}")
    #subprocess.Popen(["Receipt_DV.exe", entity, str(index)])

# Function to be called when button is clicked
def button_click(button_name):
    print(f"{button_name} clicked!")
    
# Access check for the App
print (f"User is {current_user}")
if current_user not in allowed_users:
    print(f"Access denied for user: {current_user}")
    messagebox.showinfo(f"Error:", f"Access denied for user: {current_user}")
    sys.exit(1)

# Create the main window
root = tk.Tk()
root.title("App")

# Bind the F11 key to toggle maximize/restore
root.bind("<F11>", lambda event: toggle_maximize_restore(root, event))

screen_width, screen_height = get_screen_size()
# Set the window size to the screen size
root.geometry(f"{screen_width}x{screen_height}+0+0")

# Create a Frame to hold the buttons
frame = tk.Frame(root, bg="lightblue")
frame.pack(anchor='w', fill='both', expand=True)

if current_user == sgpm_dn:
    buttons_to_disable = [1, 2, 3]
elif current_user == spk_dps:
    buttons_to_disable = [0, 2, 3]
elif current_user in all_access:
    buttons_to_disable = []

# Create 4 buttons and place them in the grid
buttons = []
for i in range(4):
    # Check if this button should be disabled
    should_disable = i in buttons_to_disable

    button = tk.Button(frame, text=f"{button_names[i]}", command=lambda i=i: [button_click(f"{button_names[i]}"), 
        open_second_window(options[i], i)], font=("Arial", 13), width=50, height=2, state="disabled" if should_disable else "normal")
    buttons.append(button)
    button.grid(row=i, column=0, pady=35, padx=70)  # Place buttons in a single column

# Start the Tkinter event loop
root.mainloop()
