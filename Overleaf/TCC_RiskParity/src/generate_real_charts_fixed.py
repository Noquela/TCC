"""
Geração de Gráficos com Dados Reais da Economática
Para substituir os gráficos fictícios no TCC
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuração para gráficos em português
plt.style.use('seaborn-v0_8')
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 14

def load_real_data():
    """
    Carrega todos os dados reais necessários
    """
    # Dados de retornos e preços
    returns_df = pd.read_csv('../results/real_returns_data.csv', index_col=0, parse_dates=True)
    prices_df = pd.read_csv('../results/real_prices_data.csv', index_col=0, parse_dates=True)
    
    # Resultados das estratégias
    with open('../results/detailed_portfolio_results.json', 'r') as f:
        portfolio_results = json.load(f)
    
    # Estatísticas completas
    stats_df = pd.read_csv('../results/complete_real_stats.csv')
    
    return returns_df, prices_df, portfolio_results, stats_df

def create_correlation_matrix(returns_df):
    """
    Figura 2: Matriz de Correlação entre Ativos Selecionados
    """
    plt.figure(figsize=(10, 8))
    
    corr_matrix = returns_df.corr()
    
    # Criar heatmap
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdYlBu_r', 
                center=0, square=True, fmt='.2f', cbar_kws={"shrink": .8})
    
    plt.title('Matriz de Correlação entre Ativos Selecionados (2018-2019)')
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/correlation_matrix.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/correlation_matrix.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 2: Matriz de correlacao criada")

def create_price_evolution(prices_df):
    """
    Figura 3: Evolução dos Preços Normalizados dos Ativos
    """
    plt.figure(figsize=(12, 8))
    
    # Normalizar preços (base 100 no início do período)
    normalized_prices = (prices_df / prices_df.iloc[0] * 100)
    
    # Plotar evolução de cada ativo
    for asset in normalized_prices.columns:
        plt.plot(normalized_prices.index, normalized_prices[asset], 
                label=asset, linewidth=2)
    
    plt.title('Evolução dos Preços Normalizados dos Ativos Selecionados (2018-2019)')
    plt.xlabel('Data')
    plt.ylabel('Preço Normalizado (Base 100)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/price_evolution.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/price_evolution.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 3: Evolucao dos precos criada")

def create_rolling_volatility(returns_df):
    """
    Figura 4: Evolução da Volatilidade Rolling (3 meses) por Ativo
    """
    plt.figure(figsize=(12, 8))
    
    # Calcular volatilidade rolling de 3 meses (anualizada)
    rolling_vol = returns_df.rolling(window=3).std() * np.sqrt(12)
    
    # Plotar apenas alguns ativos principais para clareza
    main_assets = ['PETR4', 'VALE3', 'ITUB4', 'WEGE3', 'ELET3']
    
    for asset in main_assets:
        if asset in rolling_vol.columns:
            plt.plot(rolling_vol.index, rolling_vol[asset] * 100, 
                    label=asset, linewidth=2)
    
    plt.title('Evolução da Volatilidade Rolling (3 meses) por Ativo')
    plt.xlabel('Data')
    plt.ylabel('Volatilidade Anual (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/rolling_volatility.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/rolling_volatility.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 4: Volatilidade rolling criada")

def create_sector_analysis(stats_df):
    """
    Figura 6: Análise de Performance por Setor Econômico
    """
    plt.figure(figsize=(12, 8))
    
    # Agrupar por setor
    sector_stats = stats_df.groupby('Setor').agg({
        'Retorno_Anual_Pct': 'mean',
        'Volatilidade_Anual_Pct': 'mean',
        'Sharpe_Ratio': 'mean'
    }).reset_index()
    
    # Criar gráfico de dispersão Retorno x Volatilidade por setor
    colors = plt.cm.tab10(np.linspace(0, 1, len(sector_stats)))
    
    for i, (_, row) in enumerate(sector_stats.iterrows()):
        plt.scatter(row['Volatilidade_Anual_Pct'], row['Retorno_Anual_Pct'], 
                   s=200, alpha=0.7, color=colors[i], label=row['Setor'])
        
        # Adicionar texto com o setor
        plt.annotate(row['Setor'], 
                    (row['Volatilidade_Anual_Pct'], row['Retorno_Anual_Pct']),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    plt.title('Análise de Performance por Setor Econômico (2018-2019)')
    plt.xlabel('Volatilidade Anual (%)')
    plt.ylabel('Retorno Anual (%)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/sector_analysis.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/sector_analysis.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 6: Analise setorial criada")

def create_portfolio_evolution(portfolio_results, returns_df, benchmark_returns=None):
    """
    Figura 7: Evolução das Carteiras vs. Benchmark de Mercado
    """
    plt.figure(figsize=(12, 8))
    
    # VALIDAÇÃO: Apenas Ibovespa B3 oficial é aceito
    if benchmark_returns is None:
        # ERRO: Sem Ibovespa B3 oficial
        print("    ERRO CRÍTICO: TCC requer exclusivamente Ibovespa B3 oficial!")
        print("    Sistema não pode continuar - benchmark obrigatório ausente")
        return
    
    # Verificar se é realmente Ibovespa B3
    bench_type = getattr(benchmark_returns, 'benchmark_type', 'Desconhecido')
    if 'Ibovespa B3' not in bench_type:
        print(f"    ERRO: Benchmark inválido '{bench_type}' - apenas Ibovespa B3 oficial aceito")
        return
        
    benchmark_returns = benchmark_returns.reindex(returns_df.index).dropna()
    benchmark_cumulative = (1 + benchmark_returns).cumprod()
    bench_label = bench_type
    print(f"    ✓ Benchmark validado: {bench_label}")
    
    # Plotar evolução de cada estratégia
    strategies = ['Equal Weight', 'Markowitz', 'Risk Parity']
    colors = ['blue', 'green', 'red']
    
    for i, strategy in enumerate(strategies):
        if strategy in portfolio_results:
            monthly_returns = pd.Series(portfolio_results[strategy]['monthly_returns'],
                                      index=returns_df.index)
            cumulative_returns = (1 + monthly_returns).cumprod()
            plt.plot(cumulative_returns.index, cumulative_returns.values, 
                    label=strategy, color=colors[i], linewidth=2)
    
    # Plotar benchmark
    plt.plot(benchmark_cumulative.index, benchmark_cumulative.values, 
            label=bench_label, color='black', linestyle='--', linewidth=2)
    
    plt.title('Evolução das Carteiras vs. Ibovespa B3 Oficial (2018-2019)')
    plt.xlabel('Data')
    plt.ylabel('Retorno Acumulado')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/portfolio_evolution.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/portfolio_evolution.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 7: Evolucao das carteiras vs benchmark de mercado criada")

def create_risk_return_plot(portfolio_results):
    """
    Figura 8: Posicionamento das Estratégias no Plano Risco-Retorno
    """
    plt.figure(figsize=(10, 8))
    
    strategies = ['Equal Weight', 'Markowitz', 'Risk Parity']
    colors = ['blue', 'green', 'red']
    
    for i, strategy in enumerate(strategies):
        if strategy in portfolio_results:
            ret = portfolio_results[strategy]['annual_return'] * 100
            vol = portfolio_results[strategy]['annual_volatility'] * 100
            sharpe = portfolio_results[strategy]['sharpe_ratio']
            
            plt.scatter(vol, ret, s=300, alpha=0.7, color=colors[i], 
                       label=f'{strategy} (Sharpe: {sharpe:.2f})')
            
            # Adicionar texto com o nome da estratégia
            plt.annotate(strategy, (vol, ret), 
                        xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    plt.title('Posicionamento das Estratégias no Plano Risco-Retorno')
    plt.xlabel('Volatilidade Anual (%)')
    plt.ylabel('Retorno Anual (%)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/risk_return_plot.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/risk_return_plot.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 8: Plano risco-retorno criado")

def create_returns_distribution(portfolio_results, returns_df):
    """
    Figura 9: Distribuição dos Retornos Mensais por Estratégia
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    strategies = ['Equal Weight', 'Markowitz', 'Risk Parity']
    
    for i, strategy in enumerate(strategies):
        if strategy in portfolio_results:
            monthly_returns = pd.Series(portfolio_results[strategy]['monthly_returns'])
            
            # Histograma
            axes[i].hist(monthly_returns * 100, bins=15, alpha=0.7, 
                        density=True, label='Dados', color='skyblue')
            
            # Curva normal teórica
            mean = monthly_returns.mean() * 100
            std = monthly_returns.std() * 100
            x = np.linspace(monthly_returns.min() * 100, 
                          monthly_returns.max() * 100, 100)
            normal_curve = stats.norm.pdf(x, mean, std)
            axes[i].plot(x, normal_curve, 'r-', linewidth=2, label='Normal Teórica')
            
            axes[i].set_title(f'Distribuição - {strategy}')
            axes[i].set_xlabel('Retorno Mensal (%)')
            axes[i].set_ylabel('Densidade')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
    
    # Remover subplot não usado
    axes[3].remove()
    
    plt.suptitle('Distribuição dos Retornos Mensais por Estratégia')
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/returns_distribution.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/returns_distribution.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 9: Distribuicao de retornos criada")

