from pydantic import BaseModel, Field
from typing import List

class PesosObjetivo(BaseModel):
    alpha: float = 1.0
    beta: float = 0.5
    gamma: float = 50.0

class SAParametros(BaseModel):
    temperatura_inicial: float = 100.0
    temperatura_minima: float = 0.01
    taxa_resfriamento: float = 0.95
    iteracoes_por_temperatura: int = 100
    criterio_parada_iteracoes_globais: int = 5000

class ParametrosExecucao(BaseModel):
    pesos_objetivo: PesosObjetivo = Field(default_factory=PesosObjetivo)
    sa_parametros: SAParametros = Field(default_factory=SAParametros)
    periodos_por_dia: int = 5
    dias_letivos: int = 5

class Professor(BaseModel):
    id_professor: str
    carga_maxima: int
    indisponibilidades: List[int] = Field(default_factory=list)

class Demanda(BaseModel):
    id_professor: str
    id_turma: str
    disciplina: str
    quantidade_aulas: int

class STPState(BaseModel):
    parametros_execucao: ParametrosExecucao = Field(default_factory=ParametrosExecucao)
    professores: List[Professor] = Field(default_factory=list)
    turmas: List[str] = Field(default_factory=list)
    demandas: List[Demanda] = Field(default_factory=list)
