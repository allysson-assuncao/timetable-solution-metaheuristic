# pyrefly: ignore [missing-import]
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.stp_state import STPState, Professor, Demanda, Turma, Disciplina
from src.models.validators import STPValidator

class StateManager(QObject):
    validation_failed = pyqtSignal(str)
    validation_success = pyqtSignal()
    
    # Sinais de notificação de CRUD (Event Bus)
    state_updated = pyqtSignal()
    professors_changed = pyqtSignal()
    classes_changed = pyqtSignal()
    disciplines_changed = pyqtSignal()
    demands_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.state = STPState()

    # --- Disciplinas ---
    def add_or_update_discipline(self, id_disc: str, nome: str):
        existing = next((d for d in self.state.disciplinas if d.id_disciplina == id_disc), None)
        if existing:
            existing.nome = nome
        else:
            self.state.disciplinas.append(Disciplina(id_disciplina=id_disc, nome=nome))
        self.disciplines_changed.emit()

    def delete_discipline(self, id_disc: str) -> bool:
        if any(d.id_disciplina == id_disc for d in self.state.demandas):
            self.validation_failed.emit(f"Não é possível excluir a Disciplina '{id_disc}' pois ela possui demandas vinculadas.")
            return False
        self.state.disciplinas = [d for d in self.state.disciplinas if d.id_disciplina != id_disc]
        self.disciplines_changed.emit()
        return True

    # --- Turmas ---
    def add_or_update_class(self, id_turma: str, nome: str):
        existing = next((t for t in self.state.turmas if t.id_turma == id_turma), None)
        if existing:
            existing.nome = nome
        else:
            self.state.turmas.append(Turma(id_turma=id_turma, nome=nome))
        self.classes_changed.emit()

    def delete_class(self, id_turma: str) -> bool:
        if any(d.id_turma == id_turma for d in self.state.demandas):
            self.validation_failed.emit(f"Não é possível excluir a Turma '{id_turma}' pois ela possui demandas vinculadas.")
            return False
        self.state.turmas = [t for t in self.state.turmas if t.id_turma != id_turma]
        self.classes_changed.emit()
        return True

    # --- Professores ---
    def add_or_update_professor(self, id_prof: str, nome: str, carga: int, indisp: list[int]):
        existing = next((p for p in self.state.professores if p.id_professor == id_prof), None)
        if existing:
            existing.nome = nome
            existing.carga_maxima = carga
            existing.indisponibilidades = indisp
        else:
            self.state.professores.append(Professor(
                id_professor=id_prof, nome=nome, carga_maxima=carga, indisponibilidades=indisp
            ))
        self.professors_changed.emit()

    def delete_professor(self, id_prof: str) -> bool:
        if any(d.id_professor == id_prof for d in self.state.demandas):
            self.validation_failed.emit(f"Não é possível excluir o Professor '{id_prof}' pois ele possui demandas vinculadas.")
            return False
        self.state.professores = [p for p in self.state.professores if p.id_professor != id_prof]
        self.professors_changed.emit()
        return True

    # --- Demandas ---
    def validate_demanda(self, id_professor: str, id_turma: str, quantidade_aulas: int) -> bool:
        if not STPValidator.check_h3_workload(id_professor, quantidade_aulas, self.state):
            cap = STPValidator.get_dynamic_capacity(id_professor, self.state)
            self.validation_failed.emit(f"(H2+H3) Capacidade Dinâmica Excedida. Espaço disponível: {cap}")
            return False
        
        if not STPValidator.check_h4_capacity(id_turma, quantidade_aulas, self.state):
            self.validation_failed.emit(f"(H4) Capacidade da Turma {id_turma} Excedida")
            return False
        
        self.validation_success.emit()
        return True

    def add_or_update_demanda(self, idx: int, id_professor: str, id_turma: str, id_disciplina: str, quantidade_aulas: int) -> bool:
        old_demanda = None
        if idx >= 0 and idx < len(self.state.demandas):
            old_demanda = self.state.demandas.pop(idx)
        
        if self.validate_demanda(id_professor, id_turma, quantidade_aulas):
            novo = Demanda(id_professor=id_professor, id_turma=id_turma, id_disciplina=id_disciplina, quantidade_aulas=quantidade_aulas)
            if idx >= 0:
                self.state.demandas.insert(idx, novo)
            else:
                self.state.demandas.append(novo)
            self.demands_changed.emit()
            return True
        else:
            if old_demanda:
                self.state.demandas.insert(idx, old_demanda)
            return False

    def delete_demanda(self, idx: int):
        if idx >= 0 and idx < len(self.state.demandas):
            self.state.demandas.pop(idx)
            self.demands_changed.emit()
