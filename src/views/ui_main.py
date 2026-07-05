# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QListWidget
from src.models.state_manager import StateManager
from src.views.crud.tab_workspace import TabWorkspace
from src.views.crud.tab_parameters import TabParameters
from src.views.crud.tab_disciplines import TabDisciplines
from src.views.crud.tab_classes import TabClasses
from src.views.crud.tab_professors import TabProfessors
from src.views.crud.tab_demands import TabDemands

class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STP Application - Otimização de Horários")
        self.setMinimumSize(950, 650)
        self.state_manager = StateManager()
        
        self.state_manager.validation_failed.connect(self.show_error)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.addItem("🏠 Workspace (I/O)")
        self.sidebar.addItem("Parâmetros")
        self.sidebar.addItem("Disciplinas")
        self.sidebar.addItem("Turmas")
        self.sidebar.addItem("Professores (H2)")
        self.sidebar.addItem("Demandas (H3, H4)")
        self.sidebar.addItem("🚀 Hub de Execução")
        self.sidebar.addItem("🎬 Auditoria & Playback")
        
        # Stacked Widget (Content)
        self.stack = QStackedWidget()
        self.stack.addWidget(TabWorkspace(self.state_manager, self))
        self.stack.addWidget(TabParameters(self.state_manager))
        self.stack.addWidget(TabDisciplines(self.state_manager))
        self.stack.addWidget(TabClasses(self.state_manager))
        self.stack.addWidget(TabProfessors(self.state_manager))
        self.stack.addWidget(TabDemands(self.state_manager))
        
        # O Hub de execução será instanciado agora
        from src.views.crud.tab_execution import TabExecution
        self.stack.addWidget(TabExecution(self.state_manager, self))
        
        # A aba de Playback também precisa ser instanciada
        from src.views.crud.tab_playback import TabPlayback
        self.stack.addWidget(TabPlayback())
        
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        
        layout.addWidget(self.sidebar)
        
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.stack)
        
        layout.addLayout(content_layout)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_error(self, msg: str):
        if "excluir" in msg:
            QMessageBox.warning(self, "Bloqueio de Exclusão", msg)

    def refresh_all_tabs(self):
        """Dispara recarregamento das tabelas e inputs com base no novo state."""
        try:
            self.stack.widget(1).load_params()
            self.stack.widget(2).refresh_table()
            self.stack.widget(3).refresh_table()
            self.stack.widget(4).build_grid()
            self.stack.widget(5).refresh_table()
        except Exception as e:
            print("Warning: Erro no refresh_all_tabs:", e)
