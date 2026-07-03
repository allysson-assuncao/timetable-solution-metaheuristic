from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.engine.grasp import GRASPEngine
from src.engine.sa_optimizer import SimulatedAnnealingEngine

class MetaheuristicEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None):
        self.state = state
        self.recorder = recorder

    def run(self):
        print("Iniciando Fase 1: GRASP...")
        grasp_engine = GRASPEngine(self.state, self.recorder)
        grasp_engine.build_initial_solution()
        
        print("Iniciando Fase 2 e 3: Simulated Annealing...")
        # Lendo os parâmetros do estado para inicializar a temperatura
        p = self.state.stp_state.parametros_execucao.sa_parametros
        sa_engine = SimulatedAnnealingEngine(
            self.state, 
            self.recorder, 
            t_initial=p.temperatura_inicial,
            t_final=p.temperatura_final,
            alpha_cooling=p.taxa_resfriamento,
            iter_per_temp=p.iteracoes_por_temperatura
        )
        sa_engine.run()
        
        print("Execução finalizada.")
