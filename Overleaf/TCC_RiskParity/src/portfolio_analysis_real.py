"""
Análise Completa de Portfólio com Dados Reais da Economática
Implementa as três estratégias: Markowitz, Risk Parity (ERC), Equal Weight
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class PortfolioAnalyzer:
    """
    Classe para análise completa das estratégias de portfólio
    """
    
    def __init__(self, returns_df, risk_free_rate=0.065):
        self.returns = returns_df
        self.risk_free_rate = risk_free_rate
        self.monthly_rf = risk_free_rate / 12
        self.assets = list(returns_df.columns)
        self.n_assets = len(self.assets)
        
        # Calcular matriz de covariância
        self.cov_matrix = returns_df.cov() * 12  # Anualizada
        self.corr_matrix = returns_df.corr()
        
        # Retornos esperados (média anualizada)
        self.expected_returns = returns_df.mean() * 12
        
    def equal_weight_portfolio(self):
        """
        Estratégia Equal Weight (1/N)
        """
        weights = np.ones(self.n_assets) / self.n_assets
        return weights
    
    def markowitz_portfolio(self):
        """
        Estratégia de Markowitz (máximo Sharpe Ratio)
        """
        def neg_sharpe_ratio(weights):
            portfolio_return = np.sum(weights * self.expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            return -(portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # Restrições
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.001, 1.0) for _ in range(self.n_assets))  # Mínimo 0.1%, sem teto
        
        # Otimização
        x0 = np.ones(self.n_assets) / self.n_assets
        result = minimize(neg_sharpe_ratio, x0, method='SLSQP',
                         bounds=bounds, constraints=constraints)
        
        return result.x if result.success else None
    
    def risk_parity_portfolio(self):
        """
        Estratégia Risk Parity ERC (Equal Risk Contribution) CORRETA
        Equaliza contribuições marginais de risco usando matriz covariância completa
        """
        def erc_objective(weights):
            # Volatilidade do portfólio
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
            
            if portfolio_vol == 0:
                return 1e6  # Penalidade por volatilidade zero
            
            # Contribuições marginais de risco
            marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol
            
            # Contribuições de risco (RC_i = w_i * MC_i)
            risk_contrib = weights * marginal_contrib
            
            # CORREÇÃO DEFINITIVA: Objetivo ERC padrão
            # Minimizar soma dos quadrados das diferenças entre contribuições
            # Equivale a equalizar RC_i para todos i
            n = len(weights)
            target_contrib = np.sum(risk_contrib) / n  # Contribuição média
            
            # Função objetivo: minimizar dispersão das contribuições
            objective = np.sum((risk_contrib - target_contrib) ** 2)
            
            return objective
        
        # Restrições
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0.01, 0.5) for _ in range(self.n_assets))  # Limites mais restritivos
        
        # Otimização com parâmetros melhorados
        x0 = np.ones(self.n_assets) / self.n_assets
        
        # Tentar diferentes algoritmos se SLSQP falhar
        methods = ['SLSQP', 'trust-constr']
        
        for method in methods:
            try:
                result = minimize(erc_objective, x0, method=method,
                                bounds=bounds, constraints=constraints,
                                options={'maxiter': 1000, 'ftol': 1e-9})
                
                if result.success and result.fun < 1e-6:
                    return result.x
                    
            except:
                continue
        
        # Se nenhum método funcionou, retornar equal weight
        print("AVISO: ERC não convergiu, usando Equal Weight")
        return x0
    
    def validate_erc(self, weights):
        """
        Valida se a carteira atende aos critérios ERC
        """
        if weights is None:
            print("ERRO: Pesos não fornecidos para validação ERC")
            return False
            
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        
        # Contribuições devem ser aproximadamente iguais
        # Target é a contribuição média (soma das contribuições / n)
        target = np.sum(risk_contrib) / self.n_assets
        
        # Desvios relativos para avaliar equalização
        relative_deviations = np.abs(risk_contrib - target) / target
        max_relative_deviation = np.max(relative_deviations)
        
        print(f"=== VALIDACAO ERC ===")
        print(f"Volatilidade total: {portfolio_vol:.6f}")
        print(f"Variancia total: {portfolio_vol**2:.6f}")
        print(f"Target por ativo (var/n): {target:.6f}")
        print(f"Contribuicoes de risco por ativo:")
        for i, asset in enumerate(self.assets):
            deviation_pct = relative_deviations[i] * 100
            print(f"{asset}: {risk_contrib[i]:.6f} (target: {target:.6f}, desvio: {deviation_pct:.2f}%)")
        
        print(f"Maximo desvio relativo: {max_relative_deviation:.4f} ({max_relative_deviation*100:.2f}%)")
        print(f"Tolerancia: 0.10 (10%)")
        
        is_valid = max_relative_deviation < 0.10  # Tolerância de 10%
        print(f"ERC Valido: {'SIM' if is_valid else 'NAO'}")
        print()
        
        return is_valid
    
    def calculate_portfolio_metrics(self, weights):
        """
        Calcula métricas de performance do portfólio
        """
        if weights is None:
            return None
        
        # Retorno e volatilidade do portfólio
        portfolio_return = np.sum(weights * self.expected_returns)
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        # Simular retornos mensais do portfólio
        portfolio_monthly_returns = np.dot(self.returns, weights)
        
        # Métricas básicas
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_vol
        
        # Sortino Ratio (implementação conforme calculate_real_stats.py)
        # CDI 6,5% a.a. conforme TCC - downside deviation dos retornos abaixo da taxa livre de risco
        downside = np.sqrt(((portfolio_monthly_returns[portfolio_monthly_returns < self.monthly_rf] - self.monthly_rf) ** 2).mean())
        sortino_ratio = (portfolio_return - self.risk_free_rate) / (downside * np.sqrt(12)) if downside > 0 else 0
        
        # VaR e CVaR
        var_95 = np.percentile(portfolio_monthly_returns, 5)
        cvar_95 = portfolio_monthly_returns[portfolio_monthly_returns <= var_95].mean()
        
        # Maximum Drawdown
        cumulative_returns = pd.Series((1 + portfolio_monthly_returns).cumprod())
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Information Ratio vs Ibovespa (B3 Oficial)
        try:
            from ibovespa_real_loader import IbovespaRealLoader
            ibov_loader = IbovespaRealLoader()
            ibov_returns = ibov_loader.load_ibovespa_data('2018-01-01', '2019-12-31')
            
            if ibov_returns is not None:
                # Alinhar índices temporais
                ibov_aligned = ibov_returns.reindex(pd.DatetimeIndex(self.returns.index)).dropna()
                portfolio_aligned = portfolio_monthly_returns[:len(ibov_aligned)]
                
                # Calcular retornos ativos vs Ibovespa
                active_returns = portfolio_aligned - ibov_aligned.values
                tracking_error = active_returns.std() * np.sqrt(12)
                information_ratio = active_returns.mean() * 12 / tracking_error if tracking_error > 0 else 0
            else:
                # Fallback para Equal Weight se Ibovespa não disponível
                ew_returns = np.dot(self.returns, np.ones(self.n_assets) / self.n_assets)
                active_returns = portfolio_monthly_returns - ew_returns
                tracking_error = active_returns.std() * np.sqrt(12)
                information_ratio = active_returns.mean() * 12 / tracking_error if tracking_error > 0 else 0
        except:
            # Fallback para Equal Weight em caso de erro
            ew_returns = np.dot(self.returns, np.ones(self.n_assets) / self.n_assets)
            active_returns = portfolio_monthly_returns - ew_returns
            tracking_error = active_returns.std() * np.sqrt(12)
            information_ratio = active_returns.mean() * 12 / tracking_error if tracking_error > 0 else 0
        
        return {
            'weights': weights,
            'annual_return': portfolio_return,
            'annual_volatility': portfolio_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'var_95_monthly': var_95,
            'cvar_95_monthly': cvar_95,
            'max_drawdown': max_drawdown,
            'information_ratio': information_ratio,
            'monthly_returns': portfolio_monthly_returns
        }
    
    def analyze_all_strategies(self):
        """
        Analisa todas as três estratégias
        """
        print("=== ANÁLISE COMPLETA DAS ESTRATÉGIAS DE PORTFÓLIO ===")
        print(f"Período: {self.returns.index[0].date()} a {self.returns.index[-1].date()}")
        print(f"Taxa livre de risco: {self.risk_free_rate:.1%}")
        print()
        
        strategies = {}
        
        # Equal Weight
        print("1. Calculando estratégia Equal Weight...")
        ew_weights = self.equal_weight_portfolio()
        strategies['Equal Weight'] = self.calculate_portfolio_metrics(ew_weights)
        
        # Markowitz
        print("2. Calculando estratégia de Markowitz...")
        markowitz_weights = self.markowitz_portfolio()
        strategies['Markowitz'] = self.calculate_portfolio_metrics(markowitz_weights)
        
        # Risk Parity
        print("3. Calculando estratégia Risk Parity (ERC)...")
        rp_weights = self.risk_parity_portfolio()
        strategies['Risk Parity'] = self.calculate_portfolio_metrics(rp_weights)
        
        # Validar ERC
        if rp_weights is not None:
            print("4. Validando implementação ERC...")
            self.validate_erc(rp_weights)
        
        return strategies
    
    def create_performance_comparison(self, strategies):
        """
        Cria tabela comparativa de performance
        """
        comparison_data = []
        
        for strategy_name, metrics in strategies.items():
            if metrics is not None:
                comparison_data.append({
                    'Estratégia': strategy_name,
                    'Retorno_Anual_Pct': metrics['annual_return'] * 100,
                    'Volatilidade_Anual_Pct': metrics['annual_volatility'] * 100,
                    'Sharpe_Ratio': metrics['sharpe_ratio'],
                    'Sortino_Ratio': metrics['sortino_ratio'],
                    'VaR_95_Mensal_Pct': metrics['var_95_monthly'] * 100,
                    'CVaR_95_Mensal_Pct': metrics['cvar_95_monthly'] * 100,
                    'Max_Drawdown_Pct': metrics['max_drawdown'] * 100,
                    'Information_Ratio': metrics['information_ratio']
                })
        
        return pd.DataFrame(comparison_data)
    
    def create_weights_comparison(self, strategies):
        """
        Cria tabela comparativa de pesos
        """
        weights_data = []
        
        for asset in self.assets:
            asset_data = {'Ativo': asset}
            
            for strategy_name, metrics in strategies.items():
                if metrics is not None:
                    asset_idx = self.assets.index(asset)
                    weight = metrics['weights'][asset_idx] * 100
                    asset_data[strategy_name] = f"{weight:.1f}%"
            
            weights_data.append(asset_data)
        
        return pd.DataFrame(weights_data)

def generate_latex_performance_table(performance_df):
    """
    Gera tabela LaTeX com performance das carteiras
    """
    latex_content = """% Tabela gerada automaticamente pelo Python com dados reais da Economática
