import os
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow
import sys

def main():
    app = QApplication(sys.argv)
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
    style_path = os.path.join(script_dir, 'style.qss')
    
    # Load the stylesheet
    with open(style_path, 'r') as f:
        stylesheet = f.read()
    app.setStyleSheet(stylesheet)
    
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
