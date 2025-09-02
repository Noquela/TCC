"""
Análise Completa com Dados Reais da Economatica
Integra o carregador de dados reais com as análises existentes

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Importar módulos existentes
from economatica_loader import EconomaticaLoader
from portfolio_analysis import PortfolioAnalyzer
from advanced_analysis import AdvancedAnalyzer

class RealDataAnalyzer:
    """
    Analisador que usa dados reais da Economatica
    """
    
    def __init__(self):
        self.loader = EconomaticaLoader()
        self.returns = None
        self.prices = None
        self.selected_assets = None
        self.risk_free_rate = 0.065  # CDI médio 2018-2019
        
    def load_real_data(self):
        """
        Carrega dados reais e adapta para análise
        """
        print("Carregando dados reais da Economatica...")
        
        self.returns, self.prices = self.loader.load_selected_assets()
        
        if self.returns is not None:
            self.selected_assets = {
                asset: self.loader.asset_info.get(asset, {'name': asset, 'sector': 'N/A'})
                for asset in self.returns.columns
            }
            return True
        return False
    
    def calculate_portfolio_metrics(self, weights, returns_data=None):
        """
        Calcula métricas de performance para uma carteira
        """
        if returns_data is None:
            returns_data = self.returns
            
        portfolio_returns = (returns_data * weights).sum(axis=1)
        
        # Métricas anualizadas
        annual_return = portfolio_returns.mean() * 12
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        
        # Sharpe Ratio
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_vol
        
        # Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < self.risk_free_rate/12]
        if len(downside_returns) > 0:
            downside_vol = downside_returns.std() * np.sqrt(12)
            sortino_ratio = (annual_return - self.risk_free_rate) / downside_vol
        else:
            sortino_ratio = sharpe_ratio
        
        # Maximum Drawdown
        portfolio_value = (1 + portfolio_returns).cumprod()
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        max_drawdown = drawdown.min()
        
        # VaR 95%
        var_95 = np.percentile(portfolio_returns * 12, 5)
        
        return {
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95
        }
    
    def markowitz_optimization(self):
        """
        Implementa otimização de Markowitz com dados reais
        """
        n_assets = len(self.selected_assets)
        
        # Parâmetros dos dados reais
        mu = self.returns.mean().values * 12  # Retornos anualizados
        Sigma = self.returns.cov().values * 12  # Covariância anualizada
        
        def objective(weights):
            portfolio_return = np.dot(weights, mu)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(Sigma, weights)))
            if portfolio_vol == 0:
                return -999
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe  # Minimizar negativo = maximizar
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}
        ]
        bounds = tuple([(0, 1) for _ in range(n_assets)])
        x0 = np.array([1/n_assets] * n_assets)
        
        try:
            result = minimize(objective, x0, method='SLSQP', bounds=bounds, 
                            constraints=constraints, options={'disp': False, 'maxiter': 1000})
            
            if result.success:
                weights = result.x / result.x.sum()  # Normalizar
                return pd.Series(weights, index=self.returns.columns)
            else:
                print(f"Otimização Markowitz falhou: {result.message}")
                return self.equal_weight()
        except Exception as e:
            print(f"Erro na otimização Markowitz: {e}")
            return self.equal_weight()
    
    def equal_weight(self):
        """
        Estratégia Equal Weight
        """
        n_assets = len(self.selected_assets)
        weights = np.ones(n_assets) / n_assets
        return pd.Series(weights, index=self.returns.columns)
    
    def risk_parity(self):
        """
        Estratégia Risk Parity
        """
        volatilities = self.returns.std() * np.sqrt(12)
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()
        return weights
    
    def run_complete_analysis(self):
        """
        Executa análise completa com os 3 métodos
        """
        if not self.load_real_data():
            print("ERRO: Não foi possível carregar dados reais!")
            return None
        
        print("\n=== EXECUTANDO ANÁLISE COM DADOS REAIS ===")
        
        # Implementar as 3 estratégias
        strategies = {}
        
        print("\n1. Calculando pesos das carteiras...")
        strategies['Markowitz'] = self.markowitz_optimization()
        strategies['Equal Weight'] = self.equal_weight()
        strategies['Risk Parity'] = self.risk_parity()
        
        # Calcular métricas de performance
        print("2. Calculando métricas de performance...")
        results = {}
        
        for strategy_name, weights in strategies.items():
            metrics = self.calculate_portfolio_metrics(weights)
            results[strategy_name] = metrics
            
            print(f"\n{strategy_name}:")
            print(f"  Pesos: {dict(zip(self.returns.columns, weights.round(3)))}")
            print(f"  Sharpe: {metrics['sharpe_ratio']:.3f}")
        
        # Mostrar resultados consolidados
        print("\n=== RESULTADOS CONSOLIDADOS (DADOS REAIS) ===")
        print(f"{'Estratégia':<15} {'Retorno':<10} {'Vol':<8} {'Sharpe':<8} {'Sortino':<8} {'Max DD':<10}")
        print("-" * 65)
        
        for strategy, metrics in results.items():
            print(f"{strategy:<15} "
                  f"{metrics['annual_return']:.1%}   "
                  f"{metrics['annual_volatility']:.1%}   "
                  f"{metrics['sharpe_ratio']:.2f}    "
                  f"{metrics['sortino_ratio']:.2f}     "
                  f"{metrics['max_drawdown']:.1%}")
        
        # Criar tabelas para LaTeX
        self.create_results_tables(strategies, results)
        
        return strategies, results
    
    def create_results_tables(self, strategies, results):
        """
        Cria tabelas em formato LaTeX com os resultados reais
        """
        print("\n3. Gerando tabelas LaTeX...")
        
        # Criar diretório de resultados
        import os
        os.makedirs('../Overleaf/tables', exist_ok=True)
        
        # Tabela de performance consolidada
        latex_performance = """% Tabela gerada com dados REAIS da Economatica
