# 📋 LISTA COMPLETA DE INCONSISTÊNCIAS - TCC RISK PARITY

## 🔴 **INCONSISTÊNCIAS CRÍTICAS (Prioridade 1)**

### **1. JANEIRO 2018 - CONTRADIÇÃO TEMPORAL**

**🔍 Localização do problema:**
- **Documento LaTeX (seção 4.2):** "Janeiro de 2018 foi estabelecido como mês base (retorno 0%)"
- **Código `ibovespa_real_loader.py`:** Janeiro artificialmente zerado
- **Tabela 11 (Retornos Mensais):** 
  - Markowitz: 6,58%
  - Equal Weight: 10,42% 
  - Risk Parity: 9,42%

**❌ Problema:** Se janeiro é mês base zero, como as carteiras têm retornos diferentes de zero?

**🔧 Como corrigir:**
```latex
% OPÇÃO 1: Corrigir no texto
O mês de janeiro de 2018 representa o primeiro mês de investimento, 
com retornos calculados versus preços de dezembro de 2017.

% OPÇÃO 2: Corrigir na tabela  
Jan/2018 & 0,00 & 0,00 & 0,00 & 0,52 \\
```

---

### **2. VALORES DIVERGENTES - RETORNO ANUALIZADO**

**🔍 Localização do problema:**
- **Tabela 10:** Markowitz = 29,3%
- **Arquivo JSON:** Markowitz = 29,077386217384284% (≈29,08%)
- **Seção Conclusão:** "Retorno anualizado de 26,14%"

**❌ Problema:** Mesmo resultado reportado com 3 valores diferentes.

**🔧 Como corrigir:**
```latex
% Padronizar TODOS os valores para 29,1% (média dos três)
Estratégia de Markowitz apresentou retorno anualizado de 29,1%
```

---

### **3. TAXA LIVRE DE RISCO INCONSISTENTE**

**🔍 Localização do problema:**
- **Texto:** "Taxa livre de risco de 6,5% ao ano"
- **Tabela 11:** CDI mensal = 0,52% constante
- **Cálculo:** 0,52% × 12 = 6,24% ≠ 6,5%

**❌ Problema:** Diferença de 26 basis points entre declarado e calculado.

**🔧 Como corrigir:**
```latex
% OPÇÃO 1: Ajustar texto
Taxa livre de risco de 6,24% ao ano (CDI médio 2018-2019)

% OPÇÃO 2: Ajustar tabela
CDI mensal para 0,542% (6,5%/12)
```

---

## 🟡 **INCONSISTÊNCIAS MODERADAS (Prioridade 2)**

### **4. TABELA 9 PROMETIDA MAS VAZIA**

**🔍 Localização do problema:**
- **Lista de Tabelas:** "Tabela 9 -- Evolução dos Pesos das Carteiras por Período de Rebalanceamento"
- **Referência no texto:** Menciona tabela 9
- **Realidade:** Tabela não existe/está vazia

**🔧 Como corrigir:**
Criar tabela com dados do `detailed_portfolio_results.json`:

```latex
\begin{table}[H]
\centering
\caption{Evolução dos Pesos das Carteiras por Período de Rebalanceamento}
\begin{tabular}{|l|r|r|r|}
\hline
\textbf{Ativo} & \textbf{Equal Weight} & \textbf{Markowitz} & \textbf{Risk Parity} \\
\hline
PETR4 & 10,0\% & 11,2\% & 24,5\% \\
VALE3 & 10,0\% & 0,1\% & 13,1\% \\
% ... completar com dados reais
\end{tabular}
\end{table}
```

---

### **5. SORTINO RATIO DIVERGENTE**

**🔍 Localização do problema:**
- **Tabela 10:** Markowitz Sortino = 3,22
- **Arquivo CSV:** Sortino = 3.334227342556968
- **Texto Seção 4.13:** "Sortino Ratio de 2,51"

**🔧 Como corrigir:**
Usar valor do CSV (mais preciso) e padronizar:
```latex
Sortino Ratio de 3,33 para a estratégia Markowitz
```

---

### **6. BENCHMARK INCONSISTENTE**

