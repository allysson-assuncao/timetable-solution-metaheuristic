import json
import os
import pickle
from datetime import datetime
from src.models.stp_state import STPState

class WorkspacePersistence:
    @staticmethod
    def export_workspace(state: STPState, filepath: str):
        """Exporta o estado atual para JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state.model_dump(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def import_workspace(filepath: str) -> STPState:
        """Importa JSON e força a validação rígida do Pydantic."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Ao instanciar STPState, todas as restrições matemáticas e tipos são validados.
        # Se algo estiver corrompido, levantará ValueError/ValidationError
        return STPState(**data)

    @staticmethod
    def save_telemetry(session_data: dict, prefix: str = "run") -> str:
        """Salva a telemetria consolidada em um arquivo .pickle para auditoria posterior."""
        os.makedirs("telemetry_history", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"telemetry_history/{prefix}_{timestamp}.pickle"
        with open(filename, 'wb') as f:
            pickle.dump(session_data, f)
        return filename
