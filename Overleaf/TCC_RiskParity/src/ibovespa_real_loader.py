"""
Carregador de dados reais do Ibovespa da B3
Processa os arquivos CSV com dados diários históricos do índice
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class IbovespaRealLoader:
    """
    Carrega e processa dados reais do Ibovespa dos arquivos da B3
    """
    
    def __init__(self, data_path="../data/DataBase/"):
        self.data_path = Path(data_path)
        
    def load_ibovespa_data(self, start_date='2018-01-01', end_date='2019-12-31'):
        """
        Carrega dados reais do Ibovespa para o período especificado
        
        Returns:
            pd.Series: Série temporal com retornos mensais do Ibovespa
        """
        print("Carregando dados reais do Ibovespa da B3...")
        
        # Carregar dados de 2018 e 2019
        ibov_2018 = self._load_year_data(2018)
        ibov_2019 = self._load_year_data(2019)
        
        # Combinar os dados
        all_data = pd.concat([ibov_2018, ibov_2019]).sort_index()
        
        if all_data.empty:
            print("ERRO: Nenhum dado foi processado dos arquivos")
            return None
        
        # Filtrar pelo período solicitado - só se tivermos dados
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if len(all_data) > 0 and hasattr(all_data.index, 'date'):
            filtered_data = all_data[(all_data.index >= start) & (all_data.index <= end)]
        else:
            print("AVISO: Usando todos os dados disponiveis (filtragem de data falhou)")
            filtered_data = all_data
        
        if filtered_data.empty:
            print("ERRO: Nenhum dado encontrado para o periodo especificado")
            return None
            
        # Converter para retornos mensais
        monthly_returns = self._convert_to_monthly_returns(filtered_data)
        
        # Adicionar metadata
        monthly_returns.name = 'IBOV'
        monthly_returns.benchmark_type = 'Ibovespa (B3 Oficial)'
        monthly_returns.data_source = 'B3 - Dados Históricos Oficiais'
        
        print(f"OK: Ibovespa carregado: {len(monthly_returns)} observacoes mensais")
        print(f"   Periodo: {monthly_returns.index[0].date()} a {monthly_returns.index[-1].date()}")
        
        return monthly_returns
    
    def _load_year_data(self, year):
        """
        Carrega dados de um ano específico
        """
        file_mapping = {
            2018: "Evolucao_Diaria (1).csv",
            2019: "Evolucao_Diaria.csv"
        }
        
        filename = file_mapping.get(year)
        if not filename:
            raise ValueError(f"Dados não disponíveis para o ano {year}")
            
        filepath = self.data_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        # Ler arquivo CSV - skip header, pois vem mesclado
        df = pd.read_csv(filepath, sep=';', encoding='utf-8', skiprows=1)
        
        # Processar os dados
        daily_data = self._parse_csv_data(df, year)
        
        return daily_data
    
    def _parse_csv_data(self, df, year):
        """
        Converte os dados do CSV em formato de série temporal
        """
        # Remover linhas de estatísticas (LOWEST, HIGHEST)
        data_df = df[~df['Day'].isin(['LOWEST', 'HIGHEST'])].copy()
        data_df = data_df.dropna(subset=['Day'])
        
        # Converter Day para numeric
        data_df['Day'] = pd.to_numeric(data_df['Day'], errors='coerce')
        data_df = data_df.dropna(subset=['Day'])
        
        # Meses em ordem
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        daily_values = []
        
        for month_idx, month in enumerate(months):
            if month not in data_df.columns:
                continue
                
            month_data = data_df[['Day', month]].copy()
            month_data = month_data.dropna(subset=[month])
            
            for _, row in month_data.iterrows():
                try:
                    # Converter valor do formato brasileiro: 87,887.27 -> 87887.27
                    value_str = str(row[month])
                    # Remover vírgulas (separadores de milhares) e manter apenas o último ponto
                    if ',' in value_str and '.' in value_str:
                        # Formato: 87,887.27 -> 87887.27
                        value_str = value_str.replace(',', '')
                    elif ',' in value_str and '.' not in value_str:
                        # Formato: 87,27 -> 87.27
                        value_str = value_str.replace(',', '.')
                    
                    value = float(value_str)
                    
                    # Criar data
                    day = int(row['Day'])
                    date = pd.Timestamp(year=year, month=month_idx+1, day=day)
                    
                    daily_values.append({'date': date, 'value': value})
                    
                except (ValueError, TypeError):
                    continue
        
        # Converter para DataFrame e Series
        if not daily_values:
            return pd.Series(dtype=float)
            
        values_df = pd.DataFrame(daily_values)
        values_df = values_df.sort_values('date')
        
        # Criar série temporal
        series = pd.Series(values_df['value'].values, index=values_df['date'])
        series = series.sort_index()
        
        return series
    
    def _convert_to_monthly_returns(self, daily_data):
        """
        Converte dados diários para retornos mensais
        """
        if daily_data.empty:
            return pd.Series(dtype=float)
        
        # Usar último valor de cada mês
        monthly_prices = daily_data.groupby(daily_data.index.to_period('M')).last()
        
        # Converter período de volta para timestamp (último dia do mês) com mesmo formato dos ativos
        monthly_prices.index = monthly_prices.index.to_timestamp('M')
        # Normalizar timestamp para coincidir com os dados dos ativos (último nanosegundo do mês)
        monthly_prices.index = monthly_prices.index.normalize() + pd.Timedelta(days=1, nanoseconds=-1)
        
        # Calcular retornos mensais
        monthly_returns = monthly_prices.pct_change().dropna()
        
        # CORREÇÃO: Adicionar retorno real para janeiro 2018 para alinhar com dados dos ativos
        if len(monthly_prices) >= 2:
            # Verificar se janeiro 2018 existe nos preços mensais
            jan_2018_exists = any(ts.year == 2018 and ts.month == 1 for ts in monthly_prices.index)
            
            if jan_2018_exists:
                # Valor histórico real do Ibovespa em 29/12/2017: 76.402 pontos
                ibov_dec_2017 = 76402.0
                jan_2018_price = monthly_prices.iloc[0]
                jan_2018_return = (jan_2018_price - ibov_dec_2017) / ibov_dec_2017
                jan_2018_timestamp = pd.Timestamp('2018-01-31 23:59:59.999999999')
                jan_return = pd.Series([jan_2018_return], index=[jan_2018_timestamp], name=monthly_returns.name)
                monthly_returns = pd.concat([jan_return, monthly_returns]).sort_index()
                print(f"OK: Incluido retorno real de janeiro 2018: {jan_2018_return:.4f}")
        
        return monthly_returns
    
    def validate_data_quality(self, ibov_returns):
        """
        Valida a qualidade dos dados carregados
        """
        if ibov_returns is None or ibov_returns.empty:
            return False
            
        print("\n=== VALIDAÇÃO DOS DADOS DO IBOVESPA ===")
        print(f"Observações: {len(ibov_returns)}")
        print(f"Período: {ibov_returns.index[0].date()} a {ibov_returns.index[-1].date()}")
        print(f"Valores nulos: {ibov_returns.isnull().sum()}")
        print(f"Retorno médio mensal: {ibov_returns.mean():.4f} ({ibov_returns.mean()*12:.2%} aa)")
        print(f"Volatilidade mensal: {ibov_returns.std():.4f} ({ibov_returns.std()*np.sqrt(12):.2%} aa)")
        print(f"Min/Max: {ibov_returns.min():.4f} / {ibov_returns.max():.4f}")
        
        # Verificar outliers extremos
        outliers = np.abs(ibov_returns) > 0.5  # Mais de 50% em um mês
        if outliers.any():
            print(f"AVISO: Outliers extremos detectados: {outliers.sum()}")
            print(ibov_returns[outliers])
        else:
            print("OK: Nenhum outlier extremo detectado")
            
        return True

def main():
    """
    Teste do carregador de dados do Ibovespa
    """
    print("=== TESTE DO CARREGADOR IBOVESPA REAL ===")
    
    # Criar loader
    loader = IbovespaRealLoader()
    
    # Carregar dados
    ibov_returns = loader.load_ibovespa_data('2018-01-01', '2019-12-31')
    
    if ibov_returns is not None:
        # Validar dados
        loader.validate_data_quality(ibov_returns)
        
        # Salvar para uso posterior
        output_path = "../results/ibovespa_real_returns.csv"
        ibov_returns.to_csv(output_path)
        print(f"\nOK: Dados salvos em: {output_path}")
        
        return ibov_returns
    else:
        print("ERRO: Falha ao carregar dados do Ibovespa")
        return None

if __name__ == "__main__":
    ibov_data = main()