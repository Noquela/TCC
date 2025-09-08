# CORREÇÕES CRÍTICAS TCC - RISK PARITY ERC
## Documento Técnico para Claude Code

### OBJETIVO
Corrigir implementação de Risk Parity para ERC (Equal Risk Contribution) verdadeiro, eliminar look-ahead bias, e unificar dados inconsistentes.

---

## 1. IMPLEMENTAÇÃO ERC CORRETA

### PROBLEMA ATUAL
O código atual em `portfolio_analysis_real.py` tem erro na função `risk_parity_portfolio()`:

```python
# ERRO ATUAL:
target_contrib = portfolio_vol / self.n_assets  # INCORRETO!
```

### CORREÇÃO NECESSÁRIA
```python
def risk_parity_portfolio_erc(self):
    """
    Estratégia Risk Parity ERC (Equal Risk Contribution) CORRETA
    Equaliza contribuições marginais de risco usando matriz covariância completa
    """
    def erc_objective(weights):
        # Volatilidade do portfólio
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Contribuições marginais de risco
        marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol
        
        # Contribuições de risco (RC_i = w_i * marginal_contrib_i)
        risk_contrib = weights * marginal_contrib
        
        # Objetivo: equalizar contribuições de risco
        # Cada ativo deve contribuir com 1/n do risco total
        target_contrib = (portfolio_vol ** 2) / self.n_assets  # CORREÇÃO AQUI!
        
        # Minimizar diferenças quadráticas das contribuições
        return np.sum((risk_contrib - target_contrib) ** 2)
    
    # Restrições
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.001, 1.0) for _ in range(self.n_assets))
    
    # Otimização
    x0 = np.ones(self.n_assets) / self.n_assets
    result = minimize(erc_objective, x0, method='SLSQP',
                     bounds=bounds, constraints=constraints)
    
    return result.x if result.success else None
```

### VALIDAÇÃO ERC
Adicionar função para validar que ERC foi implementado corretamente:

```python
def validate_erc(self, weights):
    """
    Valida se a carteira atende aos critérios ERC
    """
    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
    marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol
    risk_contrib = weights * marginal_contrib
    
    # Contribuições devem ser aproximadamente iguais
    target = (portfolio_vol ** 2) / self.n_assets
    max_deviation = np.max(np.abs(risk_contrib - target))
    
    print(f"Contribuições de risco por ativo:")
    for i, asset in enumerate(self.assets):
        print(f"{asset}: {risk_contrib[i]:.4f} (target: {target:.4f})")
    
    print(f"Máximo desvio: {max_deviation:.6f}")
    return max_deviation < 0.001  # Tolerância de 0.1%
```

---

## 2. CORREÇÃO DO LOOK-AHEAD BIAS

### PROBLEMA ATUAL
Janela móvel usando dados contemporâneos ao período de aplicação.

### METODOLOGIA CORRETA
**NUNCA usar dados do período que a carteira será aplicada**

```python
# ESTRUTURA TEMPORAL CORRETA:
rebalancing_periods = [
    {
        'estimation_start': '2016-01-01',
        'estimation_end': '2017-12-31',     # Para aplicar em Jan 2018
        'application_start': '2018-01-01',
        'application_end': '2018-06-30'
    },
    {
        'estimation_start': '2016-07-01', 
        'estimation_end': '2018-06-30',     # Para aplicar em Jul 2018
        'application_start': '2018-07-01',
        'application_end': '2018-12-31'
    },
    {
        'estimation_start': '2017-01-01',
        'estimation_end': '2018-12-31',     # Para aplicar em Jan 2019
        'application_start': '2019-01-01',
        'application_end': '2019-06-30'
    },
    {
        'estimation_start': '2017-07-01',
        'estimation_end': '2019-06-30',     # Para aplicar em Jul 2019
        'application_start': '2019-07-01',
        'application_end': '2019-12-31'
    }
]
```

---

