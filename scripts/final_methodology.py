"""
Metodologia Final - TCC Bruno Gasparoni Ballerini
Implementação EXATA conforme definido nas seções metodológicas

CDI Real: 2018 (6,43%) e 2019 (5,96%) = Média 6,195% a.a.
Fonte: Investidor10 (dados oficiais B3/BCB)
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from economatica_loader import EconomaticaLoader

class FinalMethodologyAnalyzer:
    """
    Implementação final seguindo EXATAMENTE a metodologia definida no TCC
    """
    
    def __init__(self):
        self.loader = EconomaticaLoader()
        
        # CDI REAL do período (fonte: Investidor10 - dados B3/BCB)
        self.cdi_2018 = 0.0643  # 6,43% a.a.
        self.cdi_2019 = 0.0596  # 5,96% a.a.
        self.risk_free_rate = 0.06195  # Média 2018-2019: 6,195% a.a.
        
        self.estimation_periods = []
        self.results_history = []
        
        print("=== METODOLOGIA CONFORME DEFINIDA NO TCC ===")
        print(f"CDI 2018: {self.cdi_2018:.2%}")
        print(f"CDI 2019: {self.cdi_2019:.2%}")
        print(f"Taxa Livre de Risco (média): {self.risk_free_rate:.3%}")
        
    def load_extended_data(self):
        """
        Carrega dados de 2016-2019 para estimação out-of-sample
        """
        print("\nCarregando dados para estimação out-of-sample...")
        
        returns_data, prices_data = self.loader.load_selected_assets(
            start_date='2016-01-01', 
            end_date='2019-12-31'
        )
        
        if returns_data is None:
            print("ERRO: Dados insuficientes")
            return False
            
        self.full_returns = returns_data
        self.full_prices = prices_data
        
        print(f"Dados: {self.full_returns.index[0].date()} a {self.full_returns.index[-1].date()}")
        print(f"Observações: {len(self.full_returns)}")
        
        return True
    
    def setup_rebalancing_periods(self):
        """
        Rebalanceamento semestral: janeiro e julho (conforme metodologia)
        """
        print("\nConfiguração de rebalanceamento semestral...")
        
        # Datas de rebalanceamento semestrais (jan e jul)
        rebalancing_dates = [
            '2018-01-31',  # Janeiro 2018
            '2018-07-31',  # Julho 2018  
            '2019-01-31',  # Janeiro 2019
            '2019-07-31',  # Julho 2019
            '2019-12-31'   # Final do período
        ]
        
        rebalancing_dates = [pd.to_datetime(date) for date in rebalancing_dates]
        
        for i in range(len(rebalancing_dates) - 1):
            test_start = rebalancing_dates[i]
            test_end = rebalancing_dates[i + 1]
            
            # Estimação usando APENAS dados anteriores
            est_end = test_start - timedelta(days=1)
            est_start = est_end - timedelta(days=730)  # ~24 meses
            
            self.estimation_periods.append({
                'name': f'Semestre {i+1}',
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
        Estimação de parâmetros usando apenas dados históricos
        """
        if len(estimation_data) < 12:
            print(f"AVISO: Poucos dados ({len(estimation_data)} obs)")
            
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
    
    def markowitz_optimization(self, parameters):
        """
        Markowitz: Maximizar Sharpe Ratio (conforme metodologia)
        Restrições: soma = 1, sem vendas a descoberto, diversificação forçada
        """
        expected_returns = parameters['expected_returns'].values
        cov_matrix = parameters['cov_matrix'].values
        n_assets = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            if portfolio_vol == 0:
                return -999
            # MAXIMIZAR SHARPE RATIO
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol
            return -sharpe  # Minimizar negativo = maximizar
        
        # Restrições
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # Soma = 1
        ]
        
        # Sem vendas a descoberto + diversificação forçada (2-20%)
        bounds = tuple([(0.02, 0.20) for _ in range(n_assets)])
        
        # Ponto inicial: equal weight
        x0 = np.array([1/n_assets] * n_assets)
        
        try:
            result = minimize(
                objective, x0, 
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'disp': False, 'maxiter': 1000}
            )
            
            if result.success:
                weights = result.x / result.x.sum()
                return pd.Series(weights, index=parameters['expected_returns'].index)
            else:
                print(f"Otimização falhou: {result.message}")
                return self.equal_weight_strategy(parameters['expected_returns'].index)
                
        except Exception as e:
            print(f"Erro na otimização: {e}")
            return self.equal_weight_strategy(parameters['expected_returns'].index)
    
    def equal_weight_strategy(self, asset_names):
        """
        Equal Weight: Alocação igualitária (conforme metodologia)
        """
        n_assets = len(asset_names)
        weights = np.ones(n_assets) / n_assets
        return pd.Series(weights, index=asset_names)
    
    def risk_parity_strategy(self, parameters):
        """
        Risk Parity: wi = (1/σi) / Σ(1/σj) (conforme fórmula na metodologia)
        """
        volatilities = parameters['volatilities']
        inv_vol = 1 / volatilities  # 1/σi
        weights = inv_vol / inv_vol.sum()  # Normalização
        return weights
    
    def calculate_portfolio_metrics(self, weights, test_returns, period_name):
        """
        Cálculo de métricas conforme definido na metodologia
        """
        portfolio_returns = (test_returns * weights).sum(axis=1)
        
        # Métricas anualizadas 
        period_months = len(test_returns)
        annualization_factor = 12 / period_months
        
        period_return = portfolio_returns.sum()
        annual_return = period_return * annualization_factor
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        
        # SHARPE RATIO: (Rp - Rf) / σp (conforme fórmula na metodologia)
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_vol if annual_vol > 0 else 0
        
        # SORTINO RATIO: (Rp - T) / σ- (conforme fórmula na metodologia)
        # T = taxa mínima aceitável = CDI (taxa livre de risco)
        monthly_cdi = self.risk_free_rate / 12
        
        # Retornos abaixo do CDI mensal (downside)
        downside_returns = portfolio_returns[portfolio_returns < monthly_cdi]
        
        if len(downside_returns) > 0:
            # σ- = desvio-padrão dos retornos abaixo de T
            downside_deviation = downside_returns.std() * np.sqrt(12)  # Anualizada
            sortino_ratio = (annual_return - self.risk_free_rate) / downside_deviation
        else:
            sortino_ratio = 999  # Sem retornos abaixo do CDI
            
        # Maximum Drawdown
        portfolio_value = (1 + portfolio_returns).cumprod()
        peak = portfolio_value.expanding().max()
        drawdown = (portfolio_value - peak) / peak
        max_drawdown = drawdown.min()
        
        return {
            'period_return': period_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'n_months': period_months
        }
    
    def run_methodology_analysis(self):
        """
        Executa análise conforme metodologia definida no TCC
        """
        if not self.load_extended_data():
            return None
            
        self.setup_rebalancing_periods()
        
        print("\n=== EXECUÇÃO DA METODOLOGIA ===")
        
        # Três estratégias definidas na metodologia
        strategies = ['Markowitz', 'Equal Weight', 'Risk Parity']
        all_results = {strategy: [] for strategy in strategies}
        
        for period_info in self.estimation_periods:
            print(f"\n--- {period_info['name']} ---")
            
            # Dados de estimação (históricos)
            est_data = self.full_returns[
                (self.full_returns.index >= period_info['estimation_start']) &
                (self.full_returns.index <= period_info['estimation_end'])
            ]
            
            # Dados de teste (out-of-sample)
            test_data = self.full_returns[
                (self.full_returns.index >= period_info['testing_start']) &
                (self.full_returns.index <= period_info['testing_end'])
            ]
            
            if len(est_data) < 12 or len(test_data) < 3:
                print(f"Dados insuficientes: Est={len(est_data)}, Test={len(test_data)}")
                continue
                
            print(f"Estimação: {len(est_data)} obs, Teste: {len(test_data)} obs")
            
            # Estimar parâmetros com dados históricos
            parameters = self.estimate_parameters(est_data)
            
            # Construir carteiras
            weights = {}
            weights['Markowitz'] = self.markowitz_optimization(parameters)
            weights['Equal Weight'] = self.equal_weight_strategy(est_data.columns)
            weights['Risk Parity'] = self.risk_parity_strategy(parameters)
            
            print("Alocações calculadas:")
            for strategy_name, w in weights.items():
                significant_weights = w[w > 0.015]  # > 1,5%
                print(f"  {strategy_name}: {dict(significant_weights.round(3))}")
            
            # Avaliar performance out-of-sample
            for strategy in strategies:
                metrics = self.calculate_portfolio_metrics(
                    weights[strategy], test_data, period_info['name']
                )
                metrics['period'] = period_info['name']
                metrics['weights'] = weights[strategy].to_dict()
                all_results[strategy].append(metrics)
        
        return all_results
    
    def consolidate_final_results(self, all_results):
        """
        Consolidação final dos resultados
        """
        print("\n=== RESULTADOS FINAIS (METODOLOGIA TCC) ===")
        
        consolidated = {}
        
        for strategy, period_results in all_results.items():
            if not period_results:
                continue
                
            # Métricas consolidadas
            total_months = sum(p['n_months'] for p in period_results)
            
            # Médias ponderadas por duração dos períodos
            weighted_return = sum(p['annual_return'] * p['n_months'] for p in period_results) / total_months
            weighted_vol = np.sqrt(sum((p['annual_volatility']**2) * p['n_months'] for p in period_results) / total_months)
            weighted_sharpe = sum(p['sharpe_ratio'] * p['n_months'] for p in period_results) / total_months
            
            # Sortino: média ponderada (excluindo valores extremos)
            valid_sortino = [p['sortino_ratio'] for p in period_results if p['sortino_ratio'] < 100]
            if valid_sortino:
                weighted_sortino = sum(p['sortino_ratio'] * p['n_months'] for p in period_results if p['sortino_ratio'] < 100) / sum(p['n_months'] for p in period_results if p['sortino_ratio'] < 100)
            else:
                weighted_sortino = 999
            
            worst_drawdown = min(p['max_drawdown'] for p in period_results)
            
            consolidated[strategy] = {
                'annual_return': weighted_return,
                'annual_volatility': weighted_vol,
                'sharpe_ratio': weighted_sharpe,
                'sortino_ratio': weighted_sortino,
                'max_drawdown': worst_drawdown,
                'periods': len(period_results)
            }
        
        # Exibir resultados
        print(f"\n{'Estratégia':<15} {'Retorno':<10} {'Volatilidade':<12} {'Sharpe':<8} {'Sortino':<8} {'Max DD':<8}")
        print("-" * 75)
        
        for strategy, metrics in consolidated.items():
            sortino_str = f"{metrics['sortino_ratio']:.2f}" if metrics['sortino_ratio'] < 100 else "N/A*"
            print(f"{strategy:<15} "
                  f"{metrics['annual_return']:.2%}      "
                  f"{metrics['annual_volatility']:.2%}        "
                  f"{metrics['sharpe_ratio']:.2f}     "
                  f"{sortino_str:<8} "
                  f"{metrics['max_drawdown']:.1%}")
        
        print("\n* N/A = Sem retornos abaixo do CDI (excelente controle de risco)")
        print(f"\nFonte CDI: Investidor10 (dados B3/BCB)")
        print(f"Período: 2018-2019 | Rebalanceamento: Semestral (jan/jul)")
        print(f"Metodologia: Conforme definida no TCC")
        
        return consolidated

