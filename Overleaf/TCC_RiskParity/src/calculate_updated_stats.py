"""
Cálculo de Estatísticas dos 10 Ativos Quantitativamente Selecionados
SPRINT 4.1: Recálculo completo com dados unificados

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
import json
import os

def calculate_comprehensive_stats():
    """
    Calcula estatísticas completas dos 10 ativos selecionados
    """
    print("=== CÁLCULO DE ESTATÍSTICAS DOS 10 ATIVOS SELECIONADOS ===")
    
    # Carregar dados dos retornos
    returns_df = pd.read_csv('../results/real_returns_data.csv', index_col=0, parse_dates=True)
    
    print(f"Calculando estatísticas dos dados reais...")
    print(f"Período: {returns_df.index[0].date()} a {returns_df.index[-1].date()}")
    print(f"Ativos: {list(returns_df.columns)}")
    print()
    
    # Carregar informações dos ativos selecionados
    with open('../results/quantitative_selection.json', 'r', encoding='utf-8') as f:
        selection_data = json.load(f)
    
    # Taxa livre de risco
    rf_rate = 0.065  # 6.5% a.a.
    rf_monthly = rf_rate / 12
    
    stats_list = []
    
    for asset in returns_df.columns:
        asset_returns = returns_df[asset]
        
        # Estatísticas básicas
        mean_return = asset_returns.mean()
        std_return = asset_returns.std()
        
        # Anualizadas
        annual_return = mean_return * 12
        annual_volatility = std_return * np.sqrt(12)
        
        # Sharpe Ratio
        excess_return_annual = annual_return - rf_rate
        sharpe_ratio = excess_return_annual / annual_volatility if annual_volatility > 0 else 0
        
        # Sortino Ratio
        downside_returns = asset_returns[asset_returns < rf_monthly] - rf_monthly
        downside_deviation = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(12)
        sortino_ratio = excess_return_annual / downside_deviation if downside_deviation > 0 else 0
        
        # Maximum Drawdown
        cum_returns = (1 + asset_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Beta (calculado contra equal weight dos ativos como proxy do mercado)
        market_returns = returns_df.mean(axis=1)  # Equal weight portfolio
        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance if market_variance > 0 else 1.0
        
        # Informações do ativo
        asset_info = selection_data['asset_details'].get(asset, {})
        sector = asset_info.get('sector', 'N/A')
        selection_score = asset_info.get('score', 0)
        
        stats_list.append({
            'Ativo': asset,
            'Setor': sector,
            'Score_Selecao': round(selection_score, 4),
            'Retorno_Anual_Pct': round(annual_return * 100, 2),
            'Volatilidade_Anual_Pct': round(annual_volatility * 100, 2),
            'Sharpe_Ratio': round(sharpe_ratio, 3),
            'Sortino_Ratio': round(sortino_ratio, 3),
            'Beta': round(beta, 3),
            'Max_Drawdown_Pct': round(max_drawdown * 100, 2)
        })
    
    stats_df = pd.DataFrame(stats_list)
    
    print("ESTATÍSTICAS CALCULADAS:")
    print(stats_df.to_string(index=False))
    
    return stats_df

def generate_latex_table(stats_df):
    """
    Gera tabela LaTeX das estatísticas
    """
    print("\nGerando tabela LaTeX...")
    
    latex_content = """
\\begin{table}[htbp]
\\centering
\\caption{Estatísticas dos Ativos Quantitativamente Selecionados (2018-2019)}
\\label{tab:selected_assets_stats}
\\begin{adjustbox}{width=\\textwidth}
\\begin{tabular}{lllrrrrrr}
\\toprule
\\textbf{Ativo} & \\textbf{Setor} & \\textbf{Score} & 
\\textbf{Retorno} & \\textbf{Vol.} & \\textbf{Sharpe} & 
\\textbf{Sortino} & \\textbf{Beta} & \\textbf{Max DD} \\\\
& & \\textbf{Seleção} & \\textbf{(\\%)} & \\textbf{(\\%)} & 
\\textbf{Ratio} & \\textbf{Ratio} & & \\textbf{(\\%)} \\\\
\\midrule
"""
    
    for _, row in stats_df.iterrows():
        latex_content += f"{row['Ativo']} & {row['Setor'][:15]} & {row['Score_Selecao']:.3f} & "
        latex_content += f"{row['Retorno_Anual_Pct']:.1f} & {row['Volatilidade_Anual_Pct']:.1f} & "
        latex_content += f"{row['Sharpe_Ratio']:.2f} & {row['Sortino_Ratio']:.2f} & "
        latex_content += f"{row['Beta']:.2f} & {row['Max_Drawdown_Pct']:.1f} \\\\\n"
    
    latex_content += """\\bottomrule
\\end{tabular}
\\end{adjustbox}
\\begin{tablenotes}
\\small
\\item Fonte: Elaboração própria com dados da Economática.
\\item Período: Janeiro 2018 a Dezembro 2019 (24 meses).
\\item Ativos selecionados por metodologia quantitativa ex-ante baseada em dados 2014-2017.
\\item Score de Seleção: resultado da otimização multi-objetivo (liquidez + diversificação + qualidade).
\\item Taxa livre de risco: 6,5\\% a.a. (SELIC média do período).
\\end{tablenotes}
\\end{table}
"""
    
    return latex_content

def main():
    """
    Execução principal
    """
    # Calcular estatísticas
    stats_df = calculate_comprehensive_stats()
    
    # Gerar tabela LaTeX
    latex_table = generate_latex_table(stats_df)
    
    # Salvar arquivos
    results_dir = '../results'
    docs_dir = '../docs/Overleaf/tables'
    
    # Salvar CSV
    stats_file = os.path.join(results_dir, 'selected_assets_statistics.csv')
    stats_df.to_csv(stats_file, index=False)
    
    # Salvar LaTeX
    latex_file = os.path.join(docs_dir, 'selected_assets_statistics.tex')
    os.makedirs(docs_dir, exist_ok=True)
    with open(latex_file, 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    print(f"\nARQUIVOS SALVOS:")
    print(f"- Estatísticas CSV: {stats_file}")
    print(f"- Tabela LaTeX: {latex_file}")
    
    # Mostrar resumo
    print(f"\nRESUMO:")
    print(f"- Melhor Sharpe Ratio: {stats_df['Ativo'][stats_df['Sharpe_Ratio'].idxmax()]} ({stats_df['Sharpe_Ratio'].max():.3f})")
    print(f"- Maior Retorno: {stats_df['Ativo'][stats_df['Retorno_Anual_Pct'].idxmax()]} ({stats_df['Retorno_Anual_Pct'].max():.1f}%)")
    print(f"- Menor Volatilidade: {stats_df['Ativo'][stats_df['Volatilidade_Anual_Pct'].idxmin()]} ({stats_df['Volatilidade_Anual_Pct'].min():.1f}%)")
    print(f"- Setores representados: {stats_df['Setor'].nunique()}")
    
    return stats_df

if __name__ == "__main__":
    stats_df = main()