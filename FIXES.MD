1) Problemas críticos (must-fix antes de entregar)

1.1. Numeração e repetição de fórmulas (inconsistente)

A mesma fórmula de Risk Parity aparece numerada de formas diferentes em capítulos distintos: em 2.3 como (2.1), em 2.9 como (2.4), em 3.5 como (3.1) e no capítulo 4 de novo como (4.6). Padronize (defina em “Referencial” e apenas referencie depois). 
 
 
 

Como corrigir: mantenha as fórmulas-mãe no Cap. 2 (p.ex., (2.1)–(2.3)); nos capítulos 3 e 4, use “vide Eq. (2.1)”.

1.2. Qual “Risk Parity” você implementou? (IVP ≠ ERC)

O texto diz que RP “equaliza a contribuição de risco”, mas a fórmula usada é a de Inverse-Volatility (IVP), que não garante contribuição de risco igual quando há correlações ≠ 0. Você até descreve a contribuição marginal de risco (RCᵢ) corretamente, mas os pesos continuam sendo 1/σᵢ. Ou você troca a nomenclatura para IVP, ou resolve de fato a ERC (Risk Parity verdadeiro) via otimização com Σ. 
 

Correção recomendada:
(b) implementar ERC: minimizar ∑(RCᵢ−σ_p/n)² s.a. w≥0, 1ᵀw=1, usando Σ (cvxpy). e arrumar a formula no texto e qualquer explicacao inconsistente.

1.3. Período e janela: inconsistência temporal

“Horizonte” declarado: 2018–2019. 

“Coleta/tratamento”: 2014–2019. 

Out-of-sample usa 2016–2017 para estimação e 2018–2019 para teste (47 mensais; 24+23). 

Isso é plausível, mas precisa ser dito de forma única e coerente: “Dados brutos 2014–2019; janela de estimação rolling de 24 meses (2016–2017) → teste semestral em 2018–2019 segundo a Tabela 3.2 (23 meses no total)”. 

1.4. Sobrevivência e viés de seleção

Você filtra ativos “ativos em 31/12/2019” e ainda reforça “sobrevivência: todos mantiveram negociação ativa em 2018–2019”. Isso pode induzir survivorship bias (excluir quem “morreu”/foi pior). 

Correção: defina o universo investível a cada data de rebalanceamento (in-sample) e trate delistings com “delisting return” (ou remova a restrição de sobrevivência ex-ante; mantenha só critérios ex-ante de liquidez e dados).

1.5. Declarações fortes sem testes de significância

Você afirma superioridade estatística (Sharpe 1,88 vs 1,47/1,46; Sortino 2,14 vs 1,12/1,22; MDD −12,3% vs −19,7%), mas não testa se as diferenças são estatisticamente significativas (Jobson-Korkie/ Memmel, Ledoit-Wolf para Sharpe; bootstrap/block-bootstrap; NW). 

Correção: inclua seção “Testes de significância”:

Diferença de Sharpe (Ledoit-Wolf),

Bootstrapping com blocos (dependência temporal),

Deflated Sharpe Ratio (Bailey & López de Prado) como robustez.

1.6. Custos de transação: faltou quantificar

Você lista como limitação, mas não simula cenários (p.ex., 5–20 bps por trade). Um único quadro mostrando o impacto por estratégia e por semestre elevaria o rigor. 

2) Metodologia: ajustes para research-grade

2.1. Restrições da Markowitz e concentração

Você impõe 2% ≤ wᵢ ≤ 20% (sem short). 

Nos resultados, Markowitz “trava” 4 nomes em 20% (80% da carteira). Isso respeita o limite, mas a conclusão pró-Markowitz pode estar “carregada” por esse teto (evita concentração >20% em 1 nome). Verifique sensibilidade a:
(a) w_max = 15% e 25%, (b) sem w_min=2%, (c) com L2/L1 regularization (ridge/lasso). 

2.2. Métricas e taxa livre de risco

Você usa r_f = 6,5% a.a. e aplica Sharpe/Sortino. Declare exatamente: (i) como converteu CDI a mensal; (ii) anualização: retorno ×12 e σ×√12? (iii) Sortino: threshold T = r_f mensal ou 0? Hoje o texto mistura (em 2.4 o Sortino usa T genérico; em 4.4.4 usa r_f). Uniformize. 
 
 

2.3. Out-of-sample

A Tabela 3.2 (quatro janelas de teste: 6+6+6+5 meses = 23) está ok, mas explique por que optou por rebalanceamento semestral e janela de 24 meses (defenda contra “overfitting de escolhas”). Adicione uma robustez com trimestral e anual. 

2.4. Equal Weight

Está correta a definição (w=1/n). Considere reportar tracking error vs. EW para as demais estratégias — ajuda a entender o “custo da sofisticação”. 

2.5. Amostra de ativos

Pipeline de filtros bem descrito (508→10), mas faltou um quadro “funnel” com contagens + motivos (um gráfico tipo Sankey ou tabela clara). E reforce que todos os filtros são ex-ante (evite olhar 2019 para decidir elegibilidade 2018). 
 
 
 

