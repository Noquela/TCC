"""
Implementação Completa da Fronteira Eficiente de Markowitz
Metodologia Academicamente Correta com Out-of-Sample Testing

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from economatica_loader import EconomaticaLoader

class MarkowitzFrontierAnalyzer:
    """
    Implementação rigorosa da fronteira eficiente de Markowitz
    """
    
    def __init__(self):
        self.loader = EconomaticaLoader()
        self.risk_free_rate = 0.065  # CDI médio 2018-2019
        self.estimation_periods = []
        self.results_history = []
        
    def load_extended_data(self):
        """
        Carrega dados de 2016-2019 (precisa de 2016-2017 para estimação)
        """
        print("Carregando dados estendidos 2016-2019...")
        
        returns_data, prices_data = self.loader.load_selected_assets(
            start_date='2016-01-01', 
            end_date='2019-12-31'
        )
        
        if returns_data is None:
            print("ERRO: Não foi possível carregar dados históricos suficientes")
            return False
            
        self.full_returns = returns_data
        self.full_prices = prices_data
        
        print(f"Dados carregados: {self.full_returns.index[0].date()} a {self.full_returns.index[-1].date()}")
        print(f"Total de observações: {len(self.full_returns)}")
        
        return True
    
    def setup_rebalancing_periods(self):
        """
        Define períodos de estimação e teste de forma rigorosa
        """
        print("Configurando períodos de rebalanceamento...")
        
        rebalancing_dates = [
            '2018-01-31',  # Início do período de teste
            '2018-07-31',  # Primeiro rebalanceamento  
            '2019-01-31',  # Segundo rebalanceamento
            '2019-07-31',  # Terceiro rebalanceamento
            '2019-12-31'   # Final do período
        ]
        
        rebalancing_dates = [pd.to_datetime(date) for date in rebalancing_dates]
        
        for i in range(len(rebalancing_dates) - 1):
            test_start = rebalancing_dates[i]
            test_end = rebalancing_dates[i + 1]
            
            # Período de estimação: usar APENAS dados anteriores ao teste
            est_end = test_start - timedelta(days=1)
            est_start = est_end - timedelta(days=730)  # ~24 meses antes
            
            self.estimation_periods.append({
                'name': f'Período {i+1}',
                'estimation_start': est_start,
                'estimation_end': est_end,
                'testing_start': test_start,
                'testing_end': test_end
            })
            
        print("Períodos configurados:")
        for period in self.estimation_periods:
            print(f"  {period['name']}:")
            print(f"    Estimação: {period['estimation_start'].date()} a {period['estimation_end'].date()}")
            print(f"    Teste: {period['testing_start'].date()} a {period['testing_end'].date()}")
    
    def estimate_parameters(self, estimation_data):
        """
        Estima parâmetros usando APENAS dados de estimação
        """
        if len(estimation_data) < 12:
            print(f"AVISO: Poucos dados para estimação ({len(estimation_data)} obs)")
            
        # Retornos esperados (média histórica anualizada)
        expected_returns = estimation_data.mean() * 12
        
        # Matriz de covariância (anualizada)
        cov_matrix = estimation_data.cov() * 12
        
        # Volatilidades individuais
        volatilities = estimation_data.std() * np.sqrt(12)
        
        return {
            'expected_returns': expected_returns,
            'cov_matrix': cov_matrix,
            'volatilities': volatilities,
            'n_observations': len(estimation_data)
        }
    
    def optimize_portfolio(self, parameters, target_return=None, min_variance=False):
        """
        Otimização de portfólio com diferentes objetivos
        """
        expected_returns = parameters['expected_returns'].values
        cov_matrix = parameters['cov_matrix'].values
        n_assets = len(expected_returns)
        
        # Restrições base
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Soma = 1
        ]
        
        # Bounds realistas: todos os ativos devem ter participação
        bounds = tuple([(0.02, 0.20) for _ in range(n_assets)])
        
        # Ponto inicial: equal weight
        x0 = np.array([1/n_assets] * n_assets)
        
        if min_variance:
            # Carteira de mínima variância
            def objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
                
        elif target_return is not None:
            # Carteira com retorno alvo (minimizar variância)
            constraints.append({
                'type': 'eq', 
                'fun': lambda w: np.dot(w, expected_returns) - target_return
            })
            
            def objective(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
        else:
            # Máximo Sharpe Ratio (padrão)
            def objective(weights):
                portfolio_return = np.dot(weights, expected_returns)
                portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                if portfolio_vol == 0:
                    return -999
                sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
                return -sharpe  # Minimizar negativo = maximizar
        
        try:
            result = minimize(
                objective, x0, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'disp': False, 'maxiter': 1000, 'ftol': 1e-9}
            )
            
            if result.success:
                weights = result.x / result.x.sum()  # Normalizar
                return pd.Series(weights, index=parameters['expected_returns'].index)
            else:
                print(f"Otimização falhou: {result.message}")
                # Fallback para equal weight
                weights = np.array([1/n_assets] * n_assets)
                return pd.Series(weights, index=parameters['expected_returns'].index)
                
        except Exception as e:
            print(f"Erro na otimização: {e}")
            weights = np.array([1/n_assets] * n_assets)
            return pd.Series(weights, index=parameters['expected_returns'].index)
    
    def equal_weight_strategy(self, asset_names):
        """
        Estratégia Equal Weight
        """
        n_assets = len(asset_names)
        weights = np.ones(n_assets) / n_assets
        return pd.Series(weights, index=asset_names)
    
    def risk_parity_strategy(self, parameters):
        """
        Estratégia Risk Parity
        """
        volatilities = parameters['volatilities']
        inv_vol = 1 / volatilities
        weights = inv_vol / inv_vol.sum()
        return weights
    
    def calculate_portfolio_metrics(self, weights, test_returns):
        """
        Calcula métricas completas de performance para um período específico
        """
        portfolio_returns = (test_returns * weights).sum(axis=1)
        
        # Métricas anualizadas 
        period_months = len(test_returns)
        annualization_factor = 12 / period_months
        
        period_return = portfolio_returns.sum()
        annual_return = period_return * annualization_factor
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        
        # Sharpe Ratio
        period_rf = self.risk_free_rate / 12 * period_months
        excess_return = period_return - period_rf
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_vol if annual_vol > 0 else 0
        
        # Sortino Ratio (CORRIGIDO)
        # Calcula downside deviation usando retornos mensais
        monthly_rf = self.risk_free_rate / 12
        downside_returns = portfolio_returns[portfolio_returns < monthly_rf]
        
        if len(downside_returns) > 0:
            downside_deviation = downside_returns.std() * np.sqrt(12)  # Anualizada
            sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation
        else:
            sortino_ratio = 999  # Sem retornos negativos
            
        # Maximum Drawdown
        portfolio_value = (1 + portfolio_returns).cumprod()
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        max_drawdown = drawdown.min()
        
        # Value at Risk 95%
        var_95 = np.percentile(portfolio_returns, 5) * 12  # Anualizado
        
        return {
            'period_return': period_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'var_95': var_95,
            'n_months': period_months
        }
    
    def run_frontier_analysis(self):
        """
        Executa análise completa da fronteira eficiente
        """
        if not self.load_extended_data():
            return None
            
        self.setup_rebalancing_periods()
        
        print("\n=== ANÁLISE DA FRONTEIRA EFICIENTE DE MARKOWITZ ===")
        
        # Diferentes estratégias Markowitz + benchmarks
        strategies = [
            ('Markowitz Min Variance', 'min_var'),
            ('Markowitz Max Sharpe', 'max_sharpe'), 
            ('Equal Weight', 'equal_weight'),
            ('Risk Parity', 'risk_parity')
        ]
        
        all_results = {name: [] for name, _ in strategies}
        
        for period_info in self.estimation_periods:
            print(f"\n--- {period_info['name']} ---")
            
            # Extrair dados de estimação
            est_data = self.full_returns[
                (self.full_returns.index >= period_info['estimation_start']) &
                (self.full_returns.index <= period_info['estimation_end'])
            ]
            
            # Extrair dados de teste
            test_data = self.full_returns[
                (self.full_returns.index >= period_info['testing_start']) &
                (self.full_returns.index <= period_info['testing_end'])
            ]
            
            if len(est_data) < 12 or len(test_data) < 3:
                print(f"Dados insuficientes: Est={len(est_data)}, Test={len(test_data)}")
                continue
                
            print(f"Estimação: {len(est_data)} obs, Teste: {len(test_data)} obs")
            
            # Estimar parâmetros
            parameters = self.estimate_parameters(est_data)
            
            # Calcular pesos para cada estratégia
            weights = {}
            
            # Markowitz - Mínima Variância
            weights['Markowitz Min Variance'] = self.optimize_portfolio(
                parameters, min_variance=True
            )
            
            # Markowitz - Máximo Sharpe
            weights['Markowitz Max Sharpe'] = self.optimize_portfolio(
                parameters
            )
            
            # Equal Weight
            weights['Equal Weight'] = self.equal_weight_strategy(est_data.columns)
            
            # Risk Parity
            weights['Risk Parity'] = self.risk_parity_strategy(parameters)
            
            print("Pesos calculados:")
            for strategy_name, w in weights.items():
                non_zero = w[w > 0.01]  # Mostrar apenas pesos > 1%
                print(f"  {strategy_name}: {dict(non_zero.round(3))}")
            
            # Testar performance
            for strategy_name in [name for name, _ in strategies]:
                performance = self.calculate_portfolio_metrics(weights[strategy_name], test_data)
                performance['period'] = period_info['name']
                performance['weights'] = weights[strategy_name].to_dict()
                all_results[strategy_name].append(performance)
        
        return all_results
    
    def consolidate_results(self, all_results):
        """
        Consolida resultados de todos os períodos
        """
        print("\n=== RESULTADOS CONSOLIDADOS - FRONTEIRA EFICIENTE ===")
        
        consolidated = {}
        
        for strategy, period_results in all_results.items():
            if not period_results:
                continue
                
            # Calcular métricas agregadas
            total_periods = len(period_results)
            total_months = sum(p['n_months'] for p in period_results)
            
            weighted_return = sum(p['annual_return'] * p['n_months'] for p in period_results) / total_months
            weighted_vol = np.sqrt(sum((p['annual_volatility']**2) * p['n_months'] for p in period_results) / total_months)
            weighted_sharpe = sum(p['sharpe_ratio'] * p['n_months'] for p in period_results) / total_months
            weighted_sortino = sum(p['sortino_ratio'] * p['n_months'] for p in period_results) / total_months
            
            worst_drawdown = min(p['max_drawdown'] for p in period_results)
            worst_var = min(p['var_95'] for p in period_results)
            
            consolidated[strategy] = {
                'annual_return': weighted_return,
                'annual_volatility': weighted_vol,
                'sharpe_ratio': weighted_sharpe,
                'sortino_ratio': weighted_sortino,
                'max_drawdown': worst_drawdown,
                'var_95': worst_var,
                'periods': total_periods
            }
        
        # Mostrar resultados
        print(f"\n{'Estratégia':<20} {'Retorno':<10} {'Vol':<8} {'Sharpe':<8} {'Sortino':<8} {'MaxDD':<8} {'VaR95%':<8}")
        print("-" * 85)
        
        for strategy, metrics in consolidated.items():
            print(f"{strategy:<20} "
                  f"{metrics['annual_return']:.1%}    "
                  f"{metrics['annual_volatility']:.1%}   "
                  f"{metrics['sharpe_ratio']:.2f}    "
                  f"{metrics['sortino_ratio']:.2f}     "
                  f"{metrics['max_drawdown']:.1%}   "
                  f"{metrics['var_95']:.1%}")
        
        return consolidated

def main():
    """
    Executa análise completa da fronteira eficiente
    """
    print("=== FRONTEIRA EFICIENTE DE MARKOWITZ - ANÁLISE COMPLETA ===")
    print("(Metodologia Academicamente Correta)")
    
    analyzer = MarkowitzFrontierAnalyzer()
    
    # Executar análise da fronteira
    all_results = analyzer.run_frontier_analysis()
    
    if all_results:
        consolidated_results = analyzer.consolidate_results(all_results)
        
        print("\nMETODOLOGIA APLICADA:")
        print("- Fronteira eficiente completa de Markowitz")
        print("- Mínima variância + Máximo Sharpe")
        print("- Sortino ratio corrigido")
        print("- Out-of-sample rigoroso")
        print("- Todos os 10 ativos obrigatórios (2-20%)")
        
        return analyzer, consolidated_results
    else:
        print("ERRO na execução da análise")
        return None, None

if __name__ == "__main__":
    analyzer, results = main()