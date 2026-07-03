import numpy as np

class STPEvaluator:
    @staticmethod
    def evaluate_windows(matrix: np.ndarray, periodos_por_dia: int) -> int:
        """Calcula janelas ociosas para todos os professores."""
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
        """Calcula o número total de dias em que os professores dão aula."""
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
        """Calcula choques de turma (mesmo código de turma na mesma coluna)."""
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
