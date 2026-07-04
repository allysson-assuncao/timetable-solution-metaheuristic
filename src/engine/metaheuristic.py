import concurrent.futures
from src.core.state import TimetableState
from src.core.telemetry import SessionRecorder
from src.engine.grasp import GRASPEngine
from src.engine.sa_optimizer import SimulatedAnnealingEngine
from src.core.evaluator import STPEvaluator

def _run_single_instance(stp_data: dict, seed: int):
    # Processo Isolado: Instanciando tudo dentro da thread separada
    import random
    import numpy as np
    from src.models.stp_state import STPState
    
    random.seed(seed)
    np.random.seed(seed)
    
    stp = STPState(**stp_data)
    state = TimetableState(stp)
    recorder = SessionRecorder(state)
    
    grasp_engine = GRASPEngine(state, recorder)
    grasp_engine.build_initial_solution()
    
    p = state.stp_state.parametros_execucao.sa_parametros
    sa_engine = SimulatedAnnealingEngine(
        state, 
        recorder, 
        t_initial=p.temperatura_inicial,
        t_final=p.temperatura_minima,
        alpha_cooling=p.taxa_resfriamento,
        iter_per_temp=p.iteracoes_por_temperatura
    )
    sa_engine.run()
    
    final_cost = STPEvaluator.calculate_total_cost(
        state.matrix, 
        state.stp_state.parametros_execucao.pesos_objetivo.alpha, 
        state.stp_state.parametros_execucao.pesos_objetivo.beta, 
        state.stp_state.parametros_execucao.pesos_objetivo.gamma, 
        state.stp_state.parametros_execucao.periodos_por_dia, 
        state.int_to_class_disc
    )
    
    return final_cost, state.matrix, recorder.snapshots

class MetaheuristicEngine:
    def __init__(self, state: TimetableState, recorder: SessionRecorder = None, multi_start_runs: int = 4):
        self.state = state
        self.recorder = recorder
        self.multi_start_runs = multi_start_runs

    def run(self):
        print(f"Iniciando Otimização Multi-Start Paralela ({self.multi_start_runs} instâncias concorrentes)...")
        
        stp_data = self.state.stp_state.model_dump()
        
        import random
        seeds = [random.randint(0, 999999) for _ in range(self.multi_start_runs)]
        
        best_cost = float('inf')
        best_matrix = None
        best_snapshots = []
        
        if self.multi_start_runs <= 1:
            cost, matrix, snaps = _run_single_instance(stp_data, seeds[0])
            best_cost = cost
            best_matrix = matrix
            best_snapshots = snaps
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=self.multi_start_runs) as executor:
                futures = [executor.submit(_run_single_instance, stp_data, s) for s in seeds]
                
                for future in concurrent.futures.as_completed(futures):
                    try:
                        cost, matrix, snaps = future.result()
                        if cost < best_cost:
                            best_cost = cost
                            best_matrix = matrix
                            best_snapshots = snaps
                    except Exception as exc:
                        print(f"Erro no Processo: {exc}")
                        
        print(f"Execução Multi-Start finalizada. Melhor Custo Global: {best_cost}")
        
        # Consolida o vencedor na thread principal
        self.state.matrix = best_matrix
        if self.recorder:
            self.recorder.snapshots = best_snapshots
