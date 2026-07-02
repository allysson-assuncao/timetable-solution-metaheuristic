# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from src.models.state_manager import StateManager

class TabParameters(QWidget):
    def __init__(self, state_manager: StateManager):
        super().__init__()
        self.state_manager = state_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        
        self.inp_alpha = QLineEdit()
        self.inp_beta = QLineEdit()
        self.inp_gamma = QLineEdit()
        self.inp_temp = QLineEdit()
        self.inp_dias = QLineEdit()
        self.inp_periodos = QLineEdit()

        form.addRow("Peso Alpha:", self.inp_alpha)
        form.addRow("Peso Beta:", self.inp_beta)
        form.addRow("Peso Gamma (H1):", self.inp_gamma)
        form.addRow("Temp Inicial SA:", self.inp_temp)
        form.addRow("Dias Letivos:", self.inp_dias)
        form.addRow("Períodos por Dia:", self.inp_periodos)
        
        btn_save = QPushButton("Salvar Parâmetros")
        btn_save.clicked.connect(self.save_params)
        
        layout.addLayout(form)
        layout.addWidget(btn_save)
        layout.addStretch()
        self.setLayout(layout)
        self.load_params()

    def load_params(self):
        p = self.state_manager.state.parametros_execucao
        self.inp_alpha.setText(str(p.pesos_objetivo.alpha))
        self.inp_beta.setText(str(p.pesos_objetivo.beta))
        self.inp_gamma.setText(str(p.pesos_objetivo.gamma))
        self.inp_temp.setText(str(p.sa_parametros.temperatura_inicial))
        self.inp_dias.setText(str(p.dias_letivos))
        self.inp_periodos.setText(str(p.periodos_por_dia))

    def save_params(self):
        try:
            p = self.state_manager.state.parametros_execucao
            p.pesos_objetivo.alpha = float(self.inp_alpha.text())
            p.pesos_objetivo.beta = float(self.inp_beta.text())
            p.pesos_objetivo.gamma = float(self.inp_gamma.text())
            p.sa_parametros.temperatura_inicial = float(self.inp_temp.text())
            p.dias_letivos = int(self.inp_dias.text())
            p.periodos_por_dia = int(self.inp_periodos.text())
            self.state_manager.state_updated.emit()
            QMessageBox.information(self, "Sucesso", "Parâmetros atualizados!")
        except ValueError:
            QMessageBox.warning(self, "Erro", "Valores numéricos inválidos.")
