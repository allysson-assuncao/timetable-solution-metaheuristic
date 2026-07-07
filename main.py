import sys
from pathlib import Path
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QApplication
from src.views.ui_main import UIMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)


    window = UIMainWindow()
    window.show()
    sys.exit(app.exec())