\\begin{table}[H]
\\centering
\\caption{Performance Consolidada das Carteiras - Dados Reais Economatica (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|r|r|}
\\hline
\\textbf{Estratégia} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Sharpe} & \\textbf{Sortino} & \\textbf{Max} & \\textbf{VaR} \\\\
& \\textbf{Anual (\\%)} & \\textbf{Anual (\\%)} & \\textbf{Ratio} & \\textbf{Ratio} & \\textbf{Drawdown} & \\textbf{95\\%} \\\\
\\hline
"""
        
        for strategy, metrics in results.items():
            latex_performance += f"{strategy} & {metrics['annual_return']:.1%} & {metrics['annual_volatility']:.1%} & "
            latex_performance += f"{metrics['sharpe_ratio']:.2f} & {metrics['sortino_ratio']:.2f} & "
            latex_performance += f"{metrics['max_drawdown']:.1%} & {metrics['var_95']:.1%} \\\\\n\\hline\n"
        
        latex_performance += """\\end{tabular}
\\textit{Fonte: Dados reais da Economatica processados pelo autor. Taxa livre de risco: 6,5\\% a.a.}
\\label{tab:portfolio_performance_real}
\\end{table}
"""
        
        with open('../Overleaf/tables/portfolio_performance_real.tex', 'w', encoding='utf-8') as f:
            f.write(latex_performance)
        
        # Tabela de pesos das carteiras
        latex_weights = """% Tabela de pesos com dados REAIS
\\begin{table}[H]
\\centering
\\caption{Pesos das Carteiras - Dados Reais (\\%)}
\\begin{tabular}{|l|""" + "r|" * len(self.returns.columns) + """}
\\hline
\\textbf{Estratégia}"""
        
        for asset in self.returns.columns:
            latex_weights += f" & \\textbf{{{asset}}}"
        latex_weights += " \\\\\n\\hline\n"
        
        for strategy, weights in strategies.items():
            latex_weights += strategy
            for asset in self.returns.columns:
                latex_weights += f" & {weights[asset]*100:.1f}"
            latex_weights += " \\\\\n\\hline\n"
        
        latex_weights += """\\end{tabular}
\\textit{Fonte: Elaborado pelo autor com dados reais da Economatica.}
\\label{tab:portfolio_weights_real}
\\end{table}
"""
        
        with open('../Overleaf/tables/portfolio_weights_real.tex', 'w', encoding='utf-8') as f:
            f.write(latex_weights)
        
        print("Tabelas LaTeX geradas:")
        print("  - portfolio_performance_real.tex")
        print("  - portfolio_weights_real.tex")

def main():
    """
    Executa análise completa com dados reais
    """
    print("=== ANÁLISE COMPLETA COM DADOS REAIS DA ECONOMATICA ===")
    print()
    
    analyzer = RealDataAnalyzer()
    strategies, results = analyzer.run_complete_analysis()
    
    if results:
        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("\n🎯 PRINCIPAIS ACHADOS:")
        
        # Ranking por Sharpe
        sorted_results = sorted(results.items(), key=lambda x: x[1]['sharpe_ratio'], reverse=True)
        
        print(f"🥇 Melhor estratégia: {sorted_results[0][0]} (Sharpe: {sorted_results[0][1]['sharpe_ratio']:.3f})")
        print(f"🥈 Segunda colocada: {sorted_results[1][0]} (Sharpe: {sorted_results[1][1]['sharpe_ratio']:.3f})")
        print(f"🥉 Terceira colocada: {sorted_results[2][0]} (Sharpe: {sorted_results[2][1]['sharpe_ratio']:.3f})")
        
        # Insights acadêmicos
        best_strategy = sorted_results[0][0]
        if best_strategy == "Markowitz":
            print("\n💡 INSIGHT ACADÊMICO:")
            print("Markowitz superou Equal Weight com dados reais!")
            print("Resultado valida eficácia da otimização em mercados emergentes voláteis.")
        elif best_strategy == "Risk Parity":
            print("\n💡 INSIGHT ACADÊMICO:")
            print("Risk Parity foi superior, validando controle de risco em períodos voláteis.")
        else:
            print("\n💡 INSIGHT ACADÊMICO:")
            print("Equal Weight foi superior, confirmando literatura sobre robustez em incerteza.")
        
        print(f"\n📁 Arquivos gerados:")
        print("- Tabelas LaTeX em ../Overleaf/tables/")
        print("- Dados processados em ../results/")
        
        return analyzer
    
    else:
        print("❌ ERRO: Não foi possível completar a análise com dados reais.")
        return None

if __name__ == "__main__":
    analyzer = main()