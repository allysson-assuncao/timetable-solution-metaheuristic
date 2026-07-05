import sys
import os
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.stp_state import STPState, Professor, Demanda, Turma, Disciplina, ParametrosExecucao, PesosObjetivo
from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.core.evaluator import STPEvaluator
from src.engine.sa_optimizer import SimulatedAnnealingEngine

def test_sa_execution():
    stp = STPState(
        parametros_execucao=ParametrosExecucao(
            dias_letivos=2,
            periodos_por_dia=3,
            pesos_objetivo=PesosObjetivo(alpha=1.0, beta=1.0, gamma=50.0)
        ),
        professores=[
            Professor(id_professor="P1", nome="Alice", carga_maxima=6, indisponibilidades=[]),
            Professor(id_professor="P2", nome="Bob", carga_maxima=6, indisponibilidades=[]),
        ],
        turmas=[Turma(id_turma="T1", nome="Turma 1")],
        disciplinas=[Disciplina(id_disciplina="MAT", nome="Matemática"), Disciplina(id_disciplina="FIS", nome="Física")],
        demandas=[
            Demanda(id_professor="P1", id_turma="T1", id_disciplina="MAT", quantidade_aulas=2),
            Demanda(id_professor="P2", id_turma="T1", id_disciplina="FIS", quantidade_aulas=2)
        ]
    )
    
    state = TimetableState(stp)
    recorder = SessionRecorder(state)
    
    code_mat = state.class_disc_to_int[("T1", "MAT")]
    code_fis = state.class_disc_to_int[("T1", "FIS")]
    
    state.matrix[0, 0] = code_mat
    state.matrix[0, 1] = code_mat
    
    state.matrix[1, 0] = code_fis
    state.matrix[1, 1] = code_fis
    
    initial_cost = STPEvaluator.calculate_total_cost(
        state.matrix, 1.0, 1.0, 50.0, 3, state.int_to_class_disc
    )
    assert initial_cost >= 2000, "Estado inicial deve ter Custo altíssimo devido a 2 choques!"
    
    engine = SimulatedAnnealingEngine(state, recorder, t_initial=500.0, t_final=0.1, alpha_cooling=0.90, iter_per_temp=100)
    engine.run()
    
    final_cost = STPEvaluator.calculate_total_cost(
        state.matrix, 1.0, 1.0, 50.0, 3, state.int_to_class_disc
    )
    
    choques = STPEvaluator.evaluate_clashes(state.matrix, state.int_to_class_disc)
    
    recorder.export_session("mock_sa.pickle")
    
    print(f"Custo Inicial: {initial_cost}")
    print(f"Custo Final: {final_cost}")
    print(f"Choques Restantes: {choques}")
    
    assert choques == 0, "O SA deveria ter eliminado todos os choques!"
    assert final_cost < initial_cost, "O Custo Final deve ser menor que o Inicial!"
    print("Test passed! Simulated Annealing optimizou a grade com sucesso.")

if __name__ == "__main__":
    test_sa_execution()
