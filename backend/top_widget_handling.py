import configparser
import os, sys

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\config.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
bank_IFSC = {key: config.get('Bank', key, fallback="HDFC_IFSC") for key in ['HDFC_IFSC', 'KAR_IFSC', 'CNR_IFSC','UBI_IFSC']}