import numpy as np

class STPEvaluator:
    # --- Avaliações Completas ---
    @staticmethod
    def evaluate_windows(matrix: np.ndarray, periodos_por_dia: int) -> int:
        total_janelas = 0
        dias = matrix.shape[1] // periodos_por_dia
        for row in range(matrix.shape[0]):
            for d in range(dias):
                inicio = d * periodos_por_dia
                fim = inicio + periodos_por_dia
                dia_aulas = matrix[row, inicio:fim]
                
                idx_com_aula = np.where(dia_aulas > 0)[0]
                if len(idx_com_aula) > 1:
                    primeiro = idx_com_aula[0]
                    ultimo = idx_com_aula[-1]
                    buracos = np.sum(dia_aulas[primeiro:ultimo+1] <= 0)
                    total_janelas += buracos
        return total_janelas

    @staticmethod
    def evaluate_days(matrix: np.ndarray, periodos_por_dia: int) -> int:
        total_dias = 0
        dias = matrix.shape[1] // periodos_por_dia
        for row in range(matrix.shape[0]):
            for d in range(dias):
                inicio = d * periodos_por_dia
                fim = inicio + periodos_por_dia
                if np.any(matrix[row, inicio:fim] > 0):
                    total_dias += 1
        return total_dias

    @staticmethod
    def evaluate_clashes(matrix: np.ndarray, int_to_class_disc: dict) -> int:
        choques = 0
        for col in range(matrix.shape[1]):
            turmas_na_coluna = []
            for row in range(matrix.shape[0]):
                val = matrix[row, col]
                if val > 0:
                    turma_id = int_to_class_disc[val][0]
                    turmas_na_coluna.append(turma_id)
            
            if len(turmas_na_coluna) > 1:
                from collections import Counter
                contagem = Counter(turmas_na_coluna)
                for count in contagem.values():
                    if count > 1:
                        choques += (count - 1)
        return choques

    @staticmethod
    def calculate_total_cost(matrix: np.ndarray, alpha: float, beta: float, gamma: float, periodos: int, int_to_class_disc: dict) -> float:
        J = STPEvaluator.evaluate_windows(matrix, periodos)
        D = STPEvaluator.evaluate_days(matrix, periodos)
        C = STPEvaluator.evaluate_clashes(matrix, int_to_class_disc)
        return (alpha * J) + (beta * D) + (gamma * C)

    # --- Avaliações Delta (Otimizadas para SA) ---
    
    @staticmethod
    def evaluate_row_ergonomics(row_array: np.ndarray, periodos_por_dia: int) -> tuple[int, int]:
        """Avalia janelas (J) e dias (D) de uma única linha O(P)."""
        janelas = 0
        dias_usados = 0
        dias = len(row_array) // periodos_por_dia
        for d in range(dias):
            inicio = d * periodos_por_dia
            fim = inicio + periodos_por_dia
            dia_aulas = row_array[inicio:fim]
            
            idx_com_aula = np.where(dia_aulas > 0)[0]
            if len(idx_com_aula) > 0:
                dias_usados += 1
                if len(idx_com_aula) > 1:
                    primeiro = idx_com_aula[0]
                    ultimo = idx_com_aula[-1]
                    buracos = np.sum(dia_aulas[primeiro:ultimo+1] <= 0)
                    janelas += buracos
        return janelas, dias_usados

    @staticmethod
    def evaluate_column_clashes(col_array: np.ndarray, int_to_class_disc: dict) -> int:
        """Avalia choques (H1) de uma única coluna O(M)."""
        turmas_na_coluna = []
        for val in col_array:
            if val > 0:
                turma_id = int_to_class_disc[val][0]
                turmas_na_coluna.append(turma_id)
        
        choques = 0
        if len(turmas_na_coluna) > 1:
            from collections import Counter
            contagem = Counter(turmas_na_coluna)
            for count in contagem.values():
                if count > 1:
                    choques += (count - 1)
        return choques

    @staticmethod
    def calculate_delta(matrix: np.ndarray, row: int, j1: int, j2: int, 
                        int_to_class_disc: dict, alpha: float, beta: float, gamma: float, periodos: int) -> float:
        """
        Simula a troca de matrix[row, j1] com matrix[row, j2] e retorna o Delta_Cost.
        Se retornar < 0, a troca melhora a solução.
        """
        # --- ANTES do Swap ---
        old_J, old_D = STPEvaluator.evaluate_row_ergonomics(matrix[row], periodos)
        old_C1 = STPEvaluator.evaluate_column_clashes(matrix[:, j1], int_to_class_disc)
        old_C2 = STPEvaluator.evaluate_column_clashes(matrix[:, j2], int_to_class_disc) if j1 != j2 else 0
        
        old_cost = (alpha * old_J) + (beta * old_D) + (gamma * (old_C1 + old_C2))
        
        # --- FAZ Swap (temporário) ---
        matrix[row, j1], matrix[row, j2] = matrix[row, j2], matrix[row, j1]
        
        # --- DEPOIS do Swap ---
        new_J, new_D = STPEvaluator.evaluate_row_ergonomics(matrix[row], periodos)
        new_C1 = STPEvaluator.evaluate_column_clashes(matrix[:, j1], int_to_class_disc)
        new_C2 = STPEvaluator.evaluate_column_clashes(matrix[:, j2], int_to_class_disc) if j1 != j2 else 0
        
        new_cost = (alpha * new_J) + (beta * new_D) + (gamma * (new_C1 + new_C2))
        
        # --- DESFAZ Swap ---
        matrix[row, j1], matrix[row, j2] = matrix[row, j2], matrix[row, j1]
        
        return float(new_cost - old_cost)
