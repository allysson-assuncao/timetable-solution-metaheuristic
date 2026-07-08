# =============================================================================
# src/core/constants.py
# Módulo central de constantes do projeto STP.
# Todos os valores numéricos padrão e strings literais reutilizadas devem
# ser definidos aqui. NUNCA hardcode valores diretamente em outros módulos.
# =============================================================================

# -----------------------------------------------------------------------------
# SEÇÃO 1: Pesos da Função Objetivo f(X) = α·J + β·D + γ·C
# Calibração científica conforme Zhang et al. (2010) e Souza et al. (2003).
# Invariante obrigatória: γ >> α > β
# -----------------------------------------------------------------------------
DEFAULT_ALPHA: float = 1.0        # Peso das janelas (S1) — referência unitária
DEFAULT_BETA: float = 4.0         # Peso dos dias de deslocamento (S2) — 4× janelas
DEFAULT_GAMMA: float = 10000.0    # Penalidade de choque (H1) — domina toda a função

# -----------------------------------------------------------------------------
# SEÇÃO 2: Parâmetros do Simulated Annealing
# Calibrados para instâncias de média/alta densidade (30–50 professores × 25 períodos).
# Referência: Aarts & Korst (1989), Zhang et al. (2010).
# -----------------------------------------------------------------------------
DEFAULT_T_INICIAL: float = 5000.0    # Temperatura inicial: aceita pioras de ~exp(-1) no início
DEFAULT_T_MINIMA: float = 0.01       # Temperatura mínima: threshold de congelamento
DEFAULT_TAXA_RESFRIAMENTO: float = 0.98  # Taxa de resfriamento geométrico (lento = melhor qualidade)
DEFAULT_ITER_POR_TEMP: int = 500     # Iterações por plateau de temperatura

# -----------------------------------------------------------------------------
# SEÇÃO 3: Parâmetros de Grade (Calendário Escolar)
# -----------------------------------------------------------------------------
DEFAULT_DIAS_LETIVOS: int = 5        # Semana padrão (segunda a sexta)
DEFAULT_PERIODOS_POR_DIA: int = 5    # Períodos diários padrão

# -----------------------------------------------------------------------------
# SEÇÃO 4: Avaliador Guloso GRASP
# Penalidade interna do avaliador de slot do GRASP — deve refletir a
# magnitude relativa de γ para que a RCL diferencie slots com/sem choque.
# -----------------------------------------------------------------------------
GRASP_PENALIDADE_CHOQUE: float = DEFAULT_GAMMA   # Penalidade de choque no slot
GRASP_BONUS_ADJACENCIA: float = -10.0            # Bônus por aula adjacente
GRASP_BONUS_DIA_USADO: float = -5.0              # Bônus por dia já utilizado
GRASP_THRESHOLD_CHOQUE: float = DEFAULT_GAMMA    # Threshold do alpha reativo

# -----------------------------------------------------------------------------
# SEÇÃO 5: Fases de Snapshot (Telemetria)
# Strings canônicas usadas por GRASPEngine e SimulatedAnnealingEngine
# ao chamar SessionRecorder.record_step(phase=...).
# -----------------------------------------------------------------------------
FASE_GRASP_INICIAL: str = "GRASP Inicial"
FASE_GRASP_CONSTRUINDO: str = "GRASP Construindo"
FASE_GRASP_FINALIZADO: str = "GRASP Finalizado"
FASE_SA_INICIO: str = "SA Início"
FASE_SA_GLOBAL_BEST: str = "SA Global Best"
FASE_SA_REHEATING: str = "SA Reheating"
FASE_SA_FIM_PLATEAU: str = "SA Fim Plateau"
FASE_SA_CONCLUIDO: str = "SA Concluído"

# -----------------------------------------------------------------------------
# SEÇÃO 6: Chaves de Dicionário JSON (para construtores de dados sintéticos)
# Usadas em synthetic_factory.py para garantir alinhamento com os campos Pydantic.
# -----------------------------------------------------------------------------
KEY_PROFESSOR: str = "id_professor"
KEY_TURMA: str = "id_turma"
KEY_DISCIPLINA: str = "id_disciplina"
KEY_QUANTIDADE_AULAS: str = "quantidade_aulas"
KEY_PARAMETROS_EXECUCAO: str = "parametros_execucao"
KEY_PESOS_OBJETIVO: str = "pesos_objetivo"
KEY_SA_PARAMETROS: str = "sa_parametros"
KEY_PROFESSORES: str = "professores"
KEY_TURMAS: str = "turmas"
KEY_DISCIPLINAS: str = "disciplinas"
KEY_DEMANDAS: str = "demandas"
