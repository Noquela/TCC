"""
Análise Comparativa de Estratégias de Alocação de Carteiras
Autor: Bruno Gasparoni Ballerini
TCC - Engenharia de Produção - Mackenzie

Este script implementa a análise comparativa entre as estratégias:
- Markowitz (Média-Variância)
- Equal Weight (Pesos Iguais) 
- Risk Parity (Paridade de Risco)

Para o período 2018-2019 no mercado brasileiro.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class PortfolioAnalyzer:
    """
    Classe principal para análise de carteiras seguindo metodologia acadêmica
    """
    
    def __init__(self):
        self.selected_assets = {
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
        
        self.analysis_period = ['2018', '2019']
        self.returns = None
        self.prices = None
        
    def load_sample_data(self):
        """
        Carrega dados simulados baseados em características reais do mercado brasileiro 2018-2019
        Na implementação real, carregaria da base Economática
        """
        print("Carregando dados dos ativos selecionados...")
        
        # Simulando dados mensais para demonstração
        dates = pd.date_range('2018-01-01', '2019-12-31', freq='M')
        np.random.seed(42)  # Para reprodutibilidade
        
        # Simulando retornos mensais com características do período (alta volatilidade)
        n_assets = len(self.selected_assets)
        n_periods = len(dates)
        
        # Retornos médios anualizados (baseados em dados históricos estimados)
        mean_returns = np.array([0.05, 0.08, 0.12, 0.10, 0.15, 0.18, 0.20, 0.22, 0.16, 0.08])
        volatilities = np.array([0.45, 0.35, 0.32, 0.28, 0.25, 0.30, 0.28, 0.33, 0.35, 0.25])
        
        # Gerando retornos com correlações realistas
        correlation_matrix = self.generate_realistic_correlation_matrix()
        
        # Convertendo para retornos mensais
        monthly_means = mean_returns / 12
        monthly_vols = volatilities / np.sqrt(12)
        
        # Simulando retornos correlacionados
        returns_data = np.random.multivariate_normal(
            monthly_means, 
            np.outer(monthly_vols, monthly_vols) * correlation_matrix,
            n_periods
        )
        
        # Criando DataFrame de retornos
        self.returns = pd.DataFrame(
            returns_data,
            index=dates,
            columns=list(self.selected_assets.keys())
        )
        
        # Calculando preços (simulados) a partir dos retornos
        initial_prices = np.array([20, 45, 35, 28, 15, 40, 25, 30, 35, 12])  # Preços iniciais simulados
        self.prices = pd.DataFrame(index=dates, columns=list(self.selected_assets.keys()))
        
        for i, asset in enumerate(self.selected_assets.keys()):
            price_series = [initial_prices[i]]
            for ret in returns_data[:, i]:
                price_series.append(price_series[-1] * (1 + ret))
            self.prices[asset] = price_series[1:]  # Remove o preço inicial
            
        print(f"Dados carregados: {len(self.returns)} períodos, {len(self.returns.columns)} ativos")
        return self.returns, self.prices
    
    def generate_realistic_correlation_matrix(self):
        """
        Gera matriz de correlação realista para ativos brasileiros
        """
        assets = list(self.selected_assets.keys())
        n = len(assets)
        
        # Correlações base (simuladas com base no conhecimento do mercado brasileiro)
        correlation_matrix = np.eye(n)
        
        # Bancos correlacionados entre si
        bank_indices = [2, 3, 5]  # ITUB4, BBDC4, B3SA3
        for i in bank_indices:
            for j in bank_indices:
                if i != j:
                    correlation_matrix[i, j] = 0.7
        
        # Commodities correlacionadas
        commodity_indices = [0, 1]  # PETR4, VALE3
        for i in commodity_indices:
            for j in commodity_indices:
                if i != j:
                    correlation_matrix[i, j] = 0.6
                    
        # Correlações gerais do mercado (0.3-0.5)
        for i in range(n):
            for j in range(n):
                if correlation_matrix[i, j] == 0:
                    correlation_matrix[i, j] = np.random.uniform(0.3, 0.5)
                    correlation_matrix[j, i] = correlation_matrix[i, j]
                    
        return correlation_matrix
    
    def calculate_descriptive_statistics(self):
        """
        Calcula estatísticas descritivas dos retornos dos ativos
        """
        print("Calculando estatísticas descritivas...")
        
        # Retornos anualizados
        annual_returns = self.returns.mean() * 12
        annual_volatility = self.returns.std() * np.sqrt(12)
        
        # Estatísticas adicionais
        min_returns = self.returns.min()
        max_returns = self.returns.max()
        skewness = self.returns.skew()
        kurtosis = self.returns.kurtosis()
        
        # Consolidando estatísticas
        stats_df = pd.DataFrame({
            'Ativo': list(self.selected_assets.keys()),
            'Empresa': [info['name'] for info in self.selected_assets.values()],
            'Setor': [info['sector'] for info in self.selected_assets.values()],
            'Retorno Anual (%)': (annual_returns * 100).round(2),
            'Volatilidade Anual (%)': (annual_volatility * 100).round(2),
            'Retorno Min (%)': (min_returns * 100).round(2),
            'Retorno Max (%)': (max_returns * 100).round(2),
            'Assimetria': skewness.round(3),
            'Curtose': kurtosis.round(3)
        })
        
        return stats_df
    
    def generate_correlation_heatmap(self, save_path=None):
        """
        Gera heatmap de correlações entre os ativos
        """
        correlation_matrix = self.returns.corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix, 
            annot=True, 
            cmap='RdYlBu_r', 
            center=0,
            square=True,
            fmt='.3f',
            cbar_kws={'label': 'Correlação'}
        )
        plt.title('Matriz de Correlação entre Ativos Selecionados (2018-2019)', 
                  fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('')
        plt.ylabel('')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Heatmap salvo em: {save_path}")
        
        return plt.gcf()
    
    def generate_returns_distribution(self, save_path=None):
        """
        Gera gráfico de distribuição dos retornos
        """
        fig, axes = plt.subplots(2, 5, figsize=(20, 10))
        axes = axes.ravel()
        
        for i, asset in enumerate(self.selected_assets.keys()):
            axes[i].hist(self.returns[asset] * 100, bins=15, alpha=0.7, 
                        color=sns.color_palette()[i % len(sns.color_palette())])
            axes[i].set_title(f'{asset}\n{self.selected_assets[asset]["name"][:20]}...', 
                            fontsize=10, fontweight='bold')
            axes[i].set_xlabel('Retorno Mensal (%)')
            axes[i].set_ylabel('Frequência')
            axes[i].grid(True, alpha=0.3)
            
            # Estatísticas no gráfico
            mean_ret = self.returns[asset].mean() * 100
            std_ret = self.returns[asset].std() * 100
            axes[i].axvline(mean_ret, color='red', linestyle='--', alpha=0.7, 
                          label=f'Média: {mean_ret:.1f}%')
            axes[i].legend(fontsize=8)
        
        plt.suptitle('Distribuição dos Retornos Mensais por Ativo (2018-2019)', 
                     fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Distribuições salvas em: {save_path}")
        
        return fig

# Instancia e executa análise inicial
if __name__ == "__main__":
    print("Iniciando Análise de Carteiras - TCC Bruno Ballerini")
    print("=" * 60)
    
    analyzer = PortfolioAnalyzer()
    
    # Carrega dados
    returns, prices = analyzer.load_sample_data()
    
    # Calcula estatísticas descritivas
    stats_table = analyzer.calculate_descriptive_statistics()
    print("\nEstatísticas Descritivas dos Ativos:")
    print(stats_table.to_string(index=False))
    
    # Gera gráficos
    print("\nGerando visualizações...")
    correlation_fig = analyzer.generate_correlation_heatmap(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/correlation_matrix.png"
    )
    
    distribution_fig = analyzer.generate_returns_distribution(
        save_path="C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/images/returns_distribution.png"
    )
    
    # Salva estatísticas em formato LaTeX
    latex_table = stats_table.to_latex(index=False, escape=False, 
                                      caption="Estatísticas Descritivas dos Ativos Selecionados (2018-2019)",
                                      label="tab:estatisticas_descritivas")
    
    with open("C:/Users/BrunoGaspariniBaller/OneDrive - HAND/Documentos/TCC/Overleaf/tables/descriptive_stats.tex", "w", encoding="utf-8") as f:
        f.write(latex_table)
    
    print("Análise inicial concluída!")
    print("Arquivos gerados:")
    print("   - correlation_matrix.png")
    print("   - returns_distribution.png") 
    print("   - descriptive_stats.tex")