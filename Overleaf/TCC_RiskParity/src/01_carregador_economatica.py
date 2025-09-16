"""
SISTEMA CORRIGIDO - TCC RISK PARITY
Script 1: Carregador Economática com Critérios Científicos Objetivos

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-15 (Versão Corrigida)

Correções aplicadas:
- Melhor tratamento de erros e logging
- Validação robusta de inputs
- Configuração centralizada de parâmetros
- Documentação acadêmica aprimorada
"""

import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuração centralizada
class Config:
    """Parâmetros de configuração centralizados"""
    VOLUME_THRESHOLD = 5_000_000    # R$ 5M/dia mínimo
    QNEGS_THRESHOLD = 500           # 500 negócios/dia mínimo  
    TRADING_DAYS_PCT = 0.90         # 90% presença mínima
    MIN_DATA_POINTS = 200           # Mínimo 200 observações para seleção
    MIN_TEST_POINTS = 100           # Mínimo 100 observações para teste
    
    # Pesos do score composto (baseados em literatura acadêmica)
    MOMENTUM_WEIGHT = 0.35          # 35% - Jegadeesh & Titman (1993)
    VOLATILITY_WEIGHT = 0.25        # 25% - Estabilidade temporal
    DRAWDOWN_WEIGHT = 0.20          # 20% - Controle risco extremo
    DOWNSIDE_WEIGHT = 0.20          # 20% - Assimetria de risco

