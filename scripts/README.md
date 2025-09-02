# Scripts de Análise - TCC Bruno Ballerini

## Comparação entre Métodos de Alocação de Carteiras no Mercado Brasileiro (2018-2019)

Este diretório contém todos os scripts Python necessários para reproduzir a análise completa do TCC.

## 📁 Estrutura dos Arquivos

- `main_analysis.py` - Motor principal da análise (classe PortfolioAnalyzer)
- `generate_charts.py` - Gerador de todos os gráficos para o TCC
- `run_full_analysis.py` - Script principal que executa tudo
- `requirements.txt` - Dependências necessárias
- `README.md` - Este arquivo

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Preparar Dados

Certifique-se de que o arquivo da Economatica está no local correto:
```
TCC/
├── DataBase/
│   └── economatica (1).xlsx
└── scripts/
    └── [arquivos python]
```

### 3. Executar Análise Completa

```bash
python run_full_analysis.py
```

Este script irá:
- ✅ Carregar e processar os dados da Economatica
- ✅ Implementar as 3 estratégias (Markowitz, Equal Weight, Risk Parity)
- ✅ Executar backtest com rebalanceamento semestral
- ✅ Gerar todas as tabelas em LaTeX
- ✅ Gerar todos os gráficos
- ✅ Produzir relatório final

## 📊 Estratégias Implementadas

### 1. Markowitz (Média-Variância)
- Otimização de máximo Sharpe Ratio
- Usa biblioteca `cvxpy` para programação quadrática
- Restrições: soma = 1, sem vendas a descoberto

### 2. Equal Weight
- Alocação igualitária: 10% para cada ativo
- Benchmark simples e robusto

### 3. Risk Parity
- Pesos inversamente proporcionais à volatilidade
- Fórmula: wi = (1/σi) / Σ(1/σj)

## 📈 Saídas Geradas

### Tabelas LaTeX (salvas em `../Overleaf/tables/`)
- `portfolio_performance.tex` - Performance consolidada
- `descriptive_stats.tex` - Estatísticas descritivas dos ativos
- `risk_metrics.tex` - Métricas avançadas de risco
- `sector_stats.tex` - Análise setorial

### Gráficos (salvos em `../Overleaf/images/`)
- `correlation_matrix.png` - Matriz de correlação
- `price_evolution.png` - Evolução dos preços
- `volatility_rolling.png` - Volatilidade rolling
- `portfolio_evolution.png` - Evolução das carteiras
- `risk_return_plot.png` - Gráfico risco-retorno
- `returns_distribution.png` - Distribuição de retornos
- `sector_analysis.png` - Análise por setor

## 🔧 Configurações Principais

### Período de Análise
- **Início:** Janeiro 2018
- **Fim:** Dezembro 2019
- **Rebalanceamento:** Semestral

### Parâmetros
- **Taxa livre de risco:** 6,5% a.a. (CDI médio do período)
- **Frequência dos dados:** Mensal
- **Número de ativos:** 10

### Ativos Analisados
1. PETR4 - Petróleo Brasileiro
2. VALE3 - Vale
3. ITUB4 - Itaú Unibanco
4. BBDC4 - Banco Bradesco
5. ABEV3 - Ambev
6. B3SA3 - B3
7. WEGE3 - WEG
8. RENT3 - Localiza
9. LREN3 - Lojas Renner
10. ELET3 - Centrais Elétricas Brasileiras

## 📋 Métricas Calculadas

### Performance
- Retorno anualizado
- Volatilidade anualizada
- Índice de Sharpe
- Sortino Ratio

### Risco
- Maximum Drawdown
- Value at Risk (VaR) 95%
- Conditional VaR (CVaR)

### Estatísticas
- Média, desvio-padrão
- Assimetria, curtose
- Teste de Jarque-Bera

## 🛠 Personalização

### Alterar Período
Edite no `main_analysis.py`:
```python
start_date = '2018-01-01'  # Altere aqui
end_date = '2019-12-31'    # Altere aqui
```

### Alterar Taxa Livre de Risco
```python
self.risk_free_rate = 0.065  # 6.5% a.a.
```

### Alterar Ativos
```python
self.assets = ['PETR4', 'VALE3', ...]  # Liste os códigos
```

## ⚡ Execução Rápida (Somente Resultados)

Se quiser apenas os resultados principais:

```python
from main_analysis import PortfolioAnalyzer

analyzer = PortfolioAnalyzer("../DataBase/economatica (1).xlsx")
analyzer.load_data()
_, results = analyzer.backtest_strategies()

# Ver resultados
for strategy, metrics in results.items():
    print(f"{strategy}: Sharpe = {metrics['sharpe_ratio']:.2f}")
```

## 🐛 Resolução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se o caminho para `economatica (1).xlsx` está correto
- O script tentará gerar dados sintéticos se não encontrar o arquivo

### Erro: "cvxpy solver failed"
- Instale solver adicional: `pip install cvxopt`
- O script usará Equal Weight como fallback

### Erro de memória
- Reduza o período de análise
- Use menos ativos na amostra

## 📞 Suporte

Para dúvidas sobre os scripts:
1. Verifique se todas as dependências estão instaladas
2. Confira se os caminhos dos arquivos estão corretos
3. Execute `python -c "import pandas; print('OK')"` para testar

## 🎯 Próximos Passos

Após executar os scripts:
1. Incluir as tabelas geradas no LaTeX
2. Verificar se os gráficos estão sendo referenciados
3. Ajustar discussão baseada nos resultados reais
4. Compilar o documento final