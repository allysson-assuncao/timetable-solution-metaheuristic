import sys
import json
import os

# Adiciona o diretório raiz ao path para importar 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers.main_controller import MainController
from src.utils.json_exporter import export_to_json

def run_test():
    controller = MainController()
    
    # Path to default_dataset.json
    mock_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'default_dataset.json')
    with open(mock_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Inject parameters
    params = data.get("parametros_execucao", {})
    controller.state.parametros_execucao.periodos_por_dia = params.get("periodos_por_dia", 5)
    controller.state.parametros_execucao.dias_letivos = params.get("dias_letivos", 5)

    # Inject professors
    for p in data.get("professores", []):
        controller.add_professor(
            p["id_professor"],
            p["carga_maxima"],
            p["indisponibilidades"]
        )

    # Inject demands
    for d in data.get("demandas", []):
        success = controller.add_demanda(
            d["id_professor"],
            d["id_turma"],
            d["disciplina"],
            d["quantidade_aulas"]
        )
        if not success:
            print(f"Falha ao adicionar demanda para prof {d['id_professor']}")

    # Export to verify
    out_path = os.path.join(os.path.dirname(__file__), 'output_dataset.json')
    export_to_json(controller.state, out_path)
    
    print("Teste semi-automatizado concluído.")
    print("Confira o output gerado idêntico em:", out_path)
    
if __name__ == '__main__':
    run_test()
