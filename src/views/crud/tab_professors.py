# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout, QLabel
from src.models.state_manager import StateManager

class TabProfessors(QWidget):
    def __init__(self, state_manager: StateManager):
        super().__init__()
        self.state_manager = state_manager
        self.indisponibilidades = set()
        self.buttons = {}
        self.init_ui()
        self.state_manager.professors_changed.connect(self.refresh_table)
        self.state_manager.state_updated.connect(self.build_grid) # Rebuild grid if parameters change

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        
        self.input_id = QLineEdit()
        self.input_id.setPlaceholderText("ID")
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Nome")
        self.input_carga = QLineEdit()
        self.input_carga.setPlaceholderText("Carga Máxima")
        
        self.btn_submit = QPushButton("Adicionar")
        self.btn_submit.clicked.connect(self.submit_data)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self.reset_form)
        
        form_layout.addWidget(self.input_id)
        form_layout.addWidget(self.input_nome)
        form_layout.addWidget(self.input_carga)
        form_layout.addWidget(self.btn_submit)
        form_layout.addWidget(self.btn_cancel)
        layout.addLayout(form_layout)
        
        self.lbl_grade = QLabel("Indisponibilidades (Vermelho = Indisponível)")
        layout.addWidget(self.lbl_grade)
        
        self.grid_layout = QGridLayout()
        layout.addLayout(self.grid_layout)
        self.build_grid()

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nome", "Carga", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh_table()

    def build_grid(self):
        for btn in self.buttons.values():
            btn.deleteLater()
        self.buttons.clear()

        dias = self.state_manager.state.parametros_execucao.dias_letivos
        periodos = self.state_manager.state.parametros_execucao.periodos_por_dia

        for dia in range(dias):
            for periodo in range(periodos):
                indice = (dia * periodos) + periodo + 1
                btn = QPushButton(f"P{periodo+1}\nD{dia+1}")
                btn.setCheckable(True)
                btn.setStyleSheet("QPushButton:checked { background-color: #ff4c4c; color: white; font-weight: bold; }")
                btn.clicked.connect(lambda checked, idx=indice: self.toggle_indisp(idx, checked))
                self.grid_layout.addWidget(btn, periodo, dia)
                self.buttons[indice] = btn

    def toggle_indisp(self, indice, checked):
        if checked:
            self.indisponibilidades.add(indice)
        else:
            self.indisponibilidades.discard(indice)

    def submit_data(self):
        id_prof = self.input_id.text().strip()
        nome = self.input_nome.text().strip()
        try:
            carga = int(self.input_carga.text().strip())
        except:
            return
        if not id_prof:
            return
        
        self.state_manager.add_or_update_professor(id_prof, nome, carga, list(self.indisponibilidades))
        self.reset_form()

    def reset_form(self):
        self.input_id.clear()
        self.input_nome.clear()
        self.input_carga.clear()
        self.input_id.setEnabled(True)
        self.btn_submit.setText("Adicionar")
        self.btn_cancel.setVisible(False)
        self.indisponibilidades.clear()
        for btn in self.buttons.values():
            btn.setChecked(False)

    def edit_record(self, id_prof: str, nome: str, carga: int, indisp: list):
        self.reset_form()
        self.input_id.setText(id_prof)
        self.input_id.setEnabled(False)
        self.input_nome.setText(nome)
        self.input_carga.setText(str(carga))
        self.btn_submit.setText("Atualizar")
        self.btn_cancel.setVisible(True)
        
        self.indisponibilidades = set(indisp)
        for idx in indisp:
            if idx in self.buttons:
                self.buttons[idx].setChecked(True)

    def delete_record(self, id_prof: str):
        self.state_manager.delete_professor(id_prof)

    def refresh_table(self):
        self.table.setRowCount(0)
        for p in self.state_manager.state.professores:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p.id_professor))
            self.table.setItem(row, 1, QTableWidgetItem(p.nome))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.carga_maxima)))
            
            btn_panel = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0,0,0,0)
            
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, i=p.id_professor, n=p.nome, c=p.carga_maxima, ind=p.indisponibilidades: self.edit_record(i, n, c, ind))
            
            btn_del = QPushButton("Excluir")
            btn_del.clicked.connect(lambda checked, i=p.id_professor: self.delete_record(i))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            btn_panel.setLayout(btn_layout)
            
            self.table.setCellWidget(row, 3, btn_panel)
