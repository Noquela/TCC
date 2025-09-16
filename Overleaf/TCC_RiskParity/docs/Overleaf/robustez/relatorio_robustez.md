
# RELATÓRIO DAS ANÁLISES DE ROBUSTEZ
**Gerado em:** 09/09/2025 às 14:43

## Interpretações para inserir no TCC

### 2.1 Custos de Transação*"Sob custos de 25 bps por rebalance, Equal Risk Contribution mantém vantagem relativa (Sharpe 0.500), sugerindo **resiliência a custos**. Em 50 bps, o ranking se altera, indicando que Mean-Variance é **sensível** à execução."*

### 2.2 Covariância com Shrinkage  
*"Com shrinkage (intensidade: 0.305), o portfólio MVO reduz concentração de 0.185 para 0.134, mantendo performance. Isso **mitiga risco de overfitting** de covariâncias amostrais."*

### 2.3 Bootstrap e Intervalos de Confiança
*"O bootstrap (2.000 iterações) confirma robustez estatística. ICs que não cruzam zero sustentam **diferenças significativas** entre estratégias, reforçando achados principais."*

### 2.4 Sensibilidade de Seleção
*"A remoção de BBDC4 (menor score) **não altera** o ranking de estratégias, sugerindo robustez do achado principal à composição do universo."*

## Quadro Resumo de Robustez

| Teste | Resultado | Interpretação |
|-------|-----------|---------------|
| Custos 25bps | Ranking mantido | ✓ Resiliência moderada |
| Custos 50bps | Alteração ranking | ⚠ Sensibilidade alta |
| Shrinkage | Performance preservada | ✓ Reduz overfitting |
| Bootstrap | ICs não cruzam zero | ✓ Significância confirmada |
| Sensibilidade | Ranking estável | ✓ Robustez de universo |

## Como usar no TCC

### Nova subseção "Análises de Robustez"
1. Inserir após seção de Resultados principais
2. Incluir os 4 testes com 1 parágrafo cada
3. Adicionar quadro resumo de robustez
4. Discutir implicações para implementação

### Texto-modelo para cada teste:
- **Custos**: "Simulações com custos de X bps mostram que..."  
- **Shrinkage**: "Regularização de covariância via Ledoit-Wolf preserva..."
- **Bootstrap**: "Intervalos de confiança de 95% confirmam..."
- **Sensibilidade**: "Alteração no universo de ativos não afeta..."

## Próximos Passos
1. Inserir gráficos na seção de Robustez
2. Adicionar tabela resumo de todos os testes
3. Conectar com conclusões sobre implementabilidade
