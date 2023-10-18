from PyQt6.QtWidgets import QApplication, QWidget, QRadioButton, QGroupBox, QVBoxLayout, QFileDialog, QPushButton, QLabel, QLineEdit, QGridLayout
from PyQt6.QtGui import QPixmap, QDoubleValidator
from PyQt6.QtCore import QSize
import sys
import os
import re
from openpyxl import load_workbook

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1920,1080)
        self.setWindowTitle("EBCS Image Sorter")
        self.init_vars()
        self.init_ui()

        self.sorting_folder_path = None
        self.excel_path = None

        self.folder_btn.clicked.connect(self.launch_dialog)
        self.excel_btn.clicked.connect(self.launch_dialog)

    def init_ui(self):
        self.radios = []
        self.radio_group = QGroupBox("Image Category", self)
        self.radio_vbox = QVBoxLayout()
        self.layout = QGridLayout()
        
        self.counterfeit_radio = QRadioButton("Counterfeit Bills", self)
        self.money_order_radio = QRadioButton("Money Order/Transfer", self)
        self.wire_radio = QRadioButton("Wire Transfer", self)
        self.ach_radio = QRadioButton("ACH", self)
        self.id_radio = QRadioButton("SSN/Citizenship/ID cards", self)
        self.credit_radio = QRadioButton("Credit Score", self)
        self.enrollment_radio = QRadioButton("Bank/CC Enrollment", self)
        self.receipt_radio = QRadioButton("Receipts", self)
        self.radios.extend((self.counterfeit_radio, self.money_order_radio, self.wire_radio, self.ach_radio, self.id_radio, self.credit_radio, self.enrollment_radio, self.receipt_radio))

        self.amount_text = QLineEdit(self)
        self.amount_text.hide()
        self.amount_text.move(500,500)
        self.amount_text.setValidator(QDoubleValidator())
        self.amount_text.setMaxLength(15)
        self.amount_text.textChanged.connect(self.amount_changed)

        self.img_box = QLabel(self)
        #self.img_box.move(700,0)
        #self.img_box.resize(1000,1000)

        #self.layout.lay

        for radio in self.radios:
            radio.toggled.connect(self.radio_clicked)
            self.radio_vbox.addWidget(radio)
            radio.setEnabled(False)

        self.radio_group.setLayout(self.radio_vbox)
        self.folder_btn = QPushButton("Select EBCS sorting folder", self)
        self.excel_btn = QPushButton("Excel sheet", self)
        self.folder_btn.setMinimumSize(100, 100)
        self.excel_btn.setMinimumSize(100, 100)
        self.folder_btn.hide()

        self.next_btn = QPushButton("Next Image", self)
        self.prev_btn = QPushButton("Previous Image", self)
        self.next_btn.clicked.connect(self.cycle_img)
        self.prev_btn.clicked.connect(self.cycle_img)
        self.next_btn.hide()
        self.prev_btn.hide()
        self.prev_btn.setMinimumSize(100, 100)
        self.next_btn.setMinimumSize(100, 100)
        self.prev_btn.setEnabled(False)

        self.layout.addWidget(self.img_box, 1, 3, 1, 2)
        self.layout.addWidget(self.prev_btn, 2, 3)
        self.layout.addWidget(self.next_btn, 2, 4)
        self.layout.addWidget(self.radio_group, 1, 1, 1, 2)
        self.layout.addWidget(self.excel_btn, 2, 1)
        self.layout.addWidget(self.folder_btn, 2, 2)

    def init_vars(self):
        self.current_image_name = None
        self.excel_columns = {"Counterfeit": ["C", 2], 
                "Money Order": ["D", 2], 
                "Wire": ["E", 2], 
                "ACH": ["F", 2], 
                "SSN": ["G", 2], 
                "Credit Score": ["H", 2], 
                "Enrollment": ["I", 2], 
                "Enrolled Bank": ["J", ""], 
                "Receipt": ["K", 2], 
                "Receipt Type": ["L", ""], 
                "Receipt Bank": ["M", ""], 
                "Amount": ["N", ""]}
        self.img_num = 0
        self.cycling = False


    def launch_dialog(self):
        if self.sender().text() == "Select EBCS sorting folder":
            self.sorting_folder_path = QFileDialog.getExistingDirectory()
            if not self.sorting_folder_path:
                print("Nothing selected")
            else:
                self.setup_images()
                for radio in self.radios:
                    radio.setEnabled(True)
        elif self.sender().text() == "Excel sheet":
            self.excel_path = QFileDialog.getOpenFileName(filter = 'Excel File (*.xlsx *.xls)')[0]
            if not self.excel_path:
                print("Nothing selected")
            else:
                self.folder_btn.show()
                self.setup_excel()

    def amount_changed(self):
        try:
            if self.receipt_radio.isChecked():
                self.excel_columns["Amount"][1] = float(self.sender().text())
                self.write_excel()
        except ValueError:
            pass

    def radio_clicked(self):
        # TODO: Clean up repeated switch statement
        match self.sender():
            case self.counterfeit_radio:
                if self.sender().isChecked():
                    self.excel_columns["Counterfeit"][1] = 1
                else:
                    self.excel_columns["Counterfeit"][1] = 2
            case self.money_order_radio:
                if self.sender().isChecked():
                    self.excel_columns["Money Order"][1] = 1
                else:
                    self.excel_columns["Money Order"][1] = 2
            case self.wire_radio:
                if self.sender().isChecked():
                    self.excel_columns["Wire"][1] = 1
                else:
                    self.excel_columns["Wire"][1] = 2
            case self.ach_radio:
                if self.sender().isChecked():
                    self.excel_columns["ACH"][1] = 1
                else:
                    self.excel_columns["ACH"][1] = 2
            case self.id_radio:
                if self.sender().isChecked():
                    self.excel_columns["SSN"][1] = 1
                else:
                    self.excel_columns["SSN"][1] = 2
            case self.credit_radio:
                if self.sender().isChecked():
                    self.excel_columns["Credit Score"][1] = 1
                else:
                    self.excel_columns["Credit Score"][1] = 2
            case self.enrollment_radio:
                if self.sender().isChecked():
                    self.excel_columns["Enrollment"][1] = 1
                else:
                    self.excel_columns["Enrollment"][1] = 2
            case self.receipt_radio:
                if self.sender().isChecked():
                    self.excel_columns["Receipt"][1] = 1
                    self.amount_text.show()
                else:
                    self.excel_columns["Receipt"][1] = 2
                    self.amount_text.hide()
        # FIXME: This writes to excel sheet multiple times just for one action
        if not self.cycling and self.sender().isChecked():
            self.write_excel()
    
    def setup_excel(self):
        self.excel = load_workbook(filename=self.excel_path)
        self.excel_others = self.excel["5. Other"]
    
    # Find if image id in excel
    def find_entry(self):
        radio_columns = ["C","D","E","F","G","H","I","K"]
        split = re.split("_|@|\.", self.current_image_name)
        self.excel_row = 1
        while True:
            self.excel_row += 1
            if self.excel_others[f"A{self.excel_row}"].value == int(split[1]):
                print(f"existing entry found on row {self.excel_row}")
                break
            elif not self.excel_others[f"A{self.excel_row}"].value:
                print(f"new entry, empty row available to write on row {self.excel_row}")
                break

        self.excel_columns["Enrolled Bank"][1] = self.excel_others[f"J{self.excel_row}"].value
        self.excel_columns["Receipt Bank"][1] = self.excel_others[f"M{self.excel_row}"].value
        self.excel_columns["Amount"][1] = self.excel_others[f"N{self.excel_row}"].value
        
        if self.excel_columns["Amount"][1]:
            self.amount_text.setText(str(self.excel_columns["Amount"][1]))
        else:
            self.amount_text.setText("")
        
        for i, column in enumerate(radio_columns):
            if self.excel_others[f"{column}{self.excel_row}"].value == 1:
                self.radios[i].setChecked(True)
            else:
                self.radios[i].setAutoExclusive(False)
                self.radios[i].setChecked(False)
                self.radios[i].setAutoExclusive(True)
        



    
    def write_excel(self):
        # File name is split into 5 parts
        # 0. The string "photo", 1. photo id, 2. date (DD/MM/YYYY), 3. time (24 HR), 4. file type
        split = re.split("_|@|\.", self.current_image_name)

        # Find empty row or row where entry already exists
        row = 1
        while True:
            row += 1
            if not self.excel_others[f"A{row}"].value:
                print(f"writing new entry on row {row}")
                break
            elif self.excel_others[f"A{row}"].value == int(split[1]):
                print(f"overwriting existing entry found on row {row}")
                break
        
        self.excel_others[f"A{row}"] = int(split[1])
        self.excel_others[f"B{row}"] = split[2]
        for type in self.excel_columns:
            self.excel_others[f"{self.excel_columns[type][0]}{row}"] = self.excel_columns[type][1]
        self.excel.save(f'{__file__}/../NFCU_coding_template.xlsx')

    
    def setup_images(self):
        self.folder_files = os.listdir(self.sorting_folder_path)
        if len(self.folder_files) > 0:
            self.cycling = True
            self.img_box.setPixmap(QPixmap(f"{self.sorting_folder_path}/{self.folder_files[self.img_num]}").scaled(QSize(1000,1000)))
            self.update()
            self.current_image_name = self.folder_files[self.img_num]
            self.find_entry()
            self.next_btn.show()
            self.prev_btn.show()
            self.cycling = False
    
    def cycle_img(self):
        if self.sender().text() == "Next Image" and self.img_num < len(self.folder_files) - 1:
            self.img_num += 1
        elif self.sender().text() == "Previous Image" and self.img_num > 0:
            self.img_num -= 1
        
        self.cycling = True
        if self.img_num > 0:
            self.prev_btn.setEnabled(True)
        else:
            self.prev_btn.setEnabled(False)
        if self.img_num < len(self.folder_files) - 1:
            self.next_btn.setEnabled(True)
        else:
            self.next_btn.setEnabled(False)
        self.cycling = False

        self.update()
        self.setup_images()



def main():
    app = QApplication(sys.argv)
    window = Window()
    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()