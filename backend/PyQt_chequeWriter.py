import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QDesktopWidget, QLineEdit, QDateEdit, QSizePolicy, QGridLayout, QSpacerItem, QComboBox, QPushButton, QCheckBox, QScrollArea
from PyQt5.QtCore import Qt, QPointF, QDate
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QIntValidator

headers = ["Bill Details:", "Payee Details:", "Payment Details:"]
labels = ["Name:","Name:","Cheque#","Cheque Date:","Invoice#","Bank:","IFSC:","Bank:","GST:","Branch:","Branch:","PAN:","IFSC","Digital Signature:"]
banks = ["HDFC Bank", "Karnataka Bank", "Canara Bank", "Union Bank"]
toggle = ["Self", "Yourself", "A/C Payee", "Cancel Cheque", "RTGS", "NEFT", "Cheque"]
Exp_type = ["Expense Type","Revenue", "Capital"]
rows_columns = [4, 4, 3, 3]
combo_options = ["Revenue", "Capital","test1", "test2","HDFC Bank", "Canara", "7688","6478"]

class TopWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QWidget(self)
        layout = QGridLayout()

        # Load background image
        self.bg_pixmap = QPixmap("Images/HDFC.jpg")
        self.setFixedHeight(500)
        self.setFixedWidth(1500)

        self.entries = []
        for i in range (11):
            if i == 2:
                line_edit = QDateEdit(self)
                line_edit.setDate(QDate.currentDate()) 
                line_edit.setFixedSize(300, 40)
            else:
                line_edit = QLineEdit(self)
                line_edit.setPlaceholderText(f"Enter text {i}")
                line_edit.setMaximumSize(400, 50)
            self.entries.append(line_edit)  # Add to the list
            
        self.entries[4].setPlaceholderText("Payee") 
        self.entries[4].setFixedSize(500, 40)
        self.entries[7].setPlaceholderText("Amount") 
        validator = QIntValidator()  # Allows only integer input
        self.entries[7].setValidator(validator)

        # Add widgets to the grid layout
        self.spacer = QSpacerItem(0, 90, QSizePolicy.Minimum, QSizePolicy.Fixed) #Expanding)
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

        widget.setLayout(layout)
        widget.setFixedSize(1500, 500) 

        for index in range(11):
            if index not in [2,4,7]:
                self.entries[index].setVisible(False)

    def paintEvent(self, event):
        """Custom painting for the top portion"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the background image first
        painter.drawPixmap(0, 0, self.width(), self.height(), self.bg_pixmap)

        font = QFont('Arial', 12)                   # Set the font for the text
        painter.setFont(font)

        painter.setPen(QColor(0, 0, 0))             # Set pen to black for lines
        painter.drawLine(0, 80, 80, 0)              # First slanting line
        painter.drawLine(0, 120, 120, 0)            # Second slanting line

        text_position = QPointF(10, 100)            # Position where you want to draw the text
        painter.translate(text_position)
        painter.rotate(-45)                         # Negative value for rotating upwards
        painter.drawText(0, 0, "A/C Payee")         # Draw the text

        painter.resetTransform()                    # Reset the rotation before drawing the lines

        text_position = QPointF(100, 100)
        painter.translate(text_position)
        painter.drawText(1200, 50, "XXXXXXXX")
        painter.end()

class BottomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QWidget(self)
        layout = QGridLayout()
        font = QFont()
        font.setBold(True) 
        font.setPointSize(8)
        font.setUnderline(True)
        
        column = 0
        for i in range(3):
            header_label = QLabel(headers[i], self)
            header_label.setFont(font)
            layout.addWidget(header_label, 0, column,1,2)
            header_label.setFixedSize(300, 20)
            header_label.setAlignment(Qt.AlignCenter)
            column = column + 2

        widget_counter = 0

        for row, col_count in enumerate(rows_columns, start=1):             # Iterate through rows (4 rows in total)
            for col in range(col_count):                                    # For each row, iterate through the number of columns
                widget_counter = self.add_fields(labels[widget_counter], col, row, layout, widget_counter)

        self.setStyleSheet("background-color: white;")
        widget.setLayout(layout)
        widget.setFixedSize(1500, 500)

    def add_fields(self, label_name, col, row, layout, widget_counter):
        label = QLabel(label_name, self)
        line_edit = QLineEdit(self)
        line_edit.setStyleSheet("border: 2px solid black;")
        layout.addWidget(label, row, col * 2)  # Place label in column (2 * col)
        layout.addWidget(line_edit, row, col * 2 + 1)
        label.setMaximumSize(150, 30)
        line_edit.setMaximumSize(200, 30)
        widget_counter += 1
        return widget_counter

class SideWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QWidget(self)
        layout = QGridLayout()

        self.combo_box = QComboBox(self)
        for i in range(4):
            self.combo_box.addItem(banks[i])
        self.combo_box.setFixedSize(200, 40)
        self.combo_box.currentIndexChanged.connect(self.on_selection_changed)
        layout.addWidget(self.combo_box,0,0,1,2)

        for i in range(7):
            self.toggle_button = QPushButton("Turn ON", self)
            self.label = QLabel(toggle[i], self)
            self.toggle_button.setFixedSize(100, 40)
            self.toggle_button.clicked.connect(self.toggle_button_state)
            i= i+1
            layout.addWidget(self.label,i,0)
            layout.addWidget(self.toggle_button,i,1)

        self.spacer = QSpacerItem(0, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)
        #layout.addItem(self.spacer)
        self.print_button = QPushButton("PRINT - Front", self)
        self.print_button.setStyleSheet(""" QPushButton {
                border: 2px solid blue; border-radius: 5px; padding: 10px; background-color: white;
            } """)
        self.print_button.setFixedSize(300, 40)
        self.print_button.clicked.connect(self.toggle_button_state)
        i = i+2
        layout.addWidget(self.print_button,i,0,1,2)

        layout.addItem(self.spacer)

        self.label = QLabel("Expense_type:", self)
        self.label.setFixedSize(100, 30)
        i=i+5
        layout.addWidget(self.label,i,0)
        self.create_combobox(layout, combo_options[0], combo_options[1], i, 1)

        self.label = QLabel("Classification Type", self)
        i=i+1
        layout.addWidget(self.label,i,0)
        i= i+1

        indx = 2
        for n in range(3):
            self.create_combobox(layout, combo_options[indx], combo_options[indx+1], i+n,0)
            indx= indx+2

        i=i+4
        i = self.create_fields("Code:", layout, i)
        i = self.create_fields("Description:", layout, i)
        layout.addItem(self.spacer)
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
        self.print_button.clicked.connect(self.toggle_button_state)
        layout.addWidget(self.print_button,i+14,0,1,2)

        self.setStyleSheet("background-color: white;")
        widget.setLayout(layout)

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
        #self.label.setText(f"Selected: {selected_text}")                   # Update the label with the selected option

    def toggle_button_state(self):
        if self.toggle_button.text() == "Turn ON":                          # Check if the button's text is "Turn ON"
            self.toggle_button.setText("Turn OFF")
            self.toggle_button.setStyleSheet("background-color: green; color: black;")  # Change the button color
        else:
            self.toggle_button.setText("Turn ON")
            self.toggle_button.setStyleSheet("background-color: red; color: black;")  # Change the button color

    def on_checkbox_state_changed(self, state):
        if state == 2:                                                      # Update the label based on the checkbox state, 2 means checked
            self.label.setText("Checkbox is checked")
        else:
            self.label.setText("Checkbox is not checked")

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Cheque Writer")

        # Initialize normal size variables (for restoring window to this size)
        self.normal_width = 800
        self.normal_height = 600

        self.screen_geometry = QDesktopWidget().availableGeometry() # Get screen geometry to constrain the window size
        self.max_width = self.screen_geometry.width()       # Maximum available screen width
        self.max_height = self.screen_geometry.height()     # Maximum available screen height

        self.setGeometry(self.screen_geometry)              # Full screen based on available screen space

        # **Main Layout**
        main_layout = QHBoxLayout()  # Horizontal layout to place top, bottom, and sidebar

        self.top_widget = TopWidget(self)  # TopWidget instance created here
        self.bottom_widget = BottomWidget(self)
        self.sidebar_widget = SideWidget(self)

        vertical_layout = QVBoxLayout()                 # **Top and Bottom layout in a vertical layout**
        vertical_layout.addWidget(self.top_widget)      # Add the custom top widget (with painting)
        vertical_layout.addWidget(self.bottom_widget)

        # Set main layout
        main_layout.addLayout(vertical_layout)          # Add top and bottom part
        main_layout.addWidget(self.sidebar_widget)      # Add sidebar on the right side

        self.setLayout(main_layout)                     # Set layout for the main window

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
        resized_pixmap = self.top_widget.bg_pixmap.scaled(
            new_width, new_height // 2, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        self.top_widget.bg_pixmap = resized_pixmap          # Update the background pixmap for TopWidget

    def changeEvent(self, event):
        """Handle window state changes (restoring from title bar)."""
        if event.type() == event.WindowStateChange:
            if self.isMaximized():
                print("Window is maximized.")
            else:
                print("Window is restored to normal state.")
                self.resize(self.normal_width, self.normal_height)  # Restore to normal size
                self.move(0, 100)                           # Optionally, set a specific position when restored

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()                                           # Show the window
    sys.exit(app.exec_())                                   # Start the event loop