def create_drawdown_evolution(portfolio_results, returns_df):
    """
    Figura 10: Evolução dos Drawdowns das Carteiras
    """
    plt.figure(figsize=(12, 8))
    
    strategies = ['Equal Weight', 'Markowitz', 'Risk Parity']
    colors = ['blue', 'green', 'red']
    
    for i, strategy in enumerate(strategies):
        if strategy in portfolio_results:
            monthly_returns = pd.Series(portfolio_results[strategy]['monthly_returns'],
                                      index=returns_df.index)
            
            # Calcular drawdown
            cumulative_returns = (1 + monthly_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            
            plt.plot(drawdown.index, drawdown.values * 100, 
                    label=strategy, color=colors[i], linewidth=2)
    
    plt.title('Evolução dos Drawdowns das Carteiras (2018-2019)')
    plt.xlabel('Data')
    plt.ylabel('Drawdown (%)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.tight_layout()
    plt.savefig('../docs/Overleaf/figures/drawdown_evolution.png', dpi=300, bbox_inches='tight')
    plt.savefig('../docs/Overleaf/figures/drawdown_evolution.pdf', bbox_inches='tight')
    plt.close()
    
    print("OK Figura 10: Evolucao dos drawdowns criada")

def main():
    """
    Execução principal - gera todos os gráficos
    """
    print("=== GERACAO DE GRAFICOS COM DADOS REAIS DA ECONOMÁTICA ===")
    print()
    
    # Criar diretórios
    import os
    os.makedirs('../docs/Overleaf/figures', exist_ok=True)
    
    # Carregar dados
    print("Carregando dados reais...")
    returns_df, prices_df, portfolio_results, stats_df = load_real_data()
    
    # Carregar benchmark de mercado (FORÇAR Ibovespa B3 Oficial)
    print("\nCarregando benchmark Ibovespa B3 (OBRIGATÓRIO)...")
    from ibovespa_real_loader import IbovespaRealLoader
    from economatica_loader import EconomaticaLoader
    
    # ÚNICA OPÇÃO: Ibovespa B3 oficial (sem fallbacks)
    try:
        ibov_loader = IbovespaRealLoader()
        benchmark_returns = ibov_loader.load_ibovespa_data('2018-01-01', '2019-12-31')
        if benchmark_returns is not None and len(benchmark_returns) >= 10:
            benchmark_returns.benchmark_type = 'Ibovespa B3 (Oficial)'
            print("  ✓ Ibovespa B3 oficial carregado com sucesso")
        else:
            raise FileNotFoundError("Dados B3 insuficientes")
    except Exception as e:
        # ERRO CRÍTICO: TCC só aceita Ibovespa B3 oficial
        print(f"  ✗ ERRO CRÍTICO: {e}")
        print("  Sistema abortado - TCC requer exclusivamente Ibovespa B3 oficial")
        benchmark_returns = None
    
    # Gerar gráficos
    print("\nGerando graficos...")
    create_correlation_matrix(returns_df)
    create_price_evolution(prices_df)
    create_rolling_volatility(returns_df)
    create_sector_analysis(stats_df)
    create_portfolio_evolution(portfolio_results, returns_df, benchmark_returns)
    create_risk_return_plot(portfolio_results)
    create_returns_distribution(portfolio_results, returns_df)
    create_drawdown_evolution(portfolio_results, returns_df)
    
    print(f"\n=== GRAFICOS GERADOS COM SUCESSO ===")
    print("Todos os graficos foram salvos em:")
    print("- ../docs/Overleaf/figures/ (formato PNG e PDF)")
    print("\nGraficos criados:")
    print("- Figura 2: correlation_matrix.png/.pdf")
    print("- Figura 3: price_evolution.png/.pdf") 
    print("- Figura 4: rolling_volatility.png/.pdf")
    print("- Figura 6: sector_analysis.png/.pdf")
    print("- Figura 7: portfolio_evolution.png/.pdf (vs. Ibovespa B3 Oficial)")
    print("- Figura 8: risk_return_plot.png/.pdf")
    print("- Figura 9: returns_distribution.png/.pdf")
    print("- Figura 10: drawdown_evolution.png/.pdf")

if __name__ == "__main__":
    main()