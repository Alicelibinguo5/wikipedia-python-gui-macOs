from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yellow Box Test")
        self.setMinimumSize(400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create yellow entry box
        self.entry = QLineEdit()
        self.entry.setStyleSheet("""
            QLineEdit {
                background-color: #FFFF00;
                padding: 10px;
                font-size: 18px;
                border: 2px solid #808080;
                border-radius: 5px;
            }
        """)
        self.entry.setPlaceholderText("Type something here!")
        layout.addWidget(self.entry)

        # Create label
        self.label = QLabel("Type in the yellow box above!")
        self.label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.label)

        # Create button
        self.button = QPushButton("Show Text")
        self.button.clicked.connect(self.update_label)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: lightblue;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.button)

    def update_label(self):
        self.label.setText(f"You typed: {self.entry.text()}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()