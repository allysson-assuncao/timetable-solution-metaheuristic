import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton

app = QApplication(sys.argv)
w = QWidget()
l = QVBoxLayout(w)

lbl1 = QLabel("Default Font")
lbl2 = QLabel("EM Font")
lbl2.setStyleSheet("font-size: 2em;")

btn = QPushButton("Zoom In")
def zoom():
    f = app.font()
    f.setPointSize(f.pointSize() + 2)
    app.setFont(f)

btn.clicked.connect(zoom)

l.addWidget(lbl1)
l.addWidget(lbl2)
l.addWidget(btn)
w.show()
sys.exit(app.exec())
