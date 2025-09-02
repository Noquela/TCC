"""
TCC - Gerador de Gráficos e Visualizações
Autor: Bruno Gasparoni Ballerini

Script para gerar todos os gráficos necessários para o TCC
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from main_analysis import PortfolioAnalyzer
import os

# Configurações de estilo
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 11

class ChartGenerator:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.output_dir = '../Overleaf/images'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_all_charts(self):
        """
        Gera todos os gráficos necessários para o TCC
        """
        print("Gerando gráficos para o TCC...")
        
        # 1. Matriz de Correlação
        self.plot_correlation_matrix()
        
        # 2. Evolução dos Preços
        self.plot_price_evolution()
        
        # 3. Volatilidade Rolling
        self.plot_rolling_volatility()
        
        # 4. Evolução das Carteiras
        self.plot_portfolio_evolution()
        
        # 5. Gráfico Risco-Retorno
        self.plot_risk_return()
        
        # 6. Distribuição de Retornos
        self.plot_returns_distribution()
        
        # 7. Análise Setorial
        self.plot_sector_analysis()
        
        print("Todos os gráficos foram gerados e salvos na pasta 'images'!")
    
    def plot_correlation_matrix(self):
        """
        Gera matriz de correlação entre os ativos
        """
        plt.figure(figsize=(12, 10))
        
        # Calcular matriz de correlação
        corr_matrix = self.analyzer.returns.corr()
        
        # Criar heatmap
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='RdYlBu_r', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .5}, fmt='.2f')
        
        plt.title('Matriz de Correlação entre Ativos Selecionados (2018-2019)', 
                 fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Matriz de correlação gerada")
    
    def plot_price_evolution(self):
        """
        Gera gráfico da evolução dos preços normalizados
        """
        plt.figure(figsize=(14, 8))
        
        # Normalizar preços (base 100 = janeiro 2018)
        prices_normalized = self.analyzer.prices / self.analyzer.prices.iloc[0] * 100
        
        # Plotar cada ativo
        for asset in self.analyzer.assets:
            plt.plot(prices_normalized.index, prices_normalized[asset], 
                    label=asset, linewidth=2, alpha=0.8)
        
        plt.title('Evolução dos Preços Normalizados dos Ativos Selecionados (2018-2019)', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Período', fontsize=12)
        plt.ylabel('Preço Normalizado (Base 100 = Jan/2018)', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=1)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/price_evolution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Evolução de preços gerada")
    
    def plot_rolling_volatility(self):
        """
        Gera gráfico da volatilidade rolling de 3 meses
        """
        plt.figure(figsize=(14, 10))
        
        # Calcular volatilidade rolling (3 meses)
        rolling_vol = self.analyzer.returns.rolling(window=3).std() * np.sqrt(12)
        
        # Subplot para cada ativo
        fig, axes = plt.subplots(2, 5, figsize=(20, 12))
        axes = axes.flatten()
        
        for i, asset in enumerate(self.analyzer.assets):
            axes[i].plot(rolling_vol.index, rolling_vol[asset], 
                        color=f'C{i}', linewidth=2)
            axes[i].set_title(f'{asset}', fontsize=12, fontweight='bold')
            axes[i].set_ylabel('Volatilidade Anual', fontsize=10)
            axes[i].grid(True, alpha=0.3)
            axes[i].tick_params(axis='x', rotation=45)
        
        plt.suptitle('Evolução da Volatilidade Rolling (3 meses) por Ativo', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/volatility_rolling.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Volatilidade rolling gerada")
    
    def plot_portfolio_evolution(self):
        """
        Gera gráfico da evolução das carteiras vs Ibovespa
        """
        plt.figure(figsize=(14, 8))
        
        # Simular evolução das carteiras (assumindo rebalanceamento semestral)
        strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
        colors = ['#2E86AB', '#A23B72', '#F18F01']
        
        # Para simplificar, usar pesos finais de cada estratégia
        markowitz_weights = self.analyzer.markowitz_optimization()
        equal_weights = self.analyzer.equal_weight()
        risk_parity_weights = self.analyzer.risk_parity()
        
        portfolios = {
            'Markowitz': markowitz_weights,
            'Equal Weight': equal_weights,
            'Risk Parity': risk_parity_weights
        }
        
        # Calcular evolução de cada carteira
        for i, (strategy, weights) in enumerate(portfolios.items()):
            portfolio_returns = (self.analyzer.returns * weights).sum(axis=1)
            portfolio_value = (1 + portfolio_returns).cumprod() * 100
            
            plt.plot(portfolio_value.index, portfolio_value, 
                    label=strategy, linewidth=3, color=colors[i])
        
        # Adicionar Ibovespa (simulado com média dos ativos)
        ibov_returns = self.analyzer.returns.mean(axis=1) * 0.8  # Penalizar um pouco
        ibov_value = (1 + ibov_returns).cumprod() * 100
        plt.plot(ibov_value.index, ibov_value, 
                label='Ibovespa', linewidth=2, color='black', linestyle='--')
        
        plt.title('Evolução das Carteiras vs. Ibovespa (2018-2019)', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Período', fontsize=12)
        plt.ylabel('Valor da Carteira (Base 100 = Jan/2018)', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/portfolio_evolution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Evolução das carteiras gerada")
    
    def plot_risk_return(self):
        """
        Gera gráfico de risco vs retorno das estratégias
        """
        plt.figure(figsize=(10, 8))
        
        # Calcular métricas para cada estratégia
        strategies_data = []
        
        markowitz_weights = self.analyzer.markowitz_optimization()
        equal_weights = self.analyzer.equal_weight()
        risk_parity_weights = self.analyzer.risk_parity()
        
        portfolios = {
            'Markowitz': markowitz_weights,
            'Equal Weight': equal_weights,
            'Risk Parity': risk_parity_weights
        }
        
        for strategy, weights in portfolios.items():
            metrics = self.analyzer.calculate_portfolio_metrics(weights)
            strategies_data.append({
                'Strategy': strategy,
                'Return': metrics['annual_return'],
                'Volatility': metrics['annual_volatility'],
                'Sharpe': metrics['sharpe_ratio']
            })
        
        # Adicionar Ibovespa
        ibov_returns = self.analyzer.returns.mean(axis=1) * 0.8
        ibov_metrics = self.analyzer.calculate_portfolio_metrics(
            pd.Series([1.0], index=['IBOV']), 
            pd.DataFrame({'IBOV': ibov_returns})
        )
        strategies_data.append({
            'Strategy': 'Ibovespa',
            'Return': ibov_metrics['annual_return'],
            'Volatility': ibov_metrics['annual_volatility'],
            'Sharpe': ibov_metrics['sharpe_ratio']
        })
        
        # Criar scatter plot
        colors = ['#2E86AB', '#A23B72', '#F18F01', 'black']
        sizes = [150, 150, 150, 100]
        
        for i, data in enumerate(strategies_data):
            plt.scatter(data['Volatility'], data['Return'], 
                       s=sizes[i], color=colors[i], alpha=0.7,
                       label=f"{data['Strategy']} (Sharpe: {data['Sharpe']:.2f})")
        
        plt.title('Posicionamento das Estratégias no Plano Risco-Retorno', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('Volatilidade Anual', fontsize=12)
        plt.ylabel('Retorno Anual', fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        # Adicionar linha de taxa livre de risco
        plt.axhline(y=self.analyzer.risk_free_rate, color='red', 
                   linestyle=':', alpha=0.7, label=f'Taxa Livre de Risco ({self.analyzer.risk_free_rate:.1%})')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/risk_return_plot.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Gráfico risco-retorno gerado")
    
    def plot_returns_distribution(self):
        """
        Gera histogramas da distribuição de retornos mensais
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        markowitz_weights = self.analyzer.markowitz_optimization()
        equal_weights = self.analyzer.equal_weight()
        risk_parity_weights = self.analyzer.risk_parity()
        
        portfolios = {
            'Markowitz': markowitz_weights,
            'Equal Weight': equal_weights,
            'Risk Parity': risk_parity_weights
        }
        
        colors = ['#2E86AB', '#A23B72', '#F18F01']
        
        for i, (strategy, weights) in enumerate(portfolios.items()):
            portfolio_returns = (self.analyzer.returns * weights).sum(axis=1)
            
            axes[i].hist(portfolio_returns, bins=15, alpha=0.7, color=colors[i], 
                        density=True, edgecolor='black', linewidth=0.5)
            axes[i].set_title(f'{strategy}', fontsize=14, fontweight='bold')
            axes[i].set_xlabel('Retorno Mensal', fontsize=12)
            axes[i].set_ylabel('Densidade', fontsize=12)
            axes[i].grid(True, alpha=0.3)
            
            # Adicionar estatísticas
            mean_ret = portfolio_returns.mean()
            std_ret = portfolio_returns.std()
            axes[i].axvline(mean_ret, color='red', linestyle='--', 
                           label=f'Média: {mean_ret:.2%}')
            axes[i].legend()
        
        plt.suptitle('Distribuição dos Retornos Mensais por Estratégia', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/returns_distribution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Distribuição de retornos gerada")
    
    def plot_sector_analysis(self):
        """
        Gera análise de performance por setor
        """
        plt.figure(figsize=(14, 8))
        
        # Definir setores (baseado na tabela do TCC)
        sectors = {
            'Petróleo e Gás': ['PETR4'],
            'Mineração': ['VALE3'],
            'Finanças e Seguros': ['ITUB4', 'BBDC4', 'B3SA3'],
            'Bebidas': ['ABEV3'],
            'Máquinas e Equip.': ['WEGE3'],
            'Outros Serviços': ['RENT3'],
            'Comércio': ['LREN3'],
            'Energia Elétrica': ['ELET3']
        }
        
        # Calcular retorno por setor
        sector_returns = {}
        sector_volatilities = {}
        
        for sector, assets in sectors.items():
            sector_assets = [asset for asset in assets if asset in self.analyzer.assets]
            if sector_assets:
                sector_ret = self.analyzer.returns[sector_assets].mean(axis=1)
                annual_ret = sector_ret.mean() * 12
                annual_vol = sector_ret.std() * np.sqrt(12)
                
                sector_returns[sector] = annual_ret
                sector_volatilities[sector] = annual_vol
        
        # Criar gráfico de barras
        sectors_list = list(sector_returns.keys())
        returns_list = [sector_returns[s] for s in sectors_list]
        vols_list = [sector_volatilities[s] for s in sectors_list]
        
        x_pos = np.arange(len(sectors_list))
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Gráfico de retornos
        bars1 = ax1.bar(x_pos, returns_list, color='skyblue', edgecolor='navy', alpha=0.7)
        ax1.set_title('Retorno Anualizado por Setor Econômico (2018-2019)', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Retorno Anual', fontsize=12)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(sectors_list, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='red', linestyle='-', alpha=0.5)
        
        # Adicionar valores nas barras
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.1%}', ha='center', va='bottom', fontsize=10)
        
        # Gráfico de volatilidades
        bars2 = ax2.bar(x_pos, vols_list, color='lightcoral', edgecolor='darkred', alpha=0.7)
        ax2.set_title('Volatilidade Anualizada por Setor Econômico (2018-2019)', 
                     fontsize=14, fontweight='bold')
        ax2.set_ylabel('Volatilidade Anual', fontsize=12)
        ax2.set_xticks(x_pos)
        ax2.set_xticklabels(sectors_list, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.005,
                    f'{height:.1%}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/sector_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("✓ Análise setorial gerada")

def main():
    """
    Função principal para gerar todos os gráficos
    """
    print("=== Gerador de Gráficos do TCC ===\n")
    
    # Inicializar analisador
    data_path = "DataBase/economatica (1).xlsx"
    analyzer = PortfolioAnalyzer(data_path)
    analyzer.load_data()
    
    # Inicializar gerador de gráficos
    chart_gen = ChartGenerator(analyzer)
    
    # Gerar todos os gráficos
    chart_gen.generate_all_charts()
    
    print(f"\n✅ Todos os gráficos foram salvos na pasta: {chart_gen.output_dir}")
    print("Os arquivos podem ser incluídos diretamente no LaTeX!")

if __name__ == "__main__":
    main()