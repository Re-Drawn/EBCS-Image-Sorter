import sys, os, re
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QDoubleValidator
from PyQt6.QtCore import QSize
from openpyxl import load_workbook

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(1920,1080)
        self.setWindowTitle("EBCS Image Sorter")
        self.init_ui()
        self.init_vars()

    def init_ui(self):
        self.radios = []
        self.radio_group = QGroupBox("Image Category", self)
        self.radio_vbox = QVBoxLayout()
        
        self.counterfeit_radio = QRadioButton("Counterfeit Bills", self)
        self.money_order_radio = QRadioButton("Money Order/Transfer", self)
        self.wire_radio = QRadioButton("Wire Transfer", self)
        self.ach_radio = QRadioButton("ACH", self)
        self.id_radio = QRadioButton("SSN/Citizenship/ID cards", self)
        self.credit_radio = QRadioButton("Credit Score", self)
        self.enrollment_radio = QRadioButton("Bank/CC Enrollment", self)
        self.receipt_radio = QRadioButton("Receipts", self)
        self.radios.extend((self.counterfeit_radio, self.money_order_radio, self.wire_radio, self.ach_radio, self.id_radio, self.credit_radio, self.enrollment_radio, self.receipt_radio))

        for radio in self.radios:
            radio.toggled.connect(self.radio_clicked)
            self.radio_vbox.addWidget(radio)
            radio.setEnabled(False)

        self.radio_group.setLayout(self.radio_vbox)

        self.subcategory_group = QGroupBox("Image Subcategory", self)
        self.subcategory_vbox = QVBoxLayout()
        self.receipt_type_group = QGroupBox("Receipt Type", self)
        self.receipt_type_vbox = QVBoxLayout()

        self.deposit_radio = QRadioButton("Deposit", self.receipt_type_group)
        self.withdraw_radio = QRadioButton("Withdraw", self.receipt_type_group)
        self.other_radio = QRadioButton("Other", self.receipt_type_group)

        for radio in self.receipt_type_group.children():
            radio.toggled.connect(self.radio_clicked)
            self.receipt_type_vbox.addWidget(radio)
            radio.setEnabled(False)

        self.subcategory_vbox.addWidget(self.receipt_type_group)

        self.receipt_type_group.setLayout(self.receipt_type_vbox)
        self.subcategory_group.setLayout(self.subcategory_vbox)

        self.cash_amount = QLineEdit(self)
        self.cash_amount.setMinimumSize(10, 10)
        self.cash_amount.setValidator(QDoubleValidator())
        self.cash_amount.setMaxLength(15)
        self.cash_amount.setPlaceholderText("Cash Amount")
        self.cash_amount.textChanged.connect(self.amount_changed)
        self.subcategory_vbox.addWidget(self.cash_amount)
        self.cash_amount.setDisabled(True)

        self.bank_text = QLineEdit(self)
        self.subcategory_vbox.addWidget(self.bank_text)
        self.bank_text.setPlaceholderText("Bank")
        self.bank_text.textChanged.connect(self.amount_changed)
        self.bank_text.setDisabled(True)
        
        self.img_display = QLabel(self)
        self.img_display.setMinimumSize(1000,100)

        self.folder_btn = QPushButton("Select EBCS sorting folder", self)
        self.folder_btn.setMinimumSize(100, 100)
        self.folder_btn.clicked.connect(self.launch_dialog)
        self.folder_btn.setDisabled(True)

        self.excel_btn = QPushButton("Excel sheet", self)
        self.excel_btn.setMinimumSize(100, 100)
        self.excel_btn.clicked.connect(self.launch_dialog)

        self.prev_btn = QPushButton("Previous Image", self)
        self.prev_btn.setMinimumSize(100, 100)
        self.prev_btn.clicked.connect(self.cycle_img)
        self.prev_btn.setDisabled(True)
        self.prev_btn.hide()

        self.next_btn = QPushButton("Next Image", self)
        self.next_btn.setMinimumSize(100, 100)
        self.next_btn.clicked.connect(self.cycle_img)
        self.next_btn.hide()

        self.layout = QGridLayout()
        self.layout.addWidget(self.img_display, 1, 3, 1, 2)
        self.layout.addWidget(self.prev_btn, 2, 3)
        self.layout.addWidget(self.next_btn, 2, 4)
        self.layout.addWidget(self.radio_group, 1, 1)
        self.layout.addWidget(self.subcategory_group, 1, 2)
        self.layout.addWidget(self.excel_btn, 2, 1)
        self.layout.addWidget(self.folder_btn, 2, 2)

    def init_vars(self):
        self.sorting_folder_path = None
        self.excel_path = None
        self.current_image_name = None
        self.excel_columns = {self.counterfeit_radio: ["C", 2], 
                self.money_order_radio: ["D", 2], 
                self.wire_radio: ["E", 2], 
                self.ach_radio: ["F", 2], 
                self.id_radio: ["G", 2], 
                self.credit_radio: ["H", 2], 
                self.enrollment_radio: ["I", 2], 
                "Enrolled Bank": ["J", ""], 
                self.receipt_radio: ["K", 2], 
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
                self.setup_image()
                for radio in self.radios:
                    radio.setEnabled(True)
        elif self.sender().text() == "Excel sheet":
            self.excel_path = QFileDialog.getOpenFileName(filter = 'Excel File (*.xlsx *.xls)')[0]
            if not self.excel_path:
                print("Nothing selected")
            else:
                self.folder_btn.setEnabled(True)
                self.excel = load_workbook(filename=self.excel_path)
                self.excel_others = self.excel["5. Other"]

    def amount_changed(self):
        try:
            if self.sender() == self.cash_amount:
                # FIXME: This will save to excel when trying to cycle images and there is a dollar amount on the excel
                if self.receipt_radio.isChecked() and not self.cycling:
                    self.excel_columns["Amount"][1] = float(self.sender().text())
                    self.write_excel()
            elif self.sender() == self.bank_text:
                if self.receipt_radio.isChecked():
                    self.excel_columns["Receipt Bank"][1] = self.sender().text()
                    self.write_excel()
                elif self.enrollment_radio.isChecked():
                    self.excel_columns["Enrolled Bank"][1] = self.sender().text()
                    self.write_excel()
        except ValueError:
            pass

    def radio_clicked(self):
        # TODO: Clean nested if else, if possible
        print(self.sender().text())
        if self.sender().parent() == self.receipt_type_group:
            if self.sender().isChecked():
                self.excel_columns["Receipt Type"][1] = self.receipt_type_group.children().index(self.sender()) + 1
                print(self.receipt_type_group.children().index(self.sender()) + 1)
        else:
            if self.sender().isChecked():
                self.excel_columns[self.sender()][1] = 1
                if self.sender() == self.receipt_radio:
                    self.cash_amount.setDisabled(False)
                    self.bank_text.setDisabled(False)
                    for radio in self.receipt_type_group.children():
                        radio.setEnabled(True)
                elif self.sender() == self.enrollment_radio:
                    self.bank_text.setDisabled(False)
            else:
                self.excel_columns[self.sender()][1] = 2
                if self.sender() == self.receipt_radio:
                    self.cash_amount.setDisabled(True)
                    self.bank_text.setDisabled(True)
                    self.cash_amount.setText("")
                    self.bank_text.setText("")
                    self.excel_columns["Amount"][1] = ""
                    self.excel_columns["Receipt Type"][1] = ""
                    self.excel_columns["Receipt Bank"][1] = ""
                    for radio in self.receipt_type_group.findChildren(QRadioButton):
                        radio.setAutoExclusive(False)
                        radio.setChecked(False)
                        radio.setAutoExclusive(True)
                        radio.setEnabled(False)
                elif self.sender() == self.enrollment_radio:
                    self.bank_text.setDisabled(True)
                    self.bank_text.setText("")
                    self.excel_columns["Enrolled Bank"][1] = ""

        if not self.cycling and self.sender().isChecked():
            self.write_excel()
    
    # Find if image id in excel
    def find_entry(self):
        radio_columns = ["C","D","E","F","G","H","I","K"]

        # File name is split into 5 parts
        # 0. The string "photo", 1. photo id, 2. date (DD/MM/YYYY), 3. time (24 HR), 4. file type
        split = re.split("_|@|\.", self.current_image_name)
        self.excel_row = 1

        # Find empty row or row where entry already exists
        while True:
            self.excel_row += 1
            if self.excel_others[f"A{self.excel_row}"].value == int(split[1]):
                print(f"existing entry found on row {self.excel_row}")
                break
            elif not self.excel_others[f"A{self.excel_row}"].value:
                print(f"new entry, empty row available to write on row {self.excel_row}")
                break

        self.excel_columns["Enrolled Bank"][1] = self.excel_others[f"J{self.excel_row}"].value
        self.excel_columns["Receipt Type"][1] = self.excel_others[f"L{self.excel_row}"].value
        self.excel_columns["Receipt Bank"][1] = self.excel_others[f"M{self.excel_row}"].value
        self.excel_columns["Amount"][1] = self.excel_others[f"N{self.excel_row}"].value
        
        # Set amount & radio state for new img
        
        for i, column in enumerate(radio_columns):
            if self.excel_others[f"{column}{self.excel_row}"].value == 1:
                self.radios[i].setChecked(True)
            else:
                # SetAutoExclusive to allow radio unchecking
                self.radios[i].setAutoExclusive(False)
                self.radios[i].setChecked(False)
                self.radios[i].setAutoExclusive(True)
        
        if self.excel_others[f"L{self.excel_row}"].value:
            print(f"Receipt Type: {self.excel_others[f'L{self.excel_row}'].value}")
            self.receipt_type_group.findChildren(QRadioButton)[self.excel_others[f"L{self.excel_row}"].value - 1].setChecked(True)
        else:
            for radio in self.receipt_type_group.findChildren(QRadioButton):
                radio.setAutoExclusive(False)
                radio.setChecked(False)
                radio.setAutoExclusive(True)
        
        if self.excel_columns["Amount"][1]:
            self.cash_amount.setText(str(self.excel_columns["Amount"][1]))
        else:
            self.cash_amount.setText("")
        
        if self.excel_columns["Enrolled Bank"][1]:
            self.bank_text.setText(self.excel_columns["Enrolled Bank"][1])
        elif self.excel_columns["Receipt Bank"][1]:
            self.bank_text.setText(self.excel_columns["Receipt Bank"][1])
        else:
            self.bank_text.setText("")

    
    def write_excel(self):
        print(f"Writing on row {self.excel_row}")
        split = re.split("_|@|\.", self.current_image_name)
        
        self.excel_others[f"A{self.excel_row}"] = int(split[1])
        self.excel_others[f"B{self.excel_row}"] = split[2]
        for type in self.excel_columns:
            self.excel_others[f"{self.excel_columns[type][0]}{self.excel_row}"] = self.excel_columns[type][1]

        try:
            self.excel.save(self.excel_path)
        except:
            print("Failed to save excel sheet.")

    def setup_image(self):
        self.folder_files = os.listdir(self.sorting_folder_path)
        if len(self.folder_files) > 0:
            self.cycling = True
            self.img_display.setPixmap(QPixmap(f"{self.sorting_folder_path}/{self.folder_files[self.img_num]}").scaled(QSize(1000,1000)))
            self.current_image_name = self.folder_files[self.img_num]
            self.update()
            self.find_entry()
            self.next_btn.show()
            self.prev_btn.show()
            self.cycling = False
    
    def cycle_img(self):
        self.cycling = True
        if self.sender() == self.next_btn:
            self.img_num += 1
        elif self.sender() == self.prev_btn:
            self.img_num -= 1
        
        self.prev_btn.setEnabled(self.img_num > 0)
        self.next_btn.setEnabled(self.img_num < len(self.folder_files) - 1)
        self.cycling = False

        self.update()
        self.setup_image()

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.setLayout(window.layout)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()