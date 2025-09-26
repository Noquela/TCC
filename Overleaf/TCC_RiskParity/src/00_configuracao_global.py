"""
CONFIGURAÇÃO GLOBAL - Sistema Profissional TCC Risk Parity
Centraliza todas as configurações, paths relativos, logging e reprodutibilidade.

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-16
Versão: 2.0 - Profissional com consistência total
"""

import os
import sys
import logging
import warnings
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class ConfiguracaoGlobal:
    """
    Classe central para configurações padronizadas do projeto
    """
    
    def __init__(self):
        """Inicializa configurações globais"""
        # Detectar diretório do projeto automaticamente
        self.projeto_root = self._detectar_projeto_root()
        self.results_dir = self.projeto_root / "results"
        self.figures_dir = self.projeto_root / "docs" / "Overleaf" / "figures"
        self.tables_dir = self.projeto_root / "docs" / "Overleaf" / "tables"
        self.robustez_dir = self.projeto_root / "docs" / "Overleaf" / "robustez"
        self.src_dir = self.projeto_root / "src"
        
        # Criar diretórios se não existirem
        dirs_to_create = [
            self.results_dir, self.figures_dir, 
            self.tables_dir, self.robustez_dir
        ]
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Configurar logging padronizado
        self._configurar_logging()
        
        # Configurar warnings e pandas
        self._configurar_ambiente()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Configuração global inicializada")
        self.logger.info(f"Projeto root: {self.projeto_root}")
    
    def _detectar_projeto_root(self):
        """Detecta automaticamente o diretório raiz do projeto"""
        current = Path(__file__).parent
        
        # Procurar pelo diretório que contém 'src' e 'results'
        while current.parent != current:
            if (current / "src").exists() and current.name == "TCC_RiskParity":
                return current
            current = current.parent
        
        # Fallback para estrutura atual
        return Path(__file__).parent.parent
    
    def _configurar_logging(self):
        """Configura sistema de logging padronizado"""
        log_dir = self.projeto_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Formato padronizado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para arquivo
        file_handler = logging.FileHandler(
            log_dir / "tcc_risk_parity.log",
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Configurar root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _configurar_ambiente(self):
        """Configura pandas, warnings e reprodutibilidade"""
        # Pandas display options
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        pd.set_option('display.max_colwidth', 50)
        pd.set_option('display.precision', 4)
        
        # Suprimir warnings específicos
        warnings.filterwarnings('ignore', category=FutureWarning)
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', message='.*distplot.*')
        
        # Configurar reprodutibilidade TOTAL
        self.SEED = 42
        np.random.seed(self.SEED)
        
        # Gerador moderno para análises estatísticas
        self.rng = np.random.default_rng(self.SEED)
        
        # Configurações específicas do projeto
        self._configurar_projeto()
    
    def _configurar_projeto(self):
        """Configurações específicas do TCC Risk Parity - CONSISTÊNCIA TOTAL"""
        
        # === PESOS DO SCORE COMPOSTO (35/25/20/20) ===
        self.SCORE_WEIGHTS = {
            'momentum': 0.35,      # 35% - Jegadeesh & Titman (1993)
            'volatility': 0.25,    # 25% - Ang et al. (2006) 
            'max_drawdown': 0.20,  # 20% - Burke (1994)
            'downside_dev': 0.20   # 20% - Sortino & van der Meer (1991)
        }
        
        # === CRITÉRIOS DE LIQUIDEZ ===
        self.LIQUIDEZ_CRITERIA = {
            'volume_min_diario': 5_000_000,  # R$ 5M por dia
            'negocios_min_diario': 500,      # 500 negócios por dia
            'presenca_min_bolsa': 0.90,      # 90% dos dias
            'zero_return_days_max': 0.20,    # Máx 20% dias com retorno zero
            'autocorr_min': -0.30            # Autocorrelação mínima
        }
        
        # === RESTRIÇÕES DE CARTEIRA ===
        self.WEIGHT_CONSTRAINTS = {
            'peso_min': 0.00,           # 0% mínimo por ativo
            'peso_max': 0.40,           # 40% máximo por ativo  
            'peso_setor_max': 0.40,     # 40% máximo por setor
            'setores_min': 3            # Mínimo 3 setores
        }
        
        # === PERÍODOS TEMPORAIS ===
        self.PERIODOS = {
            'estimacao_inicio': '2016-01-01',
            'estimacao_fim': '2017-12-31', 
            'teste_inicio': '2018-01-01',
            'teste_fim': '2019-12-31',
            'rebalance_meses': [1, 7]  # Janeiro e Julho
        }
        
        # === CONFIGURAÇÕES FINANCEIRAS ===
        self.TAXA_LIVRE_RISCO = {
            'mensal': 0.0052,     # 0,52% a.m. (CDI médio 2018-2019)
            'anual': 0.065        # ~6,5% a.a.
        }
        
        # === ANÁLISES DE VALIDAÇÃO ===
        self.VALIDACAO_CONFIG = {
            'confidence_level': 0.95,
            'random_state': self.SEED
        }

    def obter_caminhos(self):
        """Retorna dicionário com todos os caminhos padronizados"""
        return {
            'projeto_root': self.projeto_root,
            'results': self.results_dir,
            'figures': self.figures_dir,
            'tables': self.tables_dir,
            'robustez': self.robustez_dir,
            'src': self.src_dir,
            'dados_economática': self.results_dir / "dados_economática_2014_2019.csv",
            'ativos_selecionados': self.results_dir / "01_ativos_selecionados.csv",
            'retornos_mensais': self.results_dir / "02_retornos_mensais_2018_2019.csv",
            'comparacao_estratégias': self.results_dir / "03_comparacao_estrategias.csv",
            'validacao_final': self.results_dir / "04_validacao_final.json"
        }
    
    def get_path(self, categoria, arquivo):
        """
        Função de conveniência para obter caminhos de arquivos.
        
        Args:
            categoria (str): 'results', 'figures', 'tables', 'robustez'
            arquivo (str): Nome do arquivo
            
        Returns:
            Path: Caminho completo do arquivo
        """
        mapeamento = {
            'results': self.results_dir,
            'figures': self.figures_dir, 
            'tables': self.tables_dir,
            'robustez': self.robustez_dir
        }
        
        if categoria not in mapeamento:
            raise ValueError(f"Categoria '{categoria}' inválida. Use: {list(mapeamento.keys())}")
            
        return mapeamento[categoria] / arquivo
        
    def salvar_configuracoes_projeto(self):
        """Salva todas as configurações em JSON para auditoria"""
        config_dict = {
            'projeto': 'TCC Risk Parity - Bruno Gasparini Ballerini',
            'versao': '2.0_profissional',
            'data_execucao': datetime.now().isoformat(),
            'diretorio_raiz': str(self.projeto_root),
            'seed_reprodutibilidade': self.SEED,
            'score_weights': self.SCORE_WEIGHTS,
            'liquidez_criteria': self.LIQUIDEZ_CRITERIA,
            'weight_constraints': self.WEIGHT_CONSTRAINTS,
            'periodos': self.PERIODOS,
            'taxa_livre_risco': self.TAXA_LIVRE_RISCO,
            'validacao_config': self.VALIDACAO_CONFIG
        }
        
        config_file = self.results_dir / "00_configuracoes_projeto.json"
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Configurações salvas: {config_file}")
        return config_file
    
    def validar_arquivos_necessarios(self):
        """Valida se arquivos essenciais existem"""
        logger = logging.getLogger(__name__)
        caminhos = self.obter_caminhos()
        
        arquivos_essenciais = [
            'dados_economática',
            'ativos_selecionados', 
            'retornos_mensais',
            'comparacao_estratégias'
        ]
        
        arquivos_faltando = []
        for arquivo in arquivos_essenciais:
            if not caminhos[arquivo].exists():
                arquivos_faltando.append(caminhos[arquivo])
        
        if arquivos_faltando:
            logger.warning("Arquivos faltando:")
            for arquivo in arquivos_faltando:
                logger.warning(f"  - {arquivo}")
            return False
        
        logger.info("Todos os arquivos essenciais estão presentes")
        return True
    
    def obter_configuracoes_graficos(self):
        """Retorna configurações padronizadas para gráficos"""
        return {
            'figsize': (12, 8),
            'dpi': 300,
            'cores_estrategias': {
                'Equal Weight': '#1f4e79',
                'MVO (Markowitz)': '#c5504b', 
                'ERC (Risk Parity)': '#70ad47'
            },
            'rcParams': {
                'font.size': 14,
                'axes.titlesize': 16,
                'axes.labelsize': 14,
                'xtick.labelsize': 12,
                'ytick.labelsize': 12,
                'legend.fontsize': 12,
                'lines.linewidth': 2.5,
                'font.family': 'DejaVu Serif',
                'figure.dpi': 300,
                'savefig.dpi': 300,
                'savefig.bbox': 'tight'
            }
        }
    
    def imprimir_resumo(self):
        """Imprime resumo da configuração"""
        print("="*70)
        print("CONFIGURAÇÃO GLOBAL TCC RISK PARITY")
        print("="*70)
        print(f"Projeto Root: {self.projeto_root}")
        print(f"Results Dir:  {self.results_dir}")
        print(f"Figures Dir:  {self.figures_dir}")
        print(f"Source Dir:   {self.src_dir}")
        print()
        print("✓ Logging configurado")
        print("✓ Caminhos padronizados")
        print("✓ Pandas configurado")
        print("✓ Warnings suprimidos")
        print("="*70)

# === INSTÂNCIA GLOBAL ===
CONFIG = ConfiguracaoGlobal()

# === FUNÇÕES DE CONVENIÊNCIA ===

def get_logger(name):
    """Retorna logger configurado para módulo específico"""
    return logging.getLogger(name)

def get_path(categoria, arquivo):
    """Função global para obter caminhos de arquivos"""
    return CONFIG.get_path(categoria, arquivo)

def get_rng():
    """Retorna gerador de números aleatórios configurado"""
    return CONFIG.rng

def get_config():
    """Retorna configuração global completa"""
    return CONFIG

def save_project_config():
    """Salva configurações do projeto"""
    return CONFIG.salvar_configuracoes_projeto()

if __name__ == "__main__":
    print("="*70)
    print("CONFIGURAÇÃO GLOBAL TCC RISK PARITY - v2.0 PROFISSIONAL")
    print("="*70)
    
    CONFIG.imprimir_resumo()
    CONFIG.validar_arquivos_necessarios()
    config_file = save_project_config()
    
    print("\n✅ SISTEMA CONFIGURADO COM SUCESSO!")
    print(f"📁 Diretório raiz: {CONFIG.projeto_root}")
    print(f"🎯 Seed reprodutibilidade: {CONFIG.SEED}")
    print(f"⚖️ Pesos Score: {CONFIG.SCORE_WEIGHTS}")
    print(f"💾 Configurações salvas: {config_file}")
    print("="*70)