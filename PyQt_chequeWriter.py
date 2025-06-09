from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QDesktopWidget, QLineEdit, QDateEdit, QSizePolicy, QGridLayout, QSpacerItem, QComboBox, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QPointF, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QDoubleValidator
from functools import partial
import os, sys
import configparser

from backend import bottom_widget_handling, side_widget_handling
import json
SAVE_FILE = "saved_data.json"

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\config.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
headers = config.get('UI', 'headers').split(',')
labels = config.get('UI', 'labels').split(',')
banks = config.get('UI', 'banks').split(',')
toggle = config.get('UI', 'toggle').split(',')
rows_columns = list(map(int, config.get('UI', 'rows_columns').split(',')))
#combo1 = config.get('UI', 'combo1').split(',')
#combo2 = config.get('UI', 'combo2').split(',')
#combo3 = config.get('UI', 'combo3').split(',')
#code = config.get('UI', 'code').split(',')
combo_options = config.get('UI', 'combo_options').split(',')
bank_bg_path = config.get('Bank', 'Bank_bg_path').split(',')
entries = config.get('UI', 'entries').split(',')
#entries = ["Name1_entry", "Bank_entry", "Branch_entry", "IFSC_entry"]
checkbox = config.get('UI', 'checkbox').split(',')
Exp_type = config.get('Purchase', 'Exp_type').split(',')
purchase_ph = config.get('Purchase', 'purchase_ph').split(',')
Administration = config.get('Purchase', 'Administration').split(',')
#purchase_pc1 = config.get('Purchase', 'purchase_pc1').split(',')

