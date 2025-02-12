import tkinter as tk
from num2words import num2words
from tkinter import messagebox

# Custom function to convert number to INR words (Indian Rupees in English)
def convert_to_words(amount):
    try:
        amount = int(amount)
    except ValueError:
        messagebox.showerror("Amount Error", "Please enter a valid amount.")
        return
    # Split the amount into whole and fractional parts
    whole_number = int(amount)
    fraction_part = round((amount - whole_number) * 100)  # Getting the fraction part as Paise
    # Convert whole number into words in English
    whole_in_words = num2words(whole_number, lang='en_IN')
    # Capitalize the first letter of each word
    capitalized_number = whole_in_words.title()
    # Convert fraction part (Paise) into words if it's non-zero
    if fraction_part > 0:
        fraction_in_words = num2words(fraction_part, lang='en_IN')
        capitalized_fractions = fraction_in_words.title()
        result = f"{capitalized_number} Rupees {capitalized_fractions} Paise"
    else:
        result = f"{capitalized_number} Rupees"

    return result

def wrap_text(text, font, max_width):
    """
    Wrap the text to fit within the given max_width using the textbbox method to calculate text width.
    """
    lines = []
    words = text.split()
    current_line = words[0]

    for word in words[1:]:
        # Check width of current line with the next word
        test_line = current_line + " " + word
        bbox = font.getbbox(test_line)  # Get the bounding box of the text
        line_width = bbox[2] - bbox[0]  # Calculate the width of the text (difference in x coordinates)

        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)  # Add the last line
    return lines

def format_number(number):
    # For Indian formatting, start by reversing the string
    number = number[::-1]
    
    # Format the first three digits
    formatted_number = number[:3]

    # Add commas every two digits after the first three digits
    for i in range(3, len(number), 2):
        formatted_number += ',' + number[i:i+2]

    # Reverse the number again to restore original order and return
    return formatted_number[::-1]