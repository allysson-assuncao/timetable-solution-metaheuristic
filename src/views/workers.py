from PyQt6.QtCore import QThread, pyqtSignal
from src.core.state import TimetableState
from src.engine.metaheuristic import MetaheuristicEngine

class EngineWorker(QThread):
    finished_signal = pyqtSignal(TimetableState)
    error_signal = pyqtSignal(str)
    
    def __init__(self, state: TimetableState, multi_start_runs: int = 4):
        super().__init__()
        self.state = state
        self.multi_start_runs = multi_start_runs
        
    def run(self):
        try:
            # Instancia o motor com o estado e o recorder já atrelado ao estado
            engine = MetaheuristicEngine(self.state, self.state.session_recorder, self.multi_start_runs)
            engine.run()
            # Envia o estado completo e consolidado de volta para a Main Thread
            self.finished_signal.emit(self.state)
        except Exception as e:
            self.error_signal.emit(str(e))
