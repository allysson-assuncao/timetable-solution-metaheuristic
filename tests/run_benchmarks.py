import argparse
import time
import json
import csv
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models.stp_state import STPState
from src.core.state import TimetableState
from src.core.evaluator import STPEvaluator
from src.engine.metaheuristic import MetaheuristicEngine

def run_benchmarks(runs: int, input_file: str):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    csv_file = "benchmark_results.csv"
    write_header = not os.path.exists(csv_file)
    
    with open(csv_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["Execution_ID", "File", "Time_Elapsed_Sec", "Final_Cost", "Final_H1_Violations"])
            
        for r in range(1, runs + 1):
            print(f"\n--- Batch Run {r}/{runs} ---")
            
            stp = STPState(**data)
            state = TimetableState(stp)
            
            p = state.stp_state.parametros_execucao
            
            start_time = time.time()
            
            # Roda via Orquestrador Multi-Start (4 processos paralelos por default)
            engine = MetaheuristicEngine(state, multi_start_runs=4)
            engine.run()
            
            end_time = time.time()
            time_elapsed = end_time - start_time
            
            final_cost = STPEvaluator.calculate_total_cost(
                state.matrix, p.pesos_objetivo.alpha, p.pesos_objetivo.beta, 
                p.pesos_objetivo.gamma, p.periodos_por_dia, state.int_to_class_disc
            )
            
            final_h1 = STPEvaluator.evaluate_clashes(state.matrix, state.int_to_class_disc)
            
            writer.writerow([r, input_file, round(time_elapsed, 2), final_cost, final_h1])
            
            print(f"Time: {time_elapsed:.2f}s | Final Cost: {final_cost} | H1 Violations: {final_h1}")
            
            if final_h1 > 0:
                print("WARNING: Custo final contém choques! Heurística falhou neste lote.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Benchmarks")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--input", type=str, required=True)
    args = parser.parse_args()
    
    run_benchmarks(args.runs, args.input)
