"""
Calcula todas as estatísticas necessárias com dados reais da Economática
Para substituir os dados fictícios no TCC
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

def calculate_comprehensive_stats():
    """
    Calcula estatísticas completas dos dados reais
    """
    # Carregar dados reais
    returns_df = pd.read_csv('../results/real_returns_data.csv', index_col=0, parse_dates=True)
    
    print("Calculando estatísticas completas dos dados reais...")
    print(f"Período: {returns_df.index[0].date()} a {returns_df.index[-1].date()}")
    print(f"Ativos: {list(returns_df.columns)}")
    
    # Informações dos ativos
    asset_info = {
        'PETR4': {'name': 'Petróleo Brasileiro S.A.', 'sector': 'Petróleo e Gás'},
        'VALE3': {'name': 'Vale S.A.', 'sector': 'Mineração'},
        'ITUB4': {'name': 'Itaú Unibanco Holding S.A.', 'sector': 'Finanças e Seguros'},
        'BBDC4': {'name': 'Banco Bradesco S.A.', 'sector': 'Finanças e Seguros'},
        'ABEV3': {'name': 'Ambev S.A.', 'sector': 'Bebidas'},
        'B3SA3': {'name': 'B3 S.A.', 'sector': 'Finanças e Seguros'},
        'WEGE3': {'name': 'WEG S.A.', 'sector': 'Máquinas e Equipamentos'},
        'RENT3': {'name': 'Localiza Rent a Car S.A.', 'sector': 'Outros Serviços'},
        'LREN3': {'name': 'Lojas Renner S.A.', 'sector': 'Comércio'},
        'ELET3': {'name': 'Centrais Elétricas Brasileiras', 'sector': 'Energia Elétrica'}
    }
    
    stats_data = []
    
    for asset in returns_df.columns:
        asset_returns = returns_df[asset]
        
        # Estatísticas básicas anualizadas
        annual_return = asset_returns.mean() * 12
        annual_vol = asset_returns.std() * np.sqrt(12)
        min_monthly = asset_returns.min()
        max_monthly = asset_returns.max()
        
        # Estatísticas de forma
        skewness = stats.skew(asset_returns)
        kurtosis_val = stats.kurtosis(asset_returns)
        
        # Teste de normalidade Jarque-Bera
        jb_stat, jb_pvalue = stats.jarque_bera(asset_returns)
        
        # Métricas de risco
        # VaR 95% mensal
        var_95 = np.percentile(asset_returns, 5)
        
        # CVaR 95% mensal (média dos retornos abaixo do VaR)
        cvar_95 = asset_returns[asset_returns <= var_95].mean()
        
        # Maximum Drawdown (método padronizado com carteiras)
        cumulative_returns = (1 + asset_returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Sharpe Ratio anualizado (assumindo risk-free = 6.5%)
        rf_rate = 0.065 / 12  # Taxa livre de risco mensal
        excess_returns = asset_returns - rf_rate
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(12)
        
        # Sortino Ratio anualizado (implementação conforme especificação)
        # CDI 6,5% a.a. conforme TCC
        rf_rate_annual = 0.065
        rf_rate_monthly = rf_rate_annual / 12
        annual_return_calc = asset_returns.mean() * 12
        
        # Downside deviation: apenas retornos abaixo da taxa livre de risco
        downside = np.sqrt(((asset_returns[asset_returns < rf_rate_monthly] - rf_rate_monthly) ** 2).mean())
        sortino_ratio = (annual_return_calc - rf_rate_annual) / (downside * np.sqrt(12)) if downside > 0 else np.nan
        
        stats_data.append({
            'Ativo': asset,
            'Nome': asset_info[asset]['name'],
            'Setor': asset_info[asset]['sector'],
            'Retorno_Anual_Pct': annual_return * 100,
            'Volatilidade_Anual_Pct': annual_vol * 100,
            'Min_Mensal_Pct': min_monthly * 100,
            'Max_Mensal_Pct': max_monthly * 100,
            'Assimetria': skewness,
            'Curtose': kurtosis_val,
            'VaR_95_Mensal_Pct': var_95 * 100,
            'CVaR_95_Mensal_Pct': cvar_95 * 100,
            'Max_Drawdown_Pct': max_drawdown * 100,
            'Sharpe_Ratio': sharpe_ratio,
            'Sortino_Ratio': sortino_ratio,
            'JB_Stat': jb_stat,
            'JB_PValue': jb_pvalue
        })
    
    stats_df = pd.DataFrame(stats_data)
    return stats_df

def generate_latex_descriptive_table(stats_df):
    """
    Gera tabela LaTeX com estatísticas descritivas
    """
    latex_content = """% Tabela gerada automaticamente pelo Python com dados reais da Economática
