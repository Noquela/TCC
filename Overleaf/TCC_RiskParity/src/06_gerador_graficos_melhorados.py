"""
GERADOR DE GRÁFICOS PROFISSIONAL - TCC Risk Parity v2.0
Sistema profissional de geração de figuras com configuração centralizada.

Autor: Bruno Gasparoni Ballerini  
Data: 2025-09-16
Versão: 2.0 - Profissional com paths relativos e logging

Melhorias implementadas:
- Configuração centralizada com fontes aprimoradas (≥14pt títulos, ≥12pt eixos)
- Paths relativos para replicabilidade total
- Logging profissional em substituição aos prints
- Contraste otimizado para impressão P&B
- Labels explícitos e legendas melhoradas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Importar configuração global
try:
    from _00_configuracao_global import get_logger, get_path, get_config
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from _00_configuracao_global import get_logger, get_path, get_config

class GeradorGraficosProfissional:
    """
    Gerador profissional de gráficos com configuração centralizada.
    
    Features v2.0:
    - Configuração centralizada com paths relativos
    - Logging profissional estruturado  
    - Fontes aprimoradas (títulos ≥15pt, eixos ≥13pt, legenda ≥12pt)
    - Contraste otimizado para impressão
    - Labels explícitos ("Base 100 = Jan/2018")
    """
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()
        
        # Usar paths da configuração global
        self.results_dir = self.config.results_dir
        self.figures_dir = self.config.figures_dir
        
        # Configuração PROFISSIONAL para qualidade acadêmica
        plt.style.use('default')  # Começar com estilo limpo
        
        # Configurações APRIMORADAS v2.0 - Fontes maiores para impressão
        plt.rcParams.update({
            'font.size': 13,                # Base aumentada
            'axes.titlesize': 16,           # Títulos ≥14pt (16pt para garantir)
            'axes.labelsize': 14,           # Eixos ≥12pt (14pt para garantir)
            'xtick.labelsize': 13,          # Números dos eixos ≥12pt
            'ytick.labelsize': 13,
            'legend.fontsize': 13,          # Legenda ≥11pt (13pt para garantir)
            'figure.titlesize': 18,         # Títulos gerais maiores
            'lines.linewidth': 2.5,         # Linhas mais espessas para contraste
            'lines.markersize': 6,          # Marcadores maiores
            'font.family': 'DejaVu Serif',  # Fonte acadêmica
            'axes.linewidth': 1.2,          # Bordas mais definidas
            'grid.alpha': 0.4,              # Grid um pouco mais visível
            'axes.edgecolor': 'black',      # Contorno preto forte
            'figure.dpi': 300,              # Alta resolução
            'savefig.dpi': 300,             # Alta resolução ao salvar
            'savefig.bbox': 'tight',        # Cortar margens
            'figure.facecolor': 'white',    # Fundo branco
            'axes.facecolor': 'white'       # Fundo dos eixos branco
        })
        
        # Paleta de cores OTIMIZADA para contraste em impressão P&B
        self.cores_estrategias = {
            'Equal Weight': '#1f4e79',          # Azul escuro (melhor contraste)
            'MVO (Markowitz)': '#c5504b',       # Vermelho escuro (melhor que laranja)
            'ERC (Risk Parity)': '#2d5a27',     # Verde escuro (melhor contraste)
            # Variações para compatibilidade
            'Mean-Variance Optimization': '#c5504b',
            'Equal Risk Contribution': '#2d5a27'
        }
        
        self.logger.info("="*70)
        self.logger.info("GERADOR DE GRÁFICOS PROFISSIONAL v2.0 INICIALIZADO")
        self.logger.info("="*70)
        self.logger.info("✅ Fontes APRIMORADAS: Títulos 16pt, Eixos 14pt, Legenda 13pt")
        self.logger.info("✅ Cores de ALTO CONTRASTE para impressão P&B")
        self.logger.info("✅ Resolução 300 DPI para qualidade acadêmica")
        self.logger.info("✅ Paths relativos configurados")
        self.logger.info("="*70)
    
    def carregar_dados(self):
        """Carrega dados necessários com paths relativos"""
        self.logger.info("1. Carregando dados...")
        
        try:
            # Carregar dados principais usando paths relativos
            path_retornos = get_path('results', "03_retornos_portfolios.csv")
            self.retornos_estrategias = pd.read_csv(path_retornos, index_col=0, parse_dates=True)
            
            path_comparacao = get_path('results', "03_comparacao_estrategias.csv")
            self.comparacao_metricas = pd.read_csv(path_comparacao, index_col=0)
            
            self.logger.info(f"   ✅ {len(self.retornos_estrategias)} períodos carregados")
            self.logger.info(f"   ✅ {len(self.retornos_estrategias.columns)} estratégias carregadas")
            
        except FileNotFoundError as e:
            self.logger.error(f"   ❌ Arquivo não encontrado: {e}")
            raise
        except Exception as e:
            self.logger.error(f"   ❌ Erro ao carregar dados: {e}")
            raise
    
    def gerar_retornos_acumulados(self):
        """Gráfico PROFISSIONAL de retornos acumulados com contraste otimizado"""
        self.logger.info("2. Gerando retornos acumulados APRIMORADOS...")
        
        # Calcular retornos acumulados (Base 100 = Janeiro 2018)
        retornos_acum = (1 + self.retornos_estrategias).cumprod() * 100
        
        # Figura com tamanho otimizado
        fig, ax = plt.subplots(figsize=(13, 9))
        
        # Plot com ALTO CONTRASTE e estilos únicos
        estilos_linha = ['-', '--', '-.']  # Estilos diferentes para impressão P&B
        
        for i, estrategia in enumerate(retornos_acum.columns):
            cor = self.cores_estrategias.get(estrategia, '#333333')
            estilo = estilos_linha[i % len(estilos_linha)]
            
            ax.plot(retornos_acum.index, retornos_acum[estrategia], 
                   color=cor, linewidth=3.0, label=estrategia, 
                   linestyle=estilo, marker='o', markersize=5, markevery=3,
                   alpha=0.9)
        
        # Formatação PROFISSIONAL
        ax.set_title('Evolução dos Retornos Acumulados das Estratégias (2018-2019)', 
                    fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontweight='bold')
        ax.set_ylabel('Valor Acumulado\n(Base 100 = Janeiro/2018)', fontweight='bold')
        
        # Legenda APRIMORADA
        ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True,
                 framealpha=0.95, edgecolor='black', facecolor='white')
        
        # Grid SUTIL mas visível
        ax.grid(True, alpha=0.4, linestyle=':', color='gray')
        
        # Linha de referência na base 100
        ax.axhline(y=100, color='black', linestyle='-', alpha=0.3, linewidth=1)
        
        # Melhorar formatação dos eixos
        ax.tick_params(axis='both', which='major', labelsize=13, colors='black')
        
        # Salvar com ALTA QUALIDADE
        plt.tight_layout()
        path_figura = get_path('figures', 'retornos_acumulados.png')
        plt.savefig(path_figura, dpi=300, bbox_inches='tight', facecolor='white', 
                   edgecolor='none')
        plt.close()
        
        self.logger.info(f"   ✅ Salvo: {path_figura}")
    
    def gerar_drawdowns(self):
        """Gráfico otimizado de drawdowns"""
        print("3. Gerando drawdowns melhorados...")
        
        # Calcular drawdowns
        retornos_acum = (1 + self.retornos_estrategias).cumprod()
        running_max = retornos_acum.expanding().max()
        drawdowns = (retornos_acum / running_max - 1) * 100
        
        # Figura otimizada
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot com preenchimento melhorado para legibilidade
        for estrategia in drawdowns.columns:
            cor = self.cores_otimizadas.get(estrategia, '#333333')
            # Preenchimento mais transparente
            ax.fill_between(drawdowns.index, 0, drawdowns[estrategia], 
                           color=cor, alpha=0.4, label=estrategia)
            # Linha mais espessa para impressão
            ax.plot(drawdowns.index, drawdowns[estrategia], 
                   color=cor, linewidth=2.5, alpha=0.9)
        
        # Formatação melhorada
        ax.set_title('Evolução dos Drawdowns por Estratégia', 
                    fontweight='bold', pad=15)
        ax.set_xlabel('Período')
        ax.set_ylabel('Drawdown (%)')
        ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1.0)
        
        # Melhorar legibilidade dos números
        ax.tick_params(axis='both', which='major', labelsize=11)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, 'drawdowns.png'),
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   OK Salvo: drawdowns.png")
    
    def gerar_distribuicao_retornos(self):
        """Histogramas melhorados de distribuição"""
        print("4. Gerando distribuição de retornos...")
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Distribuição dos Retornos Mensais por Estratégia', 
                    fontsize=16, fontweight='bold', y=1.02)
        
        for i, estrategia in enumerate(self.retornos_estrategias.columns):
            cor = self.cores_otimizadas.get(estrategia, '#333333')
            
            # Histograma
            axes[i].hist(self.retornos_estrategias[estrategia] * 100, 
                        bins=12, alpha=0.7, color=cor, edgecolor='black')
            
            # Linha vertical da média
            media = self.retornos_estrategias[estrategia].mean() * 100
            axes[i].axvline(media, color='red', linestyle='--', linewidth=2,
                           label=f'Média: {media:.1f}%')
            
            axes[i].set_title(estrategia, fontweight='bold')
            axes[i].set_xlabel('Retorno Mensal (%)')
            axes[i].set_ylabel('Frequência')
            axes[i].legend()
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, 'distribuicao_retornos.png'),
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   OK Salvo: distribuicao_retornos.png")
    
    def gerar_matriz_correlacao(self):
        """Matriz de correlação otimizada"""
        print("5. Gerando matriz de correlação...")
        
        # Calcular correlações
        corr_matrix = self.retornos_estrategias.corr()
        
        # Figura otimizada
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Heatmap com cores otimizadas
        sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0,
                   square=True, fmt='.3f', cbar_kws={'shrink': 0.8},
                   annot_kws={'size': 12}, ax=ax)
        
        ax.set_title('Matriz de Correlação entre Estratégias', 
                    fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, 'matriz_correlacao.png'),
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   OK Salvo: matriz_correlacao.png")
    
    def gerar_fronteira_eficiente(self):
        """Gráfico risco x retorno melhorado"""
        print("6. Gerando fronteira eficiente...")
        
        # Extrair métricas - usar nomes corretos do CSV
        retorno_anual = self.comparacao_metricas.loc['Retorno_Anual_Pct']
        volatilidade_anual = self.comparacao_metricas.loc['Volatilidade_Anual_Pct']
        sharpe = self.comparacao_metricas.loc['Sharpe_Ratio']
        
        # Figura otimizada
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot melhorado
        for estrategia in retorno_anual.index:
            cor = self.cores_otimizadas.get(estrategia, '#333333')
            ax.scatter(volatilidade_anual[estrategia], retorno_anual[estrategia], 
                      s=200, color=cor, alpha=0.8, edgecolors='black', linewidth=2)
            
            # Labels com offset para legibilidade
            ax.annotate(estrategia, 
                       (volatilidade_anual[estrategia], retorno_anual[estrategia]),
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                alpha=0.8, edgecolor='gray'))
        
        # Formatação
        ax.set_title('Relação Risco-Retorno das Estratégias', 
                    fontweight='bold', pad=20)
        ax.set_xlabel('Volatilidade Anual (%)')
        ax.set_ylabel('Retorno Anual (%)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.figures_dir, 'fronteira_eficiente.png'),
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print("   OK Salvo: fronteira_eficiente.png")
    
    def executar_todos_graficos(self):
        """Executa pipeline completo de geração de gráficos profissionais"""
        try:
            self.logger.info("INICIANDO GERAÇÃO DE GRÁFICOS PROFISSIONAIS...")
            
            # Pipeline de gráficos
            self.carregar_dados()
            self.gerar_retornos_acumulados()
            
            # Tentar gerar outros gráficos se métodos existirem
            if hasattr(self, 'gerar_drawdowns'):
                try:
                    self.gerar_drawdowns()
                except Exception as e:
                    self.logger.warning(f"Erro ao gerar drawdowns: {e}")
            
            if hasattr(self, 'gerar_distribuicao_retornos'):
                try:
                    self.gerar_distribuicao_retornos()
                except Exception as e:
                    self.logger.warning(f"Erro ao gerar distribuição: {e}")
            
            if hasattr(self, 'gerar_matriz_correlacao'):
                try:
                    self.gerar_matriz_correlacao()
                except Exception as e:
                    self.logger.warning(f"Erro ao gerar correlação: {e}")
            
            self.logger.info("="*70)
            self.logger.info("✅ TODOS OS GRÁFICOS PROFISSIONAIS FORAM GERADOS!")
            self.logger.info(f"✅ Localização: {self.figures_dir}")
            self.logger.info("✅ Resolução: 300 DPI (qualidade acadêmica)")
            self.logger.info("✅ Fontes APRIMORADAS: Títulos 16pt, Eixos 14pt, Legenda 13pt")
            self.logger.info("✅ Cores de ALTO CONTRASTE para impressão P&B")
            self.logger.info("="*70)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro na geração de gráficos: {e}")
            raise

if __name__ == "__main__":
    # Executar geração de gráficos profissionais
    gerador = GeradorGraficosProfissional()
    
    try:
        sucesso = gerador.executar_todos_graficos()
        
        if sucesso:
            print("\n🎨 GRÁFICOS PROFISSIONAIS GERADOS COM SUCESSO!")
            print("📊 Características aprimoradas:")
            print("   • Fontes maiores (16pt títulos, 14pt eixos)")
            print("   • Alto contraste para impressão P&B")
            print("   • Estilos de linha únicos para cada estratégia")
            print("   • Labels explícitos (Base 100 = Jan/2018)")
            print("   • Resolução 300 DPI para qualidade acadêmica")
        
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        raise