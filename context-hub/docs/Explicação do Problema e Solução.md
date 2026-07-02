# **Roteiro de Apresentação: Otimização de Quadro de Horários (STP)**

Este roteiro detalha a estrutura de suporte para a apresentação oral do trabalho "Otimização Heurística de Quadro de Horários Escolares Baseada nas Meta-heurísticas GRASP e Simulated Annealing".

# **Slide 1: Capa**

## **Conteúdo**

* **Título:** Otimização Heurística de Quadro de Horários Escolares (STP) via Hibridização GRASP e Simulated Annealing.  
* **Alunos:** Allysson Bruno Chaves Assunção e Moisés Emanuel Reis da Cruz.  
* **Afiliação:** Instituto Federal de Educação, Ciência e Tecnologia de Minas Gerais (IFMG).  
* **Disciplina:** Tópicos Especiais em Algoritmos.

## **Orientação (Roteiro/Fala)**

Inicie de forma profissional e direta: "Boa noite, hoje vamos apresentar nossa proposta de otimização para o School Timetabling Problem, focada na melhoria ergonômica da grade docente".

## **Dica Visual**

Utilize o logo oficial da instituição e um design sóbrio em conformidade com os padrões acadêmicos da SBC.

# **Slide 2: Contexto e Definição do Problema**

## **Conteúdo**

* **O que é o STP?** Problema de alocação de recursos acadêmicos (turmas, docentes e espaços físicos) em blocos temporais restritos.  
* **Complexidade:** Classificado categoricamente como NP-difícil (NP-hard).  
* **Desafio:** O fenômeno da explosão combinatória torna inviável o uso de métodos exatos para instâncias reais, exigindo abordagens heurísticas.

## **Orientação**

A classificação NP-difícil (NP-hard) constitui um gargalo operacional crítico, não meramente um conceito teórico. O espaço de soluções cresce fatorialmente com a escala de turmas e docentes, invalidando a aplicabilidade de métodos exatos. Nesse cenário de explosão combinatória, as meta-heurísticas consolidam-se como a única alternativa para a obtenção de soluções de alta performance em intervalos computacionais exequíveis.

## **Dica Visual**

Ícone representando um quebra-cabeça complexo ou uma rede interconectada de restrições.

# **Slide 3: Fundamentação Teórica (Estado da Arte)**

## **Conteúdo**

* **Souza, Maculan e Ochi (2003):** Proposta baseada na ótica professor-cêntrica, utilizando matriz X(MxP) e hibridismo GRASP \+ Tabu Search.  
* **Zhang, Liu e M'Hallah (2010):** Abordagem orientada à turma via hiper-matriz tridimensional M(c, d, p) utilizando Simulated Annealing bifásico.

## **Orientação**

Existe uma dicotomia metodológica fundamental entre as abordagens de referência. Souza et al. (2003) utiliza uma matriz 2D (professor-cêntrica), ideal para gerenciar a carga docente, enquanto Zhang et al. (2010) emprega uma hiper-matriz 3D (turma-cêntrica, estruturada em classes, dias e períodos), permitindo uma visão holística da grade discente. O segundo artigo também provê uma inteligência maior de refinamento com o SA bifásico. A nossa proposta hibridiza ambos os paradigmas: integra a eficiência computacional passiva da matriz docente na mitigação de conflitos com a robustez do motor termodinâmico para a otimização global, mantendo o rigor na verificação de restrições rígidas.

## **Dica Visual**

Tabela comparativa simples dividindo as abordagens por "Representação" e "Meta-heurística".

# **Slide 4: Entrada de Dados (Dataset)**

## **Conteúdo**

* **Estrutura de Entrada:** Arquivo JSON contendo as configurações de sistema e o vetor de demandas curriculares.  
* **Entrada de Dados:** JSON estruturado contendo vetor de Demandas \[Docente, Turma, Disciplina, Qtd. Aulas\].

