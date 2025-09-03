# TCC - Análise de Estratégias de Alocação de Carteiras: Risk Parity vs Markowitz vs Equal Weight

**Autor:** Bruno Gasparoni Ballerini  
**Instituição:** Universidade Presbiteriana Mackenzie  
**Curso:** Economia  
**Orientador:** [Nome do Orientador]  

## 📋 Resumo

Este Trabalho de Conclusão de Curso analisa comparativamente três estratégias de alocação de carteiras no mercado brasileiro durante o período 2018-2019:

- **Markowitz (Média-Variância)**: Maximização do Índice de Sharpe
- **Equal Weight**: Alocação igualitária entre todos os ativos
- **Risk Parity (ERC)**: Equalização das contribuições marginais de risco

O estudo utiliza metodologia out-of-sample rigorosa com dados reais da Economática, eliminando survivorship bias e implementando testes de significância estatística.

## 🎯 Objetivos

### Objetivo Geral
Comparar o desempenho das três estratégias de alocação em termos de risco-retorno no mercado acionário brasileiro.

### Objetivos Específicos
- Implementar o modelo ERC (Equal Risk Contribution) verdadeiro utilizando matriz de covariância
- Aplicar metodologia out-of-sample com rebalanceamento semestral
- Realizar testes de significância estatística (Ledoit-Wolf e Bootstrap)
- Simular impacto de custos de transação
- Analisar a robustez dos resultados em períodos de alta volatilidade

## 📊 Resultados Principais

### Performance (2018-2019)
| Estratégia   | Retorno Anual | Volatilidade | Sharpe Ratio | Sortino Ratio | Max Drawdown |
|-------------|---------------|--------------|--------------|---------------|--------------|
| Markowitz   | 26.14%        | 14.49%       | 1.90         | 2.51          | -12.3%       |
| Equal Weight| 24.12%        | 20.87%       | 1.49         | 1.65          | -19.7%       |
| Risk Parity | 14.51%        | 16.86%       | 0.83         | N/A           | -18.6%       |

### Testes de Significância Estatística
Todas as diferenças de Sharpe Ratio são estatisticamente significativas ao nível de 5%:
- Markowitz vs Equal Weight: p-value = 0.0001
- Markowitz vs Risk Parity: p-value < 0.0001  
- Equal Weight vs Risk Parity: p-value = 0.0006

## 🗂️ Estrutura do Projeto

```
TCC_RiskParity/
├── data/
│   └── DataBase/              # Dados da Economática (2014-2019)
├── src/                       # Scripts Python
│   ├── final_methodology.py   # Metodologia principal
│   ├── economatica_loader.py  # Carregador de dados
│   ├── generate_missing_charts.py  # Geração de gráficos
│   └── create_charts_simple.py     # Gráficos adicionais
├── docs/
│   └── Overleaf/             # Documentação LaTeX
│       ├── sections/         # Capítulos do TCC
│       ├── images/           # Gráficos e figuras
│       ├── tables/           # Tabelas LaTeX
│       └── main.pdf          # PDF final compilado
└── README.md                 # Este arquivo
```

## 🔧 Metodologia

### Seleção de Ativos (Ex-Ante)
- **10 ativos** selecionados com critérios rigorosamente ex-ante
- Base: liquidez, capitalização e diversificação setorial até dezembro/2017
- Eliminação de survivorship bias

**Ativos Selecionados:**
PETR4, VALE3, ITUB4, BBDC4, ABEV3, B3SA3, WEGE3, RENT3, LREN3, ELET3

### Estrutura Temporal
- **Dados:** 2016-2019 (Economática)
- **Estimação:** 2016-2017 (24 meses rolling)
- **Teste:** 2018-2019 (23 meses out-of-sample)
- **Rebalanceamento:** Semestral (janeiro e julho)

### Implementações
- **Markowitz:** Otimização SLSQP com restrições (2%-20% por ativo)
- **Equal Weight:** Alocação uniforme (10% cada)
- **Risk Parity:** Algoritmo iterativo ERC (Spinu, 2013) com matriz de covariância

