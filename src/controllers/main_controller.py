from PyQt6.QtCore import QObject, pyqtSignal
from src.models.stp_state import STPState, Professor, Demanda
from src.models.validators import STPValidator

class MainController(QObject):
    validation_failed = pyqtSignal(str)
    validation_success = pyqtSignal()
    state_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state = STPState()

    def add_professor(self, id_professor: str, carga_maxima: int, indisponibilidades: list[int]):
        """Adiciona ou atualiza um professor no estado."""
        existing = next((p for p in self.state.professores if p.id_professor == id_professor), None)
        if existing:
            existing.carga_maxima = carga_maxima
            existing.indisponibilidades = indisponibilidades
        else:
            self.state.professores.append(Professor(
                id_professor=id_professor,
                carga_maxima=carga_maxima,
                indisponibilidades=indisponibilidades
            ))
        self.state_updated.emit()

    def validate_demanda(self, id_professor: str, id_turma: str, quantidade_aulas: int) -> bool:
        """Executa as validações H3 e H4 e emite sinais para a View."""
        if not STPValidator.check_h3_workload(id_professor, quantidade_aulas, self.state):
            self.validation_failed.emit(f"(H3) Carga Máxima Excedida para {id_professor}")
            return False
        
        if not STPValidator.check_h4_capacity(id_turma, quantidade_aulas, self.state):
            self.validation_failed.emit(f"(H4) Capacidade da Turma {id_turma} Excedida")
            return False
        
        self.validation_success.emit()
        return True

    def add_demanda(self, id_professor: str, id_turma: str, disciplina: str, quantidade_aulas: int) -> bool:
        """Tenta adicionar uma demanda, efetuando as validações antes."""
        if self.validate_demanda(id_professor, id_turma, quantidade_aulas):
            self.state.demandas.append(Demanda(
                id_professor=id_professor,
                id_turma=id_turma,
                disciplina=disciplina,
                quantidade_aulas=quantidade_aulas
            ))
            if id_turma not in self.state.turmas:
                self.state.turmas.append(id_turma)
            self.state_updated.emit()
            return True
        return False
