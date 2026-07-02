from typing import List
from .stp_state import STPState, Professor, Demanda

class STPValidator:
    @staticmethod
    def check_h3_workload(professor_id: str, new_demanda_aulas: int, state: STPState) -> bool:
        """
        Verifica se a adição de 'new_demanda_aulas' excede a carga máxima do professor (H3).
        """
        prof = next((p for p in state.professores if p.id_professor == professor_id), None)
        if not prof:
            return True # Permite se o professor não existir na lista ainda

        current_aulas = sum(d.quantidade_aulas for d in state.demandas if d.id_professor == professor_id)
        return (current_aulas + new_demanda_aulas) <= prof.carga_maxima

    @staticmethod
    def check_h4_capacity(turma_id: str, new_demanda_aulas: int, state: STPState) -> bool:
        """
        Verifica se a adição excede a capacidade física da turma (H4).
        Capacidade = periodos_por_dia * dias_letivos.
        """
        max_capacity = state.parametros_execucao.periodos_por_dia * state.parametros_execucao.dias_letivos
        current_aulas = sum(d.quantidade_aulas for d in state.demandas if d.id_turma == turma_id)
        return (current_aulas + new_demanda_aulas) <= max_capacity
