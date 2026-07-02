# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLabel
from src.models.state_manager import StateManager

class TabDemands(QWidget):
    def __init__(self, state_manager: StateManager):
        super().__init__()
        self.state_manager = state_manager
        self.current_edit_idx = -1
        self.init_ui()
        
        self.state_manager.demands_changed.connect(self.refresh_table)
        self.state_manager.professors_changed.connect(self.populate_combos)
        self.state_manager.classes_changed.connect(self.populate_combos)
        self.state_manager.disciplines_changed.connect(self.populate_combos)
        self.state_manager.validation_failed.connect(self.show_error)
        self.state_manager.validation_success.connect(self.clear_error)

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()
        
        self.combo_prof = QComboBox()
        self.combo_turma = QComboBox()
        self.combo_disc = QComboBox()
        self.input_aulas = QLineEdit()
        self.input_aulas.setPlaceholderText("Qtd Aulas")
        
        self.btn_submit = QPushButton("Adicionar")
        self.btn_submit.clicked.connect(self.submit_data)
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setVisible(False)
        self.btn_cancel.clicked.connect(self.reset_form)
        
        form_layout.addWidget(self.combo_prof)
        form_layout.addWidget(self.combo_turma)
        form_layout.addWidget(self.combo_disc)
        form_layout.addWidget(self.input_aulas)
        form_layout.addWidget(self.btn_submit)
        form_layout.addWidget(self.btn_cancel)
        layout.addLayout(form_layout)
        
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: red; font-weight: bold;")
        self.lbl_error.setVisible(False)
        layout.addWidget(self.lbl_error)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Prof", "Turma", "Disc", "Aulas", "Ações"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.populate_combos()
        self.refresh_table()

    def populate_combos(self):
        prof_data = self.combo_prof.currentData()
        turma_data = self.combo_turma.currentData()
        disc_data = self.combo_disc.currentData()

        self.combo_prof.clear()
        for p in self.state_manager.state.professores:
            self.combo_prof.addItem(f"{p.id_professor} - {p.nome}", p.id_professor)
            
        self.combo_turma.clear()
        for t in self.state_manager.state.turmas:
            self.combo_turma.addItem(f"{t.id_turma} - {t.nome}", t.id_turma)
            
        self.combo_disc.clear()
        for d in self.state_manager.state.disciplinas:
            self.combo_disc.addItem(f"{d.id_disciplina} - {d.nome}", d.id_disciplina)

        if prof_data: self.combo_prof.setCurrentIndex(self.combo_prof.findData(prof_data))
        if turma_data: self.combo_turma.setCurrentIndex(self.combo_turma.findData(turma_data))
        if disc_data: self.combo_disc.setCurrentIndex(self.combo_disc.findData(disc_data))

    def show_error(self, msg: str):
        if "(H" in msg:
            self.lbl_error.setText(msg)
            self.lbl_error.setVisible(True)

    def clear_error(self):
        self.lbl_error.setVisible(False)

    def submit_data(self):
        prof_id = self.combo_prof.currentData()
        turma_id = self.combo_turma.currentData()
        disc_id = self.combo_disc.currentData()
        try:
            aulas = int(self.input_aulas.text().strip())
        except:
            return
            
        if not prof_id or not turma_id or not disc_id:
            self.show_error("Selecione Professor, Turma e Disciplina.")
            return

        success = self.state_manager.add_or_update_demanda(self.current_edit_idx, prof_id, turma_id, disc_id, aulas)
        if success:
            self.reset_form()

    def reset_form(self):
        self.input_aulas.clear()
        self.btn_submit.setText("Adicionar")
        self.btn_cancel.setVisible(False)
        self.current_edit_idx = -1
        self.clear_error()

    def edit_record(self, idx: int, prof_id: str, turma_id: str, disc_id: str, aulas: int):
        self.reset_form()
        
        idx_prof = self.combo_prof.findData(prof_id)
        if idx_prof >= 0: self.combo_prof.setCurrentIndex(idx_prof)
        
        idx_turma = self.combo_turma.findData(turma_id)
        if idx_turma >= 0: self.combo_turma.setCurrentIndex(idx_turma)
        
        idx_disc = self.combo_disc.findData(disc_id)
        if idx_disc >= 0: self.combo_disc.setCurrentIndex(idx_disc)
        
        self.input_aulas.setText(str(aulas))
        
        self.btn_submit.setText("Atualizar")
        self.btn_cancel.setVisible(True)
        self.current_edit_idx = idx

    def delete_record(self, idx: int):
        self.state_manager.delete_demanda(idx)

    def refresh_table(self):
        self.table.setRowCount(0)
        for idx, d in enumerate(self.state_manager.state.demandas):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(d.id_professor))
            self.table.setItem(row, 1, QTableWidgetItem(d.id_turma))
            self.table.setItem(row, 2, QTableWidgetItem(d.id_disciplina))
            self.table.setItem(row, 3, QTableWidgetItem(str(d.quantidade_aulas)))
            
            btn_panel = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0,0,0,0)
            
            btn_edit = QPushButton("Editar")
            btn_edit.clicked.connect(lambda checked, i=idx, p=d.id_professor, t=d.id_turma, ds=d.id_disciplina, a=d.quantidade_aulas: self.edit_record(i, p, t, ds, a))
            
            btn_del = QPushButton("Excluir")
            btn_del.clicked.connect(lambda checked, i=idx: self.delete_record(i))
            
            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            btn_panel.setLayout(btn_layout)
            
            self.table.setCellWidget(row, 4, btn_panel)
