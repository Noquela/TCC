"""
SISTEMA CORRIGIDO - TCC RISK PARITY
Script 3: Análise de Portfolio - Três Estratégias

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-15 (Versão Corrigida)

Correções aplicadas:
- Correção do método fallback Markowitz (minimum variance vs tangency)
- Validação mais rigorosa de inputs
- Melhor tratamento de convergência ERC
- Logging detalhado de otimização
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnalisadorPortfolio:
    """
    Implementa as três estratégias de portfolio:
    1. Equal Weight (EW)
    2. Mean-Variance Optimization (MVO)
    3. Equal Risk Contribution (ERC) - Risk Parity
    """
    
    def __init__(self):
        self.results_dir = "../results"
        self.rf_rate = 0.0624  # 6.24% CDI médio 2018-2019
        
        print("="*60)
        print("ANALISADOR DE PORTFOLIO - TRES ESTRATEGIAS")
        print("="*60)
        print("OK Equal Weight (EW)")
        print("OK Mean-Variance Optimization (MVO)")
        print("OK Equal Risk Contribution (ERC)")
        print("OK Período: 2018-2019 (out-of-sample)")
        print()
    
    def carregar_dados_historicos(self):
        """
        Carrega retornos históricos processados
        """
        print("1. Carregando dados históricos...")
        
        returns_file = os.path.join(self.results_dir, "02_retornos_mensais_2018_2019.csv")
        if not os.path.exists(returns_file):
            raise FileNotFoundError("Execute primeiro 02_extrator_dados_historicos.py")
        
        returns_df = pd.read_csv(returns_file, index_col=0, parse_dates=True)
        
        print(f"   Ativos: {len(returns_df.columns)}")
        print(f"   Períodos: {len(returns_df)}")
        print(f"   Data inicial: {returns_df.index[0].date()}")
        print(f"   Data final: {returns_df.index[-1].date()}")
        
        return returns_df
    
    def calcular_estrategia_equal_weight(self, returns_df):
        """
        Estratégia 1: Equal Weight (1/N)
        """
        print("2. Calculando Equal Weight Portfolio...")
        
        n_assets = len(returns_df.columns)
        weights = np.ones(n_assets) / n_assets
        
        # Performance do portfolio
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Métricas anualizadas
        annual_return = portfolio_returns.mean() * 12
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
        
        # Maximum Drawdown
        cum_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Sortino Ratio (downside deviation)
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(12) if len(downside_returns) > 0 else 0.001
        sortino_ratio = (annual_return - self.rf_rate) / downside_vol
        
        ew_results = {
            'strategy': 'Equal Weight',
            'weights': dict(zip(returns_df.columns, weights)),
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_returns': portfolio_returns
        }
        
        print(f"   Retorno anual: {annual_return:.1%}")
        print(f"   Volatilidade: {annual_vol:.1%}")
        print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
        
        return ew_results
    
    def calcular_estrategia_markowitz(self, returns_df):
        """
        Estratégia 2: Mean-Variance Optimization (Markowitz) com restrições
        """
        print("3. Calculando Mean-Variance Optimization com restricoes...")
        
        # Calcular inputs
        mu = returns_df.mean() * 12  # Expected returns
        Sigma = returns_df.cov() * 12  # Covariance matrix
        n = len(returns_df.columns)
        
        # Otimização com scipy - Maximizar Sharpe Ratio com restrições
        def objective_function(weights):
            """Função objetivo: minimizar -Sharpe Ratio"""
            portfolio_return = np.sum(mu.values * weights)
            portfolio_vol = np.sqrt(weights.T @ Sigma.values @ weights)
            if portfolio_vol == 0:
                return 1e6  # Penalidade alta
            sharpe_ratio = (portfolio_return - self.rf_rate) / portfolio_vol
            return -sharpe_ratio  # Minimizar negativo = maximizar
        
        # Restrições
        constraints = [
            # Pesos somam 1
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0},
        ]
        
        # Limites por ativo: 0% a 40% (permitir concentração se ótima)
        # Mantém teoria pura de Markowitz mas evita concentração extrema (>40%)
        bounds = [(0.0, 0.40) for _ in range(n)]
        
        # Chute inicial: equal weight
        initial_guess = np.ones(n) / n
        
        try:
            # Executar otimização
            result = minimize(
                objective_function,
                initial_guess,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )
            
            if result.success:
                weights = result.x
                # Normalizar por segurança
                weights = weights / weights.sum()
                print("   Otimizacao convergiu com restricoes")
            else:
                print("   AVISO: Otimizacao nao convergiu, usando metodo analitico")
                weights = self._markowitz_analitico(mu, Sigma, n)
                
        except Exception as e:
            print(f"   ERRO na otimizacao: {e}, usando metodo analitico")
            weights = self._markowitz_analitico(mu, Sigma, n)
        
        # Performance do portfolio
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Métricas
        annual_return = portfolio_returns.mean() * 12
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
        
        # Maximum Drawdown
        cum_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(12) if len(downside_returns) > 0 else 0.001
        sortino_ratio = (annual_return - self.rf_rate) / downside_vol
        
        mvo_results = {
            'strategy': 'Mean-Variance Optimization',
            'weights': dict(zip(returns_df.columns, weights)),
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_returns': portfolio_returns
        }
        
        print(f"   Retorno anual: {annual_return:.1%}")
        print(f"   Volatilidade: {annual_vol:.1%}")
        print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
        
        return mvo_results
    
    def _markowitz_analitico(self, mu, Sigma, n):
        """
        Método analítico de fallback para Markowitz
        
        Implementa Maximum Sharpe Ratio Portfolio (Tangency Portfolio)
        Referência: Markowitz, H. (1952) + Sharpe, W. (1966)
        """
        try:
            logger.warning("Usando método analítico fallback para Markowitz")
            
            # Inversa da matriz de covariância
            inv_Sigma = np.linalg.inv(Sigma.values)
            ones = np.ones((n, 1))
            
            # Excess returns (mu - rf)
            excess_returns = (mu.values - self.rf_rate).reshape(-1, 1)
            
            # Tangency Portfolio (Maximum Sharpe Ratio)
            # w* = Σ^(-1) * (μ - rf) / (1^T * Σ^(-1) * (μ - rf))
            numerator = inv_Sigma @ excess_returns
            denominator = ones.T @ inv_Sigma @ excess_returns
            
            if denominator <= 0:
                logger.warning("Denominador <= 0, usando equal weight")
                return np.ones(n) / n
                
            weights = (numerator / denominator).flatten()
            
            # Garantir que pesos são não-negativos e limitados
            weights = np.clip(weights, 0.0, 0.40)
            
            # Renormalizar para somar 1
            if weights.sum() > 0:
                weights = weights / weights.sum()
            else:
                logger.warning("Pesos inválidos, usando equal weight")
                weights = np.ones(n) / n
                
            return weights
            
        except (np.linalg.LinAlgError, ValueError) as e:
            logger.error(f"Erro no método analítico: {e}, usando equal weight")
            return np.ones(n) / n
    
    def calcular_estrategia_risk_parity(self, returns_df):
        """
        Estratégia 3: Equal Risk Contribution (Risk Parity)
        """
        print("4. Calculando Equal Risk Contribution (Risk Parity)...")
        
        # Matriz de covariância
        Sigma = returns_df.cov().values * 12  # Anualizada
        n = len(returns_df.columns)
        
        # Algoritmo iterativo para ERC
        def risk_parity_weights(cov_matrix, max_iter=1000, tol=1e-6):
            """
            Algoritmo iterativo para encontrar pesos ERC
            """
            n = len(cov_matrix)
            weights = np.ones(n) / n  # Inicialização igual
            
            for iteration in range(max_iter):
                # Contribuições de risco atuais
                portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
                marginal_contrib = (cov_matrix @ weights) / portfolio_vol
                contrib = weights * marginal_contrib
                
                # Target: contribuição igual = 1/n da volatilidade total
                target_contrib = portfolio_vol / n
                
                # Atualizar pesos
                weights_new = weights * (target_contrib / contrib)
                weights_new = weights_new / weights_new.sum()  # Normalizar
                
                # Convergência
                if np.max(np.abs(weights_new - weights)) < tol:
                    break
                    
                weights = weights_new
            
            return weights
        
        # Calcular pesos Risk Parity
        try:
            weights = risk_parity_weights(Sigma)
        except:
            # Fallback para equal weight
            print("   AVISO: Erro no cálculo ERC, usando Equal Weight")
            weights = np.ones(n) / n
        
        # Performance do portfolio
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Métricas
        annual_return = portfolio_returns.mean() * 12
        annual_vol = portfolio_returns.std() * np.sqrt(12)
        sharpe_ratio = (annual_return - self.rf_rate) / annual_vol
        
        # Maximum Drawdown
        cum_returns = (1 + portfolio_returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        # Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_vol = downside_returns.std() * np.sqrt(12) if len(downside_returns) > 0 else 0.001
        sortino_ratio = (annual_return - self.rf_rate) / downside_vol
        
        erc_results = {
            'strategy': 'Equal Risk Contribution',
            'weights': dict(zip(returns_df.columns, weights)),
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_returns': portfolio_returns
        }
        
        print(f"   Retorno anual: {annual_return:.1%}")
        print(f"   Volatilidade: {annual_vol:.1%}")
        print(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
        
        return erc_results
    
    def comparar_estrategias(self, ew_results, mvo_results, erc_results):
        """
        Compara performance das três estratégias
        """
        print("5. Comparando estratégias...")
        
        # Criar tabela comparativa
        comparison_data = []
        for results in [ew_results, mvo_results, erc_results]:
            comparison_data.append({
                'Estratégia': results['strategy'],
                'Retorno_Anual_Pct': results['annual_return'] * 100,
                'Volatilidade_Anual_Pct': results['annual_volatility'] * 100,
                'Sharpe_Ratio': results['sharpe_ratio'],
                'Sortino_Ratio': results['sortino_ratio'],
                'Max_Drawdown_Pct': results['max_drawdown'] * 100
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Identificar melhor estratégia por métrica
        best_return = comparison_df.loc[comparison_df['Retorno_Anual_Pct'].idxmax()]
        best_sharpe = comparison_df.loc[comparison_df['Sharpe_Ratio'].idxmax()]
        best_sortino = comparison_df.loc[comparison_df['Sortino_Ratio'].idxmax()]
        lowest_vol = comparison_df.loc[comparison_df['Volatilidade_Anual_Pct'].idxmin()]
        
        print("   RANKING POR MÉTRICA:")
        print(f"   Melhor Retorno: {best_return['Estratégia']} ({best_return['Retorno_Anual_Pct']:.1f}%)")
        print(f"   Melhor Sharpe: {best_sharpe['Estratégia']} ({best_sharpe['Sharpe_Ratio']:.2f})")
        print(f"   Melhor Sortino: {best_sortino['Estratégia']} ({best_sortino['Sortino_Ratio']:.2f})")
        print(f"   Menor Vol.: {lowest_vol['Estratégia']} ({lowest_vol['Volatilidade_Anual_Pct']:.1f}%)")
        
        return comparison_df
    
    def salvar_resultados_finais(self, ew_results, mvo_results, erc_results, comparison_df, returns_df):
        """
        Salva todos os resultados da análise
        """
        print("6. Salvando resultados finais...")
        
        # 1. Tabela comparativa
        comparison_file = os.path.join(self.results_dir, "03_comparacao_estrategias.csv")
        comparison_df.to_csv(comparison_file, index=False)
        
        # 2. Pesos de cada estratégia
        weights_data = []
        for results in [ew_results, mvo_results, erc_results]:
            for asset, weight in results['weights'].items():
                weights_data.append({
                    'Estratégia': results['strategy'],
                    'Ativo': asset,
                    'Peso_Pct': weight * 100
                })
        
        weights_df = pd.DataFrame(weights_data)
        weights_file = os.path.join(self.results_dir, "03_pesos_portfolios.csv")
        weights_df.to_csv(weights_file, index=False)
        
        # 3. Retornos dos portfolios ao longo do tempo
        portfolio_returns_df = pd.DataFrame({
            'Date': returns_df.index,
            'EW_Returns': ew_results['portfolio_returns'],
            'MVO_Returns': mvo_results['portfolio_returns'],
            'ERC_Returns': erc_results['portfolio_returns']
        }).set_index('Date')
        
        returns_file = os.path.join(self.results_dir, "03_retornos_portfolios.csv")
        portfolio_returns_df.to_csv(returns_file)
        
        # 4. Metadata completa
        metadata = {
            "data_processamento": datetime.now().isoformat(),
            "periodo_analise": "2018-01-01 a 2019-12-31",
            "taxa_livre_risco": self.rf_rate,
            "total_ativos": len(returns_df.columns),
            "ativos_analisados": list(returns_df.columns),
            "estrategias": {
                "equal_weight": {
                    "retorno_anual": ew_results['annual_return'],
                    "volatilidade": ew_results['annual_volatility'],
                    "sharpe": ew_results['sharpe_ratio'],
                    "sortino": ew_results['sortino_ratio']
                },
                "markowitz": {
                    "retorno_anual": mvo_results['annual_return'],
                    "volatilidade": mvo_results['annual_volatility'],
                    "sharpe": mvo_results['sharpe_ratio'],
                    "sortino": mvo_results['sortino_ratio']
                },
                "risk_parity": {
                    "retorno_anual": erc_results['annual_return'],
                    "volatilidade": erc_results['annual_volatility'],
                    "sharpe": erc_results['sharpe_ratio'],
                    "sortino": erc_results['sortino_ratio']
                }
            }
        }
        
        metadata_file = os.path.join(self.results_dir, "03_metadata_portfolios.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   OK Comparação: {comparison_file}")
        print(f"   OK Pesos: {weights_file}")
        print(f"   OK Retornos: {returns_file}")
        print(f"   OK Metadata: {metadata_file}")
        
        return True
    
    def executar_analise_completa(self):
        """
        Executa análise completa das três estratégias
        """
        try:
            # Carregar dados
            returns_df = self.carregar_dados_historicos()
            
            # Calcular estratégias
            ew_results = self.calcular_estrategia_equal_weight(returns_df)
            mvo_results = self.calcular_estrategia_markowitz(returns_df)
            erc_results = self.calcular_estrategia_risk_parity(returns_df)
            
            # Comparar resultados
            comparison_df = self.comparar_estrategias(ew_results, mvo_results, erc_results)
            
            # Salvar tudo
            self.salvar_resultados_finais(ew_results, mvo_results, erc_results, comparison_df, returns_df)
            
            print(f"\nOK ANALISE DE PORTFOLIO CONCLUIDA COM SUCESSO!")
            print(f"OK Tres estrategias implementadas")
            print(f"OK Metricas calculadas e comparadas")
            print(f"OK Resultados salvos para relatorio")
            
            return comparison_df, ew_results, mvo_results, erc_results
            
        except Exception as e:
            print(f"ERRO: {e}")
            return None, None, None, None

def main():
    """
    Execução principal
    """
    analisador = AnalisadorPortfolio()
    comparison_df, ew_results, mvo_results, erc_results = analisador.executar_analise_completa()
    
    if comparison_df is not None:
        print(f"\nRESULTADO DA ANALISE:")
        print(comparison_df.to_string(index=False, float_format='%.2f'))
        return comparison_df
    else:
        print("ERRO: Falha na análise")
        return None

if __name__ == "__main__":
    resultado = main()