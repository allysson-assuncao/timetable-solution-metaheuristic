# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox, QListWidget, QTabWidget, QApplication
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from PyQt6.QtCore import Qt
from src.models.state_manager import StateManager
from src.views.crud.tab_workspace import TabWorkspace
from src.views.crud.tab_parameters import TabParameters
from src.views.crud.tab_disciplines import TabDisciplines
from src.views.crud.tab_classes import TabClasses
from src.views.crud.tab_professors import TabProfessors
from src.views.crud.tab_demands import TabDemands
from src.views.crud.tab_execution import TabExecution
from src.views.crud.tab_playback import TabPlayback

class UIMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STP Application - Otimização de Horários")
        self.setMinimumSize(1000, 700)
        self.state_manager = StateManager()
        
        self.state_manager.validation_failed.connect(self.show_error)

        self.base_font_size = 12
        self.current_font_size = self.base_font_size
        self.apply_font_size()

        self.init_ui()
        self.setup_zoom_shortcuts()

    def apply_font_size(self):
        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSize(self.current_font_size)
            app.setFont(font)

    def setup_zoom_shortcuts(self):
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self.zoom_reset)

    def zoom_in(self):
        self.current_font_size = min(self.current_font_size + 2, 36)
        self.apply_font_size()

    def zoom_out(self):
        self.current_font_size = max(self.current_font_size - 2, 8)
        self.apply_font_size()

    def zoom_reset(self):
        self.current_font_size = self.base_font_size
        self.apply_font_size()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            elif delta < 0:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def init_ui(self):
        self.top_tabs = QTabWidget()
        
        # TAB 1: WORKSTATION
        self.workstation_widget = QWidget()
        workstation_layout = QHBoxLayout()
        
        # Sidebar for Workstation
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.addItem("Workspace (I/O) 🏠")
        self.sidebar.addItem("Parâmetros")
        self.sidebar.addItem("Disciplinas")
        self.sidebar.addItem("Turmas")
        self.sidebar.addItem("Professores (H2)")
        self.sidebar.addItem("Demandas (H3, H4)")
        
        # Stacked Widget for Workstation
        self.stack = QStackedWidget()
        self.stack.addWidget(TabWorkspace(self.state_manager, self))
        self.stack.addWidget(TabParameters(self.state_manager))
        self.stack.addWidget(TabDisciplines(self.state_manager))
        self.stack.addWidget(TabClasses(self.state_manager))
        self.stack.addWidget(TabProfessors(self.state_manager))
        self.stack.addWidget(TabDemands(self.state_manager))
        
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)
        
        workstation_layout.addWidget(self.sidebar)
        workstation_layout.addWidget(self.stack)
        self.workstation_widget.setLayout(workstation_layout)
        
        # TAB 2: EXECUTION HUB
        self.execution_widget = TabExecution(self.state_manager, self)
        
        # TAB 3: AUDIT & PLAYBACK
        self.playback_widget = TabPlayback()
        
        # Add Top Tabs
        self.top_tabs.addTab(self.workstation_widget, "⚙️ Workstation (I/O)")
        self.top_tabs.addTab(self.execution_widget, "🚀 Execution Hub")
        self.top_tabs.addTab(self.playback_widget, "🎬 Audit & Playback")
        
        self.setCentralWidget(self.top_tabs)

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
            self.stack.widget(4).refresh_table() # BUGFIX: Faltava isso no código anterior!
            self.stack.widget(5).refresh_table()
        except Exception as e:
            print("Warning: Erro no refresh_all_tabs:", e)

    # Hack de roteamento para a TabExecution que tentará alterar a aba de Playback:
    # A TabExecution chama: self.ui_main.sidebar.setCurrentRow(7) e self.ui_main.stack.widget(7)
    # Precisamos expor métodos auxiliares para não quebrar a lógica de navegação do Hub:
    def open_playback_tab(self):
        self.top_tabs.setCurrentIndex(2)
