import math
import random
import numpy as np
from src.core.state import TimetableState
from src.core.evaluator import STPEvaluator
from src.core.telemetry import SessionRecorder

class SimulatedAnnealingEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None, 
                 t_initial: float = 1000.0, t_final: float = 0.1, alpha_cooling: float = 0.95, 
                 iter_per_temp: int = 500):
        self.state = state
        self.recorder = recorder
        self.t_initial = t_initial
        self.t_final = t_final
        self.alpha_cooling = alpha_cooling
        self.iter_per_temp = iter_per_temp
        
        self.periodos = state.stp_state.parametros_execucao.periodos_por_dia
        p = state.stp_state.parametros_execucao.pesos_objetivo
        self.alpha_peso = p.alpha
        self.beta_peso = p.beta
        self.gamma_peso = p.gamma

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
        
        if self.recorder:
            self.recorder.record_step(iteration=global_iter, phase="SA Início", cost=current_cost, temperature=current_temp, matrix=matrix)

        while current_temp > self.t_final:
            plateau_accepted = 0
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
                        if self.recorder:
                            self.recorder.record_step(iteration=global_iter, phase="SA Global Best", cost=best_cost, temperature=current_temp, matrix=matrix)
            
            # Resfriamento
            current_temp *= self.alpha_cooling
            
            if self.recorder and plateau_accepted > 0:
                self.recorder.record_step(iteration=global_iter, phase="SA Fim Plateau", cost=current_cost, temperature=current_temp, matrix=matrix)
                
        if self.recorder:
            self.recorder.record_step(iteration=global_iter, phase="SA Concluído", cost=current_cost, temperature=current_temp, matrix=matrix)
            
        return self.state
