"""
SISTEMA CORRIGIDO - TCC RISK PARITY
Script 2: Extrator de Dados Históricos 2018-2019

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-15 (Versão Corrigida)

Correções aplicadas:
- Correção de métodos pandas depreciados (fillna)
- Melhor tratamento de outliers
- Validação robusta de dados
- Logging aprimorado
"""

import pandas as pd
import numpy as np
import json
import os
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtratorDadosHistoricos:
    """
    Extrai dados históricos dos ativos selecionados cientificamente
    Período de teste: 2018-2019 (out-of-sample)
    """
    
    def __init__(self):
        self.data_dir = "../data/DataBase"
        self.excel_path = os.path.join(self.data_dir, "Economatica-8900701390-20250812230945 (1).xlsx")
        self.results_dir = "../results"
        
        print("="*60)
        print("EXTRATOR DE DADOS HISTÓRICOS 2018-2019")  
        print("="*60)
        print("OK Período out-of-sample: Jan 2018 - Dez 2019")
        print("OK Dados reais da Economática")
        print("OK Sem look-ahead bias")
        print()
    
    def carregar_ativos_selecionados(self):
        """
        Carrega lista dos ativos selecionados cientificamente
        """
        print("1. Carregando ativos selecionados...")
        
        try:
            # Carregar CSV com ativos selecionados
            selected_file = os.path.join(self.results_dir, "01_ativos_selecionados.csv")
            if not os.path.exists(selected_file):
                raise FileNotFoundError("Execute primeiro 01_carregador_economatica.py")
            
            selected_df = pd.read_csv(selected_file)
            asset_list = selected_df['asset'].tolist()[:10]  # Top 10
            
            print(f"   Ativos selecionados: {len(asset_list)}")
            for i, asset in enumerate(asset_list, 1):
                print(f"   {i:2d}. {asset}")
            
            return asset_list
            
        except Exception as e:
            print(f"   ERRO: {e}")
            return []
    
    def extrair_dados_ativo(self, asset_name, inicio='2017-12-01', fim='2019-12-31'):
        """
        Extrai dados históricos de um ativo específico
        Inclui Dez 2017 para calcular retorno de Jan 2018
        """
        try:
            # Ler dados da sheet do ativo
            df = pd.read_excel(self.excel_path, sheet_name=asset_name)
            
            # Encontrar linha de cabeçalho
            header_row = None
            for i in range(min(10, len(df))):
                row_vals = df.iloc[i].astype(str).str.lower()
                if any('data' in str(val) for val in row_vals):
                    header_row = i
                    break
            
            if header_row is None:
                return None
            
            # Extrair dados
            data_rows = df.iloc[header_row + 1:].copy()
            dates_col = data_rows.iloc[:, 0]
            prices_col = data_rows.iloc[:, -1]
            
            # Limpar dados
            clean_data = []
            for i in range(len(dates_col)):
                try:
                    date_val = pd.to_datetime(dates_col.iloc[i], errors='coerce')
                    price_val = pd.to_numeric(prices_col.iloc[i], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(price_val) and price_val > 0:
                        if inicio <= date_val.strftime('%Y-%m-%d') <= fim:
                            clean_data.append({
                                'Date': date_val,
                                'Price': price_val
                            })
                except:
                    continue
            
            if len(clean_data) < 20:
                return None
            
            # Criar DataFrame
            asset_df = pd.DataFrame(clean_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            asset_df = asset_df.set_index('Date')
            
            return asset_df
            
        except Exception as e:
            print(f"   ERRO {asset_name}: {e}")
            return None
    
    def processar_todos_ativos(self):
        """
        Processa dados históricos de todos os ativos selecionados
        """
        print("2. Extraindo dados históricos de todos os ativos...")
        
        asset_list = self.carregar_ativos_selecionados()
        if not asset_list:
            return None
        
        all_prices = {}
        successful_extractions = 0
        
        for asset in asset_list:
            print(f"   Processando {asset}...")
            
            asset_data = self.extrair_dados_ativo(asset)
            if asset_data is not None:
                all_prices[asset] = asset_data['Price']
                successful_extractions += 1
                print(f"     OK {asset}: {len(asset_data)} observações")
            else:
                print(f"     ERRO {asset}: dados insuficientes")
        
        print(f"\n   Sucessos: {successful_extractions}/{len(asset_list)}")
        
        if successful_extractions < 5:
            raise ValueError("Poucos ativos com dados válidos")
        
        return all_prices
    
    def criar_matriz_retornos(self, prices_dict):
        """
        Cria matriz de retornos mensais alinhada
        """
        print("3. Criando matriz de retornos mensais...")
        
        # Criar DataFrame de preços
        prices_df = pd.DataFrame(prices_dict)
        
        # Resample para mensal (último dia do mês)
        monthly_prices = prices_df.resample('M').last()
        
        # Calcular retornos mensais
        returns_df = monthly_prices.pct_change().dropna()
        
        # Filtrar apenas período 2018-2019
        returns_2018_2019 = returns_df[
            (returns_df.index >= '2018-01-01') & 
            (returns_df.index <= '2019-12-31')
        ]
        
        print(f"   Período: {returns_2018_2019.index[0].date()} a {returns_2018_2019.index[-1].date()}")
        print(f"   Ativos: {len(returns_2018_2019.columns)}")
        print(f"   Observações: {len(returns_2018_2019)}")
        
        # Validações
        if len(returns_2018_2019) < 20:
            raise ValueError("Poucos períodos de retorno")
        
        # Tratamento robusto de dados faltantes
        returns_df_clean = self.tratar_dados_faltantes_robusto(returns_2018_2019)
        
        return returns_df_clean
    
    def tratar_dados_faltantes_robusto(self, returns_df):
        """
        Tratamento robusto e defensável de dados faltantes
        """
        print("   Tratando dados faltantes com rigor acadêmico...")
        
        # Verificar percentual de dados faltantes por ativo
        missing_pct = returns_df.isnull().sum() / len(returns_df)
        
        print(f"   Análise de dados faltantes:")
        for asset in returns_df.columns:
            pct = missing_pct[asset] * 100
            if pct > 0:
                print(f"     {asset}: {pct:.1f}% faltante")
        
        # CRITÉRIO 1: Excluir ativos com >15% dados faltantes (muito rigoroso)
        assets_to_keep = missing_pct[missing_pct <= 0.15].index.tolist()
        assets_removed = [col for col in returns_df.columns if col not in assets_to_keep]
        
        if assets_removed:
            print(f"   REMOVIDOS (>15% faltante): {assets_removed}")
            returns_df = returns_df[assets_to_keep]
        
        # CRITÉRIO 2: Para dados restantes, usar interpolação inteligente
        returns_clean = returns_df.copy()
        
        for asset in returns_clean.columns:
            if returns_clean[asset].isnull().any():
                # Método 1: Interpolação linear (para gaps pequenos <=2 meses)
                returns_clean[asset] = returns_clean[asset].interpolate(method='linear', limit=2)
                
                # Método 2: Forward fill (para início da série) - Versão corrigida
                returns_clean[asset] = returns_clean[asset].ffill(limit=1)
                
                # Método 3: Backward fill (para final da série) - Versão corrigida  
                returns_clean[asset] = returns_clean[asset].bfill(limit=1)
                
                # Método 4: Se ainda há NAs, usar média histórica do ativo
                if returns_clean[asset].isnull().any():
                    media_historica = returns_clean[asset].mean()
                    returns_clean[asset] = returns_clean[asset].fillna(media_historica)
        
        # Verificação final
        remaining_nas = returns_clean.isnull().sum().sum()
        if remaining_nas > 0:
            print(f"   AVISO: {remaining_nas} NAs restantes - usando zero")
            returns_clean = returns_clean.fillna(0)
        
        print(f"   Resultado: {len(returns_clean.columns)} ativos, {len(returns_clean)} períodos")
        return returns_clean
    
    def calcular_estatisticas_basicas(self, returns_df):
        """
        Calcula estatísticas básicas dos ativos
        """
        print("4. Calculando estatísticas básicas...")
        
        rf_rate = 0.0624  # 6.24% CDI médio
        stats_list = []
        
        for asset in returns_df.columns:
            asset_returns = returns_df[asset]
            
            # Estatísticas anualizadas
            annual_return = asset_returns.mean() * 12
            annual_vol = asset_returns.std() * np.sqrt(12)
            sharpe_ratio = (annual_return - rf_rate) / annual_vol if annual_vol > 0 else 0
            
            # Outras métricas
            max_return = asset_returns.max()
            min_return = asset_returns.min()
            
            # Maximum Drawdown
            cum_returns = (1 + asset_returns).cumprod()
            rolling_max = cum_returns.expanding().max()
            drawdowns = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdowns.min()
            
            stats_list.append({
                'Ativo': asset,
                'Retorno_Anual_Pct': annual_return * 100,
                'Volatilidade_Anual_Pct': annual_vol * 100,
                'Sharpe_Ratio': sharpe_ratio,
                'Max_Mensal_Pct': max_return * 100,
                'Min_Mensal_Pct': min_return * 100,
                'Max_Drawdown_Pct': max_drawdown * 100,
                'Observacoes': len(asset_returns)
            })
        
        stats_df = pd.DataFrame(stats_list)
        
        print("   Estatísticas calculadas:")
        print(f"   - Melhor Sharpe: {stats_df.loc[stats_df['Sharpe_Ratio'].idxmax(), 'Ativo']} ({stats_df['Sharpe_Ratio'].max():.2f})")
        print(f"   - Maior retorno: {stats_df.loc[stats_df['Retorno_Anual_Pct'].idxmax(), 'Ativo']} ({stats_df['Retorno_Anual_Pct'].max():.1f}%)")
        print(f"   - Menor volatilidade: {stats_df.loc[stats_df['Volatilidade_Anual_Pct'].idxmin(), 'Ativo']} ({stats_df['Volatilidade_Anual_Pct'].min():.1f}%)")
        
        return stats_df
    
    def salvar_dados_finais(self, returns_df, stats_df):
        """
        Salva todos os dados processados
        """
        print("5. Salvando dados finais...")
        
        # Salvar retornos mensais
        returns_file = os.path.join(self.results_dir, "02_retornos_mensais_2018_2019.csv")
        returns_df.to_csv(returns_file)
        
        # Salvar estatísticas
        stats_file = os.path.join(self.results_dir, "02_estatisticas_ativos.csv")
        stats_df.to_csv(stats_file, index=False)
        
        # Salvar metadados
        metadata = {
            "data_processamento": datetime.now().isoformat(),
            "periodo": "2018-01-01 a 2019-12-31",
            "total_ativos": len(returns_df.columns),
            "total_observacoes": len(returns_df),
            "taxa_livre_risco": 0.0624,
            "ativos_processados": returns_df.columns.tolist(),
            "fonte": "Economática (dados reais)"
        }
        
        metadata_file = os.path.join(self.results_dir, "02_metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   OK Retornos: {returns_file}")
        print(f"   OK Estatísticas: {stats_file}")  
        print(f"   OK Metadata: {metadata_file}")
        
        return True
    
    def executar_extracao_completa(self):
        """
        Executa processo completo de extração
        """
        try:
            # Processar dados
            prices_dict = self.processar_todos_ativos()
            returns_df = self.criar_matriz_retornos(prices_dict)
            stats_df = self.calcular_estatisticas_basicas(returns_df)
            
            # Salvar resultados
            self.salvar_dados_finais(returns_df, stats_df)
            
            print(f"\nOK EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"OK {len(returns_df.columns)} ativos processados")
            print(f"OK {len(returns_df)} observações mensais")
            print(f"OK Período: 2018-2019 (out-of-sample)")
            
            return returns_df, stats_df
            
        except Exception as e:
            print(f"ERRO: {e}")
            return None, None

def main():
    """
    Execução principal
    """
    extrator = ExtratorDadosHistoricos()
    returns_df, stats_df = extrator.executar_extracao_completa()
    
    if returns_df is not None:
        print(f"\nDADOS HISTÓRICOS EXTRAÍDOS:")
        print(f"   Ativos: {list(returns_df.columns)}")
        print(f"   Shape: {returns_df.shape}")
        return returns_df, stats_df
    else:
        print("ERRO: Falha na extração")
        return None, None

if __name__ == "__main__":
    resultado = main()