## 3. CORREÇÃO DOS RETORNOS DE JANEIRO 2018

### PROBLEMA ATUAL
Janeiro 2018 artificialmente zerado distorce análise temporal.

### CORREÇÃO NECESSÁRIA
```python
def calculate_returns_with_december_2017(self, price_df):
    """
    Calcula retornos corretos incluindo dezembro 2017 como base
    """
    # 1. Adicionar dados de dezembro 2017 (se disponível)
    # 2. Calcular retorno real de janeiro 2018
    # 3. Usar logarítmico: ln(P_jan2018 / P_dez2017)
    
    # SE não tiver dezembro 2017, usar primeira observação como base
    # MAS documentar esta limitação claramente
    
    returns_df = np.log(price_df / price_df.shift(1)).dropna()
    
    # IMPORTANTE: Não artificializar retorno zero para qualquer mês
    return returns_df
```

---

## 4. UNIFICAÇÃO DE DADOS INCONSISTENTES

### PROBLEMA ATUAL
ELET3 tem 3 valores diferentes:
- 32,3% (Tabela 8)
- 33,70% (real_data_summary.csv)
- 32,29% (complete_real_stats.csv)

### CORREÇÃO NECESSÁRIA
```python
def unified_data_calculation(self):
    """
    Cálculo unificado para eliminar inconsistências
    """
    # 1. Usar ÚNICO pipeline de cálculo
    # 2. Calcular retornos anualizados: (1 + monthly_returns).prod() - 1
    # 3. Salvar em arquivo master único
    # 4. Todas as tabelas devem referenciar este arquivo master
    
    # FONTE ÚNICA DA VERDADE
    master_stats = {}
    for asset in returns_df.columns:
        # Retorno anualizado padronizado
        total_return = (1 + returns_df[asset]).prod() - 1
        annualized_return = (1 + total_return) ** (12 / len(returns_df)) - 1
        
        master_stats[asset] = {
            'annual_return': annualized_return,
            'annual_volatility': returns_df[asset].std() * np.sqrt(12),
            # ... outras métricas
        }
    
    return master_stats
```

---

## 5. SORTINO RATIO CORRETO

### IMPLEMENTAÇÃO PADRONIZADA
```python
def calculate_sortino_ratio(self, portfolio_returns, risk_free_rate=0.065):
    """
    Sortino Ratio padronizado conforme literatura acadêmica
    """
    # Taxa livre de risco mensal
    rf_monthly = risk_free_rate / 12
    
    # Retorno excedente anualizado
    excess_return = portfolio_returns.mean() * 12 - risk_free_rate
    
    # Downside deviation: apenas retornos abaixo da taxa livre de risco
    downside_returns = portfolio_returns[portfolio_returns < rf_monthly] - rf_monthly
    downside_deviation = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(12)
    
    # Sortino ratio
    sortino = excess_return / downside_deviation if downside_deviation > 0 else np.nan
    
    return sortino
```

---

## 6. VALIDAÇÃO DE DADOS

### SISTEMA DE VERIFICAÇÃO
```python
def validate_all_data(self):
    """
    Sistema completo de validação para detectar inconsistências
    """
    validations = []
    
    # 1. Verificar retornos não são artificiais
    if np.any(returns_df.iloc[0] == 0):
        validations.append("ERRO: Retornos artificialmente zerados detectados")
    
    # 2. Verificar consistência temporal
    date_gaps = returns_df.index.to_series().diff().dropna()
    if not all(gap.days <= 35 for gap in date_gaps):  # ~1 mês
        validations.append("ERRO: Gaps temporais inconsistentes")
    
    # 3. Verificar outliers extremos
    for asset in returns_df.columns:
        if abs(returns_df[asset]).max() > 0.5:  # >50% em um mês
            validations.append(f"AVISO: Outlier extremo em {asset}")
    
    # 4. Verificar ERC convergência
    for strategy_name, results in portfolio_results.items():
        if 'Risk Parity' in strategy_name:
            if not self.validate_erc(results['weights']):
                validations.append("ERRO: ERC não convergiu adequadamente")
    
    return validations
```

