import os
import configparser
from backend import format_amount
from datetime import datetime

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))
config = configparser.ConfigParser()
config.read(config_path)
print(f"PATH = {config_path}")
bank_IFSC = config.get('Bank', 'Bank_IFSC').split(',')

def get_ifsc(bank_idx):
    #print (f"update_ifsc {bank_IFSC[bank_idx]}")
    return bank_IFSC[bank_idx]

def set_rtgs_path():
    print ("set_rtgs_path")

def get_updated_field_data(field_data, top_widget):
    field_data.update({'chq_num': 'cheque no'}) #cheque_back.cheque_entry.get()})
    field_data.update({'ben_name': 'ben_name'}) #cheque_back.payee.get()})
    field_data.update({'ifsc_code': 'ifsc_code'}) #cheque_back.ifsc_Payee_entry.get()})
    #cheque_back_instance = cheque_back.ChequeBack()

    #if isinstance(cheque_back_instance.current_widget, tk.Entry):
    #    field_data.update({'purpose': cheque_back.current_widget.get()})
    #else:
    #    field_data.update({'purpose': cheque_back.purpose_dropdown.get()})
    amt = top_widget.entries[7].text()      #cheque_front.amount_entry.get()

    field_data.update({'amount': amt})
    in_words = format_amount.convert_to_words(amt)
    #wrapped_amount_words = format_amount.wrap_text(in_words, font_small, 100)
    print(f"WRAP = {in_words}")
    field_data.update({'in_words': in_words})
    
    #Bank specific RTGS Data handling
    if field_data['BANK'] == 'hdfc':
        field_data.update({'bank_br': 'HDFC' + " " + 'Bank Branch'})    #cheque_back.bank_entry.get()+ " " + cheque_back.branch_entry.get()})
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
        field_data.update({'PAN': 'GST635247'})         #cheque_back.gst_pan_entry.get()})
        field_data.update({'bank_name': 'Bank' })       #cheque_back.bank_entry.get()})
        field_data.update({'ben_bank_br': 'Branch' })   #cheque_back.branch_entry.get()})

    return field_data