\\begin{table}[H]
\\centering
\\caption{Estatísticas Descritivas dos Ativos Selecionados (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|r|}
\\hline
\\textbf{Ativo} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Mínimo} & \\textbf{Máximo} & \\textbf{Assimetria} & \\textbf{Curtose} \\\\
& \\textbf{Anual (\\%)} & \\textbf{Anual (\\%)} & \\textbf{Mensal (\\%)} & \\textbf{Mensal (\\%)} & & \\\\
\\hline
"""
    
    for _, row in stats_df.iterrows():
        latex_content += f"""{row['Ativo']} & {row['Retorno_Anual_Pct']:.1f} & {row['Volatilidade_Anual_Pct']:.1f} & {row['Min_Mensal_Pct']:.1f} & {row['Max_Mensal_Pct']:.1f} & {row['Assimetria']:.2f} & {row['Curtose']:.2f} \\\\
\\hline
"""
    
    latex_content += """\\end{tabular}

\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economática.}
\\label{tab:descriptive_stats}
\\end{table}
"""
    
    return latex_content

def generate_latex_risk_table(stats_df):
    """
    Gera tabela LaTeX com métricas de risco
    """
    latex_content = """% Tabela gerada automaticamente pelo Python com dados reais da Economática
\\begin{table}[H]
\\centering
\\caption{Métricas Avançadas de Risco dos Ativos (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|r|}
\\hline
\\textbf{Ativo} & \\textbf{VaR 95\\%} & \\textbf{CVaR 95\\%} & \\textbf{Max Drawdown} & \\textbf{Sharpe} & \\textbf{Sortino} & \\textbf{Jarque-Bera} \\\\
& \\textbf{Mensal} & \\textbf{Mensal} & & \\textbf{Ratio} & \\textbf{Ratio} & \\textbf{(p-valor)} \\\\
\\hline
"""
    
    for _, row in stats_df.iterrows():
        sortino_val = row['Sortino_Ratio'] if not np.isnan(row['Sortino_Ratio']) else 0.0
        latex_content += f"""{row['Ativo']} & {row['VaR_95_Mensal_Pct']:.1f}\\% & {row['CVaR_95_Mensal_Pct']:.1f}\\% & {row['Max_Drawdown_Pct']:.1f}\\% & {row['Sharpe_Ratio']:.2f} & {sortino_val:.2f} & {row['JB_PValue']:.3f} \\\\
\\hline
"""
    
    latex_content += """\\end{tabular}

\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economática.}
\\label{tab:risk_metrics}
\\end{table}
"""
    
    return latex_content

def main():
    print("=== CÁLCULO DE ESTATÍSTICAS COMPLETAS COM DADOS REAIS ===")
    
    # Calcular estatísticas
    stats_df = calculate_comprehensive_stats()
    
    # Mostrar resultados
    print("\n=== ESTATÍSTICAS DESCRITIVAS ===")
    print(stats_df[['Ativo', 'Retorno_Anual_Pct', 'Volatilidade_Anual_Pct', 'Assimetria', 'Curtose']].round(2))
    
    print("\n=== MÉTRICAS DE RISCO ===")
    print(stats_df[['Ativo', 'VaR_95_Mensal_Pct', 'CVaR_95_Mensal_Pct', 'Max_Drawdown_Pct', 'Sharpe_Ratio']].round(2))
    
    # Gerar tabelas LaTeX
    descriptive_table = generate_latex_descriptive_table(stats_df)
    risk_table = generate_latex_risk_table(stats_df)
    
    # Salvar tabelas
    with open('../docs/Overleaf/tables/descriptive_stats.tex', 'w', encoding='utf-8') as f:
        f.write(descriptive_table)
    
    with open('../docs/Overleaf/tables/risk_metrics.tex', 'w', encoding='utf-8') as f:
        f.write(risk_table)
    
    # Salvar dados completos
    stats_df.to_csv('../results/complete_real_stats.csv', index=False)
    
    print(f"\n=== ARQUIVOS GERADOS ===")
    print("- Tabela descritiva: ../docs/Overleaf/tables/descriptive_stats.tex")
    print("- Tabela de risco: ../docs/Overleaf/tables/risk_metrics.tex")
    print("- Estatísticas completas: ../results/complete_real_stats.csv")
    
    return stats_df

if __name__ == "__main__":
    stats_df = main()