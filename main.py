from PyQt6.QtWidgets import QApplication, QWidget, QRadioButton, QGroupBox, QVBoxLayout
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500,500)
        self.setWindowTitle("EBCS Image Sorter")

        self.radios = []
        self.radio_group = QGroupBox(self)
        self.radio_vbox = QVBoxLayout()
        
        self.accounts_radio = QRadioButton("Bank Account", self)
        self.checks_radio = QRadioButton("Check", self)
        self.dl_radio = QRadioButton("Driver's License", self)
        self.mta_radio = QRadioButton("Money Transfer Application", self)
        self.radios.extend((self.accounts_radio, self.checks_radio, self.dl_radio, self.mta_radio))

        for radio in self.radios:
            radio.clicked.connect(self.radioClicked)
            self.radio_vbox.addWidget(radio)

        self.radio_group.setLayout(self.radio_vbox)


    def radioClicked(self):

        match self.sender().text():
            case "Bank Account":
                print("Bank")
            case "Check":
                print("Check")
            case "Driver's License":
                print("License")
            case "Money Transfer Application":
                print("Transfer App")

def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()