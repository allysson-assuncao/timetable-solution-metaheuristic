import sys
import os
import numpy as np

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.stp_state import STPState, Professor, Demanda, Turma, Disciplina, ParametrosExecucao
from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.engine.metaheuristic import MetaheuristicEngine

def test_grasp_execution():
    # 1. Setup Data with highly constrained environment
    stp = STPState(
        parametros_execucao=ParametrosExecucao(
            dias_letivos=3,
            periodos_por_dia=3
        ),
        professores=[
            Professor(id_professor="P1", nome="Alice", carga_maxima=9, indisponibilidades=[1, 2, 3]), # Só 6 slots livres
            Professor(id_professor="P2", nome="Bob", carga_maxima=9, indisponibilidades=[4, 5, 6]),   # Só 6 slots livres
        ],
        turmas=[Turma(id_turma="T1", nome="Turma 1")],
        disciplinas=[Disciplina(id_disciplina="MAT", nome="Matemática"), Disciplina(id_disciplina="FIS", nome="Física")],
        demandas=[
            Demanda(id_professor="P1", id_turma="T1", id_disciplina="MAT", quantidade_aulas=4),
            Demanda(id_professor="P2", id_turma="T1", id_disciplina="FIS", quantidade_aulas=4)
        ]
    )
    
    state = TimetableState(stp)
    recorder = SessionRecorder(state)
    
    engine = MetaheuristicEngine(state, recorder)
    engine.run()
    
    # Assertions
    mat = state.matrix
    p1_aulas = np.sum(mat[0] > 0)
    p2_aulas = np.sum(mat[1] > 0)
    
    assert p1_aulas == 4, f"Esperado 4 aulas de P1, encontrou {p1_aulas}"
    assert p2_aulas == 4, f"Esperado 4 aulas de P2, encontrou {p2_aulas}"
    
    recorder.export_session("mock_grasp.pickle")
    print("Test passed! GRASP populated the matrix successfully.")
    
if __name__ == "__main__":
    test_grasp_execution()
