"""
Análise Avançada para TCC - Estratégias de Alocação de Carteiras
Gera análises estatísticas completas, gráficos e tabelas para LaTeX
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Importa análise base
from portfolio_analysis import PortfolioAnalyzer

class AdvancedAnalyzer(PortfolioAnalyzer):
    """
    Extensão da análise básica com métricas avançadas
    """
    
    def calculate_advanced_statistics(self):
        """
        Calcula estatísticas avançadas incluindo VaR, drawdowns, etc.
        """
        print("Calculando estatísticas avançadas...")
        
        # Estatísticas básicas
        stats_basic = self.calculate_descriptive_statistics()
        
        # Métricas de risco adicionais
        advanced_metrics = []
        
        for asset in self.selected_assets.keys():
            returns_series = self.returns[asset]
            
            # VaR 95% (mensalizado e anualizado)
            var_95_monthly = np.percentile(returns_series, 5)
            var_95_annual = var_95_monthly * np.sqrt(12)
            
            # CVaR (Expected Shortfall)
            cvar_95_monthly = returns_series[returns_series <= var_95_monthly].mean()
            cvar_95_annual = cvar_95_monthly * np.sqrt(12)
            
            # Maximum Drawdown simulado
            prices_series = (1 + returns_series).cumprod()
            rolling_max = prices_series.expanding().max()
            drawdowns = (prices_series - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            # Sharpe Ratio (assumindo taxa livre de risco = 6.5% a.a.)
            risk_free_rate = 0.065
            excess_return = (returns_series.mean() * 12) - risk_free_rate
            sharpe_ratio = excess_return / (returns_series.std() * np.sqrt(12))
            
            # Teste de normalidade (Jarque-Bera)
            jb_stat, jb_pvalue = stats.jarque_bera(returns_series)
            
            advanced_metrics.append({
                'Ativo': asset,
                'VaR 95% Anual (%)': round(var_95_annual * 100, 2),
                'CVaR 95% Anual (%)': round(cvar_95_annual * 100, 2),
                'Max Drawdown (%)': round(max_drawdown * 100, 2),
                'Sharpe Ratio': round(sharpe_ratio, 3),
                'JB Estatística': round(jb_stat, 3),
                'JB p-valor': round(jb_pvalue, 4),
                'Normal?': 'Sim' if jb_pvalue > 0.05 else 'Não'
            })
        
        advanced_df = pd.DataFrame(advanced_metrics)
        return stats_basic, advanced_df
    
    def generate_risk_metrics_table(self, save_path=None):
        """
        Gera tabela completa de métricas de risco
        """
        _, advanced_df = self.calculate_advanced_statistics()
        
        if save_path:
            # Salva em formato LaTeX
            latex_table = advanced_df.to_latex(
                index=False, 
                escape=False,
                caption="Métricas Avançadas de Risco dos Ativos Selecionados (2018-2019)",
                label="tab:risk_metrics",
                column_format='|l|r|r|r|r|r|r|c|'
            )
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(latex_table)
            
            print(f"Tabela de métricas de risco salva em: {save_path}")
        
        return advanced_df
    
    def generate_returns_evolution(self, save_path=None):
        """
        Gera gráfico da evolução dos preços normalizados
        """
        # Normaliza preços para base 100
        normalized_prices = (1 + self.returns).cumprod() * 100
        
        plt.figure(figsize=(14, 10))
        
        # Gráfico principal
        for i, asset in enumerate(self.selected_assets.keys()):
            plt.plot(normalized_prices.index, normalized_prices[asset], 
                    linewidth=2, label=asset, alpha=0.8)
        
        plt.title('Evolução dos Preços Normalizados dos Ativos (Base 100 = Jan/2018)',
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Período', fontsize=12)
        plt.ylabel('Índice de Preços (Base 100)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Adiciona eventos marcantes (simulados)
        plt.axvline(pd.to_datetime('2018-10-01'), color='red', linestyle='--', 
                   alpha=0.7, label='Eleições 1º Turno')
        plt.axvline(pd.to_datetime('2018-12-01'), color='orange', linestyle='--', 
                   alpha=0.7, label='Transição Governo')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Evolução de preços salva em: {save_path}")
        
        return plt.gcf()
    
    def generate_volatility_analysis(self, save_path=None):
        """
        Gera análise de volatilidade rolling
        """
        # Calcula volatilidade rolling de 3 meses
        rolling_vol = self.returns.rolling(window=3).std() * np.sqrt(12) * 100
        
        fig, axes = plt.subplots(2, 5, figsize=(20, 12))
        axes = axes.ravel()
        
        colors = plt.cm.Set3(np.linspace(0, 1, 10))
        
        for i, asset in enumerate(self.selected_assets.keys()):
            axes[i].plot(rolling_vol.index, rolling_vol[asset], 
                        color=colors[i], linewidth=2)
            axes[i].fill_between(rolling_vol.index, rolling_vol[asset], 
                               alpha=0.3, color=colors[i])
            
            axes[i].set_title(f'{asset}\n{self.selected_assets[asset]["name"][:25]}...', 
                            fontsize=10, fontweight='bold')
            axes[i].set_xlabel('Período')
            axes[i].set_ylabel('Volatilidade Anual (%)')
            axes[i].grid(True, alpha=0.3)
            
            # Linha da volatilidade média
            mean_vol = rolling_vol[asset].mean()
            axes[i].axhline(mean_vol, color='red', linestyle='--', 
                          alpha=0.8, label=f'Média: {mean_vol:.1f}%')
            axes[i].legend(fontsize=8)
        
        plt.suptitle('Evolução da Volatilidade Rolling (3 meses) por Ativo', 
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Análise de volatilidade salva em: {save_path}")
        
        return fig
    
    def generate_correlation_evolution(self, save_path=None):
        """
        Gera análise da evolução das correlações ao longo do tempo
        """
        # Calcula correlação rolling de 6 meses entre alguns pares importantes
        important_pairs = [
            ('ITUB4', 'BBDC4', 'Bancos'),
            ('PETR4', 'VALE3', 'Commodities'),
            ('WEGE3', 'LREN3', 'Consumo'),
            ('ABEV3', 'B3SA3', 'Diversos')
        ]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.ravel()
        
        for i, (asset1, asset2, pair_name) in enumerate(important_pairs):
            # Calcula correlação rolling
            rolling_corr = self.returns[asset1].rolling(window=6).corr(self.returns[asset2])
            
            axes[i].plot(rolling_corr.index, rolling_corr, 
                        linewidth=2, color='blue', alpha=0.8)
            axes[i].fill_between(rolling_corr.index, rolling_corr, 
                               alpha=0.3, color='blue')
            
            axes[i].set_title(f'Correlação Rolling: {asset1} vs {asset2}\n({pair_name})', 
                            fontweight='bold')
            axes[i].set_xlabel('Período')
            axes[i].set_ylabel('Correlação')
            axes[i].grid(True, alpha=0.3)
            axes[i].axhline(0, color='black', linestyle='-', alpha=0.5)
            
            # Média da correlação
            mean_corr = rolling_corr.mean()
            axes[i].axhline(mean_corr, color='red', linestyle='--', 
                          alpha=0.8, label=f'Média: {mean_corr:.3f}')
            axes[i].legend()
            
            axes[i].set_ylim(-1, 1)
        
        plt.suptitle('Evolução das Correlações Rolling (6 meses) - Pares Estratégicos', 
                     fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Evolução de correlações salva em: {save_path}")
        
        return fig
    
    def generate_sector_analysis(self, save_path=None):
        """
        Gera análise por setores
        """
        # Agrupa por setor
        sector_data = {}
        for asset, info in self.selected_assets.items():
            sector = info['sector']
            if sector not in sector_data:
                sector_data[sector] = []
            sector_data[sector].append(asset)
        
        # Calcula retorno médio por setor
        sector_returns = {}
        for sector, assets in sector_data.items():
            if len(assets) > 1:
                sector_returns[sector] = self.returns[assets].mean(axis=1)
            else:
                sector_returns[sector] = self.returns[assets[0]]
        
        # Cria DataFrame
        sector_df = pd.DataFrame(sector_returns)
        
        # Gráfico de boxplot por setor
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Boxplot dos retornos mensais
        sector_df.boxplot(ax=ax1)
        ax1.set_title('Distribuição dos Retornos Mensais por Setor', fontweight='bold')
        ax1.set_xlabel('Setor')
        ax1.set_ylabel('Retorno Mensal')
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(True, alpha=0.3)
        
        # Retornos anualizados por setor
        annual_sector_returns = sector_df.mean() * 12 * 100
        annual_sector_vol = sector_df.std() * np.sqrt(12) * 100
        
        colors = plt.cm.Set2(np.linspace(0, 1, len(annual_sector_returns)))
        bars = ax2.bar(range(len(annual_sector_returns)), annual_sector_returns, 
                      color=colors, alpha=0.8)
        
        ax2.set_title('Retorno Anualizado por Setor (2018-2019)', fontweight='bold')
        ax2.set_xlabel('Setor')
        ax2.set_ylabel('Retorno Anualizado (%)')
        ax2.set_xticks(range(len(annual_sector_returns)))
        ax2.set_xticklabels(annual_sector_returns.index, rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Adiciona valores nas barras
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Análise setorial salva em: {save_path}")
        
        # Cria tabela setorial
        sector_stats = pd.DataFrame({
            'Setor': annual_sector_returns.index,
            'Retorno Anual (%)': annual_sector_returns.round(2),
            'Volatilidade Anual (%)': annual_sector_vol.round(2),
            'Sharpe Ratio': (annual_sector_returns / annual_sector_vol).round(3),
            'Número de Ativos': [len(sector_data[sector]) for sector in annual_sector_returns.index]
        })
        
        return fig, sector_stats

# Executa análises avançadas
if __name__ == "__main__":
    print("Iniciando Análises Avançadas - TCC Bruno Ballerini")
    print("=" * 60)
    
    analyzer = AdvancedAnalyzer()
    
    # Carrega dados
    returns, prices = analyzer.load_sample_data()
    
    print("\nGerando métricas avançadas de risco...")
    risk_table = analyzer.generate_risk_metrics_table(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/tables/risk_metrics.tex"
    )
    print(risk_table.to_string(index=False))
    
    print("\nGerando visualizações avançadas...")
    
    # Evolução dos preços
    price_evolution = analyzer.generate_returns_evolution(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/price_evolution.png"
    )
    
    # Análise de volatilidade
    volatility_analysis = analyzer.generate_volatility_analysis(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/volatility_rolling.png"
    )
    
    # Evolução de correlações
    correlation_evolution = analyzer.generate_correlation_evolution(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/correlation_evolution.png"
    )
    
    # Análise setorial
    sector_fig, sector_stats = analyzer.generate_sector_analysis(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/sector_analysis.png"
    )
    
    # Salva tabela setorial
    sector_latex = sector_stats.to_latex(
        index=False, escape=False,
        caption="Análise de Performance por Setor (2018-2019)",
        label="tab:sector_analysis"
    )
    
    with open("C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/tables/sector_stats.tex", 
              "w", encoding="utf-8") as f:
        f.write(sector_latex)
    
    print("Análises avançadas concluídas!")
    print("Novos arquivos gerados:")
    print("   - risk_metrics.tex")
    print("   - price_evolution.png")
    print("   - volatility_rolling.png") 
    print("   - correlation_evolution.png")
    print("   - sector_analysis.png")
    print("   - sector_stats.tex")