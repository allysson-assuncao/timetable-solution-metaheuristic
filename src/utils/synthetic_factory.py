import random

from src.core.constants import (
    DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_GAMMA,
    DEFAULT_T_INICIAL, DEFAULT_T_MINIMA, DEFAULT_TAXA_RESFRIAMENTO, DEFAULT_ITER_POR_TEMP,
    DEFAULT_DIAS_LETIVOS, DEFAULT_PERIODOS_POR_DIA,
    KEY_PROFESSOR, KEY_PARAMETROS_EXECUCAO, KEY_PESOS_OBJETIVO, KEY_SA_PARAMETROS,
    KEY_PROFESSORES, KEY_TURMAS, KEY_DISCIPLINAS, KEY_DEMANDAS
)

# --- IF Campus Topology Constants ---
_IF_DISCIPLINES = {
    "SI":     [("ALG",  "Algoritmos"),
               ("ESD",  "Estruturas de Dados"),
               ("BDI",  "Banco de Dados"),
               ("RDC",  "Redes de Computadores"),
               ("ESW",  "Engenharia de Software")],
    "ADM":    [("CON",  "Contabilidade"),
               ("GPE",  "Gestão de Pessoas"),
               ("MKT",  "Marketing"),
               ("FIN",  "Finanças Corporativas"),
               ("DIR",  "Direito Empresarial")],
    "MET":    [("CLI",  "Climatologia"),
               ("FAT",  "Física da Atmosfera"),
               ("MNU",  "Modelagem Numérica"),
               ("SIN",  "Meteorologia Sinótica"),
               ("INS",  "Instrumentação Meteorológica")],
    "SHARED": [("CAL1", "Cálculo I"),
               ("CAL2", "Cálculo II"),
               ("ING",  "Inglês Técnico"),
               ("MET_",  "Metodologia Científica")],
}
_IF_SEMESTERS = [1, 3, 5, 7]
_IF_COURSES   = ["SI", "ADM", "MET"]

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
        elif tier == "if_campus":
            return SyntheticDataFactory._generate_if_campus()
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

    @staticmethod
    def _generate_if_campus() -> dict:
        """
        Generates a realistic IF Campus dataset:
          - 3 courses (SI, ADM, MET), 4 classes each = 12 total classes
          - 30 professors (9 per course + 3 generalists)
          - 5 days × 6 periods = 30 total periods
          - Uses Reverse Timetabling to guarantee H1, H3, H4 by construction
        """
        dias_letivos      = 5
        periodos_por_dia  = 6
        total_slots       = dias_letivos * periodos_por_dia  # 30

        # ── Build Turmas ──────────────────────────────────────────────────────────
        turmas = []
        for curso in _IF_COURSES:
            for sem in _IF_SEMESTERS:
                turmas.append({
                    "id_turma": f"{curso}{sem}",
                    "nome": f"{curso} – {sem}º Semestre"
                })

        # ── Build Disciplinas ──────────────────────────────────────────────────────
        disciplinas = []
        seen_disc_ids = set()
        for pool in _IF_DISCIPLINES.values():
            for disc_id, disc_nome in pool:
                if disc_id not in seen_disc_ids:
                    disciplinas.append({"id_disciplina": disc_id, "nome": disc_nome})
                    seen_disc_ids.add(disc_id)

        # ── Build Professores ──────────────────────────────────────────────────────
        professores = []
        prof_course_map = {}  # prof_id -> course or "SHARED"
        COURSE_NAMES = {"SI": "Sistemas de Informação",
                        "ADM": "Administração",
                        "MET": "Meteorologia"}
        p_idx = 1
        for curso in _IF_COURSES:
            for _ in range(9):
                pid = f"P{p_idx:02d}"
                professores.append({
                    "id_professor": pid,
                    "nome": f"Prof. {COURSE_NAMES[curso]} {p_idx:02d}",
                    "carga_maxima": total_slots,
                    "indisponibilidades": []
                })
                prof_course_map[pid] = curso
                p_idx += 1
        for _ in range(3):
            pid = f"P{p_idx:02d}"
            professores.append({
                "id_professor": pid,
                "nome": f"Prof. Generalista {p_idx:02d}",
                "carga_maxima": total_slots,
                "indisponibilidades": []
            })
            prof_course_map[pid] = "SHARED"
            p_idx += 1

        # ── Reverse Timetabling (course-aware) ────────────────────────────────────
        course_turmas = {c: [t["id_turma"] for t in turmas if t["id_turma"].startswith(c)]
                         for c in _IF_COURSES}
        course_profs  = {c: [p["id_professor"] for p in professores
                             if prof_course_map[p["id_professor"]] == c]
                         for c in _IF_COURSES}
        generalist_profs = [p["id_professor"] for p in professores
                            if prof_course_map[p["id_professor"]] == "SHARED"]

        grid          = {}  # (prof_idx_in_list, col) -> turma_id
        demandas_cont = {}  # (prof_id, turma_id, disc_id) -> count

        prof_id_to_idx = {p["id_professor"]: i for i, p in enumerate(professores)}

        for col in range(total_slots):
            for curso in _IF_COURSES:
                t_list = course_turmas[curso]             # 4 turmas
                pool   = course_profs[curso] + generalist_profs  # 9 + 3 = 12
                random.shuffle(pool)
                assigned = pool[:len(t_list)]             # Exactly 4 professors per course per column

                for turma_id, prof_id in zip(t_list, assigned):
                    p_row = prof_id_to_idx[prof_id]
                    grid[(p_row, col)] = turma_id

                    # Pick discipline: 70% course-specific, 30% shared
                    if random.random() < 0.70:
                        disc_pool = _IF_DISCIPLINES[curso]
                    else:
                        disc_pool = _IF_DISCIPLINES["SHARED"]
                    disc_id, _ = random.choice(disc_pool)

                    key = (prof_id, turma_id, disc_id)
                    demandas_cont[key] = demandas_cont.get(key, 0) + 1

        # ── Inject unavailabilities for idle slots ────────────────────────────────
        INDISP_RATE = 0.15
        for p_row, p_data in enumerate(professores):
            pid = p_data["id_professor"]
            for col in range(total_slots):
                if (p_row, col) not in grid:
                    if random.random() < INDISP_RATE:
                        p_data["indisponibilidades"].append(col + 1)

        # ── Assemble demandas list ─────────────────────────────────────────────────
        demandas = [
            {"id_professor": k[0], "id_turma": k[1],
             "id_disciplina": k[2], "quantidade_aulas": v}
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