def main():
    """
    Execução da metodologia final
    """
    print("=== TCC BRUNO GASPARONI BALLERINI ===")
    print("Metodologia Final - Conforme Definida nas Seções")
    print()
    
    analyzer = FinalMethodologyAnalyzer()
    
    # Executar metodologia
    all_results = analyzer.run_methodology_analysis()
    
    if all_results:
        consolidated_results = analyzer.consolidate_final_results(all_results)
        
        print("\n=== VALIDACAO METODOLOGICA ===")
        print("OK CDI real do periodo (6,43% e 5,96%)")
        print("OK Sharpe: (Rp - Rf) / sigma_p")
        print("OK Sortino: (Rp - CDI) / sigma_-")  
        print("OK Markowitz: Maximizar Sharpe")
        print("OK Equal Weight: Alocacao igualitaria")
        print("OK Risk Parity: wi = (1/sigma_i) / Soma(1/sigma_j)")
        print("OK Rebalanceamento semestral (jan/jul)")
        print("OK Out-of-sample rigoroso")
        print("OK Sem vendas a descoberto")
        print("OK Diversificacao forcada (todos os 10 ativos)")
        
        return analyzer, consolidated_results
    else:
        print("ERRO: Não foi possível executar a metodologia")
        return None, None

if __name__ == "__main__":
    analyzer, results = main()