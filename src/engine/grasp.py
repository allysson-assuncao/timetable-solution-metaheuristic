import random
import numpy as np
from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.core.evaluator import STPEvaluator
from src.core.constants import (
    GRASP_PENALIDADE_CHOQUE, GRASP_BONUS_ADJACENCIA, GRASP_BONUS_DIA_USADO,
    GRASP_THRESHOLD_CHOQUE,
    FASE_GRASP_INICIAL, FASE_GRASP_CONSTRUINDO, FASE_GRASP_FINALIZADO
)

class GRASPEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None, base_alpha: float = 0.3):
        self.state = state
        self.recorder = recorder
        self.base_alpha = base_alpha
        self.periodos = state.stp_state.parametros_execucao.periodos_por_dia

    def _sort_demands_by_constraint(self):
        """Ordena as demandas por professores mais restritos (menos slots disponíveis)."""
        prof_free_slots = {}
        for prof_id, row_idx in self.state.prof_id_to_idx.items():
            row = self.state.matrix[row_idx]
            free_slots = np.sum(row == 0)
            prof_free_slots[prof_id] = free_slots

        aulas_para_alocar = []
        for demanda in self.state.stp_state.demandas:
            for _ in range(demanda.quantidade_aulas):
                aulas_para_alocar.append(demanda)
                
        # Ordenar: professores com menos slots livres primeiro
        aulas_para_alocar.sort(key=lambda d: prof_free_slots[d.id_professor])
        return aulas_para_alocar

    def _evaluate_slot(self, row: int, col: int, class_id: str, code: int) -> float:
        """
        Calcula o custo guloso de inserir a aula 'class_id' no slot 'col' do professor 'row'.
        Quanto menor, melhor.
        """
        matrix = self.state.matrix
        if matrix[row, col] != 0:
            return float('inf')
            
        cost = 0.0
        
        # 1. Checagem de Choque de Turma (H1)
        clash = False
        for r in range(matrix.shape[0]):
            if r != row and matrix[r, col] > 0:
                outra_turma = self.state.int_to_class_disc[matrix[r, col]][0]
                if outra_turma == class_id:
                    clash = True
                    break
        if clash:
            cost += GRASP_PENALIDADE_CHOQUE
            
        # 2. Agrupamento (Janelas)
        dia = col // self.periodos
        inicio_dia = dia * self.periodos
        fim_dia = inicio_dia + self.periodos
        
        tem_adjacente = False
        if col > inicio_dia and matrix[row, col - 1] > 0: tem_adjacente = True
        if col < fim_dia - 1 and matrix[row, col + 1] > 0: tem_adjacente = True
        
        if tem_adjacente:
            cost += GRASP_BONUS_ADJACENCIA
            
        # 3. Dia já utilizado
        aulas_no_dia = np.sum(matrix[row, inicio_dia:fim_dia] > 0)
        if aulas_no_dia > 0:
            cost += GRASP_BONUS_DIA_USADO
            
        return cost

    def _get_current_cost(self):
        p = self.state.stp_state.parametros_execucao.pesos_objetivo
        return STPEvaluator.calculate_total_cost(
            self.state.matrix,
            p.alpha, p.beta, p.gamma, self.periodos, self.state.int_to_class_disc
        )

    def build_initial_solution(self):
        aulas = self._sort_demands_by_constraint()
        
        iteration = 0
        current_alpha = self.base_alpha
        
        if self.recorder:
            self.recorder.record_step(iteration=0, phase=FASE_GRASP_INICIAL, cost=self._get_current_cost(), temperature=0.0, matrix=self.state.matrix)
            
        last_prof = None
        
        for demanda in aulas:
            if last_prof != demanda.id_professor:
                if self.recorder and last_prof is not None:
                    self.recorder.record_step(iteration=iteration, phase=FASE_GRASP_CONSTRUINDO, cost=self._get_current_cost(), temperature=0.0, matrix=self.state.matrix)
                last_prof = demanda.id_professor
                
            row = self.state.prof_id_to_idx[demanda.id_professor]
            code = self.state.class_disc_to_int[(demanda.id_turma, demanda.id_disciplina)]
            
            candidates = []
            for col in range(self.state.matrix.shape[1]):
                if self.state.matrix[row, col] == 0:
                    cost = self._evaluate_slot(row, col, demanda.id_turma, code)
                    candidates.append((col, cost))
                    
            if not candidates:
                # Fallback: find ANY non-(-1) slot and force-allocate (generates clash by design)
                fallback = [
                    col for col in range(self.state.matrix.shape[1])
                    if self.state.matrix[row, col] != -1
                ]
                if fallback:
                    chosen_col = random.choice(fallback)
                    self.state.matrix[row, chosen_col] = code  # Overwrites — clash expected, SA will repair
                else:
                    print(f"[FATAL] Prof {demanda.id_professor} has NO allocatable slots (all -1). H2 overly constrained.")
                continue
                
            min_cost = min(candidates, key=lambda x: x[1])[1]
            max_cost = max(candidates, key=lambda x: x[1])[1]
            
            if min_cost >= GRASP_THRESHOLD_CHOQUE:
                current_alpha = min(1.0, current_alpha + 0.1)
            else:
                current_alpha = max(self.base_alpha, current_alpha - 0.05)
            
            threshold = min_cost + current_alpha * (max_cost - min_cost)
            rcl = [c for c in candidates if c[1] <= threshold]
            
            if not rcl:
                rcl = candidates
                
            chosen_col, chosen_cost = random.choice(rcl)
            self.state.matrix[row, chosen_col] = code
            iteration += 1
            
        if self.recorder:
            self.recorder.record_step(iteration=iteration, phase=FASE_GRASP_FINALIZADO, cost=self._get_current_cost(), temperature=0.0, matrix=self.state.matrix)
            
        return self.state
