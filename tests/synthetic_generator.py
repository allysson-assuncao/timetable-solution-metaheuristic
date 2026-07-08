import argparse
import json
import os
import sys

# Garante que podemos importar 'src' estando na pasta 'tests'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.synthetic_factory import SyntheticDataFactory

def generate_synthetic_data(tier: str, filepath: str):
    # Delega a lógica de geração para a Factory centralizada
    data = SyntheticDataFactory.generate(tier)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        
    demandas = data["demandas"]
    print(f"Dataset '{tier}' gerado em {filepath} com sucesso!")
    print(f"Total de Demandas Agrupadas: {len(demandas)}")
    print(f"Total de Aulas Exatas: {sum(d['quantidade_aulas'] for d in demandas)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Data Generator")
    parser.add_argument("--tier", type=str, choices=["loose", "standard", "constrained", "if_campus"], required=True)
    parser.add_argument("--output", type=str, required=True)
    args = parser.parse_args()
    
    generate_synthetic_data(args.tier, args.output)
