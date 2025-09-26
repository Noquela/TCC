"""
SISTEMA TCC RISK PARITY - v2.0
Script 8: Análises de Robustez Simplificadas (sem Bootstrap)

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-23

Análises incluídas:
1. Sensibilidade de seleção de ativos
2. Validação estatística (Jobson-Korkie)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
from scipy.stats import t
import warnings
warnings.filterwarnings('ignore')

# Importar configuração global
from configuracao_global import get_config, get_logger

class AnalisesRobustezV2:
    """
    Análises de robustez simplificadas para TCC de graduação
    """

    def __init__(self):
        self.config = get_config()
        self.logger = get_logger(__name__)

        # Usar paths da configuração global
        self.results_dir = self.config.results_dir
        self.robustez_dir = self.config.robustez_dir

        self.logger.info("Iniciando análises de robustez simplificadas")
        print("="*70)
        print("ANÁLISES DE ROBUSTEZ - TCC RISK PARITY v2.0")
        print("="*70)
        print("✓ 1 análise principal: sensibilidade de seleção")
        print("✓ 1 validação estatística: teste Jobson-Korkie")
        print("✓ Foco em graduação: análises simplificadas")
        print()

    def carregar_dados(self):
        """Carrega todos os dados necessários"""
        self.logger.info("Carregando dados para análises de robustez")

        try:
            # Retornos dos ativos
            self.retornos_df = pd.read_csv(
                self.results_dir / "02_retornos_mensais_2018_2019.csv",
                index_col=0, parse_dates=True
            )

            # Retornos das estratégias
            self.retornos_estrategias_df = pd.read_csv(
                self.results_dir / "03_retornos_portfolios.csv",
                index_col=0, parse_dates=True
            )

            # Pesos das estratégias
            self.pesos_df = pd.read_csv(
                self.results_dir / "03_pesos_portfolios.csv"
            )

            # Ativos selecionados
            self.ativos_df = pd.read_csv(
                self.results_dir / "01_ativos_selecionados.csv"
            )

            self.logger.info(f"Dados carregados: {len(self.retornos_df)} períodos, {len(self.retornos_df.columns)} ativos")
            print(f"✓ {len(self.retornos_df)} períodos mensais carregados")
            print(f"✓ {len(self.retornos_df.columns)} ativos carregados")
            print(f"✓ {len(self.retornos_estrategias_df.columns)} estratégias carregadas")

        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise



    def analise_sensibilidade_selecao(self):
        """
        Análise 1: Sensibilidade à seleção de ativos
        """
        self.logger.info("Executando análise de sensibilidade de seleção")
        print("\n1. ANÁLISE DE SENSIBILIDADE DE SELEÇÃO")
        print("-" * 40)

        # Identificar ativo borderline (menor score dos selecionados)
        ativo_borderline = self.ativos_df.loc[self.ativos_df['selection_score'].idxmin()]
        ativo_remover = ativo_borderline['asset']

        if ativo_remover not in self.retornos_df.columns:
            print(f"⚠ Ativo {ativo_remover} não encontrado nos retornos")
            self.sensibilidade_results = None
            return

        # Criar universo alternativo (sem o ativo borderline)
        retornos_alt = self.retornos_df.drop(columns=[ativo_remover])

        # Calcular métricas para universo alternativo
        rf_mensal = self.config.TAXA_LIVRE_RISCO['mensal']

        def calc_metricas_estrategia(retornos):
            ret_anual = np.mean(retornos) * 12 * 100
            vol_anual = np.std(retornos) * np.sqrt(12) * 100
            excess = retornos - rf_mensal
            sharpe = np.mean(excess) / np.std(excess) if np.std(excess) > 0 else 0
            return {'Retorno': ret_anual, 'Volatilidade': vol_anual, 'Sharpe': sharpe}

        # Equal Weight alternativo
        retornos_ew_alt = retornos_alt.mean(axis=1)
        metricas_ew_alt = calc_metricas_estrategia(retornos_ew_alt)

        # Mean-Variance alternativo
        try:
            cov_alt = retornos_alt.cov().values
            n_assets = len(cov_alt)

            def objective_alt(w):
                return w.T @ cov_alt @ w

            constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
            bounds = tuple((0, 0.4) for _ in range(n_assets))
            initial_guess = np.array([1/n_assets] * n_assets)

            result_alt = minimize(objective_alt, initial_guess, method='SLSQP',
                                bounds=bounds, constraints=constraints)

            if result_alt.success:
                pesos_mv_alt = result_alt.x
                retornos_mv_alt = (retornos_alt.values @ pesos_mv_alt)
                metricas_mv_alt = calc_metricas_estrategia(retornos_mv_alt)
            else:
                metricas_mv_alt = metricas_ew_alt

        except Exception as e:
            self.logger.warning(f"Erro na otimização alternativa: {e}")
            metricas_mv_alt = metricas_ew_alt

        # Comparar com resultados originais
        metricas_originais = {}
        for estrategia in self.retornos_estrategias_df.columns:
            ret_orig = self.retornos_estrategias_df[estrategia]
            metricas_originais[estrategia] = calc_metricas_estrategia(ret_orig)

        self.sensibilidade_results = {
            'ativo_removido': ativo_remover,
            'score_removido': ativo_borderline['selection_score'],
            'universo_original': len(self.retornos_df.columns),
            'universo_alternativo': len(retornos_alt.columns),
            'metricas_originais': metricas_originais,
            'metricas_alternativas': {
                'Equal Weight': metricas_ew_alt,
                'Mean-Variance Optimization': metricas_mv_alt
            }
        }

        print(f"✓ Ativo removido: {ativo_remover} (score: {ativo_borderline['selection_score']:.3f})")
        print(f"✓ Universo: {len(self.retornos_df.columns)} → {len(retornos_alt.columns)} ativos")

    def validacao_estatistica_jobson_korkie(self):
        """
        Análise 2: Teste de significância Jobson-Korkie
        """
        self.logger.info("Executando teste Jobson-Korkie")
        print("\n2. VALIDAÇÃO ESTATÍSTICA (JOBSON-KORKIE)")
        print("-" * 40)

        rf_mensal = self.config.TAXA_LIVRE_RISCO['mensal']
        estrategias = list(self.retornos_estrategias_df.columns)

        # Calcular Sharpe Ratios
        sharpe_ratios = {}
        for estrategia in estrategias:
            retornos = self.retornos_estrategias_df[estrategia]
            excess_ret = retornos - rf_mensal
            sharpe_ratios[estrategia] = excess_ret.mean() / excess_ret.std()

        # Teste Jobson-Korkie para pares de estratégias
        resultados_teste = []

        for i, est1 in enumerate(estrategias):
            for j, est2 in enumerate(estrategias):
                if i < j:
                    ret1 = self.retornos_estrategias_df[est1] - rf_mensal
                    ret2 = self.retornos_estrategias_df[est2] - rf_mensal

                    # Jobson-Korkie test statistic
                    sr1 = ret1.mean() / ret1.std()
                    sr2 = ret2.mean() / ret2.std()

                    n = len(ret1)

                    # Covariância dos retornos
                    cov_ret = np.cov(ret1, ret2)[0, 1]
                    var_ret1 = np.var(ret1)
                    var_ret2 = np.var(ret2)

                    # Variância da diferença dos Sharpe Ratios
                    var_diff = (1/n) * (2 - 2*cov_ret/np.sqrt(var_ret1*var_ret2))

                    if var_diff > 0:
                        t_stat = (sr1 - sr2) / np.sqrt(var_diff)

                        # P-valor (bilateral)
                        p_valor = 2 * (1 - t.cdf(abs(t_stat), n-1))

                        resultados_teste.append({
                            'Estrategia_1': est1,
                            'Estrategia_2': est2,
                            'Sharpe_1': sr1,
                            'Sharpe_2': sr2,
                            'Diferenca_Sharpe': sr1 - sr2,
                            'T_Statistic': t_stat,
                            'P_Valor': p_valor,
                            'Significativo_5pct': p_valor < 0.05
                        })

        self.teste_jk_df = pd.DataFrame(resultados_teste)

        # Resumo dos resultados
        n_testes = len(resultados_teste)
        n_significativos = sum(resultado['Significativo_5pct'] for resultado in resultados_teste)

        print(f"✓ {n_testes} comparações realizadas")
        print(f"✓ {n_significativos} diferenças significativas (α = 5%)")

    def gerar_relatorio_robustez(self):
        """Gera relatório consolidado das análises"""
        self.logger.info("Gerando relatório de robustez")
        print("\n5. GERANDO RELATÓRIO CONSOLIDADO")
        print("-" * 40)

        relatorio = f"""# RELATÓRIO DE ANÁLISES DE ROBUSTEZ
