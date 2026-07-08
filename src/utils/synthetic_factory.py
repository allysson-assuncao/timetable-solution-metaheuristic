import random

from src.core.constants import (
    DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_GAMMA,
    DEFAULT_T_INICIAL, DEFAULT_T_MINIMA, DEFAULT_TAXA_RESFRIAMENTO, DEFAULT_ITER_POR_TEMP,
    DEFAULT_DIAS_LETIVOS, DEFAULT_PERIODOS_POR_DIA,
    KEY_PROFESSOR, KEY_PARAMETROS_EXECUCAO, KEY_PESOS_OBJETIVO, KEY_SA_PARAMETROS,
    KEY_PROFESSORES, KEY_TURMAS, KEY_DISCIPLINAS, KEY_DEMANDAS
)

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
        disciplinas = [
            {"id_disciplina": "MAT", "nome": "Matemática"},
            {"id_disciplina": "FIS", "nome": "Física"},
            {"id_disciplina": "QUI", "nome": "Química"},
            {"id_disciplina": "BIO", "nome": "Biologia"},
            {"id_disciplina": "HIS", "nome": "História"},
            {"id_disciplina": "GEO", "nome": "Geografia"}
        ]
        
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
                    
                    disc_escolhida = random.choice(disciplinas)["id_disciplina"]
                    key = (f"P{p_idx+1}", turmas[t_idx]["id_turma"], disc_escolhida)
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
            KEY_PARAMETROS_EXECUCAO: {
                "dias_letivos": dias_letivos,
                "periodos_por_dia": periodos_por_dia,
                KEY_PESOS_OBJETIVO: {
                    "alpha": DEFAULT_ALPHA,
                    "beta": DEFAULT_BETA,
                    "gamma": DEFAULT_GAMMA
                },
                KEY_SA_PARAMETROS: {
                    "temperatura_inicial": DEFAULT_T_INICIAL,
                    "temperatura_minima": DEFAULT_T_MINIMA,
                    "taxa_resfriamento": DEFAULT_TAXA_RESFRIAMENTO,
                    "iteracoes_por_temperatura": DEFAULT_ITER_POR_TEMP
                }
            },
            KEY_PROFESSORES: professores,
            KEY_TURMAS: turmas,
            KEY_DISCIPLINAS: disciplinas,
            KEY_DEMANDAS: demandas
        }
