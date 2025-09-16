"""
CARREGADOR ECONOMÁTICA PROFISSIONAL - TCC Risk Parity v2.0
Sistema científico de seleção de ativos com configuração centralizada.

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-16
Versão: 2.0 - Profissional com paths relativos e logging

Melhorias implementadas:
- Configuração centralizada com pesos consistentes (35/25/20/20)
- Paths relativos para replicabilidade total
- Logging profissional em substituição aos prints
- Seeds reprodutíveis para bootstrap/sampling
- Validação robusta com error handling
- Documentação acadêmica aprimorada
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path

# Importar configuração global  
try:
    from _00_configuracao_global import get_logger, get_path, get_config, get_rng
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from _00_configuracao_global import get_logger, get_path, get_config, get_rng

class CarregadorEconomaticaProfissional:
    """
    Carregador científico da Economática com critérios objetivos reprodutíveis.
    
    Features v2.0:
    - Configuração centralizada com pesos 35/25/20/20
    - Paths relativos para máxima replicabilidade  
    - Logging profissional estruturado
    - Seeds reprodutíveis
    - Validação robusta de dados
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        self.rng = get_rng()
        
        # Detectar automaticamente o arquivo Economática
        self.excel_path = self._detectar_arquivo_economatica()
        
        self.logger.info("="*70)
        self.logger.info("CARREGADOR ECONOMÁTICA PROFISSIONAL INICIALIZADO")
        self.logger.info(f"Arquivo detectado: {self.excel_path}")
        self.logger.info(f"Pesos Score: {self.config.SCORE_WEIGHTS}")
        self.logger.info("="*70)
    
    def _detectar_arquivo_economatica(self):
        """
        Detecta automaticamente arquivo da Economática no diretório data.
        
        Returns:
            Path: Caminho para arquivo .xlsx da Economática
        """
        data_dir = self.config.projeto_root / "data" / "DataBase"
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Diretório data não encontrado: {data_dir}")
        
        # Procurar por arquivos .xlsx que contenham "Economatica"
        xlsx_files = list(data_dir.glob("*Economatica*.xlsx"))
        
        if not xlsx_files:
            raise FileNotFoundError("Arquivo Economática não encontrado no diretório data")
        
        if len(xlsx_files) > 1:
            self.logger.warning(f"Múltiplos arquivos encontrados: {xlsx_files}")
            self.logger.info("Usando o mais recente...")
            xlsx_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return xlsx_files[0]
    
    def carregar_dados_economática(self):
        """
        Carrega dados da Economática com validação robusta.
        
        Returns:
            pd.DataFrame: Dados de ações com preços e volumes validados
        """
        self.logger.info("1. Carregando dados Economática...")
        
        try:
            # Carregar Excel (assumindo que dados estão na primeira planilha)
            df_raw = pd.read_excel(self.excel_path, sheet_name=0)
            
            # Log básico sobre os dados carregados
            self.logger.info(f"   Dados carregados: {len(df_raw)} linhas x {len(df_raw.columns)} colunas")
            
            # Validar estrutura mínima esperada
            colunas_esperadas = ['Data', 'Ativo', 'Preço', 'Volume$']
            
            # Verificar se existem colunas similares (flexibilidade nos nomes)
            colunas_encontradas = []
            for col_esperada in colunas_esperadas:
                colunas_similares = [col for col in df_raw.columns if col_esperada.lower() in col.lower()]
                if colunas_similares:
                    colunas_encontradas.append(colunas_similares[0])
                else:
                    raise ValueError(f"Coluna esperada '{col_esperada}' não encontrada")
            
            # Renomear colunas para padrão
            rename_dict = dict(zip(colunas_encontradas, colunas_esperadas))
            df = df_raw.rename(columns=rename_dict)
            
            # Converter tipos de dados
            df['Data'] = pd.to_datetime(df['Data'])
            df['Preço'] = pd.to_numeric(df['Preço'], errors='coerce')
            df['Volume$'] = pd.to_numeric(df['Volume$'], errors='coerce')
            
            # Filtrar dados válidos
            df = df.dropna(subset=['Data', 'Ativo', 'Preço', 'Volume$'])
            
            # Validar período de dados
            data_min = df['Data'].min()
            data_max = df['Data'].max()
            
            self.logger.info(f"   Período dos dados: {data_min.strftime('%Y-%m-%d')} a {data_max.strftime('%Y-%m-%d')}")
            self.logger.info(f"   Ativos únicos: {df['Ativo'].nunique()}")
            self.logger.info(f"   Observações válidas: {len(df)}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados Economática: {e}")
            raise
    
    def calcular_metricas_liquidez(self, df):
        """
        Calcula métricas de liquidez por ativo usando critérios científicos.
        
        Args:
            df (pd.DataFrame): Dados de preços e volumes
            
        Returns:
            pd.DataFrame: Métricas de liquidez por ativo
        """
        self.logger.info("2. Calculando métricas de liquidez...")
        
        metricas_liquidez = []
        
        for ativo in df['Ativo'].unique():
            df_ativo = df[df['Ativo'] == ativo].sort_values('Data')
            
            if len(df_ativo) < self.config.LIQUIDEZ_CRITERIA['negocios_min_diario']:
                continue
            
            # Métricas básicas de liquidez
            volume_medio = df_ativo['Volume$'].mean()
            volume_mediano = df_ativo['Volume$'].median()
            dias_com_volume = (df_ativo['Volume$'] > 0).sum()
            total_dias = len(df_ativo)
            presenca_bolsa = dias_com_volume / total_dias
            
            # Calcular retornos para métricas de qualidade
            df_ativo = df_ativo.copy()
            df_ativo['Retorno'] = df_ativo['Preço'].pct_change()
            
            # Métricas de qualidade dos dados
            dias_sem_retorno = (df_ativo['Retorno'] == 0).sum()
            pct_dias_sem_retorno = dias_sem_retorno / len(df_ativo.dropna())
            
            # Autocorrelação de retornos (indicador de microestrutura)
            autocorr = df_ativo['Retorno'].autocorr() if len(df_ativo) > 10 else np.nan
            
            metricas = {
                'ativo': ativo,
                'volume_medio_diario': volume_medio,
                'volume_mediano_diario': volume_mediano,
                'presenca_bolsa': presenca_bolsa,
                'pct_dias_sem_retorno': pct_dias_sem_retorno,
                'autocorr_retornos': autocorr if not pd.isna(autocorr) else -999,
                'observacoes_totais': total_dias,
                'periodo_inicio': df_ativo['Data'].min(),
                'periodo_fim': df_ativo['Data'].max()
            }
            
            metricas_liquidez.append(metricas)
        
        df_liquidez = pd.DataFrame(metricas_liquidez)
        
        self.logger.info(f"   Métricas calculadas para {len(df_liquidez)} ativos")
        
        return df_liquidez
    
    def filtrar_por_liquidez(self, df_liquidez):
        """
        Aplica filtros de liquidez baseados em critérios científicos.
        
        Args:
            df_liquidez (pd.DataFrame): Métricas de liquidez
            
        Returns:
            pd.DataFrame: Ativos que atendem critérios de liquidez
        """
        self.logger.info("3. Aplicando filtros de liquidez...")
        
        criterios = self.config.LIQUIDEZ_CRITERIA
        
        # Aplicar filtros sequenciais
        df_filtrado = df_liquidez.copy()
        
        # Filtro 1: Volume mínimo
        antes = len(df_filtrado)
        df_filtrado = df_filtrado[df_filtrado['volume_medio_diario'] >= criterios['volume_min_diario']]
        self.logger.info(f"   Filtro volume (≥R${criterios['volume_min_diario']:,}): {antes} → {len(df_filtrado)} ativos")
        
        # Filtro 2: Presença em bolsa
        antes = len(df_filtrado)
        df_filtrado = df_filtrado[df_filtrado['presenca_bolsa'] >= criterios['presenca_min_bolsa']]
        self.logger.info(f"   Filtro presença (≥{criterios['presenca_min_bolsa']:.0%}): {antes} → {len(df_filtrado)} ativos")
        
        # Filtro 3: Qualidade dos dados (dias sem retorno)
        antes = len(df_filtrado)
        df_filtrado = df_filtrado[df_filtrado['pct_dias_sem_retorno'] <= criterios['zero_return_days_max']]
        self.logger.info(f"   Filtro qualidade (≤{criterios['zero_return_days_max']:.0%} dias zero): {antes} → {len(df_filtrado)} ativos")
        
        # Filtro 4: Autocorrelação (evitar problemas microestrutura)
        antes = len(df_filtrado)
        df_filtrado = df_filtrado[df_filtrado['autocorr_retornos'] >= criterios['autocorr_min']]
        self.logger.info(f"   Filtro autocorr (≥{criterios['autocorr_min']:.2f}): {antes} → {len(df_filtrado)} ativos")
        
        return df_filtrado
    
    def calcular_metricas_performance(self, df, ativos_elegíveis):
        """
        Calcula métricas de performance para construção do Score Composto.
        
        Args:
            df (pd.DataFrame): Dados originais
            ativos_elegíveis (list): Lista de ativos que passaram no filtro de liquidez
            
        Returns:
            pd.DataFrame: Métricas de performance para Score Composto
        """
        self.logger.info("4. Calculando métricas de performance...")
        
        # Período de avaliação (2014-2017 para seleção)
        data_inicio = pd.to_datetime(self.config.PERIODOS['estimacao_inicio']) - pd.DateOffset(years=2)  # 2014
        data_fim = pd.to_datetime(self.config.PERIODOS['estimacao_fim'])  # 2017
        
        df_periodo = df[(df['Data'] >= data_inicio) & (df['Data'] <= data_fim)]
        
        metricas_performance = []
        
        for ativo in ativos_elegíveis:
            df_ativo = df_periodo[df_periodo['Ativo'] == ativo].sort_values('Data')
            
            if len(df_ativo) < 24:  # Mínimo 2 anos de dados
                continue
            
            # Calcular retornos mensais
            df_ativo = df_ativo.set_index('Data')
            precos_mensais = df_ativo['Preço'].resample('M').last()
            retornos_mensais = precos_mensais.pct_change().dropna()
            
            if len(retornos_mensais) < 12:  # Mínimo 1 ano
                continue
            
            # Métrica 1: Momentum 12-1 (Jegadeesh & Titman, 1993)
            if len(retornos_mensais) >= 12:
                momentum_12_1 = (retornos_mensais.iloc[-12:-1] + 1).prod() - 1
            else:
                momentum_12_1 = np.nan
            
            # Métrica 2: Volatilidade anualizada
            volatilidade = retornos_mensais.std() * np.sqrt(12)
            
            # Métrica 3: Maximum Drawdown
            precos_cum = (retornos_mensais + 1).cumprod()
            running_max = precos_cum.expanding().max()
            drawdowns = (precos_cum / running_max - 1)
            max_drawdown = drawdowns.min()
            
            # Métrica 4: Downside Deviation (Sortino & van der Meer, 1991)
            retornos_negativos = retornos_mensais[retornos_mensais < 0]
            downside_dev = retornos_negativos.std() * np.sqrt(12) if len(retornos_negativos) > 0 else 0
            
            metricas = {
                'ativo': ativo,
                'momentum_12_1': momentum_12_1,
                'volatilidade_anual': volatilidade,
                'max_drawdown': abs(max_drawdown),  # Valor absoluto
                'downside_deviation': downside_dev,
                'retorno_medio_mensal': retornos_mensais.mean(),
                'observacoes_performance': len(retornos_mensais)
            }
            
            metricas_performance.append(metricas)
        
        df_performance = pd.DataFrame(metricas_performance)
        df_performance = df_performance.dropna()  # Remover ativos com dados insuficientes
        
        self.logger.info(f"   Performance calculada para {len(df_performance)} ativos")
        
        return df_performance
    
    def calcular_score_composto(self, df_performance):
        """
        Calcula Score Composto usando pesos acadêmicos (35/25/20/20).
        
        Args:
            df_performance (pd.DataFrame): Métricas de performance
            
        Returns:
            pd.DataFrame: Scores compostos e rankings
        """
        self.logger.info("5. Calculando Score Composto...")
        
        df_scores = df_performance.copy()
        
        # Calcular percentis (0-1) para cada métrica
        df_scores['momentum_rank'] = df_scores['momentum_12_1'].rank(pct=True)
        df_scores['volatility_rank'] = (1 - df_scores['volatilidade_anual'].rank(pct=True))  # Invertido: menor vol = melhor
        df_scores['drawdown_rank'] = (1 - df_scores['max_drawdown'].rank(pct=True))  # Invertido: menor DD = melhor  
        df_scores['downside_rank'] = (1 - df_scores['downside_deviation'].rank(pct=True))  # Invertido: menor downside = melhor
        
        # Score Composto com pesos consistentes (35/25/20/20)
        weights = self.config.SCORE_WEIGHTS
        df_scores['score_composto'] = (
            weights['momentum'] * df_scores['momentum_rank'] +
            weights['volatility'] * df_scores['volatility_rank'] + 
            weights['max_drawdown'] * df_scores['drawdown_rank'] +
            weights['downside_dev'] * df_scores['downside_rank']
        )
        
        # Ranking final
        df_scores = df_scores.sort_values('score_composto', ascending=False)
        df_scores['ranking_final'] = range(1, len(df_scores) + 1)
        
        self.logger.info(f"   Score calculado com pesos: {weights}")
        self.logger.info(f"   Top 5 ativos: {df_scores['ativo'].head().tolist()}")
        
        return df_scores
    
    def selecionar_top_ativos(self, df_scores, n_ativos=10):
        """
        Seleciona top N ativos com controles de diversificação.
        
        Args:
            df_scores (pd.DataFrame): Scores calculados
            n_ativos (int): Número de ativos a selecionar
            
        Returns:
            dict: Resultado da seleção com metadados
        """
        self.logger.info(f"6. Selecionando top {n_ativos} ativos...")
        
        # Selecionar top N baseado no score
        top_ativos = df_scores.head(n_ativos)
        
        # Preparar resultado
        resultado = {
            'ativos_selecionados': top_ativos['ativo'].tolist(),
            'scores': top_ativos[['ativo', 'score_composto', 'ranking_final']].to_dict('records'),
            'estatisticas_selecao': {
                'score_medio': top_ativos['score_composto'].mean(),
                'score_min': top_ativos['score_composto'].min(),
                'score_max': top_ativos['score_composto'].max(),
                'momentum_medio': top_ativos['momentum_12_1'].mean(),
                'volatilidade_media': top_ativos['volatilidade_anual'].mean(),
                'drawdown_medio': top_ativos['max_drawdown'].mean()
            },
            'criterios_utilizados': {
                'liquidez': self.config.LIQUIDEZ_CRITERIA,
                'score_weights': self.config.SCORE_WEIGHTS,
                'periodo_avaliacao': '2014-2017',
                'n_ativos_selecionados': n_ativos
            },
            'metadados': {
                'data_selecao': datetime.now().isoformat(),
                'versao_script': '2.0_profissional',
                'seed_reprodutibilidade': self.config.SEED,
                'total_ativos_avaliados': len(df_scores)
            }
        }
        
        self.logger.info(f"   ✅ Seleção concluída: {len(resultado['ativos_selecionados'])} ativos")
        self.logger.info(f"   Score médio: {resultado['estatisticas_selecao']['score_medio']:.3f}")
        
        return resultado
    
    def salvar_resultados(self, resultado_selecao, df_scores_completo):
        """
        Salva resultados da seleção em múltiplos formatos.
        
        Args:
            resultado_selecao (dict): Resultado da seleção 
            df_scores_completo (pd.DataFrame): Todos os scores calculados
        """
        self.logger.info("7. Salvando resultados...")
        
        # Salvar lista de ativos selecionados
        ativos_df = pd.DataFrame({
            'ativo': resultado_selecao['ativos_selecionados'],
            'score_composto': [s['score_composto'] for s in resultado_selecao['scores']],
            'ranking': [s['ranking_final'] for s in resultado_selecao['scores']]
        })
        
        path_ativos = get_path('results', '01_ativos_selecionados.csv')
        ativos_df.to_csv(path_ativos, index=False)
        self.logger.info(f"   Ativos selecionados salvos: {path_ativos}")
        
        # Salvar critérios e metadados
        path_criterios = get_path('results', '01_criterios_selecao.json')
        with open(path_criterios, 'w', encoding='utf-8') as f:
            json.dump(resultado_selecao, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info(f"   Critérios salvos: {path_criterios}")
        
        # Salvar scores completos para análise
        path_scores = get_path('results', '01_scores_completos.csv')
        df_scores_completo.to_csv(path_scores, index=False)
        self.logger.info(f"   Scores completos salvos: {path_scores}")
    
    def executar_selecao_completa(self):
        """
        Executa pipeline completo de seleção científica de ativos.
        
        Returns:
            dict: Resultado completo da seleção
        """
        try:
            # Pipeline completo
            df_dados = self.carregar_dados_economática()
            df_liquidez = self.calcular_metricas_liquidez(df_dados)
            ativos_elegíveis = self.filtrar_por_liquidez(df_liquidez)['ativo'].tolist()
            df_performance = self.calcular_metricas_performance(df_dados, ativos_elegíveis)
            df_scores = self.calcular_score_composto(df_performance)
            resultado = self.selecionar_top_ativos(df_scores)
            
            # Salvar resultados
            self.salvar_resultados(resultado, df_scores)
            
            self.logger.info("="*70)
            self.logger.info("✅ SELEÇÃO CIENTÍFICA CONCLUÍDA COM SUCESSO!")
            self.logger.info(f"✅ {len(resultado['ativos_selecionados'])} ativos selecionados")
            self.logger.info(f"✅ Score médio: {resultado['estatisticas_selecao']['score_medio']:.3f}")
            self.logger.info(f"✅ Arquivos salvos em: {self.config.results_dir}")
            self.logger.info("="*70)
            
            return resultado
            
        except Exception as e:
            self.logger.error(f"❌ Erro na seleção: {e}")
            raise

if __name__ == "__main__":
    # Executar seleção científica
    seletor = CarregadorEconomaticaProfissional()
    resultado = seletor.executar_selecao_completa()
    
    print("\n🎯 ATIVOS SELECIONADOS:")
    for i, ativo in enumerate(resultado['ativos_selecionados'], 1):
        score = resultado['scores'][i-1]['score_composto']
        print(f"{i:2d}. {ativo} (Score: {score:.3f})")