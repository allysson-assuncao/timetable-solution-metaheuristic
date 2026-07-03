import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.stp_state import STPState, Professor, Demanda, Turma, Disciplina, ParametrosExecucao
from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder

def generate_mock_session(filepath: str):
    # 1. Setup Data
    stp = STPState(
        parametros_execucao=ParametrosExecucao(
            dias_letivos=5,
            periodos_por_dia=4
        ),
        professores=[
            Professor(id_professor="P1", nome="Alice", carga_maxima=20, indisponibilidades=[1, 2]),
            Professor(id_professor="P2", nome="Bob", carga_maxima=15, indisponibilidades=[]),
            Professor(id_professor="P3", nome="Charlie", carga_maxima=10, indisponibilidades=[10, 11, 12])
        ],
        turmas=[Turma(id_turma="T1", nome="Turma 1"), Turma(id_turma="T2", nome="Turma 2")],
        disciplinas=[Disciplina(id_disciplina="MAT", nome="Matemática"), Disciplina(id_disciplina="FIS", nome="Física")],
        demandas=[
            Demanda(id_professor="P1", id_turma="T1", id_disciplina="MAT", quantidade_aulas=4),
            Demanda(id_professor="P2", id_turma="T2", id_disciplina="FIS", quantidade_aulas=4)
        ]
    )
    
    state = TimetableState(stp)
    recorder = SessionRecorder(state)
    
    # 2. Simulate GRASP
    matrix = state.matrix.copy()
    for i in range(5):
        matrix[0, i+2] = 1 # P1 MAT
        matrix[1, i] = 2 # P2 FIS
        recorder.record_step(iteration=i, phase="GRASP", cost=1000 - i*50, temperature=100.0, matrix=matrix)
        
    # 3. Simulate SA Cooling
    for i in range(5, 15):
        matrix[0, i] = 0
        matrix[0, i+1] = 1
        recorder.record_step(iteration=i, phase="SA Resfriamento", cost=750 - (i-5)*30, temperature=100.0 - (i-5)*10, matrix=matrix)
        
    # 4. Simulate SA Refinement
    for i in range(15, 20):
        matrix[1, i-10] = 0
        matrix[1, i-9] = 2
        recorder.record_step(iteration=i, phase="SA Refinamento", cost=450 - (i-15)*10, temperature=0.1, matrix=matrix)
        
    recorder.export_session(filepath)
    print(f"Mock session exported to {filepath}")

if __name__ == "__main__":
    export_path = "mock_session.pickle"
    generate_mock_session(export_path)
    print("Mock file generated successfully.")
