import random

class SyntheticDataFactory:
    @staticmethod
    def generate(tier: str) -> dict:
        if tier == "loose":
            num_profs = 10
            num_turmas = 5
            indisp_rate = 0.2
        elif tier == "standard":
            num_profs = 30
            num_turmas = 15
            indisp_rate = 0.3
        elif tier == "constrained":
            num_profs = 50
            num_turmas = 30
            indisp_rate = 0.4
        else:
            raise ValueError("Tier inválido")

        dias_letivos = 5
        periodos_por_dia = 5
        total_slots = dias_letivos * periodos_por_dia

        professores = [{"id_professor": f"P{i}", "nome": f"Professor {i}", "carga_maxima": total_slots, "indisponibilidades": []} for i in range(1, num_profs + 1)]
        turmas = [{"id_turma": f"T{i}", "nome": f"Turma {i}"} for i in range(1, num_turmas + 1)]
        disciplinas = [{"id_disciplina": "DISC1", "nome": "Disciplina Unica"}]
        
        # Reverse Timetabling
        grid = {} # (row, col) -> turma
        demandas_cont = {}
        
        for col in range(total_slots):
            profs_disponiveis = list(range(num_profs))
            random.shuffle(profs_disponiveis)
            
            for t_idx in range(num_turmas):
                if profs_disponiveis:
                    p_idx = profs_disponiveis.pop()
                    grid[(p_idx, col)] = turmas[t_idx]["id_turma"]
                    
                    key = (f"P{p_idx+1}", turmas[t_idx]["id_turma"], "DISC1")
                    demandas_cont[key] = demandas_cont.get(key, 0) + 1
        
        # Inject unavailabilities for unused slots
        for p_idx in range(num_profs):
            for col in range(total_slots):
                if (p_idx, col) not in grid:
                    if random.random() < indisp_rate:
                        professores[p_idx]["indisponibilidades"].append(col + 1)
                        
        demandas = [
            {"id_professor": k[0], "id_turma": k[1], "id_disciplina": k[2], "quantidade_aulas": v}
            for k, v in demandas_cont.items()
        ]
        
        return {
            "parametros_execucao": {
                "dias_letivos": dias_letivos,
                "periodos_por_dia": periodos_por_dia,
                "pesos_objetivo": {"alpha": 1.0, "beta": 1.0, "gamma": 50.0},
                "sa_parametros": {"temperatura_inicial": 50.0, "temperatura_minima": 0.1, "taxa_resfriamento": 0.95, "iteracoes_por_temperatura": 500}
            },
            "professores": professores,
            "turmas": turmas,
            "disciplinas": disciplinas,
            "demandas": demandas
        }
