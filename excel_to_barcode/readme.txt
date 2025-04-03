## Script to generate PDFs with only barcodes integrated. This is required for the initial manual receipt purpose.

Scripts required:
1. canvas_update.py
2. Images/{entity}.pdf        # this is the original pdf, that is the background on which the barcode is to be placed
3. config/receipt.ini
4. config/RobotoMono-Regular    # Font for barcode
5. barcode_app.py

C:\Users\RoopaHegde\OneDrive\Documents\Kshetra\App_Receipt\excel_to_barcode> python .\barcode_app.py

Input file : excel file with Globeid and TextColumn available

Output : generates barcode integrated pdfs, in the folder "barcodes" created in the folder where the script is run.

