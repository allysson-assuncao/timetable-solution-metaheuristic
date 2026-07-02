from typing import List
from .stp_state import STPState, Professor, Demanda

class STPValidator:
    @staticmethod
    def get_dynamic_capacity(professor_id: str, state: STPState) -> int:
        """
        Calcula a capacidade dinâmica do professor (H3 + H2).
        Capacidade = min(Carga_Maxima, Total_Periodos - Indisponibilidades) - Aulas_Ja_Alocadas
        """
        prof = next((p for p in state.professores if p.id_professor == professor_id), None)
        if not prof:
            return 9999 # Se não existe, não bloqueia por enquanto
        
        total_periodos = state.parametros_execucao.periodos_por_dia * state.parametros_execucao.dias_letivos
        slots_indisponiveis = len(prof.indisponibilidades)
        slots_disponiveis = total_periodos - slots_indisponiveis
        
        limite_real = min(prof.carga_maxima, slots_disponiveis)
        current_aulas = sum(d.quantidade_aulas for d in state.demandas if d.id_professor == professor_id)
        
        return limite_real - current_aulas

    @staticmethod
    def check_h3_workload(professor_id: str, new_demanda_aulas: int, state: STPState) -> bool:
        capacidade_livre = STPValidator.get_dynamic_capacity(professor_id, state)
        return new_demanda_aulas <= capacidade_livre

    @staticmethod
    def check_h4_capacity(turma_id: str, new_demanda_aulas: int, state: STPState) -> bool:
        """
        Verifica se a adição excede a capacidade física da turma (H4).
        Capacidade = periodos_por_dia * dias_letivos.
        """
        max_capacity = state.parametros_execucao.periodos_por_dia * state.parametros_execucao.dias_letivos
        current_aulas = sum(d.quantidade_aulas for d in state.demandas if d.id_turma == turma_id)
        return (current_aulas + new_demanda_aulas) <= max_capacity
