# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field
from typing import List

from src.core.constants import (
    DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_GAMMA,
    DEFAULT_T_INICIAL, DEFAULT_T_MINIMA, DEFAULT_TAXA_RESFRIAMENTO,
    DEFAULT_ITER_POR_TEMP, DEFAULT_DIAS_LETIVOS, DEFAULT_PERIODOS_POR_DIA
)

class PesosObjetivo(BaseModel):
    alpha: float = DEFAULT_ALPHA
    beta: float = DEFAULT_BETA
    gamma: float = DEFAULT_GAMMA

class SAParametros(BaseModel):
    temperatura_inicial: float = DEFAULT_T_INICIAL
    temperatura_minima: float = DEFAULT_T_MINIMA
    taxa_resfriamento: float = DEFAULT_TAXA_RESFRIAMENTO
    iteracoes_por_temperatura: int = DEFAULT_ITER_POR_TEMP
    criterio_parada_iteracoes_globais: int = 5000

class ParametrosExecucao(BaseModel):
    pesos_objetivo: PesosObjetivo = Field(default_factory=PesosObjetivo)
    sa_parametros: SAParametros = Field(default_factory=SAParametros)
    periodos_por_dia: int = DEFAULT_PERIODOS_POR_DIA
    dias_letivos: int = DEFAULT_DIAS_LETIVOS

class Professor(BaseModel):
    id_professor: str
    nome: str = ""
    carga_maxima: int
    indisponibilidades: List[int] = Field(default_factory=list)

class Turma(BaseModel):
    id_turma: str
    nome: str = ""

class Disciplina(BaseModel):
    id_disciplina: str
    nome: str = ""

class Demanda(BaseModel):
    id_professor: str
    id_turma: str
    id_disciplina: str
    quantidade_aulas: int

class STPState(BaseModel):
    parametros_execucao: ParametrosExecucao = Field(default_factory=ParametrosExecucao)
    professores: List[Professor] = Field(default_factory=list)
    turmas: List[Turma] = Field(default_factory=list)
    disciplinas: List[Disciplina] = Field(default_factory=list)
    demandas: List[Demanda] = Field(default_factory=list)
