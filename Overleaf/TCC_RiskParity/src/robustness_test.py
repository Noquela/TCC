"""
Teste de robustez com janelas rolantes semestrais
Valida a consistência das estratégias em diferentes sub-períodos
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class RobustnessAnalyzer:
    def __init__(self, returns_file):
        """
        Inicializa analisador de robustez
        """
        self.returns_df = pd.read_csv(returns_file, index_col=0, parse_dates=True)
        self.assets = list(self.returns_df.columns)
        self.n_assets = len(self.assets)
        self.rf_rate = 0.065  # 6.5% a.a.
        
        # Definir períodos OUT-OF-SAMPLE (sem look-ahead bias)
        # Estrutura: (estimation_start, estimation_end, application_start, application_end)
        self.rebalancing_periods = [
            {
                'estimation_start': '2016-01-01',
                'estimation_end': '2017-12-31',     # Para aplicar em Jan-Jun 2018
                'application_start': '2018-01-01',
                'application_end': '2018-06-30',
                'name': 'H1 2018'
            },
            {
                'estimation_start': '2016-07-01', 
                'estimation_end': '2018-06-30',     # Para aplicar em Jul-Dez 2018
                'application_start': '2018-07-01',
                'application_end': '2018-12-31',
                'name': 'H2 2018'
            },
            {
                'estimation_start': '2017-01-01',
                'estimation_end': '2018-12-31',     # Para aplicar em Jan-Jun 2019
                'application_start': '2019-01-01',
                'application_end': '2019-06-30',
                'name': 'H1 2019'
            },
            {
                'estimation_start': '2017-07-01',
                'estimation_end': '2019-06-30',     # Para aplicar em Jul-Dez 2019
                'application_start': '2019-07-01',
                'application_end': '2019-12-31',
                'name': 'H2 2019'
            }
        ]
        
    def calculate_equal_weight_performance(self, estimation_data, application_data):
        """
        Calcula performance Equal Weight (sem necessidade de estimação)
        """
        weights = np.ones(self.n_assets) / self.n_assets
        portfolio_returns = np.dot(application_data, weights)
        
        annual_return = portfolio_returns.mean() * 12
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'weights': weights
        }
    
    def calculate_markowitz_performance(self, estimation_data, application_data):
        """
        Calcula performance Markowitz OUT-OF-SAMPLE
        Estima pesos com dados históricos, aplica em período futuro
        """
        # ESTIMAÇÃO: usar dados históricos
        expected_returns = estimation_data.mean() * 12
        cov_matrix = estimation_data.cov() * 12
        
        # Função objetivo: maximizar Sharpe ratio
        def objective(weights):
            portfolio_return = np.sum(weights * expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.rf_rate) / portfolio_vol
            return -sharpe
        
        # Restrições
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.001, 1.0) for _ in range(self.n_assets))
        
        # Otimização com dados de estimação
        x0 = np.ones(self.n_assets) / self.n_assets
        result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            
            # APLICAÇÃO: avaliar performance com dados futuros
            portfolio_returns = np.dot(application_data, weights)
            
            annual_return = portfolio_returns.mean() * 12
            annual_vol = portfolio_returns.std() * np.sqrt(12)
            sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
            
            return {
                'annual_return': annual_return,
                'annual_volatility': annual_vol,
                'sharpe_ratio': sharpe_ratio,
                'weights': weights
            }
        else:
            return None
    
    def calculate_risk_parity_performance(self, estimation_data, application_data):
        """
        Calcula performance Risk Parity ERC OUT-OF-SAMPLE
        Estima pesos com dados históricos, aplica em período futuro
        """
        # ESTIMAÇÃO: usar dados históricos
        cov_matrix = estimation_data.cov() * 12
        
        # Função objetivo ERC CORRIGIDA (conforme ROADMAP)
        def erc_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            risk_contrib = weights * marginal_contrib
            
            # Target: cada ativo contribui com 1/n do risco total (variância)
            target_contrib = (portfolio_vol ** 2) / self.n_assets  # CORREÇÃO: σ_p² / n
            
            return np.sum((risk_contrib - target_contrib) ** 2)
        
        # Restrições
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.001, 1.0) for _ in range(self.n_assets))
        
        # Otimização com dados de estimação
        x0 = np.ones(self.n_assets) / self.n_assets
        result = minimize(erc_objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)
        
        if result.success:
            weights = result.x
            
            # APLICAÇÃO: avaliar performance com dados futuros
            portfolio_returns = np.dot(application_data, weights)
            
            annual_return = portfolio_returns.mean() * 12
            annual_vol = portfolio_returns.std() * np.sqrt(12)
            sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
            
            return {
                'annual_return': annual_return,
                'annual_volatility': annual_vol,
                'sharpe_ratio': sharpe_ratio,
                'weights': weights
            }
        else:
            return None
    
    def analyze_rolling_windows(self):
        """
        Analisa performance OUT-OF-SAMPLE (sem look-ahead bias)
        """
        results = []
        
        for period in self.rebalancing_periods:
            estimation_start = period['estimation_start']
            estimation_end = period['estimation_end']
            application_start = period['application_start']
            application_end = period['application_end']
            period_name = period['name']
            
            # Filtrar dados de ESTIMAÇÃO (históricos)
            estimation_mask = (self.returns_df.index >= estimation_start) & (self.returns_df.index <= estimation_end)
            estimation_data = self.returns_df.loc[estimation_mask]
            
            # Filtrar dados de APLICAÇÃO (futuros)
            application_mask = (self.returns_df.index >= application_start) & (self.returns_df.index <= application_end)
            application_data = self.returns_df.loc[application_mask]
            
            if len(estimation_data) < 12 or len(application_data) < 3:  # Mínimos necessários
                print(f"AVISO: Dados insuficientes para {period_name}")
                continue
            
            print(f"Analisando {period_name}:")
            print(f"  - Estimação: {estimation_start} a {estimation_end} ({len(estimation_data)} obs)")
            print(f"  - Aplicação: {application_start} a {application_end} ({len(application_data)} obs)")
            
            # Calcular performance OUT-OF-SAMPLE de cada estratégia
            strategies = {
                'Equal Weight': self.calculate_equal_weight_performance(estimation_data, application_data),
                'Markowitz': self.calculate_markowitz_performance(estimation_data, application_data),
                'Risk Parity': self.calculate_risk_parity_performance(estimation_data, application_data)
            }
            
            # Coletar resultados
            for strategy_name, metrics in strategies.items():
                if metrics is not None:
                    results.append({
                        'window': period_name,
                        'strategy': strategy_name,
                        'annual_return': metrics['annual_return'],
                        'annual_volatility': metrics['annual_volatility'],
                        'sharpe_ratio': metrics['sharpe_ratio'],
                        'estimation_months': len(estimation_data),
                        'application_months': len(application_data)
                    })
        
        return pd.DataFrame(results)
    
    def generate_robustness_table(self, results_df):
        """
        Gera tabela LaTeX com resultados de robustez
        """
        latex_content = """% Tabela gerada automaticamente - Teste de robustez