```json
{
  "parametros_execucao": {
    "pesos_objetivo": {
      "alpha": 1.0, 
      "beta": 0.5,
      "gamma": 50.0 
    },
    "sa_parametros": {
      "temperatura_inicial": 100.0,
      "temperatura_minima": 0.01,
      "taxa_resfriamento": 0.95,
      "iteracoes_por_temperatura": 100,
      "criterio_parada_iteracoes_globais": 5000
    }
    "periodos_por_dia": 5,
    "dias_letivos": 5
  },
  "professores": [
    {
      "id_professor": "M1",
      "carga_maxima": 20,
      "indisponibilidades": [1, 2, 14, 15] 
    }
  ],
  "turmas": [
    "T101", "T102", "T201"
  ],
  "demandas": [
    {
      "id_professor": "M1",
      "id_turma": "T101",
      "disciplina": "Matemática",
      "quantidade_aulas": 4
    },
    {
      "id_professor": "M1",
      "id_turma": "T102",
      "disciplina": "Física",
      "quantidade_aulas": 2
    }
  ]
}
```

## **Orientação**

O dataset é estruturado para fornecer ao algoritmo o mapeamento completo das necessidades de alocação. O vetor de demandas consolida os vínculos entre docentes, turmas e disciplinas, eliminando o subproblema de emparelhamento e permitindo uma carga inicial limpa no processo de construção heurística.

## **Dica Visual**

Diagrama esquemático de uma matriz pequena realçando uma célula com o valor "-1".

# **Slide 5: Representação da Solução**

## **Conteúdo**

* **Estrutura:** Matriz Bidimensional XMxP.  
* **Domínio:** Valor das células;  
  * xij \> 0: ID\_Turma e ID\_Disciplina (Tupla).  
  * xij \= 0: Período vago.  
  * xij \= \-1: Indisponibilidade absoluta.

## **Orientação**

A matriz bidimensional XMxP é o núcleo desta solução. A estrutura foca no docente para garantir eficiência algorítmica e o gerenciamento passivo de conflitos ('by design'), onde o valor \-1 estabelece uma barreira lógica de indisponibilidade absoluta irrecusável.

## **Dica Visual**

Diagrama esquemático de uma matriz realçando a estrutura de tuplas e a célula de indisponibilidade.

# **Slide 6: Modelagem de Restrições**

## **Conteúdo**

* **Restrições Rígidas (Hard):** Inegociáveis para a viabilidade matemática.  
  * **Satisfeita por Validação e Penalização:**   
    * **H1:** Inviolabilidade de Turma (a turma não pode ter duas aulas no mesmo horário).  
  * **Satisfeitas por Construção:**  
    * **H2:** Preservação de Indisponibilidade do professor (xij \= \-1).  
    * **H3:** Inviolabilidade da Carga Horária semanal máxima do docente.  
    * **H4:** Inviolabilidade da grade da Turma (a turma não pode ter mais ou menos disciplinas do que o previsto, ou com distribuição incorreta).

* **Restrições Flexíveis (Soft):** Qualificam a qualidade da grade.  
  * **S1:** Minimização de Janelas (ociosidade intermitente).  
  * **S2:** Minimização de Dias de Deslocamento.

## **Orientação**

As restrições rígidas são determinantes para a viabilidade matemática, sendo inegociáveis para a execução do quadro. Já as restrições flexíveis definem a qualidade da grade, priorizando a ergonomia e a produtividade docente, fundamentais para a eficácia do sistema.

## **Dica Visual**

Lista com ícones (Ex: Cadeado para Hard, Estrela para Soft).

# **Slide 7: Função Objetivo**

## **Conteúdo**

* **Modelo de Minimização:** f(X) \= α · Σ Ji(X) \+ β · Σ Di(X) \+ γ · Σ Cj(X)  
* **Variáveis:**  
  * Ji(X): Contador de janelas (ociosidade).  
  * Di(X): Contador de dias extras de trabalho.  
  * Cj(X): Contador de violações H1 (turmas com 2 aulas no mesmo horário)  
  * **Parâmetros:** γ \>\> α \> β. Ex: γ \= 50, α \= 1, β \= 0.5. (Prioridade absoluta à eliminação de janelas, com penalização dura a violação de restrições rígidas).

## **Orientação**

