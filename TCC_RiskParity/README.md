# TCC - Análise Comparativa de Estratégias de Alocação de Carteira

## Estrutura do Projeto

```
TCC_RiskParity/
├── src/                    # Código fonte principal
│   ├── final_methodology.py       # Metodologia final com cálculos corretos
│   ├── economatica_loader.py      # Carregador de dados Economatica
│   ├── create_charts_simple.py    # Gerador de gráficos simples
│   └── generate_missing_charts.py # Gerador de gráficos específicos
├── data/                   # Dados do projeto
│   └── DataBase/          # Base de dados Economatica
├── docs/                   # Documentação e LaTeX
│   └── Overleaf/          # Arquivos LaTeX do TCC
├── backup/                 # Arquivos de backup
│   ├── old_scripts/       # Scripts antigos
│   └── results/           # Resultados antigos
└── requirements.txt        # Dependências Python
```

## Resumo do Projeto

Análise comparativa das estratégias de alocação:
- **Markowitz** (Mean-Variance Optimization)
- **Equal Weight** (Peso igual para todos os ativos)
- **Risk Parity** (Paridade de risco)

**Período de análise:** 2018-2019 (dados out-of-sample)
**Mercado:** Ações brasileiras (10 blue chips)

## Resultados Principais

| Estratégia    | Retorno | Volatilidade | Sharpe | Sortino |
|---------------|---------|--------------|--------|---------|
| Markowitz     | 26,1%   | 14,5%        | 1,90   | 2,51    |
| Equal Weight  | 24,1%   | 20,9%        | 1,49   | 1,65    |
| Risk Parity   | 21,7%   | 18,8%        | 1,50   | 1,41    |

## Como Usar

1. Execute `src/final_methodology.py` para análise completa
2. Use `src/generate_missing_charts.py` para gerar gráficos
3. Compile LaTeX em `docs/Overleaf/main.tex`

## Dependências

- pandas
- numpy
- scipy
- matplotlib
- seaborn
- cvxpy