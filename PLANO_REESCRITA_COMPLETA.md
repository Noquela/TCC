# 📝 PLANO DE REESCRITA COMPLETA - TCC RISK PARITY

**Data:** 2025-09-08  
**Situação:** Sistema refatorado científico implementado - TEXTO PRECISA SER ATUALIZADO

---

## 🚨 **PROBLEMA ATUAL**

**DADOS ANTIGOS no texto** (hardcoded, não científicos) vs **DADOS NOVOS** (científicos, defensáveis)

### **COMPARAÇÃO CRÍTICA: ANTIGO vs NOVO**

| Aspecto | ANTIGO (problemático) | NOVO (científico) |
|---------|----------------------|-------------------|
| **Seleção de ativos** | Hardcoded (BDLL4, etc.) | Científica (29 analisados → 10 selecionados) |
| **Critérios** | Não documentados | Objetivos: liquidez, completude, volatilidade |
| **Diversificação** | Não controlada | 8 setores, máx 2 por setor |
| **Look-ahead bias** | Presente | ELIMINADO (seleção 2014-2017) |
| **Performance MVO** | ~42.9% | **47.5%** (com restrições) |
| **Performance EW** | ~32.3% | **33.7%** |
| **Performance ERC** | ~29.8% | **30.7%** |
| **Testes estatísticos** | Inexistentes | Jobson-Korkie implementado |
| **Significância** | Não testada | MVO > EW/ERC (p<0.05) |

---

## 📋 **PLANO SEÇÃO POR SEÇÃO**

### **SEÇÕES QUE NÃO PRECISAM MUDAR** ✅
- `01_capa.tex` - OK
- `02_folha_rosto.tex` - OK  
- `06_lista_abreviaturas.tex` - OK
- `07_lista_formulas.tex` - OK (talvez adicionar Jobson-Korkie)
- `16_referencias.tex` - OK (talvez adicionar scipy)

### **SEÇÕES COM MUDANÇAS MENORES** 🟡
- `04_lista_figuras.tex` - Atualizar nomes de figuras
- `05_lista_tabelas.tex` - Atualizar nomes de tabelas
- `08_resumo.tex` - Atualizar números-chave
- `09_abstract.tex` - Traduzir resumo atualizado

### **SEÇÕES COM MUDANÇAS MÉDIAS** 🟠
- `10_introducao.tex` - Ajustar justificativa e objetivos
- `11_referencial_teorico.tex` - Adicionar diversificação setorial

### **SEÇÕES COM MUDANÇAS GRANDES** 🔴
- `12_metodologia.tex` - **REESCREVER COMPLETA**
- `13_resultados.tex` - **REESCREVER COMPLETA**
- `14_discussao.tex` - **REESCREVER COMPLETA** 
- `15_conclusao.tex` - **REESCREVER COMPLETA**
- `17_apendice.tex` - **ATUALIZAR DADOS**

---

## 🎯 **CONTEÚDO DETALHADO POR SEÇÃO**

### **12_METODOLOGIA.TEX** 🔴
**Status:** REESCREVER COMPLETAMENTE

**Novo conteúdo deve incluir:**

#### **4.1 Base de Dados**
- ✅ **Fonte única:** Economática (não múltiplas fontes)
- ✅ **Arquivo principal:** Economatica-8900701390-20250812230945.xlsx
- ✅ **Arquivo setorial:** economatica.xlsx (mapeamento ativo-setor)
- ✅ **Período completo:** 2014-2019 (6 anos de dados)

#### **4.2 Seleção Científica de Ativos**
- ✅ **Universo inicial:** 494 ativos disponíveis (50 analisados)
- ✅ **Critérios objetivos:**
  - Completude ≥ 70%
  - Volatilidade no IQR (filtro outliers)
  - Liquidez ≥ percentil 30
  - Dados teste ≥ 20 meses
- ✅ **Diversificação setorial:** Máximo 2 ativos por setor
- ✅ **Score composto:** 40% liquidez + 30% cap + 30% completude
- ✅ **Resultado:** 10 ativos selecionados cientificamente

#### **4.3 Ativos Selecionados**
```
1. ABEV3 - Cervejas e refrigerantes (Score: 0.802)
2. ALUP11 - Energia elétrica (Score: 0.764)
3. AMER3 - Produtos diversos (Score: 0.762)
4. ALOS3 - Exploração de imóveis (Score: 0.743)
5. ABCB4 - Bancos (Score: 0.682)
6. AZZA3 - Tecidos vestuário e calçados (Score: 0.681)
7. ALPA4 - Calçados (Score: 0.660)
8. BEES3 - Serviços educacionais (Score: 0.627)
9. B3SA3 - Mercados de capitais (Score: 0.620)
10. ALPA3 - Calçados (Score: 0.604)
```

#### **4.4 Período de Análise**
- ✅ **Seleção:** 2014-2017 (in-sample, sem look-ahead bias)
- ✅ **Teste:** 2018-2019 (out-of-sample, 24 meses)
- ✅ **Taxa livre de risco:** 6.24% a.a. (CDI médio)

#### **4.5 Tratamento de Dados**
- ✅ **Frequência:** Mensal (último dia útil)
- ✅ **Missing data:** Interpolação linear → forward/backward fill → média histórica
- ✅ **Exclusão:** Ativos com >15% dados faltantes
- ✅ **Validação:** Zero NAs no dataset final

#### **4.6 Estratégias de Portfolio**
- ✅ **Equal Weight (EW):** wi = 1/n
- ✅ **Mean-Variance (MVO):** scipy.minimize com restrições 0-40%
- ✅ **Risk Parity (ERC):** Algoritmo iterativo para contribuições iguais

