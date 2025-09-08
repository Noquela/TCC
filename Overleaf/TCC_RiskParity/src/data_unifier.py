"""
Data Unifier - Pipeline Único de Dados
Elimina inconsistências e cria fonte única da verdade para o TCC
Implementa as correções do ROADMAP Sprint 2.1

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataUnifier:
    """
    Pipeline único para unificar todos os dados inconsistentes
    Implementa cálculo padronizado conforme ROADMAP
    """
    
    def __init__(self, results_dir="../results"):
        self.results_dir = results_dir
        self.master_stats_file = os.path.join(results_dir, "master_stats.json")
        self.unified_results_file = os.path.join(results_dir, "unified_results.csv")
        
        # Taxa livre de risco padronizada
        self.risk_free_rate = 0.065  # 6.5% a.a. conforme TCC
        self.monthly_rf = self.risk_free_rate / 12
        
        print("=== DATA UNIFIER - PIPELINE ÚNICO ===")
        print(f"Diretório de resultados: {results_dir}")
        print(f"Taxa livre de risco: {self.risk_free_rate:.1%} a.a.")
        print()
    
    def load_corrected_returns_data(self):
        """
        Carrega dados de retornos com as correções implementadas
        """
        print("1. Carregando dados de retornos corrigidos...")
        
        returns_file = os.path.join(self.results_dir, "real_returns_data.csv")
        
        if not os.path.exists(returns_file):
            print(f"ERRO: Arquivo {returns_file} não encontrado!")
            print("Execute primeiro economatica_loader.py com as correções")
            return None
        
        returns_df = pd.read_csv(returns_file, index_col=0, parse_dates=True)
        print(f"  OK: Carregados {len(returns_df)} observacoes de {len(returns_df.columns)} ativos")
        print(f"  OK: Periodo: {returns_df.index[0].date()} a {returns_df.index[-1].date()}")
        
        # Validar se janeiro 2018 está presente e não é artificial
        if returns_df.index[0].year == 2018 and returns_df.index[0].month == 1:
            jan_2018_returns = returns_df.iloc[0]
            if not all(jan_2018_returns == 0.0):
                print("  OK: Janeiro 2018 presente com retornos REAIS (nao artificiais)")
            else:
                print("  AVISO: Janeiro 2018 ainda artificializado (todos zeros)")
        
        return returns_df
    
    def calculate_unified_statistics(self, returns_df):
        """
        Calcula estatísticas unificadas usando PIPELINE ÚNICO
        Elimina inconsistências como ELET3 com 3 valores diferentes
        """
        print("2. Calculando estatísticas unificadas (fonte única)...")
        
        unified_stats = {}
        
        for asset in returns_df.columns:
            asset_returns = returns_df[asset]
            
            # CÁLCULO ÚNICO PADRONIZADO - FONTE ÚNICA DA VERDADE
            print(f"  Processando {asset}...")
            
            # Retorno anualizado: (1 + monthly_returns).prod() - 1 convertido para anual
            total_return = (1 + asset_returns).prod() - 1
            n_months = len(asset_returns)
            annualized_return = (1 + total_return) ** (12 / n_months) - 1
            
            # Volatilidade anualizada
            annual_volatility = asset_returns.std() * np.sqrt(12)
            
            # Sharpe Ratio padronizado
            sharpe_ratio = (annualized_return - self.risk_free_rate) / annual_volatility
            
            # Sortino Ratio padronizado (conforme ROADMAP)
            sortino_ratio = self.calculate_sortino_ratio_standardized(asset_returns)
            
            # Outras métricas
            min_return = asset_returns.min()
            max_return = asset_returns.max()
            skewness = asset_returns.skew()
            kurtosis = asset_returns.kurtosis()
            
            # VaR e CVaR
            var_95 = np.percentile(asset_returns, 5)
            cvar_95 = asset_returns[asset_returns <= var_95].mean()
            
            # Maximum Drawdown
            cumulative_returns = (1 + asset_returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # ARMAZENAR NA FONTE ÚNICA
            unified_stats[asset] = {
                'annual_return': float(annualized_return),
                'annual_return_pct': float(annualized_return * 100),
                'annual_volatility': float(annual_volatility),
                'annual_volatility_pct': float(annual_volatility * 100),
                'sharpe_ratio': float(sharpe_ratio),
                'sortino_ratio': float(sortino_ratio),
                'min_return': float(min_return),
                'max_return': float(max_return),
                'min_return_pct': float(min_return * 100),
                'max_return_pct': float(max_return * 100),
                'skewness': float(skewness),
                'kurtosis': float(kurtosis),
                'var_95_monthly': float(var_95),
                'cvar_95_monthly': float(cvar_95),
                'var_95_monthly_pct': float(var_95 * 100),
                'cvar_95_monthly_pct': float(cvar_95 * 100),
                'max_drawdown': float(max_drawdown),
                'max_drawdown_pct': float(max_drawdown * 100),
                'observations': int(n_months),
                'period_start': returns_df.index[0].strftime('%Y-%m-%d'),
                'period_end': returns_df.index[-1].strftime('%Y-%m-%d')
            }
            
            print(f"    {asset}: Retorno={annualized_return*100:.2f}% Vol={annual_volatility*100:.2f}% Sharpe={sharpe_ratio:.2f}")
        
        return unified_stats
    
    def calculate_sortino_ratio_standardized(self, returns_series):
        """
        Sortino Ratio padronizado conforme ROADMAP Sprint 2.2
        """
        # Retorno excedente anualizado
        excess_return = returns_series.mean() * 12 - self.risk_free_rate
        
        # Downside deviation: apenas retornos abaixo da taxa livre de risco mensal
        downside_returns = returns_series[returns_series < self.monthly_rf] - self.monthly_rf
        
        if len(downside_returns) == 0:
            # Se não há retornos abaixo da taxa livre de risco, Sortino é infinito
            # Usar valor alto mas finito
            return 10.0
        
        downside_deviation = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(12)
        
        # Sortino ratio
        if downside_deviation > 0:
            return excess_return / downside_deviation
        else:
            return 10.0  # Valor alto para casos sem downside
    
    def save_master_stats(self, unified_stats):
        """
        Salva estatísticas mestras como fonte única da verdade
        """
        print("3. Salvando fonte única da verdade...")
        
        # Criar diretório se não existir
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Adicionar metadados
        master_data = {
            'metadata': {
                'creation_date': datetime.now().isoformat(),
                'description': 'Fonte única da verdade para todas as métricas - Data Unifier',
                'risk_free_rate': self.risk_free_rate,
                'calculation_method': 'Unified pipeline - eliminates inconsistencies',
                'corrections_applied': [
                    'ERC implementation corrected',
                    'Look-ahead bias eliminated',
                    'January 2018 returns corrected',
                    'Sortino ratio standardized'
                ]
            },
            'assets_stats': unified_stats
        }
        
        # Salvar JSON
        with open(self.master_stats_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        print(f"  OK: Master stats salvos: {self.master_stats_file}")
        
        # Salvar CSV tambem para facilidade de uso
        self.create_unified_csv(unified_stats)
        
        return master_data
    
    def create_unified_csv(self, unified_stats):
        """
        Cria CSV unificado para uso nas tabelas LaTeX
        """
        rows = []
        
        for asset, stats in unified_stats.items():
            row = {
                'Ativo': asset,
                'Retorno_Anual_Pct': stats['annual_return_pct'],
                'Volatilidade_Anual_Pct': stats['annual_volatility_pct'],
                'Sharpe_Ratio': stats['sharpe_ratio'],
                'Sortino_Ratio': stats['sortino_ratio'],
                'Min_Mensal_Pct': stats['min_return_pct'],
                'Max_Mensal_Pct': stats['max_return_pct'],
                'VaR_95_Mensal_Pct': stats['var_95_monthly_pct'],
                'CVaR_95_Mensal_Pct': stats['cvar_95_monthly_pct'],
                'Max_Drawdown_Pct': stats['max_drawdown_pct'],
                'Observacoes': stats['observations']
            }
            rows.append(row)
        
        unified_df = pd.DataFrame(rows)
        unified_df.to_csv(self.unified_results_file, index=False)
        
        print(f"  OK: CSV unificado salvo: {self.unified_results_file}")
        
        return unified_df
    
    def validate_data_consistency(self):
        """
        Valida que não há inconsistências nos dados unificados
        """
        print("4. Validando consistência dos dados unificados...")
        
        if not os.path.exists(self.master_stats_file):
            print("  ERRO: Master stats não encontrado")
            return False
        
        with open(self.master_stats_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        assets_stats = master_data['assets_stats']
        
        # Verificar se há valores duplicados/inconsistentes
        validation_errors = []
        
        for asset, stats in assets_stats.items():
            # Verificar valores válidos
            if stats['annual_return_pct'] > 200 or stats['annual_return_pct'] < -90:
                validation_errors.append(f"{asset}: Retorno anual suspeito ({stats['annual_return_pct']:.2f}%)")
            
            if stats['sharpe_ratio'] > 5 or stats['sharpe_ratio'] < -3:
                validation_errors.append(f"{asset}: Sharpe ratio suspeito ({stats['sharpe_ratio']:.2f})")
            
            if stats['annual_volatility_pct'] > 100 or stats['annual_volatility_pct'] < 5:
                validation_errors.append(f"{asset}: Volatilidade suspeit ({stats['annual_volatility_pct']:.2f}%)")
        
        if validation_errors:
            print("  ⚠ AVISOS encontrados:")
            for error in validation_errors:
                print(f"    - {error}")
        else:
            print("  OK: Todos os dados dentro de faixas esperadas")
        
        # Verificar especificamente ELET3
        if 'ELET3' in assets_stats:
            elet3_return = assets_stats['ELET3']['annual_return_pct']
            print(f"  OK: ELET3 valor unico consolidado: {elet3_return:.2f}%")
            print("    (Elimina inconsistencia: 32.3% vs 33.70% vs 32.29%)")
        
        return len(validation_errors) == 0
    
    def generate_comparison_report(self):
        """
        Gera relatório comparativo mostrando eliminação das inconsistências
        """
        print("5. Gerando relatório de eliminação de inconsistências...")
        
        # Comparar com arquivos antigos se existirem
        old_files = [
            os.path.join(self.results_dir, "real_data_summary.csv"),
            os.path.join(self.results_dir, "complete_real_stats.csv")
        ]
        
        report_lines = []
        report_lines.append("RELATÓRIO DE UNIFICAÇÃO DE DADOS")
        report_lines.append("=" * 50)
        report_lines.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Carregar dados unificados
        if os.path.exists(self.master_stats_file):
            with open(self.master_stats_file, 'r', encoding='utf-8') as f:
                unified_data = json.load(f)
            
            report_lines.append("VALORES UNIFICADOS (fonte única):")
            for asset, stats in unified_data['assets_stats'].items():
                report_lines.append(f"  {asset}: {stats['annual_return_pct']:.2f}%")
            report_lines.append("")
        
        # Comparar com arquivos antigos
        for old_file in old_files:
            if os.path.exists(old_file):
                report_lines.append(f"COMPARAÇÃO COM: {os.path.basename(old_file)}")
                old_df = pd.read_csv(old_file)
                
                if 'ELET3' in old_df['Ativo'].values:
                    elet3_row = old_df[old_df['Ativo'] == 'ELET3'].iloc[0]
                    
                    # Tentar diferentes formatos de coluna de retorno
                    return_cols = ['Retorno Anual (%)', 'Retorno_Anual_Pct', 'annual_return_pct']
                    old_return = None
                    
                    for col in return_cols:
                        if col in old_df.columns:
                            old_val = elet3_row[col]
                            if isinstance(old_val, str) and '%' in old_val:
                                old_return = float(old_val.replace('%', ''))
                            else:
                                old_return = float(old_val)
                            break
                    
                    if old_return is not None:
                        report_lines.append(f"  ELET3 antigo: {old_return:.2f}%")
                        
                        if os.path.exists(self.master_stats_file):
                            unified_return = unified_data['assets_stats']['ELET3']['annual_return_pct']
                            diff = abs(unified_return - old_return)
                            report_lines.append(f"  ELET3 unificado: {unified_return:.2f}%")
                            report_lines.append(f"  Diferença resolvida: {diff:.2f}pp")
                
                report_lines.append("")
        
        # Salvar relatório
        report_file = os.path.join(self.results_dir, "data_unification_report.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"  OK: Relatorio salvo: {report_file}")
        
        return report_lines

def main():
    """
    Execução principal do Data Unifier
    """
    print("EXECUTANDO DATA UNIFIER - ELIMINAÇÃO DE INCONSISTÊNCIAS")
    print()
    
    # Inicializar unificador
    unifier = DataUnifier()
    
    # 1. Carregar dados corrigidos
    returns_df = unifier.load_corrected_returns_data()
    if returns_df is None:
        return None
    
    # 2. Calcular estatísticas unificadas
    unified_stats = unifier.calculate_unified_statistics(returns_df)
    
    # 3. Salvar fonte única da verdade
    master_data = unifier.save_master_stats(unified_stats)
    
    # 4. Validar consistência
    is_consistent = unifier.validate_data_consistency()
    
    # 5. Gerar relatório
    report = unifier.generate_comparison_report()
    
    print("=" * 60)
    print("DATA UNIFICATION COMPLETA!")
    print(f"OK: Fonte unica criada: master_stats.json")
    print(f"OK: CSV unificado: unified_results.csv") 
    print(f"OK: Consistencia: {'VALIDA' if is_consistent else 'COM AVISOS'}")
    print(f"OK: Relatorio: data_unification_report.txt")
    print()
    print("IMPORTANTE: Todos os scripts devem agora usar master_stats.json")
    print("como fonte unica da verdade para eliminar inconsistencias!")
    
    return master_data

if __name__ == "__main__":
    result = main()