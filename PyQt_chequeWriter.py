from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QDesktopWidget, QLineEdit, QDateEdit, QSizePolicy, QGridLayout, QSpacerItem, QComboBox, QPushButton, QCheckBox
from PyQt5.QtCore import Qt, QPointF, QDate, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QDoubleValidator
from functools import partial
import os, sys
import configparser

from backend import bottom_widget_handling, side_widget_handling

configuration_path = os.path.dirname(os.path.abspath(__file__))+"\config\config.ini"
config = configparser.ConfigParser()
config.read(configuration_path)
headers = config.get('UI', 'headers').split(',')
labels = config.get('UI', 'labels').split(',')
banks = config.get('UI', 'banks').split(',')
toggle = config.get('UI', 'toggle').split(',')
Exp_type = config.get('UI', 'Exp_type').split(',')
rows_columns = list(map(int, config.get('UI', 'rows_columns').split(',')))
combo_options = config.get('UI', 'combo_options').split(',')
bank_bg_path = config.get('Bank', 'Bank_bg_path').split(',')

class TopWidget(QWidget):
    date_changed_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.bottom_widget = BottomWidget(top_widget=self, parent=self)  # Pass reference of TopWidget
        #self.side_widget = SideWidget(self)
        #widget = QWidget(self)
        layout = QGridLayout()

        # Load background image using PaintEvent
        #self.bg_pixmap = QPixmap(bank_bg_path[0])
        self.setFixedSize(1500, 500)
        #self.IFSC = bottom_widget_handling.get_ifsc(0)
        self.set_background(bank_bg_path[0], 0) #self.IFSC)
        #self.IFSC = bottom_widget_handling.get_ifsc(0)

        self.setVisible(True)
        print(f"TW: visible {self.isVisible()}")
        # Initially, you can hide it
        self.bottom_widget.setVisible(True)  
        #self.side_widget.setVisible(True)  

        #self.label = QLabel("Selected Date: ", self)

        self.entries = []
        for i in range (11):
            if i == 2:
                line_edit = QDateEdit(self)
                line_edit.setDate(QDate.currentDate()) 
                line_edit.setFixedSize(300, 40)
                # Connect dateChanged signal to function
                line_edit.dateChanged.connect(self.update_date)
                #self.label = QLabel(f"{line_edit.date().toString('yyyy-MM-dd')}", self)
            else:
                line_edit = QLineEdit(self)
                line_edit.setPlaceholderText(f"Enter text {i}")
                line_edit.setMaximumSize(400, 50)
            self.entries.append(line_edit)  # Add to the list
           
        self.entries[4].setPlaceholderText("Payee") 
        self.entries[4].setFixedSize(500, 40)
        self.entries[7].setPlaceholderText("Amount") 
        validator = QDoubleValidator()                                     # Allows only integer input
        self.entries[7].setValidator(validator)

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

        for index in range(11):
            if index not in [2,4,7]:
                self.entries[index].setVisible(False)

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

        if IFSC != 0 and hasattr(self.bottom_widget, "entries"):  # Ensure BottomWidget has entries
            #print(f"set_bg : Found it at {self.bottom_widget.entries[1][2].text()} and set it to {IFSC}")
            #self.bottom_widget.entries[1][2].setText(IFSC)
            #print(f"set_bg Is Visible: {self.bottom_widget.entries[1][2].isVisible()}")
            #print(f"set_bg Is Enabled: {self.bottom_widget.entries[1][2].isEnabled()}")
            #self.bottom_widget.update()
            self.bottom_widget.update_ifsc(IFSC)
            #QApplication.processEvents() 
        else:
            self.IFSC = bottom_widget_handling.get_ifsc(0)
            print("entries not found in BottomWidget")

        self.update() 
        self.paintEvent(None)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background image first
        painter.drawPixmap(0, 0, self.width(), self.height(), self.bg_pixmap)
        #print (f"paintEvent : Image updated {self.bg_pixmap}")
        font = QFont('Arial', 12)                                   # Set the font for the text
        painter.setFont(font)

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

        widget = QWidget(self)
        layout = QGridLayout()
        self.setLayout(layout)

        self.top_widget.setVisible(True)
        self.setVisible(True)
        print(f"BW: TopWidget visible: {self.top_widget.isVisible()}")
        print(f"BottomWidget visible: {self.isVisible()}")

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
        self.entries = [] 

        for row, col_count in enumerate(rows_columns, start=1):             # Iterate through rows (4 rows in total)
            row_entries = []
            for col in range(col_count):                              # For each row, iterate through the number of columns
                widget_counter, row_entries = self.add_fields(labels[widget_counter], col, row, layout, widget_counter, row_entries)
            self.entries.append(row_entries)

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(vertical_spacer, 5, 0, 1, 2)
        layout.setSpacing(20)

        self.setStyleSheet("background-color: white;")
        widget.setLayout(layout)
        widget.setFixedSize(1500, 500)
    
    def add_fields(self, label_name, col, row, layout, widget_counter, row_entries):
        label = QLabel(label_name, self)
        line_edit = QLineEdit(self)
        #print(f"Before: {line_edit.isVisible()}") 
        self.setVisible(True)
        line_edit.setVisible(True)
        #print(f"After in function add_fields: {line_edit.isVisible()}") 
        line_edit.setStyleSheet("border: 2px solid black;")
        layout.addWidget(label, row, col * 2)                                  # Place label in column (2 * col)
        layout.addWidget(line_edit, row, col * 2 + 1)
        label.setMaximumSize(150, 30)
        line_edit.setMaximumSize(200, 30)
        if label_name == 'IFSC:':
            print(f"Update IFSC entry {widget_counter} = {row} {col}")  
            self.IFSC = bottom_widget_handling.get_ifsc(0)
            line_edit.setVisible(True)
            line_edit.setText(self.IFSC)    
        row_entries.append(line_edit)
        #QTimer.singleShot(100, self.ensure_visibility)
        widget_counter += 1
        return widget_counter, row_entries
    
    def update_ifsc(self, IFSC):
        #super().paintEvent(event)  # Call parent method
        self.IFSC = IFSC
        print(f"update_ifsc {self.IFSC}")
        if hasattr(self, "entries"):
            if len(self.entries) > 1 and len(self.entries[1]) > 2:
                entry = self.entries[1][2]
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
        for row in self.entries:
            for entry in row:
                entry.setVisible(True)
                print(f"Entry Visible: {entry.isVisible()}")  # Now should return True

