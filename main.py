from PyQt6.QtWidgets import QApplication, QWidget, QRadioButton, QGroupBox, QVBoxLayout, QFileDialog, QPushButton, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QSize
import sys
import os
from openpyxl import load_workbook

selected = None
class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.init_vars()
        self.init_ui()

        self.resize(1920,1080)
        self.setWindowTitle("EBCS Image Sorter")

        self.folder_btn.clicked.connect(self.launch_dialog)
        self.excel_btn.clicked.connect(self.launch_dialog)

    def init_ui(self):
        self.radios = []
        self.radio_group = QGroupBox(self)
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

        self.img_box = QLabel(self)
        self.img_box.move(300,0)
        self.img_box.resize(1000,1000)

        for radio in self.radios:
            radio.clicked.connect(self.radio_clicked)
            self.radio_vbox.addWidget(radio)

        self.radio_group.setLayout(self.radio_vbox)
        self.folder_btn = QPushButton("Select EBCS sorting folder", self)
        self.excel_btn = QPushButton("Excel sheet", self)
        self.folder_btn.move(200,100)
        self.excel_btn.move(200,150)

    def init_vars(self):
        self.sorting_folder_path = None
        self.excel_path = None
        self.current_image_name = None
        self.sorted = []


    def launch_dialog(self):
        print(self.sender().text())
        if self.sender().text() == "Select EBCS sorting folder":
            self.sorting_folder_path = QFileDialog.getExistingDirectory()
            if not self.sorting_folder_path:
                print("Nothing selected")
            else:
                self.setup_images()
        elif self.sender().text() == "Excel sheet":
            self.excel_sheet_path = QFileDialog.getOpenFileName(filter = 'Excel File (*.xlsx *.xls)')[0]
            if not self.excel_path:
                print("Nothing selected")
            else:
                self.setup_excel()

    def radio_clicked(self):
        global selected

        match self.sender():
            case self.counterfeit_radio:
                pass
            case self.money_order_radio:
                pass
            case self.wire_radio:
                pass
            case self.ach_radio:
                pass
            case self.id_radio:
                pass
            case self.credit_radio:
                pass
            case self.enrollment_radio:
                pass
            case self.receipt_radio:
                pass
        print(selected)
    
    def setup_excel(self):
        self.excel = load_workbook(filename=self.excel_path)
        self.excel_others = self.excel["5. Other"]
    
    def setup_images(self):
        dir_files = os.listdir(self.sorting_folder_path)
        #self.img_box.resize(1000,1000)
        if len(dir_files) > 0:
            self.img_box.setPixmap(QPixmap(f"{self.sorting_folder_path}/{dir_files[0]}").scaled(QSize(1000,1000)))
            self.update()
            print(self.img_box.pixmap.__getattribute__)
        print(dir_files)


def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()