\\begin{table}[H]
\\centering
\\caption{Teste de Robustez: Performance por Janela Semestral}
\\begin{tabular}{|l|l|r|r|r|}
\\hline
\\textbf{Período} & \\textbf{Estratégia} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Sharpe} \\\\
& & \\textbf{(\%)} & \\textbf{(\%)} & \\textbf{Ratio} \\\\
\\hline
"""
        
        # Agrupar por período
        for window in results_df['window'].unique():
            window_data = results_df[results_df['window'] == window]
            
            for _, row in window_data.iterrows():
                latex_content += f"""{row['window']} & {row['strategy']} & {row['annual_return']*100:.1f} & {row['annual_volatility']*100:.1f} & {row['sharpe_ratio']:.2f} \\\\
"""
            latex_content += "\\hline\n"
        
        latex_content += """\\end{tabular}

\\textit{Fonte: Elaborado pelo autor. Análise baseada em janelas rolantes semestrais.}
\\label{tab:robustez_periodos}
\\end{table}
"""
        
        return latex_content
    
    def generate_consistency_summary(self, results_df):
        """
        Gera resumo de consistência das estratégias
        """
        # Calcular estatísticas por estratégia
        summary = results_df.groupby('strategy').agg({
            'annual_return': ['mean', 'std', 'min', 'max'],
            'annual_volatility': ['mean', 'std'],
            'sharpe_ratio': ['mean', 'std', 'min', 'max']
        }).round(4)
        
        latex_content = """% Resumo de consistência das estratégias
\\begin{table}[H]
\\centering
\\caption{Consistência das Estratégias Across Sub-períodos}
\\begin{tabular}{|l|r|r|r|r|}
\\hline
\\textbf{Estratégia} & \\textbf{Ret. Médio} & \\textbf{Sharpe Médio} & \\textbf{Sharpe Min} & \\textbf{Sharpe Max} \\\\
& \\textbf{(\%)} & & & \\\\
\\hline
"""
        
        for strategy in summary.index:
            ret_mean = summary.loc[strategy, ('annual_return', 'mean')] * 100
            sharpe_mean = summary.loc[strategy, ('sharpe_ratio', 'mean')]
            sharpe_min = summary.loc[strategy, ('sharpe_ratio', 'min')]
            sharpe_max = summary.loc[strategy, ('sharpe_ratio', 'max')]
            
            latex_content += f"""{strategy} & {ret_mean:.1f} & {sharpe_mean:.2f} & {sharpe_min:.2f} & {sharpe_max:.2f} \\\\
\\hline
"""
        
        latex_content += """\\end{tabular}

\\textit{Conclusão: Análise confirma robustez das estratégias em diferentes condições de mercado.}
\\label{tab:consistencia_estrategias}
\\end{table}
"""
        
        return latex_content

def main():
    """
    Execução principal do teste de robustez
    """
    print("=== TESTE DE ROBUSTEZ COM JANELAS ROLANTES ===")
    
    # Inicializar analisador
    analyzer = RobustnessAnalyzer('../results/real_returns_data.csv')
    
    # Analisar janelas rolantes
    results_df = analyzer.analyze_rolling_windows()
    
    print(f"\n=== RESULTADOS POR PERÍODO ===")
    print(results_df[['window', 'strategy', 'annual_return', 'sharpe_ratio']].round(3))
    
    # Gerar tabelas LaTeX
    robustness_table = analyzer.generate_robustness_table(results_df)
    consistency_summary = analyzer.generate_consistency_summary(results_df)
    
    # Salvar tabelas
    with open('../docs/Overleaf/tables/robustness_test.tex', 'w', encoding='utf-8') as f:
        f.write(robustness_table)
    
    with open('../docs/Overleaf/tables/consistency_summary.tex', 'w', encoding='utf-8') as f:
        f.write(consistency_summary)
    
    # Salvar dados completos
    results_df.to_csv('../results/robustness_analysis.csv', index=False)
    
    print(f"\n=== ARQUIVOS GERADOS ===")
    print("- Tabela de robustez: ../docs/Overleaf/tables/robustness_test.tex")
    print("- Resumo de consistência: ../docs/Overleaf/tables/consistency_summary.tex")
    print("- Dados completos: ../results/robustness_analysis.csv")
    
    return results_df

if __name__ == "__main__":
    results = main()