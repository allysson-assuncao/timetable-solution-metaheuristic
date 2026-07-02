import json
from src.models.stp_state import STPState

def export_to_json(state: STPState, filepath: str):
    """
    Exporta o estado validado para um arquivo JSON estruturado.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Utilizando pydantic V2 model_dump
        json.dump(state.model_dump(), f, ensure_ascii=False, indent=2)