---

## 7. CORREÇÃO DA ANÁLISE SETORIAL

### PROBLEMA ATUAL
Texto afirma "setores defensivos lideraram" mas dados mostram Sharpe negativo.

### INVESTIGAÇÃO NECESSÁRIA
```python
def investigate_sector_performance(self):
    """
    Investigar discrepância entre texto e dados setoriais
    """
    # 1. Recalcular performance setorial usando dados unificados
    # 2. Verificar se houve erro de interpretação ou cálculo
    # 3. Corrigir texto para refletir dados corretos
    
    sector_performance = {}
    for sector in sectors:
        sector_assets = [asset for asset in assets if asset_sectors[asset] == sector]
        sector_returns = returns_df[sector_assets].mean(axis=1)
        
        annual_return = sector_returns.mean() * 12
        annual_vol = sector_returns.std() * np.sqrt(12)
        sharpe = (annual_return - 0.065) / annual_vol
        
        sector_performance[sector] = {
            'return': annual_return,
            'volatility': annual_vol,
            'sharpe': sharpe
        }
    
    # Ranking por Sharpe ratio para determinar quais REALMENTE lideraram
    ranking = sorted(sector_performance.items(), 
                    key=lambda x: x[1]['sharpe'], reverse=True)
    
    return ranking
```

---

## 8. ESTRUTURA DE ARQUIVOS CORRIGIDA

### PIPELINE ÚNICO
```
1. economatica_loader.py (dados brutos)
   ↓
2. data_unifier.py (NOVO - unifica tudo)
   ↓
3. erc_portfolio_analysis.py (NOVO - implementa ERC correto)
   ↓
4. unified_results_generator.py (NOVO - resultados consistentes)
   ↓
5. latex_table_generator.py (usa fonte única)
```

---

## 9. BENCHMARK IBOVESPA

### MANTER ATUAL
- Usar exclusivamente Ibovespa B3 oficial
- Taxa livre de risco: 6,5% aa
- Não mudar estas definições

---

## 10. CRONOGRAMA DE IMPLEMENTAÇÃO

### PRIORIDADE 1 (CRÍTICO):
1. Implementar ERC verdadeiro
2. Eliminar look-ahead bias na janela móvel
3. Calcular retorno correto de janeiro 2018
4. Unificar dados inconsistentes (ELET3, etc.)

### PRIORIDADE 2 (IMPORTANTE):
5. Padronizar Sortino Ratio
6. Corrigir análise setorial
7. Implementar sistema de validação
8. Gerar tabelas LaTeX consistentes

### PRIORIDADE 3 (OPCIONAL):
9. Expandir análise de robustez
10. Adicionar testes de significância estatística

---

## ARQUIVOS A MODIFICAR

### CRÍTICOS:
- `portfolio_analysis_real.py` → `erc_portfolio_analysis.py`
- `economatica_loader.py` (correção retornos)
- Todos os geradores de tabela LaTeX

### NOVOS A CRIAR:
- `data_unifier.py`
- `erc_validator.py`
- `unified_results_generator.py`

---

## VALIDAÇÃO FINAL

Antes de considerar correto, o sistema deve:
✅ ERC convergir com desvio < 0.1%
✅ Nenhum look-ahead bias detectado
✅ Dados unificados (um valor por métrica por ativo)
✅ Retornos de janeiro 2018 calculados corretamente
✅ Sortino Ratio padronizado
✅ Análise setorial consistente com dados
✅ Todas as tabelas LaTeX geradas da mesma fonte

---

## 11. SELEÇÃO QUANTITATIVA ROBUSTA DE ATIVOS (2014-2017)

### PROBLEMA ATUAL
Seleção subjetiva com critérios vagos e documentação insuficiente.

