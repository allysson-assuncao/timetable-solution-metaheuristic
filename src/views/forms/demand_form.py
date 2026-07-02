from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from src.controllers.main_controller import MainController

class DemandForm(QWidget):
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.init_ui()

        # Conecta os sinais do controller
        self.controller.validation_failed.connect(self.on_validation_failed)
        self.controller.validation_success.connect(self.on_validation_success)

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.input_professor = QLineEdit()
        self.input_turma = QLineEdit()
        self.input_disciplina = QLineEdit()
        self.input_aulas = QLineEdit()
        
        form_layout.addRow("ID Professor:", self.input_professor)
        form_layout.addRow("ID Turma:", self.input_turma)
        form_layout.addRow("Disciplina:", self.input_disciplina)
        form_layout.addRow("Qtd Aulas:", self.input_aulas)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: red; font-weight: bold;")
        self.lbl_error.setVisible(False)

        self.btn_submit = QPushButton("Adicionar Demanda")
        self.btn_submit.clicked.connect(self.submit_demand)

        layout.addLayout(form_layout)
        layout.addWidget(self.lbl_error)
        layout.addWidget(self.btn_submit)

        self.setLayout(layout)

        # Remove o estado de erro assim que o usuário edita os campos
        self.input_aulas.textChanged.connect(self.clear_error_state)
        self.input_professor.textChanged.connect(self.clear_error_state)
        self.input_turma.textChanged.connect(self.clear_error_state)

    def submit_demand(self):
        try:
            aulas = int(self.input_aulas.text())
        except ValueError:
            self.lbl_error.setText("Qtd Aulas deve ser um número inteiro válido.")
            self.lbl_error.setVisible(True)
            self.input_aulas.setStyleSheet("border: 2px solid red;")
            self.btn_submit.setEnabled(False)
            return

        # Disable briefly while attempting
        self.btn_submit.setEnabled(False) 

        # Controller validará (H3, H4) antes de inserir
        success = self.controller.add_demanda(
            self.input_professor.text(),
            self.input_turma.text(),
            self.input_disciplina.text(),
            aulas
        )
        if success:
            # Limpa após sucesso
            self.input_professor.clear()
            self.input_turma.clear()
            self.input_disciplina.clear()
            self.input_aulas.clear()
            self.btn_submit.setEnabled(True) # Reabilita

    def clear_error_state(self):
        self.btn_submit.setEnabled(True)
        self.lbl_error.setVisible(False)
        self.input_aulas.setStyleSheet("")
        self.input_professor.setStyleSheet("")
        self.input_turma.setStyleSheet("")

    def on_validation_failed(self, error_msg: str):
        self.lbl_error.setText(error_msg)
        self.lbl_error.setVisible(True)
        self.btn_submit.setEnabled(False)
        
        if "(H3)" in error_msg:
            self.input_aulas.setStyleSheet("border: 2px solid red;")
            self.input_professor.setStyleSheet("border: 2px solid red;")
        elif "(H4)" in error_msg:
            self.input_aulas.setStyleSheet("border: 2px solid red;")
            self.input_turma.setStyleSheet("border: 2px solid red;")

    def on_validation_success(self):
        self.btn_submit.setEnabled(True)
        self.lbl_error.setVisible(False)
        self.input_aulas.setStyleSheet("")
        self.input_professor.setStyleSheet("")
        self.input_turma.setStyleSheet("")
