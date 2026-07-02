# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QPushButton, QMessageBox, QFileDialog
from src.controllers.main_controller import MainController
from src.views.forms.teacher_form import TeacherForm
from src.views.forms.demand_form import DemandForm
from src.utils.json_exporter import export_to_json

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STP Data Entry")
        self.setMinimumSize(700, 500)
        self.controller = MainController()

        self.init_ui()

        # Update export button state on validation fail
        self.controller.validation_failed.connect(lambda: self.btn_export.setEnabled(False))
        self.controller.validation_success.connect(lambda: self.btn_export.setEnabled(True))

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.teacher_tab = TeacherForm(self.controller)
        self.demand_tab = DemandForm(self.controller)
        
        self.tabs.addTab(self.teacher_tab, "Professores (H2)")
        self.tabs.addTab(self.demand_tab, "Demandas (H3, H4)")

        layout.addWidget(self.tabs)

        self.btn_export = QPushButton("Gerar Arquivo JSON (Payload)")
        self.btn_export.setMinimumHeight(40)
        self.btn_export.clicked.connect(self.export_json)
        layout.addWidget(self.btn_export)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Payload JSON", "dataset.json", "JSON Files (*.json)")
        if path:
            export_to_json(self.controller.state, path)
            QMessageBox.information(self, "Sucesso", f"Arquivo JSON estruturado gerado com sucesso em:\n{path}")