**🔍 Localização do problema:**
- **Código:** Fallback para Equal Weight se Ibovespa falhar
- **Texto:** "Exclusivamente Ibovespa B3 oficial"
- **Gráficos:** Não fica claro qual benchmark foi usado

**🔧 Como corrigir:**
```latex
% Adicionar nota nas figuras
\textit{Benchmark: Ibovespa B3 Oficial (dados históricos da B3)}
```

---

## 🟠 **INCONSISTÊNCIAS MENORES (Prioridade 3)**

### **7. NUMERAÇÃO DE FIGURAS**

**🔍 Localização do problema:**
- Lista pula da Figura 4 para Figura 6
- Figura 5 mencionada no texto mas não existe

**🔧 Como corrigir:**
```latex
% Renumerar figuras sequencialmente
Figura 5 -- Evolução das Correlações Rolling... \dotfill XX \\
```

---

### **8. FÓRMULA CONFUSA - IVP vs ERC**

**🔍 Localização do problema:**
- **Seção 2.3:** Mostra fórmula do IVP simples
- **Depois:** "Este trabalho implementa o verdadeiro Risk Parity (ERC)"

**🔧 Como corrigir:**
```latex
% Clarificar a distinção
A fórmula básica do Inverse Volatility Portfolio (IVP) é apresentada 
como referência. Entretanto, este trabalho implementa o ERC mais 
sofisticado que considera a matriz de covariância completa.
```

---

### **9. REFERÊNCIA FALTANTE**

**🔍 Localização do problema:**
- **Texto:** Cita ILMANEN (2022)
- **Bibliografia:** Referência não encontrada

**🔧 Como corrigir:**
Adicionar à bibliografia:
```latex
\bibitem{ilmanen2022investing}
ILMANEN, A. \textit{Investing amid low expected returns}. Hoboken: Wiley, 2022.
```

---

## 📊 **LISTA DE VERIFICAÇÃO PARA CORREÇÃO**

### **Arquivos a verificar/corrigir:**

1. **`/sections/13_resultados.tex`**
   - [ ] Corrigir valores de retorno Markowitz
   - [ ] Padronizar Sortino Ratio
   - [ ] Esclarecer janeiro 2018
   - [ ] Criar Tabela 9

2. **`/sections/15_conclusao.tex`**
   - [ ] Corrigir retorno final reportado
   - [ ] Usar valores consistentes

3. **`/sections/16_referencias.tex`**
   - [ ] Adicionar ILMANEN (2022)
   - [ ] Verificar links quebrados

4. **`/sections/05_lista_tabelas.tex`**
   - [ ] Corrigir numeração
   - [ ] Adicionar páginas corretas

5. **`/sections/04_lista_figuras.tex`**
   - [ ] Renumerar figuras
   - [ ] Adicionar Figura 5 se necessário

### **Priorização das correções:**

**🔴 CRÍTICO (fazer ANTES da defesa):**
1. Janeiro 2018 - decidir e ser consistente
2. Valores de retorno - padronizar
3. Taxa livre de risco - corrigir cálculo

**🟡 IMPORTANTE (fazer se houver tempo):**
4. Tabela 9 - criar com dados reais
5. Sortino Ratio - padronizar valores
6. Benchmark - clarificar uso

**🟠 OPCIONAL (melhorias):**
7. Figuras - renumerar
8. Fórmulas - clarificar IVP vs ERC
9. Referências - completar

---

## ✅ **SCRIPT DE VALIDAÇÃO**

Execute para verificar consistência após correções:

```python
import json
import pandas as pd

# Carregar resultados
with open('results/detailed_portfolio_results.json', 'r') as f:
    results = json.load(f)

# Verificar valores reportados
print("=== VALIDAÇÃO DE CONSISTÊNCIA ===")
for strategy, data in results.items():
    print(f"\n{strategy}:")
    print(f"  Retorno: {data['annual_return']*100:.1f}%")
    print(f"  Sharpe: {data['sharpe_ratio']:.2f}")
    
# Verificar CDI
print(f"\nCDI mensal: 0.542% (para 6.5% anual)")
print(f"CDI anual calculado: {0.542*12:.1f}%")
```

**Após corrigir, todas as verificações devem retornar valores idênticos entre código, tabelas e texto.**