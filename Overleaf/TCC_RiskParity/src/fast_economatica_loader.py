"""
Fast Economatica Loader - Processamento otimizado
Carrega apenas sheets válidas da Economática de forma eficiente

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class FastEconomaticaLoader:
    """
    Carregador otimizado que processa sheets válidas rapidamente
    """
    
    def __init__(self, data_dir="../data/DataBase"):
        self.data_dir = data_dir
        
        # Arquivos da Economática
        self.main_excel = os.path.join(data_dir, "Economatica-8900701390-20250812230945 (1).xlsx")
        self.sectors_excel = os.path.join(data_dir, "economatica (1).xlsx")
        
        print("=== FAST ECONOMATICA LOADER - PROCESSAMENTO OTIMIZADO ===")
        print(f"Arquivo principal: {os.path.basename(self.main_excel)}")
        print(f"Arquivo de setores: {os.path.basename(self.sectors_excel)}")
        print()
        
        # Carregar mapeamento de setores
        self.sectors_mapping = self.load_sectors_mapping()
        
        # Lista de ativos conhecidos para tentar primeiro
        self.known_assets = [
            'ABEV3', 'B3SA3', 'BBDC4', 'BBAS3', 'BEEF3', 'BPAC11', 'BRFS3',
            'BRKM5', 'CCRO3', 'CIEL3', 'CMIG4', 'CSAN3', 'CSNA3', 'CVCB3',
            'CYRE3', 'ELET3', 'ELET6', 'EMBR3', 'ENBR3', 'EQTL3', 'FLRY3',
            'GGBR4', 'GOAU4', 'HYPE3', 'IGTA3', 'IRBR3', 'ITSA4', 'ITUB4',
            'JBSS3', 'KLBN11', 'LAME4', 'LREN3', 'MGLU3', 'MRFG3', 'MRVE3',
            'MULT3', 'NTCO3', 'PCAR3', 'PETR3', 'PETR4', 'QUAL3', 'RADL3',
            'RAIL3', 'RENT3', 'SBSP3', 'SUZB3', 'TAEE11', 'TIMS3', 'TOTS3',
            'UGPA3', 'USIM5', 'VALE3', 'VIVT4', 'VVAR3', 'WEGE3', 'YDUQ3'
        ]
        
    def load_sectors_mapping(self):
        """
        Carrega classificação setorial do excel de setores
        """
        print("1. Carregando classificação setorial...")
        
        try:
            sectors_df = pd.read_excel(self.sectors_excel, sheet_name=0)
            print(f"   Shape: {sectors_df.shape}")
            
            # Encontrar linha de cabeçalho
            header_row = None
            for i in range(min(10, len(sectors_df))):
                if pd.notna(sectors_df.iloc[i, 1]) and 'Nome' in str(sectors_df.iloc[i, 1]):
                    header_row = i
                    break
            
            if header_row is None:
                header_row = 2
                
            clean_data = sectors_df.iloc[header_row + 1:].copy()
            clean_data = clean_data.dropna(subset=[clean_data.columns[1]])
            
            sectors_map = {}
            
            # Procurar coluna de setor
            setor_col = None
            for col_idx, col_name in enumerate(sectors_df.iloc[header_row]):
                if pd.notna(col_name) and any(word in str(col_name).lower() for word in ['setor', 'econômico', 'bovespa']):
                    setor_col = col_idx
                    break
            
            if setor_col is None:
                setor_col = len(sectors_df.columns) - 2
                
            # Mapear ativos para setores
            for idx, row in clean_data.iterrows():
                try:
                    asset_name = str(row.iloc[1]).strip()
                    sector = str(row.iloc[setor_col]).strip() if setor_col < len(row) else 'Sem Setor'
                    
                    if asset_name and asset_name != 'nan' and len(asset_name) > 2:
                        asset_code = None
                        words = asset_name.split()
                        
                        for word in words:
                            if len(word) >= 5 and (word[-1].isdigit() or word[-1] in 'FMA'):
                                asset_code = word
                                break
                        
                        if not asset_code:
                            asset_code = asset_name
                        
                        sectors_map[asset_code] = sector
                        
                except Exception as e:
                    continue
            
            print(f"   OK: {len(sectors_map)} ativos mapeados")
            return sectors_map
            
        except Exception as e:
            print(f"   ERRO: {e}")
            return {}
    
    def get_sheet_names_sample(self):
        """
        Obtém lista de sheets de forma mais rápida
        """
        print("2. Obtendo lista de sheets...")
        
        try:
            excel_file = pd.ExcelFile(self.main_excel)
            all_sheets = excel_file.sheet_names
            
            print(f"   Total: {len(all_sheets)} sheets")
            
            # Priorizar assets conhecidos
            priority_sheets = []
            other_sheets = []
            
            for sheet in all_sheets:
                if any(asset in sheet.upper() for asset in self.known_assets):
                    priority_sheets.append(sheet)
                else:
                    other_sheets.append(sheet)
            
            final_sheets = priority_sheets + other_sheets[:200]  # Limitar para teste
            
            print(f"   Priorizados: {len(priority_sheets)}")
            print(f"   Para processar: {len(final_sheets)}")
            
            return final_sheets
            
        except Exception as e:
            print(f"   ERRO: {e}")
            return []
    
    def extract_quick_asset_data(self, sheet_name):
        """
        Extração rápida de dados de asset
        """
        try:
            sheet_data = pd.read_excel(self.main_excel, sheet_name=sheet_name, nrows=2000)
            
            if sheet_data.empty or len(sheet_data) < 50:
                return None
            
            # Buscar linha de data rapidamente
            data_row = 2  # Padrão Economática
            
            raw_data = sheet_data.iloc[data_row + 1:].copy()
            
            if len(raw_data) < 20:
                return None
            
            # Primeira coluna = datas, última = preços
            dates_col = raw_data.iloc[:, 0]
            prices_col = raw_data.iloc[:, -1]
            
            # Limpar dados rapidamente
            cleaned_data = []
            for i in range(min(500, len(dates_col))):  # Limitar processamento
                try:
                    date_val = pd.to_datetime(dates_col.iloc[i], errors='coerce')
                    price_val = pd.to_numeric(prices_col.iloc[i], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(price_val) and price_val > 0:
                        cleaned_data.append({
                            'Date': date_val,
                            'Price': price_val
                        })
                except:
                    continue
            
            if len(cleaned_data) < 20:
                return None
            
            asset_df = pd.DataFrame(cleaned_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            asset_df = asset_df.set_index('Date')
            
            return asset_df
            
        except Exception as e:
            return None
    
    def load_fast_sample(self, start_date='2014-01-01', end_date='2017-12-31', max_assets=50):
        """
        Carregamento rápido de amostra de ativos
        """
        print(f"3. Carregamento rápido ({start_date} a {end_date})...")
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        sheets_to_process = self.get_sheet_names_sample()
        
        assets_data = {}
        successful_assets = []
        processed = 0
        
        print(f"   Processando até {max_assets} ativos...")
        
        for sheet_name in sheets_to_process:
            if len(successful_assets) >= max_assets:
                break
                
            processed += 1
            if processed % 20 == 0:
                print(f"   Progresso: {processed} processados, {len(successful_assets)} válidos")
            
            try:
                asset_data = self.extract_quick_asset_data(sheet_name)
                
                if asset_data is not None:
                    # Filtrar período histórico
                    period_data = asset_data[
                        (asset_data.index >= start_dt) & 
                        (asset_data.index <= end_dt)
                    ]
                    
                    if len(period_data) >= 24:
                        monthly_data = period_data.resample('M').last().dropna()
                        
                        if len(monthly_data) >= 20:
                            assets_data[sheet_name] = monthly_data['Price']
                            successful_assets.append(sheet_name)
                            print(f"     VÁLIDO: {sheet_name} ({len(monthly_data)} meses)")
                            
            except Exception as e:
                continue
        
        print(f"   RESULTADO: {len(successful_assets)} ativos válidos")
        
        if len(successful_assets) == 0:
            return None, None
        
        # Criar DataFrame alinhado
        prices_df = pd.DataFrame(assets_data)
        
        # Remover ativos com muitos dados faltantes
        min_obs = int(len(prices_df) * 0.7)
        complete_assets = []
        
        for asset in prices_df.columns:
            if prices_df[asset].count() >= min_obs:
                complete_assets.append(asset)
        
        if len(complete_assets) == 0:
            return None, None
        
        final_prices = prices_df[complete_assets].dropna()
        
        print(f"   Dados finais:")
        print(f"     Ativos: {len(final_prices.columns)}")
        print(f"     Período: {final_prices.index[0].date()} a {final_prices.index[-1].date()}")
        print(f"     Observações: {len(final_prices)}")
        
        return final_prices, complete_assets

def main():
    """
    Teste do carregador rápido
    """
    print("TESTANDO CARREGAMENTO RÁPIDO DA ECONOMÁTICA")
    print()
    
    # Inicializar carregador
    loader = FastEconomaticaLoader()
    
    # Carregar amostra de dados 2014-2017
    prices_df, valid_assets = loader.load_fast_sample('2014-01-01', '2017-12-31', max_assets=100)
    
    if prices_df is not None:
        print()
        print("CARREGAMENTO BEM-SUCEDIDO!")
        print(f"Total de ativos válidos: {len(valid_assets)}")
        
        # Mostrar ativos
        print("\nAtivos carregados:")
        for i, asset in enumerate(valid_assets):
            sector = loader.sectors_mapping.get(asset, 'Setor Desconhecido')
            print(f"  {i+1:2d}. {asset} - {sector}")
        
        # Salvar resultados
        results_dir = "../results"
        os.makedirs(results_dir, exist_ok=True)
        
        prices_df.to_csv(os.path.join(results_dir, "fast_historical_prices_2014_2017.csv"))
        
        with open(os.path.join(results_dir, "fast_valid_assets_list.txt"), 'w') as f:
            for asset in valid_assets:
                sector = loader.sectors_mapping.get(asset, 'Setor Desconhecido')
                f.write(f"{asset},{sector}\n")
        
        print(f"\nArquivos salvos em {results_dir}/")
        
        return prices_df, valid_assets, loader.sectors_mapping
    else:
        print("\nERRO: Falha no carregamento!")
        return None, None, None

if __name__ == "__main__":
    prices, assets, sectors = main()