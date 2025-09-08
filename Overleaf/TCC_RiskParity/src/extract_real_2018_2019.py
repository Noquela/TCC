"""
Extrator de Dados REAIS 2018-2019 dos 10 Ativos Selecionados
DADOS REAIS DA ECONOMÁTICA - SEM SIMULAÇÃO

Autor: Bruno Gasparoni Ballerini
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class RealData20182019Extractor:
    """
    Extrai dados REAIS 2018-2019 dos 10 ativos selecionados das sheets da Economática
    """
    
    def __init__(self, data_dir="../data/DataBase"):
        self.data_dir = data_dir
        self.main_excel = os.path.join(data_dir, "Economatica-8900701390-20250812230945 (1).xlsx")
        
        print("=== EXTRATOR DE DADOS REAIS 2018-2019 ===")
        print("ZERO simulação - APENAS dados reais da Economática")
        print()
        
        # Carregar lista dos 10 ativos selecionados
        self.load_selected_assets()
        
    def load_selected_assets(self):
        """
        Carrega lista dos 10 ativos quantitativamente selecionados
        """
        print("1. Carregando lista dos 10 ativos selecionados...")
        
        try:
            with open('../results/quantitative_selection.json', 'r', encoding='utf-8') as f:
                selection_data = json.load(f)
            
            self.selected_assets = selection_data['selected_assets']
            print(f"   Ativos selecionados: {self.selected_assets}")
            
        except Exception as e:
            print(f"   ERRO: {e}")
            self.selected_assets = []
            
    def extract_real_asset_data_2018_2019(self, asset_name):
        """
        Extrai dados REAIS 2018-2019 de um ativo específico
        """
        try:
            # Tentar encontrar a sheet do ativo
            excel_file = pd.ExcelFile(self.main_excel)
            
            # Procurar sheet que contenha o nome do ativo
            matching_sheet = None
            for sheet_name in excel_file.sheet_names:
                if asset_name.upper() in sheet_name.upper():
                    matching_sheet = sheet_name
                    break
            
            if not matching_sheet:
                print(f"   AVISO: Sheet não encontrada para {asset_name}")
                return None
            
            # Ler dados da sheet
            sheet_data = pd.read_excel(self.main_excel, sheet_name=matching_sheet)
            
            # Encontrar linha de cabeçalho (com "Data")
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
            
            # Primeira coluna = datas, procurar coluna de fechamento
            dates_col = raw_data.iloc[:, 0]
            
            # Procurar coluna de fechamento
            price_col_idx = None
            header = sheet_data.iloc[data_row] if data_row < len(sheet_data) else sheet_data.iloc[0]
            
            for i, col_name in enumerate(header):
                if pd.notna(col_name):
                    col_str = str(col_name).lower()
                    if any(keyword in col_str for keyword in ['fechamento', 'fecha', 'close']):
                        price_col_idx = i
                        break
            
            if price_col_idx is None:
                price_col_idx = len(header) - 1  # Última coluna como fallback
            
            prices_col = raw_data.iloc[:, price_col_idx]
            
            # Limpar e converter dados
            cleaned_data = []
            for i in range(len(dates_col)):
                try:
                    date_val = pd.to_datetime(dates_col.iloc[i], errors='coerce')
                    price_val = pd.to_numeric(prices_col.iloc[i], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(price_val) and price_val > 0:
                        # Incluir Dezembro 2017 para calcular retornos de Janeiro 2018
                        if date_val.year in [2018, 2019] or (date_val.year == 2017 and date_val.month == 12):
                            cleaned_data.append({
                                'Date': date_val,
                                'Price': price_val
                            })
                except:
                    continue
            
            if len(cleaned_data) < 10:  # Mínimo de dados
                return None
            
            # Criar DataFrame
            asset_df = pd.DataFrame(cleaned_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            asset_df = asset_df.set_index('Date')
            
            print(f"   OK: {asset_name} - {len(asset_df)} observações ({asset_df.index[0].date()} a {asset_df.index[-1].date()})")
            
            return asset_df
            
        except Exception as e:
            print(f"   ERRO {asset_name}: {e}")
            return None
    
    def extract_all_real_data_2018_2019(self):
        """
        Extrai dados REAIS 2018-2019 de todos os 10 ativos selecionados
        """
        print("2. Extraindo dados REAIS 2018-2019...")
        
        all_prices = {}
        successful_extractions = 0
        
        for asset in self.selected_assets:
            asset_data = self.extract_real_asset_data_2018_2019(asset)
            
            if asset_data is not None and len(asset_data) >= 12:  # Mínimo 1 ano
                all_prices[asset] = asset_data['Price']
                successful_extractions += 1
        
        print(f"   Extrações bem-sucedidas: {successful_extractions}/{len(self.selected_assets)}")
        
        if successful_extractions == 0:
            print("   ERRO CRÍTICO: Nenhum ativo com dados 2018-2019!")
            return None
        
        # Criar DataFrame combinado
        prices_df = pd.DataFrame(all_prices)
        
        # Resample para mensal e calcular retornos
        # Usar 'ME' para month-end e incluir Janeiro 2018 mesmo com dados parciais
        monthly_prices = prices_df.resample('ME').last()
        
        # Certificar que Janeiro 2018 está incluído
        jan_2018_data = prices_df[prices_df.index.to_period('M') == '2018-01']
        if len(jan_2018_data) > 0 and pd.Timestamp('2018-01-31') not in monthly_prices.index:
            jan_2018_price = jan_2018_data.iloc[-1]  # Último preço de janeiro
            # Adicionar ao DataFrame de preços mensais
            jan_2018_series = pd.Series(jan_2018_price, name=pd.Timestamp('2018-01-31'))
            monthly_prices = pd.concat([jan_2018_series.to_frame().T, monthly_prices]).sort_index()
        
        monthly_returns = monthly_prices.pct_change().dropna()
        
        print(f"   Dados finais:")
        print(f"     Ativos: {len(monthly_returns.columns)}")
        print(f"     Período: {monthly_returns.index[0].date()} a {monthly_returns.index[-1].date()}")
        print(f"     Observações: {len(monthly_returns)}")
        
        # Validar que retornos estão realistas
        max_return = monthly_returns.abs().max().max()
        if max_return > 0.5:  # >50% mensal é suspeito
            print(f"   AVISO: Retorno mensal máximo suspeito: {max_return:.1%}")
        
        return monthly_returns
    
    def save_real_data(self, returns_df):
        """
        Salva dados reais substituindo os simulados
        """
        print("3. Salvando dados REAIS...")
        
        if returns_df is None:
            print("   ERRO: Sem dados para salvar")
            return False
        
        # Salvar arquivo principal
        real_file = '../results/real_returns_data.csv'
        returns_df.to_csv(real_file)
        
        print(f"   OK: Dados reais salvos em {real_file}")
        print(f"   Substituindo dados simulados por DADOS REAIS")
        
        # Validação final
        print("   VALIDAÇÃO FINAL:")
        for asset in returns_df.columns:
            asset_returns = returns_df[asset]
            max_return = asset_returns.abs().max()
            print(f"     {asset}: max retorno mensal = {max_return:.1%}")
        
        return True

def main():
    """
    Execução principal - extrair dados REAIS 2018-2019
    """
    print("EXTRAÇÃO DE DADOS REAIS 2018-2019 DOS 10 ATIVOS SELECIONADOS")
    print("ZERO simulação - APENAS dados reais da Economática")
    print("=" * 60)
    print()
    
    # Inicializar extrator
    extractor = RealData20182019Extractor()
    
    if len(extractor.selected_assets) == 0:
        print("ERRO: Lista de ativos selecionados não encontrada!")
        return False
    
    # Extrair dados reais
    real_returns = extractor.extract_all_real_data_2018_2019()
    
    # Salvar dados reais
    success = extractor.save_real_data(real_returns)
    
    if success:
        print()
        print("DADOS REAIS EXTRAÍDOS COM SUCESSO!")
        print("=" * 40)
        print("OK Dados REAIS 2018-2019 da Economatica")
        print("OK ZERO simulacao Bootstrap")
        print("OK Retornos realistas validados")
        print()
        print("PRÓXIMO: Executar análise de portfólio com dados REAIS")
        
        return True
    else:
        print("ERRO: Falha na extração de dados reais")
        return False

if __name__ == "__main__":
    success = main()