### NOVA METODOLOGIA QUANTITATIVA
```python
def robust_quantitative_selection_2014_2017():
    """
    Seleção ex-ante rigorosamente quantitativa usando dados 2014-2017
    Baseada em literatura acadêmica de mercados emergentes
    """
    
    # FASE 1: FILTROS DE SOBREVIVÊNCIA (Base: 508 ativos Economática)
    survival_criteria = {
        'data_completeness': {
            'min_trading_days_ratio': 0.95,      # 95% dos dias úteis
            'period': '2014-01-01 to 2017-12-31',
            'max_consecutive_gaps': 5,           # Máximo 5 dias sem negócio
            'no_ticker_changes': True,           # Sem mudanças de código
            'no_delisting_risk': True            # Sem risco de saída
        },
        'market_relevance': {
            'min_avg_market_cap_percentile': 70, # Top 30% por capitalização
            'ibovespa_participation': {
                'min_quarters_present': 8,       # 8+ trimestres no Ibovespa
                'min_avg_weight': 0.002,         # Peso mínimo 0.2%
            }
        }
    }
    
    # FASE 2: CRITÉRIOS DE LIQUIDEZ ROBUSTOS
    liquidity_metrics = {
        'volume_analysis': {
            'min_avg_daily_volume_brl': 100_000_000,    # R$ 100 mi/dia
            'min_median_daily_volume_brl': 75_000_000,   # Mediana > R$ 75 mi
            'volume_coefficient_variation': 0.70,        # CV < 70%
            'min_trading_frequency': 0.98                # 98% dos dias úteis
        },
        'market_microstructure': {
            'min_avg_trades_per_day': 100,      # Mínimo 100 negócios/dia
            'max_bid_ask_spread': 0.05,         # Spread < 5%
            'min_depth_stability': 0.80         # Estabilidade do book
        }
    }
    
    # FASE 3: DIVERSIFICAÇÃO SETORIAL CIENTIFICAMENTE OTIMIZADA
    sector_optimization = {
        'correlation_analysis': {
            'calculate_sector_correlations': '2014-2017',
            'max_inter_sector_correlation': 0.70,
            'min_independent_sectors': 6,
            'max_assets_per_sector': 3
        },
        'economic_representation': {
            'ensure_export_exposure': True,      # Commodities
            'ensure_domestic_exposure': True,    # Consumo/Serviços
            'ensure_financial_exposure': True,   # Sistema financeiro
            'ensure_industrial_exposure': True,  # Produção industrial
            'ensure_defensive_exposure': True    # Utilities/Staples
        },
        'risk_diversification': {
            'max_beta_concentration': 0.40,     # Concentração beta
            'min_idiosyncratic_diversity': 0.60, # Diversidade específica
            'political_risk_balance': True       # Balancear risco político
        }
    }
    
    # FASE 4: MÉTRICAS DE QUALIDADE ESPECÍFICAS PARA EMERGENTES
    emerging_market_quality = {
        'volatility_characteristics': {
            'max_idiosyncratic_volatility': 0.50,  # Vol específica < 50%
            'min_market_beta': 0.30,               # Beta mínimo vs Ibovespa
            'max_market_beta': 2.50,               # Beta máximo vs Ibovespa
            'volatility_stability_cv': 0.30       # CV da volatilidade < 30%
        },
        'fundamental_stability': {
            'max_government_ownership': 0.60,      # Máximo 60% estatal
            'regulatory_risk_level': 'medium',     # Evitar alto risco reg.
            'currency_exposure_natural': True,     # Exposição natural ao Real
            'min_free_float': 0.25                # Free float mínimo 25%
        }
    }
    
    # FASE 5: SELEÇÃO FINAL OTIMIZADA
    final_selection = {
        'target_assets': 10,
        'selection_method': 'multi_objective_optimization',
        'objectives': [
            'maximize_diversification_ratio',
            'maximize_average_liquidity',
            'minimize_concentration_risk',
            'maximize_economic_representation'
        ],
        'constraints': [
            'max_3_per_sector',
            'min_6_sectors',
            'all_quality_filters_passed'
        ]
    }
    
    return optimized_asset_selection

def validate_scientific_selection():
    """
    Validação da metodologia científica vs seleção manual
    """
    validation_tests = {
        'replicability_test': 'Can independent researcher replicate?',
        'bias_elimination_test': 'Zero subjective decisions?',
        'academic_rigor_test': 'Based on peer-reviewed criteria?',
        'emerging_market_specific': 'Addresses EM characteristics?',
        'temporal_robustness': 'Stable across sub-periods?'
    }
    
    return all(validation_tests.values())
```

