import os
import configparser
from backend import format_amount
from datetime import datetime

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
print(f"PATH = {config_path}")
bank_IFSC = config.get('Bank', 'Bank_IFSC').split(',')
import json
SAVE_FILE = "saved_data.json"

def get_ifsc(bank_idx):
    #print (f"update_ifsc {bank_IFSC[bank_idx]}")
    return bank_IFSC[bank_idx]

def set_rtgs_path():
    print ("set_rtgs_path")

def get_value(entry_name):
    """Retrieve a specific value from the JSON file."""
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        
        return data.get(entry_name, "")  # Returns the value or a default message
    
    except (FileNotFoundError, json.JSONDecodeError):
        return #"No data available"
    
def get_updated_field_data(field_data, top_widget):

    field_data.update({'chq_num': get_value('Cheque_entry')}) #'cheque no'}) #cheque_back.cheque_entry.get()})
    field_data.update({'ben_name': get_value('Name1_entry')}) #'ben_name'}) #cheque_back.payee.get()})
    name = top_widget.bottom_widget.bottom_entries[1][2].text() 
    field_data.update({'ifsc_code': name}) #cheque_back.ifsc_Payee_entry.get()})

    amt = top_widget.entries[7].text()      #cheque_front.amount_entry.get()
    field_data.update({'amount': amt})
    in_words = format_amount.convert_to_words(amt)
    print(f"WRAP = {in_words}")
    field_data.update({'in_words': in_words})
    
    #Bank specific RTGS Data handling
    if field_data['BANK'] == 'hdfc':
        field_data.update({'bank_br': get_value('Bank_entry') + " " + get_value('Branch_entry')})#'HDFC' + " " + 'Bank Branch'})    #cheque_back.bank_entry.get()+ " " + cheque_back.branch_entry.get()})
    else:
        selected_date = top_widget.entries[2].date()
        selected_date = selected_date.toPyDate() 
        #date_obj = datetime.strptime(selected_date, "%m/%d/%y")  # Parse the input date
        if 'total' in field_data and field_data['total'] == '':
            field_data.update({'total': amt})
            formatted_date = selected_date.strftime("%d.%m.%y")
            formatted_date = formatted_date.replace(".", "")
        else:
            formatted_date = selected_date.strftime("%d.%m.%Y")

        field_data.update({'chq_date': formatted_date})
        field_data.update({'PAN': get_value('PAN_entry')})         #cheque_back.gst_pan_entry.get()})
        field_data.update({'bank_name': get_value('Bank_entry') })       #cheque_back.bank_entry.get()})
        field_data.update({'ben_bank_br': get_value('Branch_entry') })   #cheque_back.branch_entry.get()})

    return field_data

def add_to_json(entry_key, text):
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            print("JSON data", data)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}                       
    data[entry_key] = text          # Store the new value
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)  # Save data persistently
    print("Saved in JSON:", entry_key, text)

def delete_from_json(entry_key, text):
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)  # Load existing data
            print("JSON data before deletion:", data)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}  # Initialize empty data if file is missing or corrupt

    # Remove the entry if it exists
    if entry_key in data:
        del data[entry_key]
        print(f"Deleted entry: {entry_key}")

    # Save the updated data back to the JSON file
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)  # Save changes with formatting

    print("Updated JSON data after deletion:", data)

def read_json():
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            print("Retrieved from JSON:", data.get("Name1_entry", "NA"))
            print("Retrieved Data:", data)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No saved data found.")
