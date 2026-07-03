import pickle
import numpy as np
from dataclasses import dataclass
from src.core.state import TimetableState

@dataclass
class Snapshot:
    iteration: int
    phase: str
    cost: float
    temperature: float
    matrix_copy: np.ndarray

class SessionRecorder:
    def __init__(self, initial_state: TimetableState):
        self.initial_state_data = initial_state.stp_state.model_dump()
        self.class_disc_to_int = initial_state.class_disc_to_int.copy()
        self.int_to_class_disc = initial_state.int_to_class_disc.copy()
        self.prof_id_to_idx = initial_state.prof_id_to_idx.copy()
        self.snapshots = []

    def record_step(self, iteration: int, phase: str, cost: float, temperature: float, matrix: np.ndarray):
        """Salva um snapshot fazendo deepcopy da matriz."""
        self.snapshots.append(Snapshot(
            iteration=iteration,
            phase=phase,
            cost=cost,
            temperature=temperature,
            matrix_copy=matrix.copy()
        ))

    def export_session(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump({
                "initial_state_data": self.initial_state_data,
                "class_disc_to_int": self.class_disc_to_int,
                "int_to_class_disc": self.int_to_class_disc,
                "prof_id_to_idx": self.prof_id_to_idx,
                "snapshots": self.snapshots
            }, f)

    @classmethod
    def load_session(cls, filepath: str) -> dict:
        with open(filepath, 'rb') as f:
            return pickle.load(f)