#### **4.7 Métricas de Avaliação**
- ✅ **Retorno anualizado:** r̄ × 12
- ✅ **Volatilidade anualizada:** σ × √12  
- ✅ **Sharpe Ratio:** (r̄ - rf) / σ
- ✅ **Sortino Ratio:** (r̄ - rf) / σ_downside
- ✅ **Maximum Drawdown:** máxima perda acumulada
- ✅ **Teste Jobson-Korkie:** Significância diferenças Sharpe

### **13_RESULTADOS.TEX** 🔴
**Status:** REESCREVER COMPLETAMENTE

**Novo conteúdo deve incluir:**

#### **5.1 Seleção de Ativos**
- **Tabela 1:** Ativos selecionados por critérios científicos (usar LaTeX gerado)
- **Figura 1:** Distribuição setorial dos ativos selecionados
- **Análise:** Diversificação alcançada (8 setores diferentes)

#### **5.2 Estatísticas Descritivas (2018-2019)**
- **Tabela 2:** Estatísticas individuais dos ativos
- **Melhor Sharpe:** AMER3 (1.48)
- **Maior retorno:** AMER3 (65.7% a.a.)
- **Menor volatilidade:** ALUP11 (20.3% a.a.)

#### **5.3 Performance das Estratégias**
- **Tabela 3:** Comparação performance (usar LaTeX gerado)

```
| Estratégia | Retorno | Volatilidade | Sharpe | Sortino | Max DD |
|------------|---------|-------------|--------|---------|--------|
| EW         | 33.7%   | 20.9%       | 1.31   | 1.46    | -18.0% |
| MVO        | 47.5%   | 21.8%       | 1.89   | 2.61    | -12.7% |
| ERC        | 30.7%   | 19.6%       | 1.25   | 1.30    | -17.6% |
```

#### **5.4 Alocação de Pesos**
- **Tabela 4:** Pesos por estratégia (usar LaTeX gerado)
- **Análise:** MVO concentrou em AMER3 e ABEV3 (respeitando limite 40%)

#### **5.5 Análise de Significância Estatística**
- **Teste Jobson-Korkie:**
  - **MVO vs EW:** p-value = 0.040 → **SIGNIFICANTE**
  - **MVO vs ERC:** p-value = 0.039 → **SIGNIFICANTE**  
  - **EW vs ERC:** p-value = 0.363 → **NÃO SIGNIFICANTE**

#### **5.6 Robustez dos Resultados**
- **Validações realizadas:**
  - Sem look-ahead bias
  - Período out-of-sample
  - Diversificação setorial controlada
  - Restrições realistas (0-40%)

### **14_DISCUSSAO.TEX** 🔴
**Status:** REESCREVER COMPLETAMENTE

#### **6.1 Interpretação dos Resultados**
- **MVO superiority:** Estatisticamente comprovada
- **Risk Parity behavior:** Menor volatilidade conforme esperado  
- **Equal Weight baseline:** Performance intermediária

#### **6.2 Comparação com Literatura**
- **Sharpe Ratios:** Todos > 1.0 (excelente para mercado brasileiro)
- **MVO vs ERC:** Resultados consistentes com DeMiguel et al. em alguns contextos

#### **6.3 Limitações do Estudo**
- **Período:** 2 anos out-of-sample (relativamente curto)
- **Ativos:** 10 ativos (amostra moderada)
- **Custos transação:** Não considerados

#### **6.4 Contribuições**
- **Metodologia científica:** Eliminação de biases
- **Diversificação setorial:** Controle de concentração
- **Testes estatísticos:** Significância das diferenças

### **15_CONCLUSAO.TEX** 🔴
**Status:** REESCREVER COMPLETAMENTE

#### **7.1 Síntese dos Resultados**
- **Hipótese confirmada:** MVO superiority com significância estatística
- **Metodologia robusta:** Sistema cientificamente defensável implementado

#### **7.2 Implicações Práticas**
- **Gestão de recursos:** MVO com restrições mostra melhor risco-retorno
- **Diversificação:** Importante controlar concentração setorial

#### **7.3 Sugestões Futuras**
- **Período mais longo:** Análise multi-décadas  
- **Mais ativos:** Expansão para small caps
- **Custos transação:** Incorporação na otimização
- **Regimes:** Análise em diferentes ciclos econômicos

---

## ⚡ **CRONOGRAMA DE EXECUÇÃO**

### **FASE 1: SEÇÕES CRÍTICAS** (Prioridade 1)
1. `12_metodologia.tex` - **2h**
2. `13_resultados.tex` - **2h** 
3. `14_discussao.tex` - **1h**
4. `15_conclusao.tex` - **1h**

### **FASE 2: AJUSTES MENORES** (Prioridade 2)
1. `08_resumo.tex` - **30min**
2. `09_abstract.tex` - **30min**
3. `04_lista_figuras.tex` - **15min**
4. `05_lista_tabelas.tex` - **15min**

### **FASE 3: FINALIZAÇÕES** (Prioridade 3)  
1. `10_introducao.tex` - **30min**
2. `17_apendice.tex` - **30min**

**TOTAL ESTIMADO: 8 horas de trabalho focado**

---

## 🎯 **READY TO START?**

Este plano garante:
- ✅ **Metodologia científica** documentada
- ✅ **Dados novos** em todas as seções
- ✅ **Resultados defensáveis** na banca
- ✅ **Eliminação completa** dos dados antigos
- ✅ **Sistema acadêmico robusto**

**Podemos começar pela METODOLOGIA?**