A função objetivo f(X) é regida pelos parâmetros α, β e γ. O peso extremo γ penaliza choques de turma (H1), permitindo que o algoritmo transite por soluções temporariamente inviáveis para otimizar o cenário global e escapar de mínimos locais.

## **Dica Visual**

A fórmula em destaque centralizada com fonte de tamanho superior.

# **Slide 8: Fase Construtiva Semi-Gulosa (GRASP)**

## **Conteúdo**

* **Fluxo Inicial:** Consumo da Pilha de Aulas (vetor de demandas do JSON).  
* **Mecanismo:** Lista Restrita de Candidatos (RCL) para inserção semi-gulosa.  
* **Relaxamento de Restrição:** Alocação com choque de turmas proposital para evitar *backtracking*.

## **Orientação**

O GRASP inicia com matriz zerada e vai alocando as aulas de forma semi-gulosa. As restrições de indisponibilidade, carga docente e grade da turma são invioláveis por projeto nesta fase, por conta da estrutura da solução e da entrada de dados. Apenas o choque de turmas é violável. Se o sistema atingir um estrangulamento de horários, o GRASP aloca a aula gerando o choque propositalmente para evitar o altíssimo custo computacional de um retrocesso (backtracking).

## **Dica Visual**

Fluxo de consumo da "Pilha de Aulas" gerada pelo vetor de **demandas** do JSON **\-\>** Mecanismo da Lista Restrita de Candidatos (RCL) baseado em janelas intermediárias **\-\>** Ponto de decisão do Relaxamento de Restrição.

# **Slide 9: Estrutura de Vizinhança e Operador de Perturbação**

## **Conteúdo**

* **Operador:** *Swap* Intra-linha.  
* **Aplicação:** Permuta de conteúdos entre dois períodos (j1, j2) na mesma linha (docente).  
* **Invariância:** Carga horária semanal e disciplinas da turma preservadas.

## **Orientação**

A escolha pelo *Swap* Intra-linha é rigorosa. Ao confinar o movimento estritamente à linha do professor, a carga horária semanal contratual e as disciplinas da turma permanecem invariantes. O algoritmo ganha eficiência extrema, pois elimina a necessidade de validações redundantes de carga horária a cada iteração, permitindo foco computacional exclusivo na otimização de janelas (S1) e eliminação de choques (H1).

## **Dica Visual**

Diagrama de uma linha da matriz (um professor) destacando duas células e uma seta bidirecional indicando a permuta.

# **Slide 10: Refinamento Estocástico e Dissipação Térmica (SA)**

## **Conteúdo**

* **Objetivo:** Dissipação do peso γ (choque de turmas) e otimização ergonômica.  
* **Mecanismo:** Critério de Metropolis para aceitação de soluções piores em altas temperaturas.  
* **Dinâmica:** Resfriamento geométrico para convergência na viabilidade estrita.

## **Orientação**

O SA atua corrigindo a inviabilidade gerada pelo GRASP. Na temperatura inicial elevada, o algoritmo aceita soluções "piores" (temporariamente com janelas maiores) para separar as aulas em choque na mesma turma. Ao desfazer os choques, o peso extremo γ é eliminado, causando uma queda vertiginosa no custo global. Com o resfriamento, o foco desloca-se para a minimização das janelas (α) e dias extras (β), garantindo a viabilidade rígida da grade.

## **Dica Visual**

Gráfico conceitual de decaimento de temperatura (eixo X) versus Custo Total (eixo Y), destacando a região de alta temperatura (exploração) e baixa temperatura (refinamento).

# **Slide 11: Considerações Finais**

## **Conteúdo**

* **Robustez:** O modelo garante viabilidade operacional e foca na eficiência humana.  
* **Status:** Modelo matemático formalizado e estruturado para implementação.  
* **Próximos Passos:** Codificação em linguagem de alta performance e testes com instâncias reais.

## **Orientação**

Este trabalho consolida a base teórica e matemática necessária para a automatização de quadros de horários complexos, priorizando o bem-estar docente. O modelo encontra-se formalizado, estruturado e pronto para a codificação em ambiente de alta performance para validação com instâncias reais.

## **Dica Visual**

Imagem limpa de uma grade de horários organizada contrastando com uma grade confusa.