### Taxa Livre de Risco
- **CDI 2018:** 6.43% a.a.
- **CDI 2019:** 5.96% a.a.  
- **Média:** 6.195% a.a.

## 📈 Principais Contribuições

1. **Implementação ERC Verdadeira**: Substituição do IVP simples por algoritmo ERC completo
2. **Eliminação de Survivorship Bias**: Critérios de seleção rigorosamente ex-ante
3. **Testes Estatísticos**: Validação com Ledoit-Wolf e Bootstrap
4. **Análise de Custos**: Simulação de impacto de custos de transação
5. **Metodologia Out-of-Sample**: Rigor acadêmico na validação

## 🛠️ Tecnologias e Ferramentas

- **Python 3.13+**
  - pandas, numpy (manipulação de dados)
  - scipy (otimização e testes estatísticos)  
  - matplotlib, seaborn (visualização)
  - cvxpy (otimização convexa - alternativa)
- **LaTeX** (documentação)
- **Economática** (fonte de dados)
- **Git/GitHub** (controle de versão)

## 📋 Requisitos

```bash
pip install pandas numpy scipy matplotlib seaborn cvxpy openpyxl
```

## 🚀 Como Executar

```bash
# Clone o repositório
git clone [URL_DO_REPOSITORIO]
cd TCC_RiskParity

# Execute a análise principal
python src/final_methodology.py

# Gere gráficos adicionais
python src/generate_missing_charts.py
```

## 📊 Resultados Detalhados

### Turnover Médio
- Markowitz: 30.4%
- Equal Weight: 25.0%
- Risk Parity: 29.0%

### Impacto de Custos de Transação (10 bps)
- Markowitz: Redução de 0.2% no Sharpe
- Equal Weight: Redução de 0.2% no Sharpe  
- Risk Parity: Redução de 0.6% no Sharpe

## 📝 Limitações

- Custos de transação, impostos e slippage não incorporados nos resultados principais
- Período de análise limitado (2018-2019) - alta volatilidade política
- Apenas três estratégias analisadas
- Taxa livre de risco simplificada (CDI médio)

## 🔮 Trabalhos Futuros

- Análise em períodos mais longos e estáveis
- Implementação de Hierarchical Risk Parity
- Incorporação de Machine Learning
- Análise de diferentes classes de ativos
- Estudo de custos de transação mais detalhado

## 📜 Citação

```bibtex
@misc{ballerini2024tcc,
  author = {Ballerini, Bruno Gasparoni},
  title = {Análise de Estratégias de Alocação de Carteiras: Risk Parity vs Markowitz vs Equal Weight},
  school = {Universidade Presbiteriana Mackenzie},
  year = {2024},
  type = {Trabalho de Conclusão de Curso}
}
```

## 📞 Contato

**Bruno Gasparoni Ballerini**  
📧 [email]  
🎓 Economia - Universidade Presbiteriana Mackenzie  

---

## 🔄 Última Atualização

**Data:** Setembro 2024  
**Status:** ✅ Completo com todas as correções implementadas  
**Versão:** 1.0 Final  

### Correções Implementadas
- ✅ ERC verdadeiro (substituindo IVP)
- ✅ Eliminação de survivorship bias  
- ✅ Testes de significância estatística
- ✅ Simulação de custos de transação
- ✅ Metodologia out-of-sample rigorosa
- ✅ Padronização de fórmulas e cross-references

**📄 PDF Final:** `docs/Overleaf/main.pdf` (4.4MB)

## 📐 Para Overleaf

### Como Importar no Overleaf
1. Acesse [Overleaf.com](https://www.overleaf.com)
2. Faça login ou crie uma conta
3. Clique em "New Project" → "Upload Project" 
4. Faça upload da pasta `TCC_RiskParity/docs/Overleaf/`
5. O documento será compilado automaticamente

### Sincronização GitHub ↔ Overleaf
1. No Overleaf: Menu → Sync → GitHub
2. Conecte este repositório
3. Sincronize a pasta `TCC_RiskParity/docs/Overleaf/`

**📁 Pasta principal para Overleaf:** `TCC_RiskParity/docs/Overleaf/`