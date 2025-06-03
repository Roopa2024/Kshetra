Commands to create an EXE:
PS C:\Users\RoopaHegde\OneDrive\Documents\Kshetra\HP_printer\Code_Accounting_SW_Rel2.0_Receipt_Voucher> python -m PyInstaller --add-data="config/receipt.ini:config" 
--add-data="config/RobotoMono-Regular.ttf:config" --add-data="Images/SPT.pdf:Images"  --add-data="Images/SGPM_DN.pdf:Images"  --add-data="Images/SPK_DPS.pdf:Images" 
--add-data="Images/SGPT.pdf:Images" --add-data="Images/SPT_receipt_data.xlsx:Images"  --add-data="Images/SGPM_DN_receipt_data.xlsx:Images"  
--add-data="Images/SPK_DPS_receipt_data.xlsx:Images" --add-data="Images/SGPT_receipt_data.xlsx:Images" --add-data="Images/DebitVoucher_SPT.pdf:Images"  
--add-data="Images/DebitVoucher_SGPM_DN.pdf:Images"  --add-data="Images/DebitVoucher_SPK_DPS.pdf:Images" --add-data="Images/DebitVoucher_SGPT.pdf:Images" 
--add-data="Images/SPT_dv_data.xlsx:Images"  --add-data="Images/SGPM_DN_dv_data.xlsx:Images"  --add-data="Images/SPK_DPS_dv_data.xlsx:Images" 
--add-data="Images/SGPT_dv_data.xlsx:Images" --add-data="canvas_update.py:." --add-data="canvas_update_voucher.py:." --add-data="pdf_data.py:." 
--add-data="excel_data.py:." --add-data="UI_support.py:." --add-data="voucher.py:." .\Receipt_voucher.py

•	Copy the Receipt_voucher.exe (created by the above command in the ./dist folder) to the current folder where you have script, Entity_Receipt_voucher.py
•	Run the following command
PS C:\Users\RoopaHegde\OneDrive\Documents\Kshetra\HP_printer\Code_Accounting_SW_Rel2.0_Receipt_Voucher> python -m PyInstaller --add-data="config/receipt.ini:config" 
.\Entity_Receipt_voucher.py     

•	Copy the 2 exes generated (in the ./dist folder)above into a single folder and also copy the _internal folder of Receipt_voucher.exe into this new single folder.
You will be able to run Entity_Receipt_voucher.exe successfully.
•	You are ready to go now