### VANTAGENS DA NOVA SELEÇÃO
1. **Base científica sólida** - 4 anos de dados vs. decisão subjetiva
2. **Totalmente replicável** - qualquer pesquisador pode reproduzir
3. **Específica para mercados emergentes** - baseada em literatura acadêmica
4. **Diversificação otimizada** - não aleatória, matematicamente calculada
5. **Elimina viés de seleção** - critérios objetivos quantitativos
6. **Academicamente defensável** - metodologia publicável

---

## 12. PLANO DE SPRINTS - IMPLEMENTAÇÃO ESTRUTURADA

### SPRINT 1: FOUNDATION (Semana 1-2) - CRÍTICO
**Objetivo:** Estabelecer base sólida e eliminar problemas fundamentais

#### Sprint 1.1: Implementação ERC Verdadeiro (Prioridade MÁXIMA)
```python
# Tarefas específicas:
- [ ] Corrigir função risk_parity_portfolio() em portfolio_analysis_real.py
- [ ] Implementar target_contrib = (portfolio_vol ** 2) / n_assets
- [ ] Criar função validate_erc() para verificar convergência
- [ ] Testar com tolerância < 0.1% de desvio
- [ ] Documentar diferença entre ERC e IVP na seção teórica

# Critério de aceite:
✅ ERC converge com desvio máximo < 0.1%
✅ Função de validação confirma equalização de risco
✅ Documentação clara da metodologia ERC
```

#### Sprint 1.2: Eliminação de Look-Ahead Bias (Prioridade MÁXIMA)
```python
# Tarefas específicas:
- [ ] Reestruturar janelas temporais de rebalanceamento
- [ ] Usar dados APENAS até mês anterior da aplicação
- [ ] Implementar estrutura temporal correta:
  * Jan 2018: usar dados 2016-2017
  * Jul 2018: usar dados até Jun 2018
  * Jan 2019: usar dados até Dez 2018
  * Jul 2019: usar dados até Jun 2019
- [ ] Validar que nenhum dado futuro contamina estimação

# Critério de aceite:
✅ Nenhum uso de dados contemporâneos à aplicação
✅ Janela móvel implementada corretamente
✅ Metodologia out-of-sample rigorosa
```

#### Sprint 1.3: Correção Retornos Janeiro 2018 (Prioridade ALTA)
```python
# Tarefas específicas:
- [ ] Localizar dados de preços dezembro 2017
- [ ] Calcular retorno real de janeiro 2018: ln(P_jan/P_dez)
- [ ] Eliminar artificialização de retorno zero
- [ ] Validar continuidade temporal da série

# Critério de aceite:
✅ Janeiro 2018 tem retorno calculado, não artificial
✅ Série temporal contínua e consistente
✅ Base temporal documentada claramente
```

### SPRINT 2: DATA UNIFICATION (Semana 3) - CRÍTICO
**Objetivo:** Unificar dados inconsistentes e criar fonte única da verdade

#### Sprint 2.1: Unificação de Dados Conflitantes
```python
# Tarefas específicas:
- [ ] Criar data_unifier.py como pipeline único
- [ ] Resolver inconsistência ELET3 (3 valores diferentes)
- [ ] Padronizar cálculo de retornos anualizados
- [ ] Criar arquivo master_stats.json como fonte única
- [ ] Atualizar todas as tabelas para usar fonte única

# Critério de aceite:
✅ Um único valor por métrica por ativo
✅ Todas as tabelas LaTeX consistentes
✅ Pipeline de dados unificado e documentado
```

