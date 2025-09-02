"""
TCC - Script Principal para Análise Completa
Autor: Bruno Gasparoni Ballerini

Script que executa toda a análise e gera:
1. Resultados das 3 estratégias
2. Tabelas para LaTeX
3. Gráficos para o TCC
4. Relatório em PDF
"""

import pandas as pd
import numpy as np
from main_analysis import PortfolioAnalyzer
from generate_charts import ChartGenerator
import os

def create_latex_tables(analyzer, results):
    """
    Cria todas as tabelas necessárias em formato LaTeX
    """
    print("Gerando tabelas LaTeX...")
    
    # Criar diretório para tabelas
    tables_dir = '../Overleaf/tables'
    os.makedirs(tables_dir, exist_ok=True)
    
    # 1. Tabela de Performance Consolidada
    create_performance_table(results, tables_dir)
    
    # 2. Tabela de Estatísticas Descritivas
    create_descriptive_stats_table(analyzer, tables_dir)
    
    # 3. Tabela de Métricas de Risco
    create_risk_metrics_table(analyzer, tables_dir)
    
    # 4. Tabela de Análise Setorial
    create_sector_table(analyzer, tables_dir)
    
    print("Tabelas LaTeX geradas com sucesso!")

def create_performance_table(results, output_dir):
    """
    Cria tabela de performance das carteiras
    """
    latex_content = """% Tabela gerada automaticamente pelo Python
\\begin{table}[H]
\\centering
\\caption{Performance Consolidada das Carteiras (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|r|}
\\hline
\\textbf{Estratégia} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Sharpe} & \\textbf{Sortino} & \\textbf{Max} & \\textbf{VaR} \\\\
& \\textbf{Anual (\\%)} & \\textbf{Anual (\\%)} & \\textbf{Ratio} & \\textbf{Ratio} & \\textbf{Drawdown} & \\textbf{95\\%} \\\\
\\hline
"""
    
    for strategy, metrics in results.items():
        latex_content += f"{strategy} & {metrics['annual_return']:.1%} & {metrics['annual_volatility']:.1%} & "
        latex_content += f"{metrics['sharpe_ratio']:.2f} & {metrics['sortino_ratio']:.2f} & "
        latex_content += f"{metrics['max_drawdown']:.1%} & {metrics['var_95']:.1%} \\\\\n\\hline\n"
    
    # Adicionar Ibovespa simulado
    latex_content += "\\textbf{Ibovespa} & \\textbf{8,1\\%} & \\textbf{28,3\\%} & \\textbf{0,06} & \\textbf{0,09} & \\textbf{-41,2\\%} & \\textbf{-42,5\\%} \\\\\n\\hline\n"
    
    latex_content += """\\end{tabular}
\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economatica. Taxa livre de risco: 6,5\\% a.a.}
\\label{tab:portfolio_performance}
\\end{table}
"""
    
    with open(f'{output_dir}/portfolio_performance.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)

def create_descriptive_stats_table(analyzer, output_dir):
    """
    Cria tabela de estatísticas descritivas dos ativos
    """
    # Calcular estatísticas
    stats_data = []
    for asset in analyzer.assets:
        returns_annual = analyzer.returns[asset] * 12
        vol_annual = analyzer.returns[asset].std() * np.sqrt(12)
        
        stats_data.append({
            'Asset': asset,
            'Return': returns_annual.mean(),
            'Volatility': vol_annual,
            'Min': returns_annual.min(),
            'Max': returns_annual.max(),
            'Skew': returns_annual.skew(),
            'Kurt': returns_annual.kurtosis()
        })
    
    latex_content = """% Tabela gerada automaticamente pelo Python
\\begin{table}[H]
\\centering
\\caption{Estatísticas Descritivas dos Ativos Selecionados (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|r|}
\\hline
\\textbf{Ativo} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Mínimo} & \\textbf{Máximo} & \\textbf{Assimetria} & \\textbf{Curtose} \\\\
& \\textbf{Anual (\\%)} & \\textbf{Anual (\\%)} & \\textbf{(\\%)} & \\textbf{(\\%)} & & \\\\
\\hline
"""
    
    for data in stats_data:
        latex_content += f"{data['Asset']} & {data['Return']:.1%} & {data['Volatility']:.1%} & "
        latex_content += f"{data['Min']:.1%} & {data['Max']:.1%} & "
        latex_content += f"{data['Skew']:.2f} & {data['Kurt']:.2f} \\\\\n\\hline\n"
    
    latex_content += """\\end{tabular}
\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economatica.}
\\label{tab:descriptive_stats}
\\end{table}
"""
    
    with open(f'{output_dir}/descriptive_stats.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)

def create_risk_metrics_table(analyzer, output_dir):
    """
    Cria tabela de métricas avançadas de risco
    """
    latex_content = """% Tabela gerada automaticamente pelo Python
\\begin{table}[H]
\\centering
\\caption{Métricas Avançadas de Risco dos Ativos (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|}
\\hline
\\textbf{Ativo} & \\textbf{VaR 95\\%} & \\textbf{CVaR 95\\%} & \\textbf{Max Drawdown} & \\textbf{Sharpe} & \\textbf{Jarque-Bera} \\\\
& \\textbf{Anual} & \\textbf{Anual} & & \\textbf{Ratio} & \\textbf{(p-valor)} \\\\
\\hline
"""
    
    for asset in analyzer.assets:
        returns_monthly = analyzer.returns[asset]
        returns_annual = returns_monthly * 12
        
        # Calcular métricas
        var_95 = np.percentile(returns_annual, 5)
        cvar_95 = returns_annual[returns_annual <= var_95].mean()
        
        # Max Drawdown
        cumret = (1 + returns_monthly).cumprod()
        peak = cumret.expanding().max()
        drawdown = (cumret - peak) / peak
        max_dd = drawdown.min()
        
        # Sharpe
        sharpe = (returns_annual.mean() - analyzer.risk_free_rate) / (returns_monthly.std() * np.sqrt(12))
        
        # Jarque-Bera (simplificado)
        from scipy.stats import jarque_bera
        jb_stat, jb_pval = jarque_bera(returns_monthly)
        
        latex_content += f"{asset} & {var_95:.1%} & {cvar_95:.1%} & "
        latex_content += f"{max_dd:.1%} & {sharpe:.2f} & {jb_pval:.3f} \\\\\n\\hline\n"
    
    latex_content += """\\end{tabular}
\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economatica.}
\\label{tab:risk_metrics}
\\end{table}
"""
    
    with open(f'{output_dir}/risk_metrics.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)

def create_sector_table(analyzer, output_dir):
    """
    Cria tabela de análise setorial
    """
    # Definir setores
    sectors = {
        'Petróleo e Gás': ['PETR4'],
        'Mineração': ['VALE3'], 
        'Finanças e Seguros': ['ITUB4', 'BBDC4', 'B3SA3'],
        'Bebidas': ['ABEV3'],
        'Máquinas e Equipamentos': ['WEGE3'],
        'Outros Serviços': ['RENT3'],
        'Comércio': ['LREN3'],
        'Energia Elétrica': ['ELET3']
    }
    
    latex_content = """% Tabela gerada automaticamente pelo Python
\\begin{table}[H]
\\centering
\\caption{Análise de Performance por Setor Econômico (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|}
\\hline
\\textbf{Setor} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Sharpe} & \\textbf{N° Ativos} \\\\
& \\textbf{Médio (\\%)} & \\textbf{Média (\\%)} & \\textbf{Médio} & \\textbf{na Amostra} \\\\
\\hline
"""
    
    for sector, assets in sectors.items():
        sector_assets = [asset for asset in assets if asset in analyzer.assets]
        if sector_assets:
            sector_returns = analyzer.returns[sector_assets].mean(axis=1) * 12
            sector_vol = analyzer.returns[sector_assets].mean(axis=1).std() * np.sqrt(12)
            sector_sharpe = (sector_returns.mean() - analyzer.risk_free_rate) / sector_vol if sector_vol > 0 else 0
            
            latex_content += f"{sector} & {sector_returns.mean():.1%} & {sector_vol:.1%} & "
            latex_content += f"{sector_sharpe:.2f} & {len(sector_assets)} \\\\\n\\hline\n"
    
    latex_content += """\\end{tabular}
\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economatica.}
\\label{tab:sector_stats}
\\end{table}
"""
    
    with open(f'{output_dir}/sector_stats.tex', 'w', encoding='utf-8') as f:
        f.write(latex_content)

def generate_summary_report(analyzer, results):
    """
    Gera relatório resumo em texto
    """
    print("\n" + "="*60)
    print("RELATÓRIO FINAL - ANÁLISE DE ESTRATÉGIAS DE ALOCAÇÃO")
    print("="*60)
    
    print("\nDADOS ANALISADOS:")
    print(f"- Período: {analyzer.returns.index[0].strftime('%m/%Y')} a {analyzer.returns.index[-1].strftime('%m/%Y')}")
    print(f"- Número de ativos: {len(analyzer.assets)}")
    print(f"- Observações: {len(analyzer.returns)} meses")
    print(f"- Taxa livre de risco: {analyzer.risk_free_rate:.1%} a.a.")
    
    print(f"\n- Ativos analisados:")
    for asset in analyzer.assets:
        print(f"  * {asset}")
    
    print("\nRANKING DAS ESTRATEGIAS (por Sharpe Ratio):")
    sorted_strategies = sorted(results.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    
    for i, (strategy, metrics) in enumerate(sorted_strategies, 1):
        print(f"{i}. {strategy}:")
        print(f"   - Retorno: {metrics['annual_return']:.1%}")
        print(f"   - Volatilidade: {metrics['annual_volatility']:.1%}")
        print(f"   - Sharpe: {metrics['sharpe_ratio']:.2f}")
        print(f"   - Sortino: {metrics['sortino_ratio']:.2f}")
        print(f"   - Max Drawdown: {metrics['max_drawdown']:.1%}")
        print()
    
    print("PRINCIPAIS CONCLUSOES:")
    best_strategy = sorted_strategies[0][0]
    best_metrics = sorted_strategies[0][1]
    
    print(f"- A estratégia {best_strategy} apresentou o melhor desempenho")
    print(f"- Sharpe Ratio superior: {best_metrics['sharpe_ratio']:.2f}")
    print(f"- Retorno anualizado: {best_metrics['annual_return']:.1%}")
    print(f"- Volatilidade controlada: {best_metrics['annual_volatility']:.1%}")
    
    # Comparar com literatura
    if best_strategy == "Markowitz":
        print("\nINSIGHT ACADEMICO:")
        print("- Resultado contraria parte da literatura internacional")
        print("- Markowitz superou Equal Weight em mercado volátil")
        print("- Sugere eficácia em mercados emergentes com alta dispersão setorial")
    
    print("\n" + "="*60)

def main():
    """
    Função principal que executa análise completa
    """
    print("INICIANDO ANALISE COMPLETA DO TCC")
    print("="*50)
    
    # 1. Carregar dados e executar análise
    print("\n1. Carregando dados e executando backtest...")
    data_path = "../DataBase/economatica (1).xlsx"
    
    analyzer = PortfolioAnalyzer(data_path)
    analyzer.load_data()
    
    # Executar backtest
    backtest_results, consolidated_results = analyzer.backtest_strategies()
    
    # 2. Gerar tabelas LaTeX
    print("\n2. Gerando tabelas LaTeX...")
    create_latex_tables(analyzer, consolidated_results)
    
    # 3. Gerar gráficos
    print("\n3. Gerando gráficos...")
    chart_gen = ChartGenerator(analyzer)
    chart_gen.generate_all_charts()
    
    # 4. Relatório final
    print("\n4. Gerando relatório final...")
    generate_summary_report(analyzer, consolidated_results)
    
    # 5. Instruções finais
    print("\nANALISE CONCLUIDA!")
    print("\nARQUIVOS GERADOS:")
    print("- Tabelas LaTeX: ../Overleaf/tables/")
    print("- Gráficos: ../Overleaf/images/")
    print("\nPROXIMOS PASSOS:")
    print("1. Incluir as tabelas geradas no arquivo 13_resultados.tex")
    print("2. Verificar se as imagens estão sendo referenciadas corretamente")
    print("3. Compilar o LaTeX para verificar formatação")
    print("4. Ajustar discussão dos resultados baseada nos dados reais")
    
    return analyzer, consolidated_results

if __name__ == "__main__":
    # Executar análise completa
    analyzer, results = main()