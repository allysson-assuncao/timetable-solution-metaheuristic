# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from src.models.state_manager import StateManager

class TabClasses(QWidget):
    def __init__(self, state_manager: StateManager):
        super().__init__()
        self.state_manager = state_manager
        self.init_ui()
        self.state_manager.classes_changed.connect(self.refresh_table)

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID da Turma")
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome da Turma")
        
        self.btn_submit = QPushButton("Adicionar")
        self.btn_submit.clicked.connect(self.submit_data)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self.reset_form)
        
        form_layout.addWidget(self.input_id)
        form_layout.addWidget(self.input_nome)
        form_layout.addWidget(self.btn_submit)
        form_layout.addWidget(self.btn_cancel)
        layout.addLayout(form_layout)
        
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_table()

    def submit_data(self):
        id_turma = self.input_id.text().strip()
        nome = self.input_nome.text().strip()
        if not id_turma:
            return
        self.state_manager.add_or_update_class(id_turma, nome)
        self.reset_form()

    def reset_form(self):
        self.input_id.clear()
        self.input_nome.clear()
        self.input_id.setEnabled(True)
        self.btn_submit.setText("Adicionar")
        self.btn_cancel.setVisible(False)

    def edit_record(self, id_turma: str, nome: str):
        self.input_id.setText(id_turma)
        self.input_id.setEnabled(False)
        self.input_nome.setText(nome)
        self.btn_submit.setText("Atualizar")
        self.btn_cancel.setVisible(True)

    def delete_record(self, id_turma: str):
        self.state_manager.delete_class(id_turma)

    def refresh_table(self):
        self.table.setRowCount(0)
        for t in self.state_manager.state.turmas:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(t.id_turma))
            self.table.setItem(row, 1, QTableWidgetItem(t.nome))
            
            btn_panel = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0,0,0,0)
            
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, i=t.id_turma, n=t.nome: self.edit_record(i, n))
            
            btn_del = QPushButton("Excluir")
            btn_del.clicked.connect(lambda checked, i=t.id_turma: self.delete_record(i))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            btn_panel.setLayout(btn_layout)
            
            self.table.setCellWidget(row, 2, btn_panel)