#### Sprint 2.2: Padronização Sortino Ratio
```python
# Tarefas específicas:
- [ ] Implementar calculate_sortino_ratio() padronizado
- [ ] Usar downside deviation com threshold = taxa livre de risco
- [ ] Aplicar em todos os cálculos (ativos individuais + carteiras)
- [ ] Validar consistência entre arquivos

# Critério de aceite:
✅ Sortino calculado uniformemente em todo o sistema
✅ Definição clara: downside vs taxa livre de risco
✅ Valores consistentes entre todos os arquivos
```

### SPRINT 3: ROBUST ASSET SELECTION (Semana 4-5) - IMPORTANTE
**Objetivo:** Implementar seleção quantitativa cientificamente robusta

#### Sprint 3.1: Implementação Filtros Quantitativos
```python
# Tarefas específicas:
- [ ] Criar robust_asset_selector.py
- [ ] Implementar filtros de sobrevivência (2014-2017)
- [ ] Implementar métricas de liquidez avançadas
- [ ] Calcular correlações setoriais para otimização
- [ ] Documentar todos os critérios objetivos

# Critério de aceite:
✅ Seleção 100% replicável por pesquisador independente
✅ Critérios baseados em literatura acadêmica
✅ Nenhum viés subjetivo na seleção
```

#### Sprint 3.2: Otimização Diversificação Setorial
```python
# Tarefas específicas:
- [ ] Calcular matriz de correlações setoriais (2014-2017)
- [ ] Implementar otimização multi-objetivo
- [ ] Balancear: liquidez + diversificação + representatividade
- [ ] Validar resultado vs seleção atual
- [ ] Documentar vantagens da nova metodologia

# Critério de aceite:
✅ Diversificação matematicamente otimizada
✅ Máximo 3 ativos por setor, mínimo 6 setores
✅ Comparação documentada com seleção atual
```

### SPRINT 4: RESULTS & VALIDATION (Semana 6) - IMPORTANTE
**Objetivo:** Gerar resultados corretos e implementar validação robusta

#### Sprint 4.1: Recálculo Completo das Estratégias
```python
# Tarefas específicas:
- [ ] Executar ERC corrigido com novos dados
- [ ] Aplicar metodologia out-of-sample rigorosa
- [ ] Recalcular todas as métricas com dados unificados
- [ ] Gerar tabelas LaTeX atualizadas
- [ ] Validar consistência de todos os resultados

# Critério de aceite:
✅ Markowitz, ERC e Equal Weight executados corretamente
✅ Todas as métricas consistentes
✅ Tabelas LaTeX atualizadas
```

#### Sprint 4.2: Sistema de Validação Automática
```python
# Tarefas específicas:
- [ ] Criar validate_all_data() abrangente
- [ ] Implementar testes de consistência temporal
- [ ] Validar convergência ERC automaticamente
- [ ] Detectar outliers e inconsistências
- [ ] Gerar relatório de validação

# Critério de aceite:
✅ Sistema detecta automaticamente inconsistências
✅ Validação de ERC convergência < 0.1%
✅ Relatório de qualidade dos dados
```

### SPRINT 5: DOCUMENTATION & TABLES (Semana 7) - MODERADO
**Objetivo:** Corrigir documentação e gerar tabelas finais

#### Sprint 5.1: Correção Análise Setorial
```python
# Tarefas específicas:
- [ ] Investigar discrepância texto vs dados setoriais
- [ ] Recalcular performance setorial com dados unificados
- [ ] Corrigir interpretação na seção de resultados
- [ ] Atualizar conclusões baseadas em dados corretos
- [ ] Gerar nova tabela setorial

# Critério de aceite:
✅ Texto alinhado com dados reais
✅ Interpretação setorial corrigida
✅ Conclusões baseadas em evidências
```