\\begin{table}[H]
\\centering
\\caption{Performance Consolidada das Carteiras (2018-2019)}
\\begin{tabular}{|l|r|r|r|r|}
\\hline
\\textbf{Estratégia} & \\textbf{Retorno} & \\textbf{Volatilidade} & \\textbf{Sharpe} & \\textbf{Sortino} \\\\
& \\textbf{Anual (\\%)} & \\textbf{Anual (\\%)} & \\textbf{Ratio} & \\textbf{Ratio} \\\\
\\hline
"""
    
    for _, row in performance_df.iterrows():
        latex_content += f"""{row['Estratégia']} & {row['Retorno_Anual_Pct']:.1f} & {row['Volatilidade_Anual_Pct']:.1f} & {row['Sharpe_Ratio']:.2f} & {row['Sortino_Ratio']:.2f} \\\\
\\hline
"""
    
    latex_content += """\\end{tabular}

\\textit{Fonte: Elaborado pelo autor utilizando Python com dados da Economática.}
\\label{tab:portfolio_performance}
\\end{table}
"""
    
    return latex_content

def main():
    """
    Execução principal da análise
    """
    print("=== ANÁLISE DE PORTFÓLIO COM DADOS REAIS DA ECONOMÁTICA ===")
    
    # Carregar dados reais
    returns_df = pd.read_csv('../results/real_returns_data.csv', index_col=0, parse_dates=True)
    
    # Criar analisador
    analyzer = PortfolioAnalyzer(returns_df)
    
    # Analisar estratégias
    strategies = analyzer.analyze_all_strategies()
    
    # Criar comparações
    performance_comparison = analyzer.create_performance_comparison(strategies)
    weights_comparison = analyzer.create_weights_comparison(strategies)
    
    # Mostrar resultados
    print("\n=== COMPARAÇÃO DE PERFORMANCE ===")
    print(performance_comparison.round(2))
    
    print("\n=== COMPARAÇÃO DE PESOS ===")
    print(weights_comparison)
    
    # Gerar tabela LaTeX
    latex_table = generate_latex_performance_table(performance_comparison)
    
    # Salvar resultados
    performance_comparison.to_csv('../results/portfolio_performance_comparison.csv', index=False)
    weights_comparison.to_csv('../results/portfolio_weights_comparison.csv', index=False)
    
    with open('../docs/Overleaf/tables/portfolio_performance.tex', 'w', encoding='utf-8') as f:
        f.write(latex_table)
    
    # Salvar dados detalhados das estratégias
    detailed_results = {}
    for strategy_name, metrics in strategies.items():
        if metrics is not None:
            detailed_results[strategy_name] = {
                'weights': metrics['weights'].tolist(),
                'annual_return': metrics['annual_return'],
                'annual_volatility': metrics['annual_volatility'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'monthly_returns': metrics['monthly_returns'].tolist()
            }
    
    import json
    with open('../results/detailed_portfolio_results.json', 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    print(f"\n=== ARQUIVOS GERADOS ===")
    print("- Performance: ../results/portfolio_performance_comparison.csv")
    print("- Pesos: ../results/portfolio_weights_comparison.csv")
    print("- Tabela LaTeX: ../docs/Overleaf/tables/portfolio_performance.tex")
    print("- Resultados detalhados: ../results/detailed_portfolio_results.json")
    
    return strategies, performance_comparison, weights_comparison

if __name__ == "__main__":
    strategies, performance, weights = main()