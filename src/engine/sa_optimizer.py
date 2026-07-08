import math
import random
import numpy as np
from src.core.state import TimetableState
from src.core.evaluator import STPEvaluator
from src.core.telemetry import SessionRecorder

from src.core.constants import (
    DEFAULT_T_INICIAL, DEFAULT_T_MINIMA, DEFAULT_TAXA_RESFRIAMENTO,
    FASE_SA_INICIO, FASE_SA_GLOBAL_BEST, FASE_SA_REHEATING,
    FASE_SA_FIM_PLATEAU, FASE_SA_CONCLUIDO
)

class SimulatedAnnealingEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None, 
                 t_initial: float = DEFAULT_T_INICIAL, t_final: float = DEFAULT_T_MINIMA, alpha_cooling: float = DEFAULT_TAXA_RESFRIAMENTO, 
                 iter_per_temp: int = 500):
        self.state = state
        self.recorder = recorder
        self.t_initial = t_initial
        self.t_final = t_final
        self.alpha_cooling = alpha_cooling
        
        self.periodos = state.stp_state.parametros_execucao.periodos_por_dia
        p = state.stp_state.parametros_execucao.pesos_objetivo
        self.alpha_peso = p.alpha
        self.beta_peso = p.beta
        self.gamma_peso = p.gamma
        
        # Parametrização Dinâmica (Dynamic Parameterization)
        M, P = state.matrix.shape
        matrix_size = M * P
        scale_factor = max(1.0, matrix_size / 250.0) # Base 250 (e.g. 10 profs x 25 periods)
        self.iter_per_temp = int(iter_per_temp * scale_factor)

    def run(self):
        matrix = self.state.matrix
        M, P = matrix.shape
        
        current_temp = self.t_initial
        
        current_cost = STPEvaluator.calculate_total_cost(
            matrix, self.alpha_peso, self.beta_peso, self.gamma_peso, 
            self.periodos, self.state.int_to_class_disc
        )
        
        best_cost = current_cost
        global_iter = 0
        
        # Mecânica de Reheating
        stuck_counter = 0
        max_stuck_plateaus = 50 
        
        if self.recorder:
            self.recorder.record_step(iteration=global_iter, phase=FASE_SA_INICIO, cost=current_cost, temperature=current_temp, matrix=matrix)

        while current_temp > self.t_final:
            plateau_accepted = 0
            improved_in_plateau = False
            
            for _ in range(self.iter_per_temp):
                global_iter += 1
                
                # 1. Gerar Vizinho (Swap Intra-linha)
                row = random.randint(0, M - 1)
                j1 = random.randint(0, P - 1)
                j2 = random.randint(0, P - 1)
                
                # Proibir swap com -1 (Indisponibilidade)
                if matrix[row, j1] == -1 or matrix[row, j2] == -1 or j1 == j2:
                    continue
                    
                # 2. Avaliação Delta
                delta = STPEvaluator.calculate_delta(
                    matrix, row, j1, j2, self.state.int_to_class_disc,
                    self.alpha_peso, self.beta_peso, self.gamma_peso, self.periodos
                )
                
                # 3. Critério de Aceitação (Metropolis)
                if delta < 0:
                    accept = True
                else:
                    prob = math.exp(-delta / current_temp)
                    accept = (random.random() < prob)
                    
                if accept:
                    # Realiza a troca
                    matrix[row, j1], matrix[row, j2] = matrix[row, j2], matrix[row, j1]
                    current_cost += delta
                    plateau_accepted += 1
                    
                    # 4. Global Best
                    if current_cost < best_cost:
                        best_cost = current_cost
                        improved_in_plateau = True
                        if self.recorder:
                            self.recorder.record_step(iteration=global_iter, phase=FASE_SA_GLOBAL_BEST, cost=best_cost, temperature=current_temp, matrix=matrix)
            
            # Resfriamento
            current_temp *= self.alpha_cooling
            
            # Recalculate true cost to eliminate floating point drift (TD-2)
            current_cost = STPEvaluator.calculate_total_cost(
                matrix, self.alpha_peso, self.beta_peso, self.gamma_peso, 
                self.periodos, self.state.int_to_class_disc
            )
            
            # Checagem de Estagnação
            if improved_in_plateau:
                stuck_counter = 0
            else:
                stuck_counter += 1
                
            # Gatilho de Reheating
            if stuck_counter > max_stuck_plateaus:
                choques = STPEvaluator.evaluate_clashes(matrix, self.state.int_to_class_disc)
                if choques > 0:
                    # Injeta calor (Terremoto estocástico)
                    current_temp = self.t_initial * 0.7
                    stuck_counter = 0
                    if self.recorder:
                        self.recorder.record_step(iteration=global_iter, phase=FASE_SA_REHEATING, cost=current_cost, temperature=current_temp, matrix=matrix)
                else:
                    # Sem choques, ignora reaquecimento e foca em lapidar ergonomia fina
                    pass
            
            if self.recorder and plateau_accepted > 0:
                self.recorder.record_step(iteration=global_iter, phase=FASE_SA_FIM_PLATEAU, cost=current_cost, temperature=current_temp, matrix=matrix)
                
        if self.recorder:
            self.recorder.record_step(iteration=global_iter, phase=FASE_SA_CONCLUIDO, cost=current_cost, temperature=current_temp, matrix=matrix)
            
        return self.state
