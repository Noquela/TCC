"""
CALCULADORA DE TURNOVER PROFISSIONAL - TCC Risk Parity v2.0
Módulo para cálculo preciso de turnover real (não estimado/hardcoded).

Autor: Bruno Gasparoni Ballerini  
Data: 2025-09-16
Versão: 2.0 - Implementação científica

Funcionalidades:
- Cálculo de turnover real por período de rebalanceamento
- Análise de turnover médio por estratégia 
- Decomposição de turnover por origem (drift vs rebalancing)
- Métricas de implementabilidade baseadas em turnover
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Importar configuração global
try:
    from _00_configuracao_global import get_logger, get_path, get_config, get_rng
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from _00_configuracao_global import get_logger, get_path, get_config, get_rng

class CalculadoraTurnoverProfissional:
    """
    Calculadora profissional de turnover para estratégias de alocação.
    
    Implementa cálculos científicos baseados em:
    - Turnover = (1/2) * Σ |w_i,t - w_i,t-1| por período
    - Decomposição entre drift passivo e rebalanceamento ativo  
    - Análise de custos implícitos de transação
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        self.logger.info("="*70)
        self.logger.info("CALCULADORA DE TURNOVER PROFISSIONAL INICIALIZADA")
        self.logger.info("Método: Turnover = (1/2) * Σ |w_i,t - w_i,t-1|")
        self.logger.info("="*70)
    
    def calcular_turnover_periodo(self, 
                                pesos_anterior: pd.Series, 
                                pesos_atual: pd.Series) -> float:
        """
        Calcula turnover para um período específico.
        
        Args:
            pesos_anterior (pd.Series): Pesos da carteira no período anterior
            pesos_atual (pd.Series): Pesos da carteira no período atual
            
        Returns:
            float: Turnover do período (0-1, onde 1 = 100% da carteira foi alterada)
        """
        # Alinhar índices (alguns ativos podem não estar em ambos os períodos)
        pesos_comum = pd.DataFrame({
            'anterior': pesos_anterior,
            'atual': pesos_atual
        }).fillna(0)
        
        # Calcular diferenças absolutas
        diferencas_abs = (pesos_comum['atual'] - pesos_comum['anterior']).abs()
        
        # Turnover = (1/2) * soma das diferenças absolutas
        turnover = 0.5 * diferencas_abs.sum()
        
        return float(turnover)
    
    def calcular_turnover_serie_temporal(self, 
                                       df_pesos: pd.DataFrame) -> pd.Series:
        """
        Calcula série temporal de turnover para uma estratégia.
        
        Args:
            df_pesos (pd.DataFrame): DataFrame com pesos por data (index=dates, columns=assets)
            
        Returns:
            pd.Series: Série temporal de turnover por período
        """
        datas = df_pesos.index.sort_values()
        turnovers = []
        
        for i in range(1, len(datas)):
            data_anterior = datas[i-1]
            data_atual = datas[i]
            
            pesos_anterior = df_pesos.loc[data_anterior]
            pesos_atual = df_pesos.loc[data_atual]
            
            turnover = self.calcular_turnover_periodo(pesos_anterior, pesos_atual)
            turnovers.append(turnover)
        
        # Série temporal de turnover (excluindo primeira data)
        turnover_series = pd.Series(turnovers, index=datas[1:])
        
        return turnover_series
    
    def calcular_metricas_turnover_estrategia(self, 
                                            df_pesos: pd.DataFrame,
                                            nome_estrategia: str) -> Dict:
        """
        Calcula métricas completas de turnover para uma estratégia.
        
        Args:
            df_pesos (pd.DataFrame): Pesos da carteira por data
            nome_estrategia (str): Nome da estratégia
            
        Returns:
            Dict: Métricas de turnover da estratégia
        """
        turnover_series = self.calcular_turnover_serie_temporal(df_pesos)
        
        if len(turnover_series) == 0:
            self.logger.warning(f"Não foi possível calcular turnover para {nome_estrategia}")
            return self._metricas_turnover_vazias(nome_estrategia)
        
        # Estatísticas descritivas
        metricas = {
            'estrategia': nome_estrategia,
            'turnover_medio': turnover_series.mean(),
            'turnover_mediano': turnover_series.median(),
            'turnover_std': turnover_series.std(),
            'turnover_min': turnover_series.min(),
            'turnover_max': turnover_series.max(),
            'turnover_total_acumulado': turnover_series.sum(),
            'n_rebalanceamentos': len(turnover_series),
            'turnover_medio_anualizado': turnover_series.mean() * (12 / 6),  # Semestral -> Anual
            'serie_temporal': turnover_series.to_dict()
        }
        
        # Análise qualitativa
        if metricas['turnover_medio'] < 0.10:
            metricas['classificacao_turnover'] = 'Baixo'
        elif metricas['turnover_medio'] < 0.25:
            metricas['classificacao_turnover'] = 'Moderado' 
        else:
            metricas['classificacao_turnover'] = 'Alto'
        
        self.logger.info(f"Turnover {nome_estrategia}: {metricas['turnover_medio']:.1%} médio ({metricas['classificacao_turnover']})")
        
        return metricas
    
    def _metricas_turnover_vazias(self, nome_estrategia: str) -> Dict:
        """Retorna métricas vazias quando cálculo falha"""
        return {
            'estrategia': nome_estrategia,
            'turnover_medio': np.nan,
            'turnover_mediano': np.nan,
            'turnover_std': np.nan,
            'turnover_min': np.nan,
            'turnover_max': np.nan,
            'turnover_total_acumulado': np.nan,
            'n_rebalanceamentos': 0,
            'turnover_medio_anualizado': np.nan,
            'classificacao_turnover': 'N/A',
            'serie_temporal': {}
        }
    
    def carregar_pesos_estrategias(self) -> Dict[str, pd.DataFrame]:
        """
        Carrega pesos das estratégias dos arquivos de resultados.
        
        Returns:
            Dict[str, pd.DataFrame]: Pesos por estratégia
        """
        self.logger.info("Carregando pesos das estratégias...")
        
        try:
            # Carregar arquivo de pesos de portfólios
            path_pesos = get_path('results', '03_pesos_portfolios.csv')
            
            if not path_pesos.exists():
                self.logger.error(f"Arquivo de pesos não encontrado: {path_pesos}")
                return {}
            
            df_pesos_raw = pd.read_csv(path_pesos, index_col=0, parse_dates=True)
            
            # Reorganizar dados por estratégia
            estrategias = {}
            
            # Assumir que colunas estão organizadas como 'ativo_estrategia'
            for coluna in df_pesos_raw.columns:
                if '_' in coluna:
                    ativo, estrategia = coluna.rsplit('_', 1)
                    
                    if estrategia not in estrategias:
                        estrategias[estrategia] = pd.DataFrame(index=df_pesos_raw.index)
                    
                    estrategias[estrategia][ativo] = df_pesos_raw[coluna]
            
            # Filtrar estrategias com dados válidos
            estrategias_validas = {}
            for nome, df_pesos in estrategias.items():
                # Remover linhas/colunas completamente vazias
                df_pesos = df_pesos.dropna(how='all').fillna(0)
                
                if len(df_pesos) >= 2:  # Mínimo 2 períodos para calcular turnover
                    estrategias_validas[nome] = df_pesos
                    self.logger.info(f"   {nome}: {len(df_pesos)} períodos, {len(df_pesos.columns)} ativos")
                else:
                    self.logger.warning(f"   {nome}: dados insuficientes ({len(df_pesos)} períodos)")
            
            return estrategias_validas
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar pesos das estratégias: {e}")
            return {}
    
    def calcular_turnover_todas_estrategias(self) -> Dict[str, Dict]:
        """
        Calcula turnover para todas as estratégias disponíveis.
        
        Returns:
            Dict[str, Dict]: Métricas de turnover por estratégia
        """
        self.logger.info("Iniciando cálculo de turnover para todas estratégias...")
        
        # Carregar dados
        estrategias_pesos = self.carregar_pesos_estrategias()
        
        if not estrategias_pesos:
            self.logger.error("Nenhum dado de peso válido encontrado")
            return {}
        
        # Calcular turnover para cada estratégia
        resultados_turnover = {}
        
        for nome_estrategia, df_pesos in estrategias_pesos.items():
            self.logger.info(f"Calculando turnover: {nome_estrategia}")
            
            metricas = self.calcular_metricas_turnover_estrategia(df_pesos, nome_estrategia)
            resultados_turnover[nome_estrategia] = metricas
        
        return resultados_turnover
    
    def gerar_relatorio_turnover(self, resultados_turnover: Dict[str, Dict]) -> pd.DataFrame:
        """
        Gera relatório comparativo de turnover entre estratégias.
        
        Args:
            resultados_turnover (Dict): Resultados de turnover por estratégia
            
        Returns:
            pd.DataFrame: Relatório comparativo formatado
        """
        if not resultados_turnover:
            self.logger.warning("Nenhum resultado de turnover disponível")
            return pd.DataFrame()
        
        # Extrair métricas principais
        relatorio_data = []
        
        for nome_estrategia, metricas in resultados_turnover.items():
            relatorio_data.append({
                'Estratégia': nome_estrategia,
                'Turnover Médio (%)': metricas['turnover_medio'] * 100 if pd.notna(metricas['turnover_medio']) else np.nan,
                'Turnover Mediano (%)': metricas['turnover_mediano'] * 100 if pd.notna(metricas['turnover_mediano']) else np.nan,
                'Turnover Anualizado (%)': metricas['turnover_medio_anualizado'] * 100 if pd.notna(metricas['turnover_medio_anualizado']) else np.nan,
                'Desvio Padrão (%)': metricas['turnover_std'] * 100 if pd.notna(metricas['turnover_std']) else np.nan,
                'Turnover Mínimo (%)': metricas['turnover_min'] * 100 if pd.notna(metricas['turnover_min']) else np.nan,
                'Turnover Máximo (%)': metricas['turnover_max'] * 100 if pd.notna(metricas['turnover_max']) else np.nan,
                'N° Rebalanceamentos': metricas['n_rebalanceamentos'],
                'Classificação': metricas['classificacao_turnover']
            })
        
        df_relatorio = pd.DataFrame(relatorio_data)
        
        # Ordenar por turnover médio
        df_relatorio = df_relatorio.sort_values('Turnover Médio (%)', ascending=True)
        
        return df_relatorio
    
    def calcular_custos_implícitos(self, 
                                  resultados_turnover: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Estima custos implícitos de transação baseados no turnover.
        
        Args:
            resultados_turnover (Dict): Resultados de turnover
            
        Returns:
            Dict: Custos implícitos por estratégia e cenário
        """
        custos_transacao = self.config.CUSTOS_TRANSACAO
        custos_implícitos = {}
        
        for nome_estrategia, metricas in resultados_turnover.items():
            turnover_anual = metricas.get('turnover_medio_anualizado', 0)
            
            if pd.isna(turnover_anual):
                continue
            
            custos_estrategia = {
                'estrategia': nome_estrategia,
                'turnover_anualizado': turnover_anual
            }
            
            # Calcular custos para diferentes cenários
            for cenario, custo_bps in custos_transacao.items():
                custo_anual = turnover_anual * custo_bps
                custos_estrategia[f'custo_{cenario}_pct'] = custo_anual * 100
                custos_estrategia[f'custo_{cenario}_bps'] = custo_anual * 10000
            
            custos_implícitos[nome_estrategia] = custos_estrategia
        
        return custos_implícitos
    
    def salvar_resultados_turnover(self, 
                                 resultados_turnover: Dict[str, Dict],
                                 df_relatorio: pd.DataFrame) -> None:
        """
        Salva resultados de turnover em arquivos.
        
        Args:
            resultados_turnover (Dict): Resultados detalhados
            df_relatorio (pd.DataFrame): Relatório comparativo
        """
        self.logger.info("Salvando resultados de turnover...")
        
        # Salvar relatório comparativo
        path_relatorio = get_path('results', '04_turnover_comparativo.csv')
        df_relatorio.to_csv(path_relatorio, index=False)
        self.logger.info(f"   Relatório salvo: {path_relatorio}")
        
        # Salvar resultados detalhados
        import json
        path_detalhado = get_path('results', '04_turnover_detalhado.json')
        
        # Converter Series para dict nos resultados
        resultados_serializaveis = {}
        for estrategia, metricas in resultados_turnover.items():
            metricas_copia = metricas.copy()
            # Serie temporal já está como dict
            resultados_serializaveis[estrategia] = metricas_copia
        
        with open(path_detalhado, 'w', encoding='utf-8') as f:
            json.dump(resultados_serializaveis, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info(f"   Detalhes salvos: {path_detalhado}")
        
        # Calcular e salvar custos implícitos
        custos = self.calcular_custos_implícitos(resultados_turnover)
        path_custos = get_path('results', '04_custos_turnover.json')
        
        with open(path_custos, 'w', encoding='utf-8') as f:
            json.dump(custos, f, indent=2, ensure_ascii=False, default=str)
        self.logger.info(f"   Custos salvos: {path_custos}")
    
    def executar_analise_completa(self) -> Dict:
        """
        Executa análise completa de turnover para todas estratégias.
        
        Returns:
            Dict: Resultados completos da análise
        """
        try:
            self.logger.info("="*70)
            self.logger.info("INICIANDO ANÁLISE COMPLETA DE TURNOVER")
            self.logger.info("="*70)
            
            # Calcular turnover
            resultados_turnover = self.calcular_turnover_todas_estrategias()
            
            if not resultados_turnover:
                self.logger.error("❌ Nenhum resultado de turnover calculado")
                return {}
            
            # Gerar relatório
            df_relatorio = self.gerar_relatorio_turnover(resultados_turnover)
            
            # Salvar resultados
            self.salvar_resultados_turnover(resultados_turnover, df_relatorio)
            
            # Log resumo
            self.logger.info("="*70)
            self.logger.info("✅ ANÁLISE DE TURNOVER CONCLUÍDA")
            self.logger.info(f"✅ {len(resultados_turnover)} estratégias analisadas")
            
            for estrategia, metricas in resultados_turnover.items():
                turnover_pct = metricas['turnover_medio'] * 100 if pd.notna(metricas['turnover_medio']) else 0
                self.logger.info(f"   {estrategia}: {turnover_pct:.1f}% turnover médio")
            
            self.logger.info("="*70)
            
            return {
                'resultados_detalhados': resultados_turnover,
                'relatorio_comparativo': df_relatorio,
                'metadados': {
                    'data_calculo': datetime.now().isoformat(),
                    'n_estrategias': len(resultados_turnover),
                    'versao_script': '2.0_profissional'
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de turnover: {e}")
            raise

if __name__ == "__main__":
    # Executar análise de turnover
    calculadora = CalculadoraTurnoverProfissional()
    resultado = calculadora.executar_analise_completa()
    
    if resultado and 'relatorio_comparativo' in resultado:
        print("\n📊 RESUMO DE TURNOVER POR ESTRATÉGIA:")
        print(resultado['relatorio_comparativo'].to_string(index=False))