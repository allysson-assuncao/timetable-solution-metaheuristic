import numpy as np
from src.models.stp_state import STPState

class TimetableState:
    """
    Representação computacional do quadro de horários.
    Linhas (M) = Professores
    Colunas (P) = Períodos Totais (dias_letivos * periodos_por_dia)
    """
    def __init__(self, stp_state: STPState):
        self.stp_state = stp_state
        
        # Mapeamentos O(1) de Indexação
        self.prof_id_to_idx = {p.id_professor: i for i, p in enumerate(stp_state.professores)}
        self.idx_to_prof_id = {i: p.id_professor for i, p in enumerate(stp_state.professores)}
        
        M = len(stp_state.professores)
        P = stp_state.parametros_execucao.dias_letivos * stp_state.parametros_execucao.periodos_por_dia
        
        # Matriz principal
        self.matrix = np.full((M, P), 0, dtype=np.int32)
        
        # Codificação Turma/Disciplina <-> Inteiro
        self.class_disc_to_int = {}
        self.int_to_class_disc = {}
        self.next_code = 1
        
        self._initialize_indisponibilidades()
        self._build_encoding_map()

    def _initialize_indisponibilidades(self):
        """Preenche -1 nos slots onde o professor não pode lecionar."""
        for prof in self.stp_state.professores:
            if prof.id_professor not in self.prof_id_to_idx: continue
            row_idx = self.prof_id_to_idx[prof.id_professor]
            for slot_1_based in prof.indisponibilidades:
                col_idx = slot_1_based - 1 # Converte para 0-based
                if 0 <= col_idx < self.matrix.shape[1]:
                    self.matrix[row_idx, col_idx] = -1

    def _build_encoding_map(self):
        """Mapeia cada combinação (Turma, Disciplina) para um inteiro único."""
        for d in self.stp_state.demandas:
            key = (d.id_turma, d.id_disciplina)
            if key not in self.class_disc_to_int:
                self.class_disc_to_int[key] = self.next_code
                self.int_to_class_disc[self.next_code] = key
                self.next_code += 1

    def get_cell_info(self, row: int, col: int):
        val = self.matrix[row, col]
        if val == -1: return "Indisponível"
        if val == 0: return "Vago"
        return self.int_to_class_disc.get(val, "Desconhecido")
