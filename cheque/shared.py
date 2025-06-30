import tkinter as tk
from datetime import datetime

current_time = datetime.now().time()
formatted_time = current_time.strftime("%H:%M")
current_date = datetime.now().date()
formatted_date = current_date.strftime("%d.%m.%Y")
formatted_date_no_dots = formatted_date.replace(".", "")

field_data_hdfc = {
    #'rtgs': 'X',
    'BANK': 'hdfc',
    'hdfc_cust_name': 'SHRI PARASHAKTHI DEGULA PUNARNIRMANA SAMITI', #'hdfc_cust_name',
    'Others': 'Others',
    'time': formatted_time,
    'cust_name': 'SHRI PARASHAKTHI DEGULA PUNARNIRMANA SAMITI',
    'acct_num': '50100128075492',
    'chq_num': '',
    'mobile': '9177199980',
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
    'PAN': 'AAFTS7088F',
    'bank_br': 'Kavoor',
    'amount': '',
    'in_words': '',
    'acct_num': '6052500100794701',
    'chq_num': '',
    'chq_date': '',
    'cust_name': 'SHREE GURUPARASHAKTHI MUTT - DEGULA NIRMANA',
    'addr_remitter': '',
    'mobile': '9177199980',
    'ben_name': '',
    'ben_acct_num': '',
    'acct_type': 'SB',
    'bank_name': '',
    'ifsc_code': '',
    'ben_bank_br': ''
    #'purpose': '',
}
field_data_canara = {
    'BANK': 'canara',
    'date': formatted_date_no_dots,
    'PAN': 'AAFTS7088F',
    'bank_br': 'Kavoor',
    'amount': '',
    'in_words': '',
    'acct_num': '0640101010503',
    'chq_num': '',
    'chq_date': '',
    'cust_name': 'SHREE PARASHAKTHI TRUST', 
    'addr_remitter': '',
    'mobile': '9177199980',
    'cust_name': 'SHREE PARASHAKTHI TRUST',
    'ben_name': '',
    'ben_acct_num': '',
    're-ben_acct_num': '',
    'ben_bank':'',
    'ifsc_code': '',
    'ben_bank_br': ''
    #'purpose': '',
}

field_data_union = {
    'BANK': 'union',
    'bank_br': 'Kavoor',
    'acct_num': '520101002057561',
    'cust_name': 'PRESIDENT SHREE GURUPARASHAKTHI TRUST', #'hdfc_cust_name',
    'mobile': '9177199980',
    'PAN': 'AAFTS7088F',
    'amount': '',
    'exchange': '0',
    'total': '',
    'in_words': '',
    'chq_num': '',
    'chq_date': '',
    'ben_acct_num': '',
    'ben_name': '',
    'ben_addr': '',
    'bank_name':'',
    'ben_bank_br': '',
    'ifsc_code': '',
    'date': formatted_date,
    #'purpose': '',
}