class SideWidget(QWidget):
    def __init__(self, top_widget, parent=None):
        super().__init__(parent)
        self.top_widget = top_widget 
        self.current_date = "" 
        self.cross = 1
        if hasattr(self.top_widget, "bottom_widget"):
            self.bottom_widget = top_widget.bottom_widget
        else:
            print("⚠️ Warning: `bottom_widget` is not initialized in `top_widget`.")

        widget = QWidget(self)
        self.layout = QGridLayout()

        #self.label = QLabel("Date: Not Set", self)
        #self.top_widget.date_changed_signal.connect(self.update_date_label) 
        #self.update_date_label("03/06/25")
        print(f" New date = {self.current_date}")
        self.use_stored_date()

        #causing extra screen
        top_widget.setVisible(True)
        self.bottom_widget.setVisible(True)
        self.bottom_widget.entries[1][2].setVisible(True)
        print(f"SW: SideWidget {self.isVisible()}")
        print(f"SW: TopWidget visible: {top_widget.isVisible()}")
        print(f"SW: BottomWidget visible: {self.bottom_widget.isVisible()}")
        print(f"Entry visible: {self.bottom_widget.entries[1][2].isVisible()}")

        self.combo_box = QComboBox(self)
        for i in range(4):
            self.combo_box.addItem(banks[i])
        self.combo_box.setFixedSize(200, 40)
        self.IFSC = 0
        self.combo_box.currentIndexChanged.connect(lambda: self.update_background(self.bottom_widget))
        self.layout.addWidget(self.combo_box,0,0,1,2)

        #self.top_widget = TopWidget(self)
        self.toggle_buttons = []  # Store all buttons
        j = 0
        for i in range(7):
            btn = QPushButton("Turn OFF", self)  # Create a new button
            btn.setStyleSheet("background-color: orange; color: black;")
            label_name = toggle[i]
            label = QLabel(toggle[i], self)
            btn.setFixedSize(100, 40)
            btn.setCheckable(False)
            if label_name == "A/C Payee":
                btn.setText("Turn ON") 
                btn.setStyleSheet("background-color: green; color: black;")
                cross = side_widget_handling.set_cross()
            #btn.clicked.connect(self.toggle_button_state(btn))
            btn.clicked.connect(lambda checked=False, b=btn, lbl=label_name: side_widget_handling.toggle_button_state(b, lbl))
            j = j+1
            self.layout.addWidget(label, j, 0)
            self.layout.addWidget(btn, j, 1)

        self.spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        #layout.addItem(self.spacer)
        self.print_button = QPushButton("PRINT - Front", self)
        self.print_button.setStyleSheet(""" QPushButton {
                border: 2px solid blue; border-radius: 5px; padding: 10px; background-color: white;
            } """)
        self.print_button.setFixedSize(300, 40)
        #self.print_button.clicked.connect(side_widget_handling.generate_cheque_front(self.IFSC, new_date))
        #self.print_button.clicked.connect(lambda: side_widget_handling.generate_cheque_front(self.IFSC, new_date))
        self.print_button.clicked.connect(partial(side_widget_handling.generate_cheque_front, self.IFSC, self.current_date, self.top_widget.entries[4], self.top_widget.entries[7], self.top_widget.entries[2]))

        i = i+2
        self.layout.addWidget(self.print_button,i,0,1,2)

        self.layout.addItem(self.spacer)

        self.label = QLabel("Expense_type:", self)
        self.label.setFixedSize(100, 30)
        i=i+5
        self.layout.addWidget(self.label,i,0)
        self.create_combobox(self.layout, combo_options[0], combo_options[1], i, 1)

        self.label = QLabel("Classification Type", self)
        i=i+1
        self.layout.addWidget(self.label,i,0)
        i= i+1

        indx = 2
        for n in range(3):
            self.create_combobox(self.layout, combo_options[indx], combo_options[indx+1], i+n,0)
            indx= indx+2

        i=i+4
        i = self.create_fields("Code:", self.layout, i)
        i = self.create_fields("Description:", self.layout, i)
        self.layout.addItem(self.spacer)

        #date = self.top_widget.label
        #print(f" DATE is {self.top_widget.selected_date}")

        self.print_button = QPushButton("PRINT - Back ", self)
        self.print_button.setStyleSheet("""
            QPushButton {
                border: 2px solid blue;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
        """)
        self.print_button.setFixedSize(300, 40)
        #self.print_button.clicked.connect(self.toggle_button_state(self.print_button))
        self.print_button.clicked.connect(lambda checked=False, b=self.print_button: side_widget_handling.toggle_button_state(self.print_button))

        
        self.layout.addWidget(self.print_button,i+14,0,1,2)
        
        self.setStyleSheet("background-color: white;")
        widget.setLayout(self.layout)

    def update_date_label(self, new_date):
        #self.label.setText(f"Date: {new_date}")  # Update label dynamically
        self.current_date = new_date 
        print(f"SideWidget Received Date: {self.current_date}")

    def use_stored_date(self):
        print(f"Using stored date: {self.current_date}")

    def update_background(self, bottom_widget):
        selected_bg = self.combo_box.currentIndex()
        print(f" New bg {selected_bg}")
        """Update background image based on the combo box selection."""

        if banks[selected_bg] in banks:
            bg_image = bank_bg_path[selected_bg]                    # Get image path
            abs_image_path = os.path.abspath(bg_image).replace("\\", "/")
            print(f"update_bg: IMAGE {abs_image_path}")
            if self.top_widget:                                     # Ensure TopWidget exists
                self.IFSC = bottom_widget_handling.get_ifsc(selected_bg)
                self.top_widget.set_background(bg_image, self.IFSC)

    def create_fields(self, label, layout, i):
        self.label = QLabel(label, self)
        layout.addWidget(self.label,i,0)
        self.label.setFixedSize(150, 30)
        i=i+1
        line_edit = QLineEdit(self)
        line_edit.setFixedSize(150, 60)
        line_edit.setStyleSheet("border: 2px solid black;")
        layout.addWidget(line_edit, i, 0, 1, 2)
        self.checkbox = QCheckBox("Print", self)
        self.checkbox.stateChanged.connect(self.on_checkbox_state_changed)
        layout.addWidget(self.checkbox,i,1)
        line_edit.setFixedSize(100, 30)
        i=i+1
        return i
    
    def create_combobox(self, layout, combo_name1, combo_name2, row, col):
        self.class_box = QComboBox(self)
        self.class_box.addItem(combo_name1)
        self.class_box.addItem(combo_name2)
        self.class_box.setFixedSize(150, 30)
        self.class_box.currentIndexChanged.connect(self.on_selection_changed)
        layout.addWidget(self.class_box, row, col)
    
    def on_selection_changed(self, index):
        selected_text = self.combo_box.currentText()

    def toggle_button_state1(self,btn):
        if btn.text() == "Turn ON":                          # Check if the button's text is "Turn ON"
            btn.setText("Turn OFF")
            btn.setStyleSheet("background-color: orange; color: black;")  # Change the button color
        else:
            btn.setText("Turn ON")
            btn.setStyleSheet("background-color: green; color: black;")  # Change the button color

    def on_checkbox_state_changed(self, state):
        if state == 2:                                                      # Update the label based on the checkbox state, 2 means checked
            self.label.setText("Checkbox is checked")
        else:
            self.label.setText("Checkbox is not checked")

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
        
        # Initially maximize the window
        self.setWindowState(Qt.WindowMaximized)


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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()     
    print(f"MAIN {window.isVisible()}")                                      # Show the window
    sys.exit(app.exec_())                                       # Start the event loop