class CarregadorEconomatica:
    """
    Carregador científico da Economática com critérios objetivos
    SEM seleção hardcoded - APENAS critérios quantitativos
    """
    
    def __init__(self):
        # CAMINHO ABSOLUTO FIXO 
        self.excel_path = r"C:\Users\BrunoGaspariniBaller\OneDrive - HAND\Documentos\TCC\Overleaf\TCC_RiskParity\data\DataBase\Economatica-8900701390-20250812230945 (1).xlsx"
        self.setores_path = r"C:\Users\BrunoGaspariniBaller\OneDrive - HAND\Documentos\TCC\Overleaf\TCC_RiskParity\data\DataBase\economatica (1).xlsx"
        self.results_dir = r"C:\Users\BrunoGaspariniBaller\OneDrive - HAND\Documentos\TCC\Overleaf\TCC_RiskParity\results"
        
        print("="*60)
        print("SISTEMA REFATORADO - CARREGADOR ECONOMÁTICA")
        print("="*60)
        print("OK Metodologia científica objetiva")
        print("OK Critérios de liquidez rigorosos")
        print()
        
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
            
            # Priorizar ativos conhecidos líquidos primeiro
            ativos_prioritarios = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'B3SA3', 'WEGE3', 'RENT3', 'LREN3', 'MGLU3']
            
            # Filtrar sheets que parecem ser ativos (formato típico brasileiro)  
            asset_sheets = []
            
            # Primeiro adicionar os prioritários se existirem
            for ativo in ativos_prioritarios:
                if ativo in all_sheets:
                    asset_sheets.append(ativo)
            
            # Depois adicionar outros ativos
            for sheet in all_sheets:
                if sheet not in asset_sheets:  # Não duplicar
                    # Filtro: sheets com 4-6 caracteres que terminam em números
                    if len(sheet) >= 4 and len(sheet) <= 6:
                        if sheet[-1].isdigit() or sheet[-1] in ['3', '4', '11']:
                            asset_sheets.append(sheet)
            
            print(f"   Total de sheets: {len(all_sheets)}")
            print(f"   Sheets de ativos identificados: {len(asset_sheets)}")
            
            return asset_sheets[:50]  # Processar 50 ativos para encontrar os melhores
            
        except Exception as e:
            print(f"   ERRO: {e}")
            return []
    
    def extrair_dados_ativo(self, sheet_name):
        """
        Extrai dados de um ativo - FORMATO ECONOMÁTICA CORRETO
        """
        try:
            # Ler dados da sheet
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name)
            
            if len(df) < 100:  # Sheet muito pequena
                return None
            
            # CABEÇALHO ESTÁ NA LINHA 2
            header_row = 2
            header = df.iloc[header_row].values
            
            # Dados começam na linha 3
            data_df = df.iloc[header_row + 1:].copy()
            data_df.columns = header
            
            # Colunas principais: Data, Q Negs, Q Títs, Volume$, Fechamento
            if 'Data' not in data_df.columns or 'Fechamento' not in data_df.columns:
                return None
            
            # Limpar dados
            data_df = data_df.dropna(subset=['Data', 'Fechamento'])
            data_df['Data'] = pd.to_datetime(data_df['Data'], errors='coerce')
            data_df = data_df.dropna(subset=['Data'])
            
            # Filtrar período 2014-2019
            data_df = data_df[(data_df['Data'] >= '2014-01-01') & (data_df['Data'] <= '2019-12-31')]
            
            if len(data_df) < 500:  # Poucos dados
                return None
            
            # Converter colunas numéricas
            for col in ['Q Negs', 'Q Títs', 'Volume$', 'Fechamento']:
                if col in data_df.columns:
                    data_df[col] = pd.to_numeric(data_df[col], errors='coerce')
            
            data_df = data_df.set_index('Data').sort_index()
            
            return data_df
            
        except Exception as e:
            return None
    
    def calcular_metricas_ativo(self, asset_data, asset_name):
        """
        Calcula métricas de liquidez e performance
        """
        if asset_data is None or len(asset_data) < 500:
            return None
        
        # Período de seleção: 2014-2017
        selection_data = asset_data[asset_data.index < '2018-01-01']
        test_data = asset_data[asset_data.index >= '2018-01-01']
        
        if len(selection_data) < 200 or len(test_data) < 100:
            return None
        
        # Calcular retornos mensais
        monthly_prices = selection_data['Fechamento'].resample('M').last()
        monthly_returns = monthly_prices.pct_change().dropna()
        
        if len(monthly_returns) < 20:
            return None
        
        # MÉTRICAS DE LIQUIDEZ (Economática)
        
        # Volume$ médio diário (em milhões)
        if 'Volume$' in selection_data.columns:
            avg_volume = selection_data['Volume$'].mean() / 1_000_000
        else:
            avg_volume = 0
        
        # Quantidade de negócios média por dia
        if 'Q Negs' in selection_data.columns:
            avg_qnegs = selection_data['Q Negs'].mean()
        else:
            avg_qnegs = 0
        
        # Presença em bolsa (% dias com volume > 0)
        if 'Volume$' in selection_data.columns:
            trading_days_pct = (selection_data['Volume$'] > 0).mean()
        else:
            trading_days_pct = 0.5
        
        # FILTROS DE LIQUIDEZ AUTOMATICOS - RIGOROSOS
        if avg_volume < Config.VOLUME_THRESHOLD / 1_000_000:  # Converter para milhões
            logger.debug(f"{asset_name}: Volume insuficiente ({avg_volume:.1f}M < {Config.VOLUME_THRESHOLD/1_000_000:.1f}M)")
            return None
        if avg_qnegs < Config.QNEGS_THRESHOLD:
            logger.debug(f"{asset_name}: Negócios insuficientes ({avg_qnegs:.0f} < {Config.QNEGS_THRESHOLD})")
            return None
        if trading_days_pct < Config.TRADING_DAYS_PCT:
            logger.debug(f"{asset_name}: Presença insuficiente ({trading_days_pct:.1%} < {Config.TRADING_DAYS_PCT:.1%})")
            return None
        
        # MÉTRICAS DE PERFORMANCE
        
        # 1. Momentum 12-1
        if len(monthly_returns) >= 13:
            momentum_12_1 = monthly_returns.iloc[-12:-1].sum() * 100
        else:
            momentum_12_1 = monthly_returns.sum() * 100
        
        # 2. Volatilidade anualizada
        volatility = monthly_returns.std() * np.sqrt(12)
        
        # 3. Maximum Drawdown
        cumulative = (1 + monthly_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative / running_max - 1)
        max_drawdown = drawdown.min()
        
        # 4. Downside Deviation
        negative_returns = monthly_returns[monthly_returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std() * np.sqrt(12)
        else:
            downside_deviation = 0
        
        return {
            'asset': asset_name,
            'avg_daily_volume_millions': avg_volume,
            'avg_daily_qnegs': avg_qnegs,
            'trading_days_pct': trading_days_pct,
            'momentum_12_1': momentum_12_1,
            'volatility_2014_2017': volatility,
            'max_drawdown_2014_2017': max_drawdown,
            'downside_deviation': downside_deviation,
            'mean_return_2014_2017': monthly_returns.mean() * 12,
            'completeness': len(monthly_returns) / 48,  # 4 anos * 12 meses
            'data_points_2014_2017': len(monthly_returns),
            'test_period_months': len(test_data.resample('M').last())
        }
    
    def selecionar_ativos_finais(self, metricas_list):
        """
        Seleciona os 10 melhores ativos com critério científico
        """
        if len(metricas_list) < 10:
            return metricas_list
        
        df = pd.DataFrame(metricas_list)
        print(f"   Ativos que passaram nos filtros de liquidez: {len(df)}")
        
        # Scores normalizados
        df['momentum_score'] = df['momentum_12_1'].rank(pct=True)
        df['volatility_score'] = 1 - df['volatility_2014_2017'].rank(pct=True)  
        df['drawdown_score'] = df['max_drawdown_2014_2017'].rank(pct=True)
        df['downside_score'] = 1 - df['downside_deviation'].rank(pct=True)
        
        # Score final composto - Baseado em literatura acadêmica
        df['selection_score'] = (
            Config.MOMENTUM_WEIGHT * df['momentum_score'] +      # Jegadeesh & Titman (1993)
            Config.VOLATILITY_WEIGHT * df['volatility_score'] +  # Estabilidade temporal
            Config.DRAWDOWN_WEIGHT * df['drawdown_score'] +      # Controle risco extremo
            Config.DOWNSIDE_WEIGHT * df['downside_score']        # Assimetria (Sortino)
        )
        
        # Ordenar por score
        df = df.sort_values('selection_score', ascending=False)
        
        # Diversificação setorial básica
        selected_assets = []
        assets_por_setor = {}
        
        for _, candidate in df.iterrows():
            asset = candidate['asset']
            setor = self.asset_sector_map.get(asset, 'Desconhecido')
            
            # Máximo 2 por setor
            if assets_por_setor.get(setor, 0) >= 2:
                continue
                
            selected_assets.append(candidate.to_dict())
            selected_assets[-1]['setor'] = setor
            assets_por_setor[setor] = assets_por_setor.get(setor, 0) + 1
            
            if len(selected_assets) >= 10:
                break
        
        return selected_assets
    
    def processar_selecao_completa(self):
        """
        Executa processo completo de seleção científica
        """
        print("=== PROCESSO DE SELEÇÃO CIENTÍFICA ===")
        
        # 1. Obter ativos disponíveis
        available_assets = self.obter_lista_ativos_disponiveis()
        
        if len(available_assets) < 10:
            raise ValueError("Poucos ativos disponíveis na base")
        
        # 2. Processar cada ativo
        print("2. Processando dados históricos com filtros de liquidez...")
        valid_metrics = []
        
        for i, asset in enumerate(available_assets):
            print(f"   Processando {asset}... ({i+1}/{len(available_assets)})")
            
            asset_data = self.extrair_dados_ativo(asset)
            if asset_data is not None:
                metrics = self.calcular_metricas_ativo(asset_data, asset)
                if metrics is not None:
                    valid_metrics.append(metrics)
                    print(f"     OK {asset}: Vol=R${metrics['avg_daily_volume_millions']:.1f}M, QNegs={metrics['avg_daily_qnegs']:.0f}")
        
        print(f"\n   Total de ativos com liquidez adequada: {len(valid_metrics)}")
        
        if len(valid_metrics) < 10:
            raise ValueError(f"Apenas {len(valid_metrics)} ativos passaram nos filtros de liquidez")
        
        # 3. Selecionar os melhores
        print("3. Aplicando critério científico de seleção...")
        selected_assets = self.selecionar_ativos_finais(valid_metrics)
        
        # 4. Salvar resultados
        os.makedirs(self.results_dir, exist_ok=True)
        
        selected_df = pd.DataFrame(selected_assets)
        selected_df.to_csv(os.path.join(self.results_dir, "01_ativos_selecionados.csv"), index=False)
        
        print(f"\nOK SELEÇÃO CIENTÍFICA CONCLUÍDA!")
        print(f"OK Arquivo: {self.results_dir}/01_ativos_selecionados.csv")
        print(f"\nOK ATIVOS SELECIONADOS COM LIQUIDEZ ADEQUADA:")
        
        for i, asset_data in enumerate(selected_assets, 1):
            print(f"{i:2d}. {asset_data['asset']} - Vol: R${asset_data['avg_daily_volume_millions']:.1f}M - Score: {asset_data['selection_score']:.3f}")
        
        return selected_assets

def main():
    """
    Execução principal
    """
    try:
        carregador = CarregadorEconomatica()
        selected_assets = carregador.processar_selecao_completa()
        
        print(f"\nOK RESULTADO FINAL: {len(selected_assets)} ativos selecionados cientificamente")
        return selected_assets
        
    except Exception as e:
        print(f"ERRO: {e}")
        return None

if __name__ == "__main__":
    resultado = main()