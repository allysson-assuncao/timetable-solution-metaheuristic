# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QMessageBox, QFileDialog, QListWidget
from src.models.state_manager import StateManager
from src.views.crud.tab_parameters import TabParameters
from src.views.crud.tab_disciplines import TabDisciplines
from src.views.crud.tab_classes import TabClasses
from src.views.crud.tab_professors import TabProfessors
from src.views.crud.tab_demands import TabDemands
from src.utils.json_exporter import export_to_json

class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STP Data Entry CRUD")
        self.setMinimumSize(900, 600)
        self.state_manager = StateManager()
        
        self.state_manager.validation_failed.connect(self.show_error)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItem("Parâmetros")
        self.sidebar.addItem("Disciplinas")
        self.sidebar.addItem("Turmas")
        self.sidebar.addItem("Professores (H2)")
        self.sidebar.addItem("Demandas (H3, H4)")
        
        # Stacked Widget (Content)
        self.stack = QStackedWidget()
        self.stack.addWidget(TabParameters(self.state_manager))
        self.stack.addWidget(TabDisciplines(self.state_manager))
        self.stack.addWidget(TabClasses(self.state_manager))
        self.stack.addWidget(TabProfessors(self.state_manager))
        self.stack.addWidget(TabDemands(self.state_manager))
        
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        
        layout.addWidget(self.sidebar)
        
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.stack)
        
        self.btn_export = QPushButton("Gerar Arquivo JSON (Payload)")
        self.btn_export.setMinimumHeight(40)
        self.btn_export.clicked.connect(self.export_json)
        content_layout.addWidget(self.btn_export)
        
        layout.addLayout(content_layout)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_error(self, msg: str):
        if "excluir" in msg:
            # Integridade referencial
            QMessageBox.warning(self, "Bloqueio de Exclusão", msg)

    def export_json(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Payload JSON", "dataset_crud.json", "JSON Files (*.json)")
        if path:
            export_to_json(self.state_manager.state, path)
            QMessageBox.information(self, "Sucesso", f"Arquivo JSON gerado com sucesso em:\n{path}")
