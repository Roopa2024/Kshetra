import tkinter as tk
from tkinter import ttk
import os

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

def open_second_window(func_name):
    print (f"Sec window opened {func_name}")
    if func_name == 'cheque':
        #os.system("python run_chequeWriter.py")
        os.system("python PyQt_chequeWriter.py")
    else:
        print(f"Function {func_name} not found!")
# Function to open the new window
def open_new_window():
    # Create a new top-level window
    new_window = tk.Toplevel(root)
    new_window.title("")
   
    new_window.bind("<F11>", lambda event: toggle_maximize_restore(new_window, event))  # Bind the F11 key to toggle maximize/restore
    screen_width, screen_height = get_screen_size()
    new_window.geometry(f"{screen_width}x{screen_height}+0+0")  # You can adjust the size as per your requirement

    # Create a main frame to hold everything
    main_frame = tk.Frame(new_window)
    main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    # Configure the grid of the main frame to have 2 rows (top and bottom)
    main_frame.grid_rowconfigure(0, weight=1)  # Top half
    main_frame.grid_rowconfigure(1, weight=1)  # Bottom half
    main_frame.grid_columnconfigure(0, weight=1)  # To make the column stretch

    # Frame 1: This is the top frame
    frame1 = tk.Frame(main_frame, bg="lightblue")
    frame1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
    label = tk.Label(frame1, text="Expense", font=("Arial", 14))     # Add a label to the new window
    label.grid(row=0, column=0, padx=20, pady=20)
    
    names = ["Cheque", "Cash", "Online", "Cheque", "Cash", "Online"]
    func_names = ["cheque"]

    # Create 3 buttons in frame1
    for i in range(3):
        button = tk.Button(frame1, text=f" {names[i]}", command=lambda i=i: [button_click(f"{names[i]}"), open_second_window(func_names[i])], font=("Arial", 13), width=35, height=4)
        button.grid(row=1, column=i, padx=30, pady=50, sticky="ew")  # Place buttons in grid

    # Frame 2: This will be placed below frame1, containing 3 buttons
    frame2 = tk.Frame(main_frame, bg="lightblue")
    frame2.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")  # Use grid to place frame2
    label2 = tk.Label(frame2, text="Income", font=("Arial", 14))
    label2.grid(row=0, column=0, padx=20, pady=10)

    # Create 3 buttons in frame2
    for i in range(3, 6):
        button = tk.Button(frame2, text=f"{names[i]}", command=lambda i=i: [button_click(f"{names [i]}"), open_second_window()], font=("Arial", 13), width=35, height=4)
        button.grid(row=1, column=i-3, padx=30, pady=50, sticky="ew")  # Place buttons in grid in the second frame

    # Ensure the frames expand vertically and horizontally as needed
    main_frame.grid_rowconfigure(0, weight=1, uniform="equal")
    main_frame.grid_rowconfigure(1, weight=1, uniform="equal")
    main_frame.grid_columnconfigure(0, weight=1, uniform="equal")

# Function to be called when button is clicked
def button_click(button_name):
    print(f"{button_name} clicked!")
    
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

button_names = ["SPM", "SPK", "SGPM", "SGPT", "DVA"]
# Create 5 buttons and place them in the grid
buttons = []
for i in range(5):
    button = tk.Button(frame, text=f"{button_names[i]}", command=lambda i=i: [button_click(f"{button_names[i]}"), open_new_window()], font=("Arial", 13), width=50, height=2)
    buttons.append(button)
    button.grid(row=i, column=0, pady=35, padx=70)  # Place buttons in a single column

# Start the Tkinter event loop
root.mainloop()
