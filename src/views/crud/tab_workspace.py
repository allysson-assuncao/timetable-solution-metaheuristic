# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from src.models.state_manager import StateManager
from src.utils.persistence import WorkspacePersistence

class TabWorkspace(QWidget):
    def __init__(self, state_manager: StateManager, ui_main):
        super().__init__()
        self.state_manager = state_manager
        self.ui_main = ui_main
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        lbl_title = QLabel("Gerenciamento de Workspace")
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Salve o estado atual do seu projeto em um arquivo JSON para continuar depois, ou carregue um arquivo existente.")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)
        
        btn_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("Salvar Workspace (Exportar JSON)")
        self.btn_export.setMinimumHeight(50)
        self.btn_export.clicked.connect(self.export_workspace)
        btn_layout.addWidget(self.btn_export)
        
        self.btn_import = QPushButton("Carregar Workspace (Importar JSON)")
        self.btn_import.setMinimumHeight(50)
        self.btn_import.setStyleSheet("font-weight: bold;")
        self.btn_import.clicked.connect(self.import_workspace)
        btn_layout.addWidget(self.btn_import)
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

    def export_workspace(self):
        path, _ = QFileDialog.getSaveFileName(self, "Salvar Workspace JSON", "workspace.json", "JSON Files (*.json)")
        if path:
            try:
                WorkspacePersistence.export_workspace(self.state_manager.state, path)
                QMessageBox.information(self, "Sucesso", f"Workspace salvo em:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao salvar workspace:\n{e}")

    def import_workspace(self):
        # Proteção contra sobrescrita
        if len(self.state_manager.state.professores) > 0 or len(self.state_manager.state.turmas) > 0:
            reply = QMessageBox.question(self, 'Alerta de Sobrescrita', 
                                        "Você já possui dados preenchidos na memória.\nCarregar um novo workspace irá limpar o progresso atual não salvo. Deseja continuar?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return
                
        path, _ = QFileDialog.getOpenFileName(self, "Abrir Workspace JSON", "", "JSON Files (*.json)")
        if path:
            try:
                # Dispara validação rigorosa
                new_state = WorkspacePersistence.import_workspace(path)
                self.state_manager.state = new_state
                # Resincroniza UI
                self.ui_main.refresh_all_tabs()
                QMessageBox.information(self, "Sucesso", "Workspace carregado e validado com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro de Validação", f"O arquivo contém inconsistências matemáticas ou está corrompido:\n{e}")
