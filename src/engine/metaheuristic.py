from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.engine.grasp import GRASPEngine

class MetaheuristicEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None):
        self.state = state
        self.recorder = recorder

    def run(self):
        print("Iniciando Fase 1: GRASP...")
        grasp_engine = GRASPEngine(self.state, self.recorder)
        grasp_engine.build_initial_solution()
        
        # Fase 2 e 3 (Simulated Annealing) serão conectadas aqui futuramente
        
        print("Execução finalizada.")
