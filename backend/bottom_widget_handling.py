import os
import configparser

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