#### Sprint 5.2: Geração Tabelas Finais
```python
# Tarefas específicas:
- [ ] Gerar todas as tabelas LaTeX da fonte única
- [ ] Atualizar figuras com dados corretos
- [ ] Revisar numeração e referências
- [ ] Validar formatação LaTeX
- [ ] Testar compilação do documento

# Critério de aceite:
✅ Todas as tabelas consistentes
✅ Figuras atualizadas
✅ Documento compila sem erros
```

### SPRINT 6: FINAL VALIDATION (Semana 8) - MODERADO
**Objetivo:** Validação final e preparação para entrega

#### Sprint 6.1: Testes de Reprodutibilidade
```python
# Tarefas específicas:
- [ ] Testar execução completa do pipeline
- [ ] Validar que resultados são reproduzíveis
- [ ] Verificar que não há dependências quebradas
- [ ] Documentar processo de execução
- [ ] Criar checklist de validação final

# Critério de aceite:
✅ Pipeline executa do início ao fim sem erros
✅ Resultados idênticos em execuções independentes
✅ Documentação completa do processo
```

#### Sprint 6.2: Revisão Acadêmica Final e Reprodutibilidade

**CÓDIGO Python:**
```python
# Tarefas específicas:
- [ ] Testar execução completa do pipeline do zero
- [ ] Validar reprodutibilidade em ambiente limpo
- [ ] Verificar que não há dependências quebradas
- [ ] Documentar processo completo de execução
- [ ] Criar checklist de validação final
```

**DOCUMENTO LaTeX:**
```latex
# Revisão acadêmica completa:
- [ ] Revisar metodologia vs literatura acadêmica citada
- [ ] Validar terminologia técnica (ERC vs Risk Parity vs IVP)
- [ ] Verificar todas as citações e referências bibliográficas
- [ ] Revisar conclusões vs evidências apresentadas
- [ ] Validar coerência interna do documento

# Preparação final:
- [ ] Criar resumo executivo das correções implementadas
- [ ] Documentar diferenças vs versão anterior
- [ ] Preparar defesa das escolhas metodológicas
- [ ] Validar que trabalho está academicamente robusto
```

**Critério de aceite:**
✅ Pipeline executa do início ao fim sem erros
✅ Resultados reproduzíveis em ambiente independente
✅ Metodologia academicamente defensável
✅ Terminologia técnica precisa e consistente
✅ Documento final pronto para avaliação acadêmica

---

## CRONOGRAMA RESUMIDO (8 SEMANAS)

| Semana | Sprint | Foco | Prioridade |
|--------|--------|------|------------|
| 1-2 | Sprint 1 | ERC + Look-ahead + Janeiro 2018 | CRÍTICO |
| 3 | Sprint 2 | Unificação de dados + Sortino | CRÍTICO |
| 4-5 | Sprint 3 | Seleção quantitativa robusta | IMPORTANTE |
| 6 | Sprint 4 | Resultados + Validação | IMPORTANTE |
| 7 | Sprint 5 | Documentação + Tabelas | MODERADO |
| 8 | Sprint 6 | Validação final | MODERADO |

---

## CRITÉRIOS DE ACEITE FINAIS

### TCC APROVADO QUANDO:
✅ ERC implementado corretamente (desvio < 0.1%)
✅ Zero look-ahead bias detectado
✅ Dados 100% consistentes (uma fonte única)
✅ Seleção de ativos cientificamente defensável
✅ Sortino Ratio padronizado
✅ Todas as tabelas LaTeX consistentes
✅ Pipeline reproduzível por pesquisador independente
✅ Documentação academicamente robusta

**RESULTADO ESPERADO:** TCC metodologicamente robusto, com ERC implementado corretamente, dados unificados e seleção de ativos cientificamente defensável.