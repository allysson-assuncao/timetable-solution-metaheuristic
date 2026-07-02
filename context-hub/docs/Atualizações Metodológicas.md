\# Atualização Metodológica: Modelagem e Hibridização Algorítmica para o School Timetabling Problem (STP)

\#\# 1\. Caracterização do Problema e Definição de Custo  
O problema abordado é caracterizado estritamente como um modelo de \*\*Minimização\*\*. O "custo" do sistema não é financeiro, mas sim uma métrica matemática que quantifica o grau de ineficiência ergonômica e a inviabilidade operacional da grade gerada. Adotando a ótica focada no docente (baseada em Souza et al., 2003), o objetivo primário é mitigar a ociosidade da jornada (janelas) e os dias de deslocamento desnecessários. Custos logísticos focados na turma (como troca de andares) são suprimidos para conter a explosão combinatória, delimitando o escopo de viabilidade do projeto.

\#\# 2\. Estruturação da Entrada de Dados (Dataset)  
Para evitar que o algoritmo enfrente um subproblema intratável de emparelhamento bipartido durante a fase construtiva, a entrada de dados encapsula todo o contexto em um único objeto JSON estruturado. A alocação de "quem ensina o quê" já vem pré-processada.

\*\*Estrutura Base do JSON:\*\*  
\* \`parametros\_execucao\`: Contém os pesos da função objetivo ($\\alpha, \\beta, \\gamma$) e os hiperparâmetros do Simulated Annealing (temperatura inicial $T\_0$, taxa de resfriamento e critério de parada).  
\* \`professores\`: Um vetor de objetos onde cada docente possui um ID único, sua carga máxima semanal e um vetor de \`indisponibilidades\` (índices absolutos dos períodos em que o docente está vetado de lecionar).  
\* \`turmas\`: Vetor com os identificadores únicos das classes (ex: "T101", "T102").  
\* \`demandas\`: O vetor crucial do modelo. Contém a matriz de requisitos desmembrada em tuplas. Cada objeto especifica o docente, a turma, a disciplina lecionada e a quantidade de aulas semanais exigidas para aquela combinação específica.

Ex:

´´´json  
{  
  "parametros\_execucao": {  
    "pesos\_objetivo": {  
      "alpha": 1.0,   
      "beta": 0.5,  
      "gamma": 10000.0   
    },  
    "sa\_parametros": {  
      "temperatura\_inicial": 100.0,  
      "taxa\_resfriamento": 0.95,  
      "criterio\_parada\_iteracoes": 5000  
    },  
    "periodos\_por\_dia": 5,  
    "dias\_letivos": 5  
  },  
  "professores": \[  
    {  
      "id\_professor": "M1",  
      "carga\_maxima": 20,  
      "indisponibilidades": \[1, 2, 14, 15\]   
    }  
  \],  
  "turmas": \[  
    "T101", "T102", "T201"  
  \],  
  "demandas": \[  
    {  
      "id\_professor": "M1",  
      "id\_turma": "T101",  
      "disciplina": "Matemática",  
      "quantidade\_aulas": 4  
    },  
    {  
      "id\_professor": "M1",  
      "id\_turma": "T102",  
      "disciplina": "Física",  
      "quantidade\_aulas": 2  
    }  
  \]  
}  
´´´

\#\# 3\. Representação Computacional da Solução  
A modelagem da grade abandona a representação unidimensional simples e adota uma matriz bidimensional estrita $X\_{M \\times P}$, onde as linhas $M$ representam os docentes e as colunas $P$ representam os períodos letivos.

Para suportar a complexidade do currículo, o domínio de cada célula $x\_{ij}$ é expandido para armazenar uma tupla de alocação:  
\* \*\*Alocação Ativa:\*\* $x\_{ij} \= (\\text{ID\\\_Turma}, \\text{ID\\\_Disciplina})$.  
\* \*\*Período Ocioso (Janela):\*\* $x\_{ij} \= (0, \\text{Nulo})$.  
\* \*\*Indisponibilidade:\*\* $x\_{ij} \= (-1, \\text{Nulo})$.   
A inicialização prévia dos valores \`-1\` nos índices bloqueados do docente trata a restrição de disponibilidade de forma passiva, em tempo constante $O(1)$.

\#\# 4\. Função Objetivo e Sistema de Penalidades  
A avaliação global da solução transita por matrizes inviáveis graças à adição de uma constante de penalização severa para restrições rígidas. A função é definida como:

$$f(X) \= \\alpha \\cdot \\sum\_{i \\in M} J\_i(X) \+ \\beta \\cdot \\sum\_{i \\in M} D\_i(X) \+ \\gamma \\cdot \\sum\_{j \\in P} C\_j(X)$$

\* $J\_i(X)$: Somatório de janelas (períodos ociosos entre aulas) do professor $i$.  
\* $D\_i(X)$: Somatório de dias letivos trabalhados pelo professor $i$.  
\* $C\_j(X)$: Número de choques de turma no período $j$ (a mesma turma alocada para dois professores simultaneamente).  
\* $\\gamma$: Peso de penalidade extrema (ex: 10000). Garante que a violação da restrição rígida H1 (Inviolabilidade da Turma) eleve o custo da solução a patamares inaceitáveis, guiando o algoritmo probabilístico para fora desse ótimo local.

\#\# 5\. Fase 1: Motor Construtivo (GRASP)  
A etapa construtiva tem a responsabilidade de gerar uma matriz de alocação inicial de forma semi-gulosa, utilizando a Lista Restrita de Candidatos (RCL). O motor consome a "Pilha de Aulas" gerada pelo vetor de demandas, alocando evento por evento.

Para garantir performance e evitar \*backtracking\* (retrocesso algorítmico) caso a matriz fique estrangulada, adota-se a técnica de relaxamento de restrições. Se a fase gulosa não encontrar nenhum período sem choque para alocar a última aula de uma turma, o GRASP alocará forçadamente essa aula gerando um choque de turma. O resultado é uma grade parcialmente inviável, delegando a correção para a fase termodinâmica.

\#\# 6\. Fase 2: Refinamento Termodinâmico (Simulated Annealing)  
O \*Simulated Annealing\* (SA) assume a matriz inicial e inicia a busca local, tendo como vizinhança estrita os movimentos de \*\*Swap Intra-linha\*\*.

\* \*\*Mecânica de Vizinhança:\*\* O SA permuta exclusivamente duas células $x\_{ij1}$ e $x\_{ij2}$ pertencentes à mesma linha $i$ (mesmo professor). Isso garante mitigações passivas em cascata: é impossível gerar choque de professores e impossível violar a carga horária semanal estipulada no vetor de demandas.  
\* \*\*Correção de Viabilidade:\*\* Devido à alta temperatura inicial, o SA tem energia para aceitar movimentos que pioram temporariamente as janelas do docente, mas que servem para separar as aulas daquela turma que estavam em choque no mesmo período. Ao resolver o choque, o peso $\\gamma$ é subtraído da função objetivo, promovendo uma queda vertiginosa do custo total e reestabelecendo a viabilidade rígida da solução, antes de finalmente resfriar e otimizar os dias de deslocamento.