import tkinter as tk
from datetime import datetime
import configparser
import os
from PIL import ImageFont

current_time = datetime.now().time()
formatted_time = current_time.strftime("%H:%M")
current_date = datetime.now().date()
formatted_date = current_date.strftime("%d.%m.%Y")
formatted_date_no_dots = formatted_date.replace(".", "")

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "config.ini"))
print(config_path)
config = configparser.ConfigParser()
config.read(config_path)
font_path = config.get('FontSettings', 'font_path')
font_name = config.get('FontSettings', 'font_name')
font10 = int(config.get('FontSettings', 'font_size'))
font_size_small = int(config.get('FontSettings', 'font_size_small'))
font12= config.get('FontSettings', 'font_small')
font_size_large = int(config.get('FontSettings', 'font_size_large'))
font_size_xl = int(config.get('FontSettings', 'font_size_xl'))
font_name_bold = config.get('FontSettings', 'font_name_bold')
font11 = int(config.get('FontSettings', 'font_size_bold'))
font_color = config.get('FontSettings', 'font_color')
xcl_file = config.get('Filenames', 'xcl_file')
xcl_sheet = config.get('Filenames', 'xcl_sheet')
banks = config.get('UI', 'banks').split(',')

field_data_hdfc = {
    #'rtgs': 'X',
    'BANK': 'hdfc',
    'hdfc_cust_name': 'Trust', #'hdfc_cust_name',
    'Others': 'Others',
    'time': formatted_time,
    'cust_name': 'Trust',
    'acct_num': '123456789',
    'chq_num': '',
    'mobile': '9234567899',
    #'addr_remitter': 'addr_remitte',
    #'email': 'email@gmail.com',
    #'cash_dep': 'cash_dep',
    'ben_name': '',
    #'ben_addr': 'ben_addr',
    #'ben_acct_num': 'ben_acct_nums',
    #'re-ben_acct_num': 're ben_acct_num Doe',
    'bank_br': '',
    'ifsc_code': '',
    #'acct_type': 'X',
    'purpose': '',
    'amount': '',
    'in_words': ''
    #'remarks': 'Payment for services'
}
field_data_kar = {
    'BANK': 'kar',
    'date': formatted_date,
    'PAN': '',
    'bank_br': 'Kavoor',
    'amount': '',
    'in_words': '',
    'acct_num': '123456789',
    'chq_num': '',
    'chq_date': '',
    'cust_name': 'Trust',
    'addr_remitter': 'addr_remitte',
    'mobile': '9234567899',
    'ben_name': '',
    'ben_acct_num': '6753789',
    'acct_type': 'SB',
    'bank_name': '',
    'ifsc_code': '',
    'ben_bank_br': ''
    #'purpose': '',
}
field_data_canara = {
    'BANK': 'canara',
    'date': formatted_date_no_dots,
    'PAN': 'aaaaaaaaa',
    'bank_br': 'Kavoor',
    'amount': '',
    'in_words': '',
    'acct_num': '123456789',
    'chq_num': '1222222222',
    'chq_date': '',
    'cust_name': 'Trust', 
    'addr_remitter': 'addr_remitte',
    'mobile': '9234567899',
    'cust_name': 'Trust',
    'ben_name': '',
    'ben_acct_num': 'ben_acct_nums',
    're-ben_acct_num': 're ben_acct_num Doe',
    'ben_bank':'',
    'ifsc_code': '',
    'ben_bank_br': ''
    #'purpose': '',
}

field_data_union = {
    'BANK': 'union',
    'bank_br': 'Kavoor',
    'acct_num': '123456789',
    'cust_name': 'Trust', #'hdfc_cust_name',
    'mobile': '9234567899',
    'PAN': 'aaaaaaaaa',
    'amount': '',
    'exchange': '0',
    'total': '',
    'in_words': '',
    'chq_num': '',
    'chq_date': '',
    'ben_acct_num': '1233566',
    'ben_name': '',
    'ben_addr': 'ben_addr',
    'bank_name':'',
    'ben_bank_br': '',
    'ifsc_code': '',
    'date': formatted_date,
    #'purpose': '',
}
