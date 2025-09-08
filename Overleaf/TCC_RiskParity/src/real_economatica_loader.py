"""
Real Economatica Loader - REFAZER COMPLETO
Carrega OBRIGATORIAMENTE todos os dados das 507 sheets da Economática
Integra com excel de setores - SEM LISTAS FIXAS

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class RealEconomaticaLoader:
    """
    Carregador que usa OBRIGATORIAMENTE os dados reais das 507 sheets
    """
    
    def __init__(self, data_dir="../data/DataBase"):
        self.data_dir = data_dir
        
        # Arquivos da Economática
        self.main_excel = os.path.join(data_dir, "Economatica-8900701390-20250812230945 (1).xlsx")
        self.sectors_excel = os.path.join(data_dir, "economatica (1).xlsx")
        
        print("=== REAL ECONOMATICA LOADER - DADOS OBRIGATÓRIOS ===")
        print(f"Arquivo principal: {os.path.basename(self.main_excel)}")
        print(f"Arquivo de setores: {os.path.basename(self.sectors_excel)}")
        print("ZERO listas fixas - TUDO baseado nos dados reais!")
        print()
        
        # Carregar mapeamento de setores REAL
        self.sectors_mapping = self.load_real_sectors_mapping()
        
    def load_real_sectors_mapping(self):
        """
        Carrega classificação setorial REAL do excel de setores
        """
        print("1. Carregando classificação setorial REAL...")
        
        try:
            # Ler excel de setores
            sectors_df = pd.read_excel(self.sectors_excel, sheet_name=0)
            print(f"   Shape do arquivo de setores: {sectors_df.shape}")
            
            # Encontrar linha de cabeçalho procurando por "Nome"
            header_row = None
            for i in range(min(20, len(sectors_df))):
                if pd.notna(sectors_df.iloc[i, 1]) and 'Nome' in str(sectors_df.iloc[i, 1]):
                    header_row = i
                    break
            
            if header_row is None:
                print("   Tentando linha 2 como padrão...")
                header_row = 2
            
            print(f"   Header encontrado na linha: {header_row}")
            
            # Extrair dados limpos
            clean_data = sectors_df.iloc[header_row + 1:].copy()
            clean_data = clean_data.dropna(subset=[clean_data.columns[1]])  # Remove linhas sem nome
            
            sectors_map = {}
            setor_col = None
            
            # Procurar coluna de setor
            for col_idx, col_name in enumerate(sectors_df.iloc[header_row]):
                if pd.notna(col_name) and any(word in str(col_name).lower() for word in ['setor', 'econômico', 'bovespa']):
                    setor_col = col_idx
                    break
            
            if setor_col is None:
                print("   Tentando colunas da direita para setor...")
                setor_col = len(sectors_df.columns) - 2  # Penúltima coluna
            
            print(f"   Coluna de setor: {setor_col}")
            
            # Mapear ativos para setores
            for idx, row in clean_data.iterrows():
                try:
                    asset_name = str(row.iloc[1]).strip()
                    sector = str(row.iloc[setor_col]).strip() if setor_col < len(row) else 'Sem Setor'
                    
                    if asset_name and asset_name != 'nan' and len(asset_name) > 2:
                        # Tentar extrair código do ativo (PETR4, VALE3, etc)
                        asset_code = None
                        words = asset_name.split()
                        
                        for word in words:
                            if len(word) >= 5 and (word[-1].isdigit() or word[-1] in 'FMA'):
                                asset_code = word
                                break
                        
                        if not asset_code:
                            # Se não achou, usar o próprio nome
                            asset_code = asset_name
                        
                        sectors_map[asset_code] = sector
                        
                except Exception as e:
                    continue
            
            print(f"   OK: {len(sectors_map)} ativos com setores mapeados")
            
            # Mostrar alguns exemplos
            print("   Exemplos de mapeamento:")
            count = 0
            for asset, sector in sectors_map.items():
                if count < 5:
                    print(f"     {asset} -> {sector}")
                    count += 1
                else:
                    break
            
            return sectors_map
            
        except Exception as e:
            print(f"   ERRO ao carregar setores: {e}")
            return {}
    
    def get_all_sheet_names(self):
        """
        Obtém nomes de TODAS as 507 sheets
        """
        print("2. Listando TODAS as sheets disponíveis...")
        
        try:
            excel_file = pd.ExcelFile(self.main_excel)
            all_sheets = excel_file.sheet_names
            
            print(f"   Total de sheets encontradas: {len(all_sheets)}")
            print(f"   Primeiras 10 sheets: {all_sheets[:10]}")
            print(f"   Últimas 5 sheets: {all_sheets[-5:]}")
            
            return all_sheets
            
        except Exception as e:
            print(f"   ERRO ao listar sheets: {e}")
            return []
    
    def extract_asset_data_from_sheet(self, sheet_name):
        """
        Extrai dados históricos REAIS de uma sheet específica
        """
        try:
            # Ler sheet
            sheet_data = pd.read_excel(self.main_excel, sheet_name=sheet_name)
            
            if sheet_data.empty or sheet_data.shape[0] < 10:
                return None
            
            # Verificar se sheet tem dados suficientes (>100 observações)
            if sheet_data.shape[0] < 100:
                return None
            
            # Procurar linha com "Data" ou similar
            data_row = None
            for i in range(min(10, len(sheet_data))):
                row_values = sheet_data.iloc[i].astype(str).str.lower()
                if any('data' in str(val) for val in row_values):
                    data_row = i
                    break
            
            if data_row is None:
                data_row = 2  # Padrão Economática
            
            # Extrair dados a partir da linha de dados
            raw_data = sheet_data.iloc[data_row + 1:].copy()
            
            if len(raw_data) < 5:
                return None
            
            # Primeira coluna = datas, procurar coluna de preços
            dates_col = raw_data.iloc[:, 0]
            
            # Na Economática, a primeira coluna são as datas, procurar coluna de preços
            # Baseado na estrutura: Data, Q Negs, Q Títs, Volume$, Fechamento, Mínimo, Máximo, Médio
            price_col_idx = None
            header = sheet_data.iloc[data_row] if data_row < len(sheet_data) else sheet_data.iloc[0]
            
            # Procurar coluna de fechamento primeiro
            for i, col_name in enumerate(header):
                if pd.notna(col_name):
                    col_str = str(col_name).lower()
                    if any(keyword in col_str for keyword in ['fechamento', 'fecha', 'close']):
                        price_col_idx = i
                        break
            
            # Se não encontrou fechamento, procurar média ou médio
            if price_col_idx is None:
                for i, col_name in enumerate(header):
                    if pd.notna(col_name):
                        col_str = str(col_name).lower()
                        if any(keyword in col_str for keyword in ['médio', 'medio', 'average']):
                            price_col_idx = i
                            break
            
            # Como último recurso, usar última coluna (geralmente tem preços)
            if price_col_idx is None:
                price_col_idx = len(header) - 1
            
            if price_col_idx is None:
                return None
            
            prices_col = raw_data.iloc[:, price_col_idx]
            
            # Limpar e converter dados
            cleaned_data = []
            for i in range(len(dates_col)):
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
            
            if len(cleaned_data) < 20:  # Mínimo de dados
                return None
            
            # Criar DataFrame final
            asset_df = pd.DataFrame(cleaned_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            asset_df = asset_df.set_index('Date')
            
            return asset_df
            
        except Exception as e:
            return None
    
    def load_all_assets_data(self, start_date='2014-01-01', end_date='2017-12-31'):
        """
        Carrega dados HISTÓRICOS de TODOS os ativos para seleção ex-ante
        """
        print(f"3. Carregando dados HISTÓRICOS ({start_date} a {end_date})...")
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        all_sheets = self.get_all_sheet_names()
        
        if not all_sheets:
            print("   ERRO: Nenhuma sheet encontrada!")
            return None, None
        
        assets_data = {}
        successful_assets = []
        failed_count = 0
        
        print(f"   Processando {len(all_sheets)} sheets...")
        
        # Processar cada sheet
        for i, sheet_name in enumerate(all_sheets):
            if i % 10 == 0:
                print(f"   Progresso: {i}/{len(all_sheets)} sheets processadas... ({len(successful_assets)} válidos)")
            
            try:
                asset_data = self.extract_asset_data_from_sheet(sheet_name)
                
                if asset_data is not None and len(asset_data) > 0:
                    # Filtrar por período histórico
                    period_data = asset_data[
                        (asset_data.index >= start_dt) & 
                        (asset_data.index <= end_dt)
                    ]
                    
                    if len(period_data) >= 24:  # Mínimo 2 anos de dados
                        # Converter para mensal
                        monthly_data = period_data.resample('M').last().dropna()
                        
                        if len(monthly_data) >= 20:  # Mínimo 20 meses
                            assets_data[sheet_name] = monthly_data['Price']
                            successful_assets.append(sheet_name)
                            print(f"     VÁLIDO: {sheet_name} ({len(monthly_data)} meses)")
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                continue
        
        print(f"   RESULTADO:")
        print(f"     Ativos com dados válidos: {len(successful_assets)}")
        print(f"     Ativos sem dados suficientes: {failed_count}")
        print(f"     Total processado: {len(all_sheets)}")
        
        if len(successful_assets) == 0:
            print("   ERRO CRÍTICO: Nenhum ativo com dados históricos suficientes!")
            return None, None
        
        # Criar DataFrame alinhado
        print("   Alinhando dados temporalmente...")
        prices_df = pd.DataFrame(assets_data)
        
        # Remover ativos com muitos dados faltantes
        min_observations = int(len(prices_df) * 0.8)  # 80% de completude
        complete_assets = []
        
        for asset in prices_df.columns:
            if prices_df[asset].count() >= min_observations:
                complete_assets.append(asset)
        
        if len(complete_assets) == 0:
            print("   ERRO: Nenhum ativo com completude suficiente!")
            return None, None
        
        final_prices = prices_df[complete_assets].dropna()
        
        print(f"   Dados finais alinhados:")
        print(f"     Ativos finais: {len(final_prices.columns)}")
        print(f"     Período: {final_prices.index[0].date()} a {final_prices.index[-1].date()}")
        print(f"     Observações: {len(final_prices)}")
        
        return final_prices, complete_assets

def main():
    """
    Teste do carregador real
    """
    print("TESTANDO CARREGAMENTO REAL DE DADOS DA ECONOMÁTICA")
    print()
    
    # Inicializar carregador
    loader = RealEconomaticaLoader()
    
    # Carregar dados históricos 2014-2017
    prices_df, valid_assets = loader.load_all_assets_data('2014-01-01', '2017-12-31')
    
    if prices_df is not None:
        print()
        print("CARREGAMENTO BEM-SUCEDIDO!")
        print(f"Total de ativos válidos: {len(valid_assets)}")
        print(f"Período dos dados: {prices_df.index[0].date()} a {prices_df.index[-1].date()}")
        
        # Mostrar alguns ativos de exemplo
        print("\nExemplos de ativos carregados:")
        for i, asset in enumerate(valid_assets[:10]):
            sector = loader.sectors_mapping.get(asset, 'Setor Desconhecido')
            print(f"  {i+1:2d}. {asset} - {sector}")
        
        if len(valid_assets) > 10:
            print(f"  ... e mais {len(valid_assets) - 10} ativos")
        
        # Salvar dados para próximas etapas
        results_dir = "../results"
        os.makedirs(results_dir, exist_ok=True)
        
        prices_df.to_csv(os.path.join(results_dir, "real_historical_prices_2014_2017.csv"))
        
        with open(os.path.join(results_dir, "valid_assets_list.txt"), 'w') as f:
            for asset in valid_assets:
                sector = loader.sectors_mapping.get(asset, 'Setor Desconhecido')
                f.write(f"{asset},{sector}\n")
        
        print(f"\nArquivos salvos em {results_dir}/")
        print("- real_historical_prices_2014_2017.csv")
        print("- valid_assets_list.txt")
        
        return prices_df, valid_assets, loader.sectors_mapping
    else:
        print("\nERRO: Falha no carregamento dos dados!")
        return None, None, None

if __name__ == "__main__":
    prices, assets, sectors = main()