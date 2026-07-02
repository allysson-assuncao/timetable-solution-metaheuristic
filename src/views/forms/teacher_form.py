from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QGridLayout, QLabel
from src.controllers.main_controller import MainController

class TeacherForm(QWidget):
    def __init__(self, controller: MainController):
        super().__init__()
        self.controller = controller
        self.indisponibilidades = set()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.input_id = QLineEdit()
        self.input_carga = QLineEdit()
        
        form_layout.addRow("ID Professor:", self.input_id)
        form_layout.addRow("Carga Máxima:", self.input_carga)

        layout.addLayout(form_layout)

        # Grade de indisponibilidade
        self.lbl_grade = QLabel("Selecione as Indisponibilidades (Vermelho = Indisponível)")
        layout.addWidget(self.lbl_grade)

        self.grid_layout = QGridLayout()
        self.buttons = {}
        
        dias = self.controller.state.parametros_execucao.dias_letivos
        periodos = self.controller.state.parametros_execucao.periodos_por_dia

        for dia in range(dias):
            for periodo in range(periodos):
                indice = (dia * periodos) + periodo + 1 # Índice baseado em 1
                btn = QPushButton(f"P{periodo+1}\nD{dia+1}")
                btn.setCheckable(True)
                btn.setStyleSheet("QPushButton:checked { background-color: #ff4c4c; color: white; font-weight: bold; }")
                btn.clicked.connect(lambda checked, idx=indice: self.toggle_indisp(idx, checked))
                self.grid_layout.addWidget(btn, periodo, dia)
                self.buttons[indice] = btn

        layout.addLayout(self.grid_layout)

        self.btn_submit = QPushButton("Salvar Professor")
        self.btn_submit.clicked.connect(self.submit_teacher)
        layout.addWidget(self.btn_submit)

        self.setLayout(layout)

    def toggle_indisp(self, indice, checked):
        if checked:
            self.indisponibilidades.add(indice)
        else:
            self.indisponibilidades.discard(indice)

    def submit_teacher(self):
        try:
            carga = int(self.input_carga.text())
        except ValueError:
            return

        self.controller.add_professor(
            self.input_id.text(),
            carga,
            list(self.indisponibilidades)
        )
        self.input_id.clear()
        self.input_carga.clear()
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.indisponibilidades.clear()