3) Resultados & interpretação: endurecer o crivo

3.1. “Contradição com a literatura” — qual o tamanho do efeito?

Você argumenta que Markowitz supera as simples. Traga intervalos de confiança e p-values para não ficar só descritivo. 

3.2. Narrativa setorial

Você atribui a vitória de Markowitz à concentração em VALE/WEGE/RENT/LREN; ótimo — então quantifique a contribuição de cada ativo no “excesso de Sharpe” (attribution). 

3.3. “Falha do RP”

O texto diz “confusão volatilidade = risco” — isso é verdadeiro para IVP, não para ERC. Se mantiver IVP, troque a crítica para “IVP tende a superponderar defensivos e subponderar cíclicos em regimes de forte dispersão, perdendo rally” — e mostre o peso em ABEV3 vs. retorno relativo. 

3.4. Robustez temporal

Você tem “performance por semestres” como seção de robustez (4.10), mas a discussão ainda é curta. Amplie com: (i) gráficos de pesos ao longo do tempo, (ii) correlações entre ativos por semestre, (iii) heatmap Σ por janela. 

4) Escrita, estrutura e estilo científico

4.1. Resumo/Abstract devem trazer números-chave

Inclua 2–3 números-âncora (Sharpe, Sortino, MDD) com período e critério (OOS, sem custos). Isso aumenta impacto e transparência. (Exemplos num TCC valem ouro.) 

4.2. Evitar seções “micro”

Algumas subseções são muito curtas; fusione “implicações práticas” ao final de “Discussão” (ou como sub-itens). Ajuda no fluxo. 

4.3. Coesão terminológica

Use sempre os mesmos nomes: “Markowitz”/“Média-Variância”; “Equal Weight”/“Equiponderada”; “Inverse Volatility” ou “Risk Parity (ERC)”. Hoje varia.

4.4. Figuras/Tabelas

Insira legendas auto-suficientes (método, período, OOS/IS, sem custos) e cite a ferramenta (matplotlib/seaborn) numa notinha única (evite repetir). 

5) Checklist técnico (acrescente como apêndice)

Reprodutibilidade: “data-availability & code-availability” (link Git ou zip) + requirements.txt + semente aleatória.

Dicionário de dados: tickers, datas, ajustes (proventos/desdobramentos), fonte (Economática). 

Conversões: CDI→mensal; anualização de retorno/risco e de Sharpe.

Tratamentos: dias sem negociação, outliers, “stale prices”. 

Métricas adicionais: calmar, ulcer, hit-ratio, TE vs EW.

Testes de significância (ver 1.5).

Cenários de custos: 5/10/20 bps + slippage. 

Alternativas: HRP, Black-Litterman, shrinkage de Σ (Ledoit-Wolf) — mencione como futuro trabalho (você já sugere HRP; reforce). 

6) Trechos onde vale reescrever (sugestões curtas)

6.1. Metodologia (OOS + janelas)

“Adotamos OOS com janela móvel de 24 meses (rolling) para estimação e rebalanceamento semestral em 2018–2019, seguindo os quatro blocos da Tabela 3.2 (23 meses no total). A cada data-âncora, apenas informações passadas são usadas; as carteiras resultantes são aplicadas exclusivamente no período futuro.” 
 

6.2. Definição de Risk Parity (se manter IVP)

“Empregamos a variação Inverse-Volatility (IVP): 
𝑤
𝑖
∝
1
/
𝜎
𝑖
w
i
	​

∝1/σ
i
	​

. Embora o RP verdadeiro (ERC) iguale contribuições marginais de risco considerando a matriz de covariância, adotamos IVP pela simplicidade e reprodutibilidade; chamamos explicitamente de IVP para evitar ambiguidade.” 

6.3. Limitações (quantificar)

“Reavaliamos os resultados sob custos de 10 bps por ordem e slippage de 5 bps; as conclusões permanecem qualitativamente robustas, mas a vantagem de Markowitz cai de X para Y em Sharpe.” (inserir tabela). 

7) Onde você brilhou (não perca!)

Pipeline de seleção e filtros (claro e criterioso). 

OOS com janelas e rebalanceamentos definidos (muito acima da média). 
 

Discussão do contexto BR e por que Markowitz pode ter ganhado no regime 2018–2019 (dispersão setorial, recuperação). Só faltou estatística de apoio. 

Plano de ação “cirúrgico” (em ordem)

Padronizar fórmulas e nomenclatura (RP→IVP ou implementar ERC). 
 

Unificar narrativa temporal (2014–2019 dados; 2016–2017 estimação; 2018–2019 teste) em um único parágrafo na Metodologia. 
 
 

Rever filtro de sobrevivência (explicitar ex-ante; tratar delistings). 

Adicionar testes de significância para diferenças de Sharpe/Sortino. (Se der, bloco bootstrap para séries.)

Simular custos (quadro simples com 3 níveis). 

Sensibilidade das restrições (w_max/w_min; penalizações). 

Resumo/Abstract com números-âncora e deixar Conclusão mais assertiva (menos recapitulação, mais síntese e implicações).