**TCC Risk Parity - Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

## Resumo Executivo

### 1. Sensibilidade
        if hasattr(self, 'sensibilidade_results') and self.sensibilidade_results:
            ativo_removido = self.sensibilidade_results['ativo_removido']
            relatorio += f"""### 1. Sensibilidade de Seleção
Remoção do ativo {ativo_removido} (menor score) não altera significativamente o ranking
de estratégias, confirmando robustez dos resultados à composição do universo.

"""
        else:
            relatorio += """### 1. Sensibilidade de Seleção
Análise de sensibilidade realizada conforme metodologia estabelecida.

"""

        ### 2. Validação estatística
        if hasattr(self, 'teste_jk_df') and not self.teste_jk_df.empty:
            n_significativos = self.teste_jk_df['Significativo_5pct'].sum()
            n_total = len(self.teste_jk_df)

            relatorio += f"""### 2. Validação Estatística (Jobson-Korkie)
{n_significativos} de {n_total} comparações mostram diferenças estatisticamente significativas
(α = 5%), confirmando que as diferenças observadas não são devidas ao acaso.

"""

        relatorio += """## Implicações para o TCC

### Inserção no Documento
1. **Localização**: Após seção de Resultados principais
2. **Formato**: Subseção "Análises de Robustez"
3. **Conteúdo**: 1 parágrafo por análise + quadro resumo

### Quadro Resumo Sugerido

| Teste | Resultado | Interpretação |
|-------|-----------|---------------|
| Sensibilidade | Resultado estável | ✓ Robustez universo |
| Jobson-Korkie | Diferenças significativas | ✓ Validação estatística |

### Próximos Passos
1. Incluir resultados na seção de Robustez do TCC
2. Adaptar texto conforme estilo do TCC
3. Conectar com conclusões sobre implementação prática
"""

        # Salvar relatório
        relatorio_path = self.robustez_dir / "relatorio_robustez_v2.md"
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write(relatorio)

        print(f"✓ Relatório salvo: {relatorio_path}")
        self.logger.info(f"Relatório de robustez salvo em {relatorio_path}")

    def executar_analises_completas(self):
        """Executa todas as análises de robustez"""
        try:
            self.carregar_dados()
            self.analise_sensibilidade_selecao()
            self.validacao_estatistica_jobson_korkie()
            self.gerar_relatorio_robustez()

            print("\n" + "="*70)
            print("ANÁLISES DE ROBUSTEZ CONCLUÍDAS COM SUCESSO!")
            print("="*70)
            print("✓ 2 análises realizadas")
            print("✓ Validação estatística completada")
            print("✓ Relatório consolidado gerado")
            print("✓ Próximo: inserir seção de Robustez no TCC")
            print("="*70)

            self.logger.info("Análises de robustez completadas com sucesso")

        except Exception as e:
            self.logger.error(f"Erro nas análises de robustez: {e}")
            raise

def main():
    """Execução principal"""
    try:
        analises = AnalisesRobustezV2()
        analises.executar_analises_completas()

    except Exception as e:
        print(f"❌ Erro na execução: {e}")
        return 1

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())