class TopWidget(QWidget):
    date_changed_signal = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.show_ac_payee = True               # Initial flag state

        self.bottom_widget = BottomWidget(top_widget=self, parent=self)  # Moved down to be able to read entries
        ##self.side_widget = SideWidget(self)
        ##widget = QWidget(self)
        layout = QGridLayout()

        # Load background image using PaintEvent
        self.setFixedSize(1500, 500)
        self.set_background(bank_bg_path[0], 0)

        #self.setVisible(True)
        #print(f"TW: visible {self.isVisible()}")
        # Initially, you can hide it
        #self.bottom_widget.setVisible(True)  

        self.entries = []
        for i in range (11):
            if i == 2:
                line_edit = QDateEdit(self)
                line_edit.setDate(QDate.currentDate()) 
                line_edit.setFixedSize(300, 40)
                # Connect dateChanged signal to function
                line_edit.dateChanged.connect(self.emit_date_change) #update_date)
                #self.label = QLabel(f"{line_edit.date().toString('yyyy-MM-dd')}", self)
            else:
                line_edit = QLineEdit(self)
                line_edit.setPlaceholderText(f"Enter text {i}")
                line_edit.setMaximumSize(400, 50)
            self.entries.append(line_edit)  # Add to the list
            print(f" Top widget INDX = {i}  Value ='{line_edit.text()}'")

        self.entries[4].setPlaceholderText("Payee") 
        self.entries[4].setFixedSize(500, 40)
        self.entries[7].setPlaceholderText("Amount") 
        validator = QDoubleValidator()                                      # Allows only integer input
        validator.setNotation(QDoubleValidator.StandardNotation)            # Prevents 'e'
        self.entries[7].setValidator(validator)

        print("TopWidget entries:", self.entries[2].text())

        # Add widgets to the grid layout
        self.spacer = QSpacerItem(0, 90, QSizePolicy.Minimum, QSizePolicy.Fixed) 
        layout.addItem(self.spacer)
        layout.addWidget(self.entries[0], 0, 0, 1, 2 )
        layout.addWidget(self.entries[1], 0, 2)  
        layout.addWidget(self.entries[2], 0, 3)  
        layout.addWidget(self.entries[3], 1, 0) #, 1, 2) 
        layout.addWidget(self.entries[4], 1, 1)
        layout.addItem(self.spacer)
        layout.addWidget(self.entries[5], 2, 0,1,2)  
        layout.addWidget(self.entries[6], 2, 2)
        layout.addWidget(self.entries[7], 2, 3)  
        self.spacer = QSpacerItem(0, 90, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(self.spacer)
        layout.addWidget(self.entries[8], 3, 0) 
        layout.addItem(self.spacer)
        layout.addWidget(self.entries[9], 4, 0)
        layout.addItem(self.spacer)
        layout.addWidget(self.entries[10], 5, 0)

        layout.setAlignment(self.entries[2], Qt.AlignCenter)
        layout.setAlignment(self.entries[4], Qt.AlignLeft)
        layout.setAlignment(self.entries[7], Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(1500, 500) 
        print("TopWidget entries 2 :", self.entries[2].text())

        for index in range(11):
            if index not in [2,4,7]:
                self.entries[index].setVisible(False)
                print(f"INDEX TW = {index} : {self.entries[index].isVisible()}")

        #self.bottom_widget = BottomWidget(top_widget=self, parent=self)  # Pass reference of TopWidget

    def emit_date_change(self, new_date: QDate):
        """Emit signal when date is changed."""
        print(f"🔄 Date changed to: {new_date.toString('yyyy-MM-dd')}")  # Debugging
        self.date_changed_signal.emit(new_date)

    def update_date(self, new_date):
        self.selected_date = new_date.toString("yyyy-MM-dd")
        print(f"TopWidget Updated Date: {self.selected_date}")
        self.date_changed_signal.emit(self.selected_date)

    def set_background(self, image_path, IFSC):
        print(f"Function to set new background image {image_path} and {IFSC}")
        abs_image_path = os.path.abspath(image_path).replace("\\", "/")
                
        if not os.path.exists(abs_image_path):
            print(f"Error: Image path does not exist: {abs_image_path}")
            return 
        
        self.bg_pixmap = QPixmap(abs_image_path)
        print(f"set_background: new background image {abs_image_path}")

        if self.bg_pixmap.isNull():  # Debug: Check if loading failed
            print(f"set_background: Failed to load image: {abs_image_path}")
        else:
            print(f"set_background: Image updated to {self.bg_pixmap}")

        #if IFSC != 0 and hasattr(self.bottom_widget, "bottom_entries"):  # Ensure BottomWidget has entries
        #    #print(f"set_bg : Found it at {self.bottom_widget.entries[1][2].text()} and set it to {IFSC}")
        #    self.bottom_widget.bottom_entries[1][2].setStyleSheet("")
        #    self.bottom_widget.bottom_entries[1][2].clearFocus()
        #    self.bottom_widget.bottom_entries[1][2].setText(IFSC)
        #    self.bottom_widget.bottom_entries[1][2].setFocus()
        #    self.bottom_widget.bottom_entries[1][2].update()
        #    #QApplication.processEvents()
        #    self.bottom_widget.bottom_entries[1][2].editingFinished.emit()
        #    # Some background process happens...
        #    self.bottom_widget.update_button.click()  # Triggers manual_update()
        #else:
        #    self.IFSC = bottom_widget_handling.get_ifsc(0)
        #    print("entries not found in BottomWidget")

        #print(f"IFSC after change is {self.bottom_widget.bottom_entries[1][2].text()}")
        self.update() 
        self.paintEvent(None)
    
    def toggle_ac_payee(self):
        print("toggle_ac_payee")
        self.show_ac_payee = not self.show_ac_payee  # Toggle visibility flag
        self.update()
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background image first
        painter.drawPixmap(0, 0, self.width(), self.height(), self.bg_pixmap)
        #print (f"paintEvent : Image updated {self.bg_pixmap}")
        font = QFont('Arial', 12)                                   # Set the font for the text
        painter.setFont(font)

        if self.show_ac_payee: 
            painter.setPen(QColor(0, 0, 0))                             # Set pen to black for lines
            painter.drawLine(0, 80, 80, 0)                              # First slanting line
            painter.drawLine(0, 120, 120, 0)                            # Second slanting line

            text_position = QPointF(10, 100)                            # Position where you want to draw the text
            painter.translate(text_position)
            painter.rotate(-45)                                         # Negative value for rotating upwards
            painter.drawText(0, 0, "A/C Payee")                         # Draw the text

            painter.resetTransform()                                    # Reset the rotation before drawing the lines

            text_position = QPointF(100, 100)
            painter.translate(text_position)
            painter.drawText(1200, 55, "XXXXXXXXXX")

        painter.end()

class BottomWidget(QWidget):
    def __init__(self, top_widget, parent=None):
        super().__init__(parent)
        self.top_widget = top_widget 
        #print("BottomWidget entries:", self.top_widget.entries[2].text())

        widget = QWidget(self)
        layout = QGridLayout()
        self.setLayout(layout)

        #self.top_widget.setVisible(True)
        self.setVisible(True)

        column = 0
        for i in range(3):
            header_label = QLabel(headers[i], self)
            #font = QFont()
            font = QFont("Arial", 10, QFont.Bold)
            font.setUnderline(True)
            header_label.setFont(font)
            header_label.setStyleSheet("text-decoration: underline;")
            layout.addWidget(header_label, 0, column,1,2)
            header_label.setFixedSize(300, 20)
            header_label.setAlignment(Qt.AlignTop | Qt.AlignCenter)
            column = column + 2

        widget_counter = 0
        self.bottom_entries = [] 
        self.stored_values = {}

        #def add_to_json(entry_key, text):  ## to be removed once tested without issues

        def on_text_changed(entry_key, x, y):
            Value = self.sender()  # Get the widget that triggered the event
            if Value:
                text = Value.text() 

            bottom_widget_handling.add_to_json(entry_key, text)

        for row, col_count in enumerate(rows_columns, start=1):             # Iterate through rows (4 rows in total)
            row_entries = []
            for col in range(col_count):                              # For each row, iterate through the number of columns
                widget_counter, row_entries = self.add_fields(labels[widget_counter], col, row, layout, widget_counter, row_entries)
            self.bottom_entries.append(row_entries)
        r = 0
        for i in range(3):                              # Looping through 4 rows to get updated values from the UI
            for j in range(4):
                    self.bottom_entries[j][i].editingFinished.connect(lambda j=j, name=entries[r]: on_text_changed(name, j, i))
                    r = r + 1
        self.bottom_entries[0][3].editingFinished.connect(lambda name=entries[12]: on_text_changed(name, 0, 3))
        self.bottom_entries[1][3].editingFinished.connect(lambda name=entries[13]: on_text_changed(name, 1, 3))

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(vertical_spacer, 5, 0, 1, 2)
        layout.setSpacing(20)

        self.setStyleSheet("background-color: white;")
        widget.setLayout(layout)
        widget.setFixedSize(1500, 500)

    def get_date_from_top(self):
        """Retrieve date from the top widget."""
        date_value = self.top_widget.entries[2].text()
        print("Date from top widget:", date_value)
        return date_value

    def update_date(self, new_date: QDate):
        selected_date = new_date.toString("yyyy-MM-dd")
        """Update label when the date changes."""
        #if isinstance(new_date, str):  # ✅ Convert string to QDate if necessary
        #    new_date = QDate.fromString(new_date, "yyyy-MM-dd")
        #formatted_date = new_date.toString("yyyy-MM-dd") 
        #label1 = QLabel(selected_date, self)
        self.bottom_entries[0][3].setText("{selected_date}")
        self.bottom_entries[0][3].update()
        self.bottom_entries[0][3].repaint()
        QApplication.processEvents()

        #self.top_widget.entries[2].setText("{selected_date}")
        if len(self.top_widget.entries) > 2 and isinstance(self.top_widget.entries[2], QDateEdit):
            self.top_widget.entries[2].setDate(new_date)  # ✅ Use setDate() instead of setText()
            print(f"✅ Updated TopWidget date entry to: {selected_date}")
        else:
            print("❌ TopWidget does not have a QDateEdit at index 2!")
        print(f"✅ BottomWidget updated with: {selected_date}") 

    def add_fields(self, label_name, col, row, layout, widget_counter, row_entries):
        label = QLabel(label_name, self)
        layout.addWidget(label, row, col * 2)                                 # Place label in column (2 * col)
        label.setMaximumSize(150, 30)
        label.setVisible(True) 
        #if label_name == 'Cheque Date:':
        #        print ("Label is", label_name, row, col)
        #    #self.IFSC = bottom_widget_handling.get_ifsc(0)
        #    date = self.get_date_from_top()
        #    label1 = QLabel(date, self)
        #    layout.addWidget(label1, row, col * 2 + 1) 
        #    row_entries.append(label1)
        #else:
        line_edit = QLineEdit(self)
        line_edit.setStyleSheet("border: 2px solid black;")
        layout.addWidget(line_edit, row, col * 2 + 1)
        line_edit.setMaximumSize(200, 30)
        line_edit.setVisible(True)
        row_entries.append(line_edit)
        #if label_name == 'IFSC:': 
            #self.IFSC = bottom_widget_handling.get_ifsc(0)
            #line_edit.setVisible(True)
            #line_edit.setText(self.IFSC)    
        
        #QTimer.singleShot(100, self.ensure_visibility)
        widget_counter += 1
        return widget_counter, row_entries
    
    def force_focus_loss(self):
        for row_entries in self.bottom_entries:
            for entry in row_entries:
                entry.clearFocus() 

    def handle_button_click(self, label, btn):
        print(f"Button {label} clicked")
        self.force_focus_loss()  # Ensure all fields register their input
        QTimer.singleShot(100, self.fetch_entries)

    def fetch_entries(self):
        values = self.get_all_entries()
        print("Latest values after delay:", values)

    def get_all_entries(self):
        all_values = []
        for row_entries in self.bottom_entries:
            row_values = [entry.text().strip() for entry in row_entries if isinstance(entry, QLineEdit)]
            all_values.append(row_values)
        print("DEBUG: Retrieved Values:", all_values)
        return all_values

    def get_all_entries1(self):
        all_values = []
        print (f" VALUE = {self.bottom_entries[0][2].text()}")
        #print(f"VALUE = {values}")
        for i, row_entries in enumerate(self.bottom_entries):
            row_values = []
            for j, entry in enumerate(row_entries):
                if isinstance(entry, QLineEdit):  # Ensure it's a valid input field
                    text = entry.text().strip()  
                    print(f"Debug - Row {i}, Col {j}, Value: '{text}'")  # Debugging
                    row_values.append(text)
                else:
                    print(f"Error: Entry at Row {i}, Col {j} is not a QLineEdit")
                    row_values.append(None)
            all_values.append(row_values)
        print("Final Retrieved Values:", all_values)
        return all_values

    def update_ifsc(self, IFSC):
        #super().paintEvent(event)  # Call parent method
        self.IFSC = IFSC
        print(f"update_ifsc {self.IFSC}")
        if hasattr(self, "entries"):
            if len(self.bottom_entries) > 1 and len(self.bottom_entries[1]) > 2:
                entry = self.bottom_entries[1][2]
                entry.setVisible(True)
                entry.setEnabled(True)
                entry.setReadOnly(False)
                print(f"Updating text field: {entry.isVisible()}")
                entry.setText(IFSC)
                entry.hide()  # Hide first
                entry.show()  # Then show
                #self.entries[1][2].textEdited.connect(lambda: self.update_ifsc(IFSC))
                entry.update()            # Request update
                #entry.repaint()
                QApplication.processEvents()
            else:
                print("Entries list is not structured as expected!")
        else:
            print("BottomWidget does not have 'entries' attribute yet!")
        
        self.update()
        #self.repaint()
        QApplication.processEvents()

    #def paintEvent(self, event):
    #    """Handle custom painting"""
    #    super().paintEvent(event)  
    #    if self.IFSC:
    #        print("BottomWidget repaint triggered!") 

    def ensure_visibility(self):
        """Ensure all entries are visible after the event loop starts"""
        for row in self.bottom_entries:
            for entry in row:
                entry.setVisible(True)
                print(f"Entry Visible: {entry.isVisible()}")  # Now should return True

    #def on_text_changed(self):
    #    print("Text entered:", self.bottom_entries[1][1].text())

class SideWidget(QWidget):
    def __init__(self, top_widget, parent=None):
        super().__init__(parent)
        self.combo_boxes = {} 
        self.code_print = 0
        self.desc_print = 0
        self.top_widget = top_widget 
        self.current_date = "" 
        self.cross = 1
        if hasattr(self.top_widget, "bottom_widget"):
            self.bottom_widget = top_widget.bottom_widget
        else:
            print("Warning: `bottom_widget` is not initialized in `top_widget`.")

        widget = QWidget(self)
        self.layout = QGridLayout()
        self.use_stored_date()

        #causing extra screen
        #top_widget.setVisible(True)
        self.bottom_widget.setVisible(True)
        self.bottom_widget.bottom_entries[1][2].setVisible(True)
        #print(f"SW: SideWidget {self.isVisible()}")
        #print(f"SW: TopWidget visible: {top_widget.isVisible()}")
        #print(f"SW: BottomWidget visible: {self.bottom_widget.isVisible()}")
        #print(f"Entry visible: {self.bottom_widget.bottom_entries[1][2].isVisible()}")

        self.combo_box = QComboBox(self)                # Bank drop down
        for i in range(4):
            self.combo_box.addItem(banks[i])
        self.combo_box.setFixedSize(200, 40)
        self.IFSC = 0
        self.combo_box.currentIndexChanged.connect(lambda: self.update_background(self.bottom_widget))
        self.layout.addWidget(self.combo_box,0,0,1,2)

        #self.top_widget = TopWidget(self)
        self.toggle_buttons = []                        # Store all Toggle buttons
        j = 0
        for i in range(7):
            btn = QPushButton("OFF", self)  # Create a new button
            btn.setStyleSheet("background-color: orange; color: black;")
            label_name = toggle[i]
            label = QLabel(toggle[i], self)
            btn.setFixedSize(100, 40)
            btn.setCheckable(False)
            print(f"Side Widget INDX = {i} , Label = {label_name}, Button = {btn}")
            if label_name == "A/C Payee":
                btn.setText("ON") 
                btn.setStyleSheet("background-color: green; color: black;")
                cross = side_widget_handling.set_cross()
            btn.clicked.connect(lambda checked=False, b=btn, lbl=label_name: side_widget_handling.toggle_button_state(b, lbl, self.bottom_widget, top_widget, self.combo_box.currentIndex()))
            j = j+1
            self.layout.addWidget(label, j, 0)
            self.layout.addWidget(btn, j, 1)
        self.spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        #layout.addItem(self.spacer)

        self.print_button = QPushButton("PRINT - Front", self)  # Print-Front button
        self.print_button.setStyleSheet(""" QPushButton {
                border: 2px solid blue; border-radius: 5px; padding: 5px; background-color: white;
            } """)
        self.print_button.setFixedSize(300, 40)
        self.print_button.clicked.connect(partial(side_widget_handling.generate_cheque_front, self.IFSC, self.current_date, self.top_widget))
        i = i+2
        self.layout.addWidget(self.print_button,i,0,1,2)
        self.layout.addItem(self.spacer)

        i = i+1
        for count in range(3):
            self.checkbox = QCheckBox(checkbox[count], self)
            self.checkbox.stateChanged.connect(lambda state, item=checkbox[count]: self.on_checkbox_state_changed(state, item))
            self.layout.addWidget(self.checkbox,i,0)
            i = i+1
        
        self.label = QLabel(Exp_type[0], self)              # Expense drop down
        self.label.setFixedSize(100, 30)
        self.label.setStyleSheet("text-decoration: underline;")
        i=i+1
        self.layout.addWidget(self.label,i,0)
        i = i+1
        self.create_dropdown(self.layout, Exp_type, 3, i, 0)
        
        self.label = QLabel("Classification Type", self)
        self.label.setStyleSheet("text-decoration: underline;")
        i=i+1
        self.layout.addWidget(self.label,i,0)
        i= i+1

        indx = 2
        combo_lists = [purchase_ph, Administration] #, combo3]
        #combo_entries = [15, 23, 5]
        combo_entries = [22,3]
        for n in range(2):
            self.create_dropdown(self.layout, combo_lists[n], combo_entries[n], i+n,0)
            indx= indx+1

        i=i+3
        #i = self.create_fields("Code:", self.layout, i)
        i = self.create_fields("Description:", self.layout, i)
        self.layout.addItem(self.spacer)

        #date = self.top_widget.label
        #print(f" DATE is {self.top_widget.selected_date}")

        self.print_button = QPushButton("PRINT - Back ", self)
        self.print_button.setStyleSheet("""
            QPushButton {
                border: 2px solid blue;  border-radius: 5px; padding: 5px; background-color: white;
            } """)
        self.print_button.setFixedSize(300, 40)
        # Print - Back button
        #self.print_button.clicked.connect(partial(side_widget_handling.generate_cheque_back, self.IFSC, self.current_date, self.top_widget, self.code_print, self.desc_print)) 
        self.print_button.clicked.connect(lambda: side_widget_handling.generate_cheque_back(self.IFSC, self.current_date, self.top_widget, self.code_print, self.desc_print))
       
        self.layout.addWidget(self.print_button,i+10,0,1,2)
        
        self.setStyleSheet("background-color: white;")
        widget.setLayout(self.layout)

    #def update_date_label(self, new_date):
    #    #self.label.setText(f"Date: {new_date}")  # Update label dynamically
    #    self.current_date = new_date 
    #    print(f"SideWidget Received Date: {self.current_date}")

    
    def get_selected_value(self, combo_box_exp, entry_key):
        text = combo_box_exp.currentText()
        index = combo_box_exp.currentIndex()
        print(f"entry_key = {entry_key} INDX = {index} text {text}")
        if text == 'Office Consumables':
           purchase_code = f"purchase_pc{index}" 
           print(f"PC is {purchase_code}")
        if entry_key == 'Service Code':
            index = combo_box_exp.currentIndex()
            #self.line_edit_code.setText(code[index])

        bottom_widget_handling.add_to_json(entry_key, text)
        
    def use_stored_date(self):
        print(f"Using stored date: {self.current_date}")

    def manual_update(self):
        """Explicitly update QLineEdit text when the button is clicked."""
        print("Before update:", self.bottom_widget.bottom_entries[1][2].text())  # Debugging
        self.bottom_widget.bottom_entries[1][2].setText("New IFSC Value")  # Set new text
        QApplication.processEvents()
        self.bottom_widget.bottom_entries[1][2].update()  # Force update
        self.bottom_widget.bottom_entries[1][2].repaint()  # Repaint UI
        print("After update:", self.bottom_widget.bottom_entries[1][2].text())

    def update_background(self, bottom_widget):
        selected_bg = self.combo_box.currentIndex()
        print(f" New bg {selected_bg}")
        """Update background image based on the combo box selection."""

        if banks[selected_bg] in banks:
            bg_image = bank_bg_path[selected_bg]                    # Get image path
            abs_image_path = os.path.abspath(bg_image).replace("\\", "/")
            print(f"update_bg: IMAGE {abs_image_path}")
            if self.top_widget:                                     # Ensure TopWidget exists
                #self.IFSC = bottom_widget_handling.get_ifsc(selected_bg)
                #bottom_widget.update_button = QPushButton("Update IFSC")
                #bottom_widget.update_button.clicked.connect(self.manual_update)
                #print(f"Sidewidget IFSC setText to {self.IFSC}")
                #bottom_widget.bottom_entries[1][2].clearFocus()
                #bottom_widget.bottom_entries[1][2].setText(self.IFSC)
                #bottom_widget.bottom_entries[1][2].setFocus()

                self.top_widget.set_background(bg_image, self.IFSC)

    def create_fields(self, label, layout, i): 
        print (f"Label = {label}")
        self.label_name = QLabel(label, self)
        layout.addWidget(self.label_name,i,0)
        self.label_name.setFixedSize(150, 30)
        i=i+1
        if label == 'Code:':
            self.line_edit_code = QLineEdit(self)
            self.line_edit_code.setFixedSize(250, 60)
            self.line_edit_code.setStyleSheet("border: 2px solid black;")
            self.line_edit_code.setText("KPS")
            layout.addWidget(self.line_edit_code, i, 0, 1, 2)
            self.line_edit_code.setFixedSize(100, 30)
        else:
            self.line_edit = QLineEdit(self)
            self.line_edit.setFixedSize(250, 60)
            self.line_edit.setStyleSheet("border: 2px solid black;")
            layout.addWidget(self.line_edit, i, 0, 1, 2)
            self.line_edit.setFixedSize(250, 50)
        self.checkbox = QCheckBox("Print", self)
        self.checkbox.stateChanged.connect(lambda state: self.on_checkbox_state_changed(state, label))
        layout.addWidget(self.checkbox,i,1)
        
        i=i+1
        return i
    
    def create_dropdown(self, layout, combo, index, row, col):
        print(f" DROP {combo[0]}")
        combo_name = f"combo_{index}" 
        self.combo_boxes[combo_name] = QComboBox()
        items = [combo[i] for i in range(1, index)]  # Generates ["Option 1", ..., "Option 13"]
        self.combo_boxes[combo_name].addItems(items)
        self.combo_boxes[combo_name].setFixedSize(250, 30)
        self.combo_boxes[combo_name].currentIndexChanged.connect(lambda: self.get_selected_value(self.combo_boxes[combo_name], combo[0])) #Exp_type[0]))
        layout.addWidget(self.combo_boxes[combo_name], row, col)
        bottom_widget_handling.add_to_json(combo[0],self.combo_boxes[combo_name].currentText())
    
    def on_selection_changed(self):
        selected_text = self.combo_box.currentText()

    def on_checkbox_state_changed(self, state, label):
        print(f"label checked is {label}")
        text=""
        if state == 2:                                                      # Update the label based on the checkbox state, 2 means checked
            #self.label.setText("Checkbox is checked")
            if label == 'Code:':
                self.code_print = 1
                text = self.line_edit_code.text()
            elif label == 'Description:':
                self.desc_print = 1
                text = self.line_edit.text()
            elif label == 'Purchase Voucher':
                print(f"label checkd is {label}")
            if text:
                bottom_widget_handling.add_to_json(label, text)
        else:
            self.label.setText("Checkbox is unchecked ")
            if label == 'Code:':
                self.code_print = 0
                text = self.line_edit_code.text()
            elif label == 'Description:':
                self.desc_print = 0
                text = self.line_edit.text()
            elif label == 'Purchase Voucher':
                print(f"label uncheckd is {label}")
            bottom_widget_handling.delete_from_json(label, text)
    
class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cheque Writer")
        self.normal_width = 800                             # Initialize normal size variables (for restoring window to this size)
        self.normal_height = 600

        self.screen_geometry = QDesktopWidget().availableGeometry() # Get screen geometry to constrain the window size
        self.max_width = self.screen_geometry.width()       # Maximum available screen width
        self.max_height = self.screen_geometry.height()     # Maximum available screen height
        self.setGeometry(self.screen_geometry)              # Full screen based on available screen space

        # **Main Layout**
        main_layout = QHBoxLayout()                         # Horizontal layout to place top, bottom, and sidebar
        print(f"Window {self.isVisible()}")
        self.top_widget = TopWidget(self)                   # TopWidget instance created here
        self.bottom_widget = BottomWidget(self.top_widget, self)
        self.sidebar_widget = SideWidget(self.top_widget, self)

        vertical_layout = QVBoxLayout()                     # **Top and Bottom layout in a vertical layout**
        vertical_layout.addWidget(self.top_widget)          # Add the custom top widget (with painting)
        vertical_layout.addWidget(self.bottom_widget)

        # Set main layout
        main_layout.addLayout(vertical_layout)              # Add top and bottom part
        main_layout.addWidget(self.sidebar_widget)          # Add sidebar on the right side
        self.setLayout(main_layout)                         # Set layout for the main window        
        self.setWindowState(Qt.WindowMaximized)             # Initially maximize the window

        #self.top_widget.date_changed_signal.connect(self.top_widget.bottom_widget.update_date)
        
    def resizeEvent(self, event):
        """Handle window resizing."""
        super().resizeEvent(event)

        new_width = min(self.width(), self.max_width)       # Ensure we don't exceed the screen width
        new_height = min(self.height(), self.max_height)    # Ensure we don't exceed the screen height
        self.resize_background_image(new_width, new_height) # Resize background image based on window size

    def resize_background_image(self, new_width, new_height):
        """Resize the background image to match the current window size."""
        if not hasattr(self.top_widget, "bg_image_path") or not self.top_widget.bg_image_path:
            return                                          # No image set yet

        abs_image_path = os.path.abspath(self.top_widget.bg_image_path).replace("\\", "/")

        self.top_widget.setStyleSheet(f"""
        QWidget {{
            background-image: url({abs_image_path});
            background-repeat: no-repeat;
            background-size: {new_width}px {new_height}px;  /* Dynamically adjust size */
        }}
        """)

    def changeEvent(self, event):
        """Handle window state changes (restoring from title bar)."""
        if event.type() == event.WindowStateChange:
            if self.isMaximized():
                print("Window is maximized.")
            else:
                print("Window is restored to normal state.")
                self.resize(self.normal_width, self.normal_height)  # Restore to normal size
                self.move(0, 100)                               # Optionally, set a specific position when restored

    def closeEvent(self, event):
        """Called when the app is closing."""
        print("App is closing...")

        # ✅ Reset the JSON file before closing
        with open(SAVE_FILE, "w") as f:
            json.dump({}, f)  # Clears all data

        event.accept()  # Accept the close event
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()     
    print(f"MAIN {window.isVisible()}")                                      # Show the window
    sys.exit(app.exec_())                                       # Start the event loop

