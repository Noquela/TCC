"""
Carregador de Dados Reais da Economatica
Adapta os dados reais para usar com os scripts existentes do TCC

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class EconomaticaLoader:
    """
    Carrega dados reais da Economatica e adapta para uso nos scripts existentes
    """
    
    def __init__(self, data_path="../DataBase/Economatica-8900701390-20250812230945 (1).xlsx"):
        self.data_path = data_path
        self.selected_assets = [
            'PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3',
            'B3SA3', 'WEGE3', 'RENT3', 'LREN3', 'ELET3'
        ]
        self.asset_info = {
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
        
    def load_selected_sheets_only(self):
        """
        Carrega apenas as abas dos ativos selecionados (mais rápido)
        """
        print("Carregando apenas abas dos ativos selecionados...")
        try:
            selected_sheets = {}
            for asset in self.selected_assets:
                try:
                    sheet_data = pd.read_excel(self.data_path, sheet_name=asset)
                    selected_sheets[asset] = sheet_data
                    print(f"  OK {asset} carregado")
                except Exception as e:
                    print(f"  ERRO {asset} não encontrado ou erro: {e}")
            
            print(f"Total de abas carregadas: {len(selected_sheets)}")
            return selected_sheets
        except Exception as e:
            print(f"Erro ao carregar arquivo: {e}")
            return None
    
    def extract_asset_data(self, sheet_data, asset_code):
        """
        Extrai dados de preço de uma aba específica
        """
        try:
            # Examinar estrutura da aba
            if sheet_data.shape[0] < 5:
                return None  # Aba muito pequena, provavelmente sem dados
            
            # Tentar encontrar onde começam os dados
            # Procurar pela coluna de Data
            date_row = None
            for i in range(min(10, sheet_data.shape[0])):
                if 'Data' in str(sheet_data.iloc[i, 0]) or 'data' in str(sheet_data.iloc[i, 0]).lower():
                    date_row = i
                    break
            
            if date_row is None:
                # Tentar estrutura padrão (linha 2 geralmente tem os headers)
                if sheet_data.shape[0] > 3:
                    date_row = 2
                else:
                    return None
            
            # Extrair dados a partir da linha identificada
            data_start = date_row + 1
            if data_start >= sheet_data.shape[0]:
                return None
                
            # Pegar dados das colunas (assumindo estrutura típica da Economatica)
            raw_data = sheet_data.iloc[data_start:].copy()
            
            # Primeira coluna deve ser data
            dates = raw_data.iloc[:, 0]
            
            # Procurar coluna de preços (geralmente "Fechamento", "Média" ou similar)
            price_col = None
            header_row = sheet_data.iloc[date_row]
            
            for i, col_name in enumerate(header_row):
                if isinstance(col_name, str):
                    if any(keyword in col_name.lower() for keyword in ['fechamento', 'média', 'medio', 'close', 'preço']):
                        price_col = i
                        break
            
            # Se não encontrou, usar uma coluna de preço padrão (geralmente coluna 6 ou 7)
            if price_col is None:
                # Tentar colunas típicas de preço
                for col_idx in [6, 7, 5, 8]:
                    if col_idx < raw_data.shape[1]:
                        sample_values = raw_data.iloc[:5, col_idx].dropna()
                        if len(sample_values) > 0 and all(pd.to_numeric(sample_values, errors='coerce').notna()):
                            price_col = col_idx
                            break
            
            if price_col is None:
                return None
                
            prices = raw_data.iloc[:, price_col]
            
            # Limpar e converter dados
            clean_data = []
            for i in range(len(dates)):
                try:
                    date_val = pd.to_datetime(dates.iloc[i], errors='coerce')
                    price_val = pd.to_numeric(prices.iloc[i], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(price_val) and price_val > 0:
                        clean_data.append({
                            'Date': date_val,
                            'Price': price_val
                        })
                except:
                    continue
            
            if len(clean_data) < 10:  # Muito poucos dados válidos
                return None
                
            # Criar DataFrame
            asset_df = pd.DataFrame(clean_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            
            return asset_df
            
        except Exception as e:
            print(f"Erro ao processar {asset_code}: {e}")
            return None
    
    def load_selected_assets(self, start_date='2018-01-01', end_date='2019-12-31'):
        """
        Carrega dados dos ativos selecionados para o período especificado
        """
        print(f"Carregando dados dos ativos selecionados para {start_date} a {end_date}...")
        
        all_sheets = self.load_selected_sheets_only()
        if all_sheets is None:
            return None, None
            
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        asset_prices = {}
        successful_assets = []
        
        for asset in self.selected_assets:
            print(f"Processando {asset}...")
            
            if asset in all_sheets:
                asset_data = self.extract_asset_data(all_sheets[asset], asset)
                
                if asset_data is not None and len(asset_data) > 0:
                    # Filtrar por período
                    period_data = asset_data[
                        (asset_data['Date'] >= start_date) & 
                        (asset_data['Date'] <= end_date)
                    ].copy()
                    
                    if len(period_data) >= 12:  # Pelo menos 12 observações no período
                        # Converter para mensal (pegar último dia de cada mês)
                        period_data['YearMonth'] = period_data['Date'].dt.to_period('M')
                        monthly_data = period_data.groupby('YearMonth').last().reset_index()
                        monthly_data['Date'] = monthly_data['YearMonth'].dt.end_time
                        
                        if len(monthly_data) >= 12:  # Pelo menos 12 meses
                            asset_prices[asset] = monthly_data[['Date', 'Price']].set_index('Date')['Price']
                            successful_assets.append(asset)
                            print(f"  OK {asset}: {len(monthly_data)} observações mensais")
                        else:
                            print(f"  ERRO {asset}: Poucos dados mensais ({len(monthly_data)})")
                    else:
                        print(f"  ERRO {asset}: Poucos dados no período ({len(period_data)})")
                else:
                    print(f"  ERRO {asset}: Não foi possível extrair dados")
            else:
                print(f"  ERRO {asset}: Aba não encontrada")
        
        if len(successful_assets) < 5:
            print(f"ATENÇÃO: Apenas {len(successful_assets)} ativos com dados suficientes!")
            print("Ativos bem-sucedidos:", successful_assets)
            return None, None
        
        # Criar DataFrame de preços alinhado
        price_df = pd.DataFrame(asset_prices)
        price_df = price_df.dropna()  # Remove períodos com dados faltantes
        
        if len(price_df) < 12:
            print("ERRO: Poucos períodos com dados completos para todos os ativos")
            return None, None
        
        # Calcular retornos logarítmicos
        returns_df = np.log(price_df / price_df.shift(1)).dropna()
        
        print(f"\nDados carregados com sucesso!")
        print(f"Ativos: {list(returns_df.columns)}")
        print(f"Período: {returns_df.index[0].date()} a {returns_df.index[-1].date()}")
        print(f"Observações: {len(returns_df)}")
        
        return returns_df, price_df
    
    def get_asset_info_for_successful(self, successful_assets):
        """
        Retorna informações dos ativos que foram carregados com sucesso
        """
        return {asset: self.asset_info[asset] for asset in successful_assets if asset in self.asset_info}
    
    def create_summary_stats(self, returns_df):
        """
        Cria estatísticas resumidas dos dados carregados
        """
        if returns_df is None:
            return None
            
        stats_data = []
        
        for asset in returns_df.columns:
            asset_returns = returns_df[asset]
            
            # Estatísticas básicas
            annual_return = asset_returns.mean() * 12
            annual_vol = asset_returns.std() * np.sqrt(12)
            min_return = asset_returns.min()
            max_return = asset_returns.max()
            
            # Informações do ativo
            info = self.asset_info.get(asset, {'name': asset, 'sector': 'N/A'})
            
            stats_data.append({
                'Ativo': asset,
                'Nome': info['name'],
                'Setor': info['sector'],
                'Retorno Anual (%)': f"{annual_return*100:.2f}%",
                'Volatilidade Anual (%)': f"{annual_vol*100:.2f}%",
                'Retorno Min (%)': f"{min_return*100:.2f}%",
                'Retorno Max (%)': f"{max_return*100:.2f}%",
                'Observações': len(asset_returns)
            })
        
        return pd.DataFrame(stats_data)

def main():
    """
    Testa o carregamento dos dados reais
    """
    print("=== TESTE DE CARREGAMENTO DOS DADOS REAIS DA ECONOMATICA ===")
    print()
    
    loader = EconomaticaLoader()
    
    # Carregar dados
    returns_df, prices_df = loader.load_selected_assets()
    
    if returns_df is not None:
        # Mostrar estatísticas
        summary_stats = loader.create_summary_stats(returns_df)
        print("\n=== ESTATÍSTICAS DOS DADOS CARREGADOS ===")
        print(summary_stats.to_string(index=False))
        
        # Salvar dados para uso nos outros scripts
        returns_df.to_csv("../results/real_returns_data.csv")
        prices_df.to_csv("../results/real_prices_data.csv")
        summary_stats.to_csv("../results/real_data_summary.csv", index=False)
        
        print(f"\nDados salvos em:")
        print("- real_returns_data.csv")
        print("- real_prices_data.csv") 
        print("- real_data_summary.csv")
        
        return returns_df, prices_df
    else:
        print("ERRO: Não foi possível carregar dados suficientes!")
        return None, None

if __name__ == "__main__":
    # Criar diretório para resultados
    import os
    os.makedirs('../results', exist_ok=True)
    
    # Executar teste
    returns, prices = main()