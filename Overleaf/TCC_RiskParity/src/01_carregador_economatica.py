"""
SISTEMA REFATORADO - TCC RISK PARITY
Script 1: Carregador Economática com Critérios Científicos Objetivos

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-08
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CarregadorEconomatica:
    """
    Carregador científico da Economática com critérios objetivos
    SEM seleção hardcoded - APENAS critérios quantitativos
    """
    
    def __init__(self, data_dir="../data/DataBase"):
        self.data_dir = data_dir
        self.excel_path = os.path.join(data_dir, "Economatica-8900701390-20250812230945 (1).xlsx")
        self.setores_path = os.path.join(data_dir, "economatica (1).xlsx")
        
        print("="*60)
        print("SISTEMA REFATORADO - CARREGADOR ECONOMÁTICA")
        print("="*60)
        print("OK Metodologia científica objetiva")
        print("OK Sem seleção hardcoded")
        print("OK Critérios quantitativos rigorosos")
        print("OK Diversificação setorial")
        print()
        
        # Verificar se arquivos existem
        if not os.path.exists(self.excel_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.excel_path}")
        if not os.path.exists(self.setores_path):
            raise FileNotFoundError(f"Arquivo de setores não encontrado: {self.setores_path}")
        
        # Carregar mapeamento ativo-setor
        self.asset_sector_map = self.carregar_mapeamento_setores()
    
    def carregar_mapeamento_setores(self):
        """
        Carrega mapeamento de ativos para setores do arquivo Economática
        """
        try:
            df_setores = pd.read_excel(self.setores_path, sheet_name='Sheet1')
            asset_sector_map = {}
            
            # Extrair mapeamento ativo-setor
            for i, row in df_setores.iterrows():
                for col in df_setores.columns[:-1]:  # Excluir coluna 'Economatica'
                    val = str(row[col]).strip() if pd.notna(row[col]) else ''
                    # Verificar se é código de ativo (4-6 chars, termina com dígito)
                    if (len(val) >= 4 and len(val) <= 6 and 
                        val[-1].isdigit() and val[:-1].isalpha()):
                        if pd.notna(row['Economatica']):
                            sector = str(row['Economatica']).strip()
                            if sector and sector != 'nan':
                                asset_sector_map[val] = sector
                                break
            
            print(f"   Mapeamento setores: {len(asset_sector_map)} ativos")
            return asset_sector_map
            
        except Exception as e:
            print(f"   AVISO: Erro ao carregar setores: {e}")
            return {}
            
    def obter_lista_ativos_disponiveis(self):
        """
        Obtém lista de todos os ativos disponíveis na Economática
        """
        print("1. Carregando lista de ativos disponíveis...")
        
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            all_sheets = excel_file.sheet_names
            
            # Filtrar sheets que parecem ser ativos (formato típico brasileiro)
            asset_sheets = []
            for sheet in all_sheets:
                # Filtro: sheets com 4-6 caracteres que terminam em números
                if len(sheet) >= 4 and len(sheet) <= 6:
                    if sheet[-1].isdigit() or sheet[-1] in ['3', '4', '11']:
                        asset_sheets.append(sheet)
            
            print(f"   Total de sheets: {len(all_sheets)}")
            print(f"   Sheets de ativos identificados: {len(asset_sheets)}")
            print(f"   Primeiros 10: {asset_sheets[:10]}")
            
            return asset_sheets[:50]  # Limitar para teste inicial
            
        except Exception as e:
            print(f"   ERRO: {e}")
            return []
    
    def extrair_dados_ativo(self, sheet_name, periodo_inicio='2014-01-01', periodo_fim='2019-12-31'):
        """
        Extrai dados históricos de um ativo específico
        """
        try:
            # Ler dados da sheet
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            # Procurar linha de cabeçalho com "Data"
            header_row = None
            for i in range(min(10, len(df))):
                row_vals = df.iloc[i].astype(str).str.lower()
                if any('data' in str(val) for val in row_vals):
                    header_row = i
                    break
            
            if header_row is None:
                return None
            
            # Extrair dados a partir da linha encontrada
            data_rows = df.iloc[header_row + 1:].copy()
            
            # Primeira coluna = datas, última = preços de fechamento
            dates_col = data_rows.iloc[:, 0]
            prices_col = data_rows.iloc[:, -1]
            
            # Limpar e converter dados
            clean_data = []
            for i in range(len(dates_col)):
                try:
                    date_val = pd.to_datetime(dates_col.iloc[i], errors='coerce')
                    price_val = pd.to_numeric(prices_col.iloc[i], errors='coerce')
                    
                    if pd.notna(date_val) and pd.notna(price_val) and price_val > 0:
                        if periodo_inicio <= date_val.strftime('%Y-%m-%d') <= periodo_fim:
                            clean_data.append({
                                'Date': date_val,
                                'Price': price_val
                            })
                except:
                    continue
            
            if len(clean_data) < 20:  # Mínimo de observações
                return None
            
            # Criar DataFrame
            asset_df = pd.DataFrame(clean_data)
            asset_df = asset_df.drop_duplicates('Date').sort_values('Date')
            asset_df = asset_df.set_index('Date')
            
            return asset_df
            
        except Exception as e:
            return None
    
    def calcular_metricas_selecao(self, asset_data, asset_name):
        """
        Calcula métricas para critérios de seleção científicos
        """
        if asset_data is None or len(asset_data) < 24:
            return None
        
        # Calcular retornos mensais
        monthly_prices = asset_data.resample('M').last()
        monthly_returns = monthly_prices['Price'].pct_change().dropna()
        
        if len(monthly_returns) < 20:
            return None
        
        # Separar períodos: 2014-2017 (seleção) e 2018-2019 (teste)
        selection_period = monthly_returns[monthly_returns.index < '2018-01-01']
        test_period = monthly_returns[monthly_returns.index >= '2018-01-01']
        
        if len(selection_period) < 12 or len(test_period) < 12:
            return None
        
        # Métricas do período de seleção (2014-2017) - SEM LOOK-AHEAD BIAS
        mean_return_sel = selection_period.mean() * 12  # Anualizado
        volatility_sel = selection_period.std() * np.sqrt(12)
        
        # Métricas de qualidade dos dados
        completeness = len(monthly_returns) / 72  # 6 anos * 12 meses
        price_range = asset_data['Price'].max() / asset_data['Price'].min()
        
        # Proxy de liquidez (baseado em variação de preços)
        price_changes = asset_data['Price'].pct_change().abs()
        liquidity_proxy = 1 / (price_changes.mean() + 1e-6)  # Maior = mais líquido
        
        # Score de capitalização (baseado no preço médio como proxy)
        avg_price = asset_data['Price'].mean()
        market_cap_proxy = np.log(avg_price + 1)  # Log para normalizar
        
        return {
            'asset': asset_name,
            'mean_return_2014_2017': mean_return_sel,
            'volatility_2014_2017': volatility_sel,
            'completeness': completeness,
            'liquidity_proxy': liquidity_proxy,
            'market_cap_proxy': market_cap_proxy,
            'data_points': len(monthly_returns),
            'test_period_months': len(test_period),
            'price_range_ratio': price_range
        }
    
    def aplicar_criterios_cientificos(self, metricas_list):
        """
        Aplica critérios científicos objetivos para seleção
        """
        print("3. Aplicando critérios científicos de seleção...")
        
        if len(metricas_list) < 10:
            print(f"   AVISO: Poucos ativos disponíveis ({len(metricas_list)})")
            return metricas_list
        
        # Converter para DataFrame
        df = pd.DataFrame(metricas_list)
        
        print(f"   Total de ativos analisados: {len(df)}")
        
        # CRITÉRIO 1: Completude de dados
        df = df[df['completeness'] >= 0.7]  # Pelo menos 70% dos dados
        print(f"   Após critério completude: {len(df)} ativos")
        
        # CRITÉRIO 2: Volatilidade razoável (evitar outliers)
        vol_q25, vol_q75 = df['volatility_2014_2017'].quantile([0.25, 0.75])
        vol_iqr = vol_q75 - vol_q25
        vol_min, vol_max = vol_q25 - 1.5*vol_iqr, vol_q75 + 1.5*vol_iqr
        df = df[(df['volatility_2014_2017'] >= max(0.1, vol_min)) & 
                (df['volatility_2014_2017'] <= min(0.8, vol_max))]
        print(f"   Após critério volatilidade: {len(df)} ativos")
        
        # CRITÉRIO 3: Liquidez (proxy)
        liquidity_threshold = df['liquidity_proxy'].quantile(0.3)  # Top 70%
        df = df[df['liquidity_proxy'] >= liquidity_threshold]
        print(f"   Após critério liquidez: {len(df)} ativos")
        
        # CRITÉRIO 4: Dados de teste suficientes
        df = df[df['test_period_months'] >= 20]  # Pelo menos 20 meses de teste
        print(f"   Após critério período teste: {len(df)} ativos")
        
        # SELEÇÃO FINAL: Top 15 por score composto + diversificação setorial
        # Score = combinação de liquidez + cap market + estabilidade
        df['selection_score'] = (
            0.4 * (df['liquidity_proxy'] / df['liquidity_proxy'].max()) +
            0.3 * (df['market_cap_proxy'] / df['market_cap_proxy'].max()) +
            0.3 * (df['completeness'] / df['completeness'].max())
        )
        
        # Aplicar diversificação setorial
        df_selected = self.aplicar_diversificacao_setorial(df)
        
        print(f"   SELEÇÃO FINAL: {len(df_selected)} ativos")
        print("\n   Top 10 ativos selecionados:")
        for i, row in df_selected.head(10).iterrows():
            print(f"   {i+1:2d}. {row['asset']} - Score: {row['selection_score']:.3f} - Vol: {row['volatility_2014_2017']:.1%}")
        
        return df_selected.to_dict('records')
    
    def aplicar_diversificacao_setorial(self, df):
        """
        Aplica critério de diversificação setorial para evitar concentração
        """
        print("   Aplicando diversificação setorial...")
        
        # Adicionar informação de setor para cada ativo
        df = df.copy()
        df['setor'] = df['asset'].map(self.asset_sector_map)
        
        # Contar ativos por setor
        setores_disponiveis = df['setor'].value_counts()
        print(f"   Setores disponíveis: {len(setores_disponiveis)}")
        
        # Seleção diversificada: máximo 2 ativos por setor
        selected_assets = []
        assets_por_setor = {}
        
        # Ordenar por score para pegar os melhores primeiro
        df_sorted = df.sort_values('selection_score', ascending=False)
        
        for _, row in df_sorted.iterrows():
            asset = row['asset']
            setor = row.get('setor', 'Desconhecido')
            
            # Limitar a 2 ativos por setor
            if assets_por_setor.get(setor, 0) < 2:
                selected_assets.append(row)
                assets_por_setor[setor] = assets_por_setor.get(setor, 0) + 1
                
                # Parar quando atingir 15 ativos
                if len(selected_assets) >= 15:
                    break
        
        # Criar DataFrame final
        df_final = pd.DataFrame(selected_assets)
        
        # Mostrar diversificação alcançada
        setores_selecionados = df_final['setor'].value_counts()
        print(f"   Diversificação setorial alcançada:")
        for setor, count in setores_selecionados.head(10).items():
            print(f"     {setor}: {count} ativo(s)")
        
        return df_final
    
    def processar_selecao_completa(self):
        """
        Executa processo completo de seleção científica
        """
        print("=== PROCESSO DE SELEÇÃO CIENTÍFICA ===")
        
        # 1. Obter lista de ativos
        available_assets = self.obter_lista_ativos_disponiveis()
        
        if len(available_assets) < 10:
            raise ValueError("Poucos ativos disponíveis na base")
        
        # 2. Processar cada ativo
        print("2. Processando dados históricos e calculando métricas...")
        all_metrics = []
        
        for i, asset in enumerate(available_assets):
            if i % 10 == 0:
                print(f"   Processando: {i+1}/{len(available_assets)}")
            
            asset_data = self.extrair_dados_ativo(asset)
            if asset_data is not None:
                metrics = self.calcular_metricas_selecao(asset_data, asset)
                if metrics is not None:
                    all_metrics.append(metrics)
        
        print(f"   Total de ativos com dados válidos: {len(all_metrics)}")
        
        # 3. Aplicar critérios científicos
        selected_assets = self.aplicar_criterios_cientificos(all_metrics)
        
        # 4. Salvar resultados
        results_dir = "../results"
        os.makedirs(results_dir, exist_ok=True)
        
        # Salvar lista final
        selected_df = pd.DataFrame(selected_assets)
        selected_df.to_csv(os.path.join(results_dir, "01_ativos_selecionados.csv"), index=False)
        
        # Salvar critérios aplicados
        criterios = {
            "data_processamento": datetime.now().isoformat(),
            "criterios_aplicados": [
                "Completude >= 70%",
                "Volatilidade entre P25-1.5*IQR e P75+1.5*IQR", 
                "Liquidez >= percentil 30",
                "Dados teste >= 20 meses",
                "Seleção final por score composto"
            ],
            "total_analisados": len(all_metrics),
            "total_selecionados": len(selected_assets),
            "ativos_finais": [item['asset'] for item in selected_assets]
        }
        
        import json
        with open(os.path.join(results_dir, "01_criterios_selecao.json"), 'w') as f:
            json.dump(criterios, f, indent=2)
        
        print(f"\nOK SELEÇÃO CIENTÍFICA CONCLUÍDA!")
        print(f"OK Arquivo: {results_dir}/01_ativos_selecionados.csv")
        print(f"OK Critérios: {results_dir}/01_criterios_selecao.json")
        
        return selected_assets[:10]  # Retornar top 10

def main():
    """
    Execução principal
    """
    try:
        carregador = CarregadorEconomatica()
        selected_assets = carregador.processar_selecao_completa()
        
        print(f"\nOK RESULTADO FINAL: {len(selected_assets)} ativos selecionados cientificamente")
        for i, asset_data in enumerate(selected_assets, 1):
            print(f"{i:2d}. {asset_data['asset']}")
        
        return selected_assets
        
    except Exception as e:
        print(f"ERRO: {e}")
        return None

if __name__ == "__main__":
    resultado = main()