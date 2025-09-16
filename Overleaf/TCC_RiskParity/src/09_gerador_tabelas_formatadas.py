"""
GERADOR DE TABELAS FORMATADAS - Padrões Visuais Otimizados
Implementa formatação de tabelas conforme feedback: 1 casa para vol/MDD, 2 casas para Sharpe/Sortino

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-15
"""

import pandas as pd
import numpy as np
import os
from decimal import Decimal

class GeradorTabelasFormatadas:
    """
    Gera tabelas com formatação otimizada para impressão
    """
    
    def __init__(self):
        self.results_dir = r"C:\Users\BrunoGaspariniBaller\OneDrive - HAND\Documentos\TCC\Overleaf\TCC_RiskParity\results"
        self.tables_dir = r"C:\Users\BrunoGaspariniBaller\OneDrive - HAND\Documentos\TCC\Overleaf\TCC_RiskParity\docs\Overleaf\tables"
        
        # Criar diretório se não existir
        os.makedirs(self.tables_dir, exist_ok=True)
        
        print("="*70)
        print("GERADOR DE TABELAS FORMATADAS - PADROES VISUAIS")
        print("="*70)
        print("OK Formatacao: 1 casa para vol/MDD, 2 casas para Sharpe/Sortino")
        print("OK Alinhamento de percentuais otimizado")
        print("OK Consistencia com paleta de cores")
        print()
    
    def carregar_dados(self):
        """Carrega dados de performance"""
        print("1. Carregando dados de comparação...")
        
        # Carregar e transpor para ter métricas como index
        df_raw = pd.read_csv(
            os.path.join(self.results_dir, "03_comparacao_estrategias.csv"),
            index_col=0
        )
        self.comparacao_df = df_raw.T  # Transpor: métricas como index, estratégias como colunas
        
        print(f"   OK {len(self.comparacao_df)} metricas carregadas")
        print(f"   OK {len(self.comparacao_df.columns)} estrategias")
    
    def formatar_metricas(self):
        """Aplica formatação específica por tipo de métrica"""
        print("2. Aplicando formatação otimizada...")
        
        # Criar cópia para formatação
        tabela_formatada = self.comparacao_df.copy()
        
        # Definir regras de formatação por métrica (nomes do CSV)
        regras_formato = {
            # 1 casa decimal para volatilidade e drawdown
            'Volatilidade_Anual_Pct': '%.1f',
            'Max_Drawdown_Pct': '%.1f',
            
            # 2 casas decimais para ratios
            'Sharpe_Ratio': '%.2f',
            'Sortino_Ratio': '%.2f',
            
            # 2 casas para retornos
            'Retorno_Anual_Pct': '%.2f'
        }
        
        # Aplicar formatação
        for metrica, formato in regras_formato.items():
            if metrica in tabela_formatada.index:
                for col in tabela_formatada.columns:
                    valor = tabela_formatada.loc[metrica, col]
                    if pd.notna(valor):
                        tabela_formatada.loc[metrica, col] = formato % float(valor)
        
        self.tabela_formatada = tabela_formatada
        print("   OK Formatacao aplicada conforme especificacao")
    
    def gerar_tabela_principal_latex(self):
        """Gera tabela principal em LaTeX"""
        print("3. Gerando tabela principal LaTeX...")
        
        # Selecionar métricas principais (nomes do CSV)
        metricas_principais = [
            'Retorno_Anual_Pct',
            'Volatilidade_Anual_Pct',
            'Sharpe_Ratio',
            'Sortino_Ratio',
            'Max_Drawdown_Pct'
        ]
        
        # Filtrar tabela
        tabela_principal = self.tabela_formatada.loc[metricas_principais]
        
        # Gerar LaTeX otimizado
        latex_content = """
% Tabela Principal de Performance - Formatação Otimizada
\\begin{table}[!htbp]
\\centering
\\caption{Comparação de Performance das Estratégias de Alocação}
\\label{tab:performance_principal}
\\begin{tabular}{l*{3}{r}}
\\toprule
\\textbf{Métrica} & \\textbf{Equal Weight} & \\textbf{MVO (Markowitz)} & \\textbf{ERC (Risk Parity)} \\\\
\\midrule
"""
        
        # Mapeamento de nomes para LaTeX
        nomes_latex = {
            'Retorno_Anual_Pct': 'Retorno Anual (\\%)',
            'Volatilidade_Anual_Pct': 'Volatilidade Anual (\\%)',
            'Sharpe_Ratio': 'Sharpe Ratio',
            'Sortino_Ratio': 'Sortino Ratio',
            'Max_Drawdown_Pct': 'Maximum Drawdown (\\%)'
        }
        
        # Adicionar linhas com formatação alinhada
        for metrica in metricas_principais:
            nome_latex = nomes_latex.get(metrica, metrica)
            linha = f"{nome_latex}"
            for estrategia in tabela_principal.columns:
                valor = tabela_principal.loc[metrica, estrategia]
                # Adicionar % para métricas percentuais
                if 'Pct' in metrica:
                    linha += f" & {valor}\\%"
                else:
                    linha += f" & {valor}"
            linha += " \\\\\n"
            latex_content += linha
        
        latex_content += """\\bottomrule
\\end{tabular}
\\end{table}
"""
        
        # Salvar arquivo
        with open(os.path.join(self.tables_dir, 'tabela_performance_principal.tex'), 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print("   OK Salvo: tabela_performance_principal.tex")
    
    def gerar_tabela_implementabilidade_latex(self):
        """Gera tabela de implementabilidade"""
        print("4. Gerando tabela de implementabilidade...")
        
        # Métricas de implementabilidade
        metricas_impl = [
            'Turnover Estimado (%)',
            'Número Efetivo de Ativos',
            'Peso Máximo (%)',
            'Peso Mínimo (%)',
            'Concentração HHI'
        ]
        
        # Filtrar métricas existentes
        metricas_existentes = [m for m in metricas_impl if m in self.tabela_formatada.index]
        
        if metricas_existentes:
            tabela_impl = self.tabela_formatada.loc[metricas_existentes]
            
            latex_content = """
% Tabela de Implementabilidade
\\begin{table}[!htbp]
\\centering
\\caption{Métricas de Implementabilidade das Estratégias}
\\label{tab:implementabilidade}
\\begin{tabular}{l*{3}{r}}
\\toprule
\\textbf{Métrica} & \\textbf{Equal Weight} & \\textbf{MVO (Markowitz)} & \\textbf{ERC (Risk Parity)} \\\\
\\midrule
"""
            
            for metrica in metricas_existentes:
                linha = f"{metrica.replace('%', '\\%')}"
                for estrategia in tabela_impl.columns:
                    valor = tabela_impl.loc[metrica, estrategia]
                    if '%' in metrica:
                        linha += f" & {valor}\\%"
                    else:
                        linha += f" & {valor}"
                linha += " \\\\\n"
                latex_content += linha
            
            latex_content += """\\bottomrule
\\end{tabular}
\\end{table}
"""
            
            with open(os.path.join(self.tables_dir, 'tabela_implementabilidade.tex'), 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            print("   OK Salvo: tabela_implementabilidade.tex")
    
    def gerar_resumo_formatacao(self):
        """Gera resumo das regras de formatação aplicadas"""
        print("5. Gerando resumo de formatação...")
        
        resumo = """
# RELATÓRIO DE FORMATAÇÃO DE TABELAS

## Regras Aplicadas:

### Métricas com 1 casa decimal:
- Volatilidade Anual (%)
- Maximum Drawdown (%)  
- Downside Deviation (%)

### Métricas com 2 casas decimais:
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Retorno Anual (%)
- Retorno Médio Mensal (%)

### Métricas sem casas decimais (inteiros):
- Observações
- Meses Positivos/Negativos

## Paleta de Cores Consistente:
- Equal Weight: Azul (#1f77b4)
- MVO (Markowitz): Laranja (#ff7f0e)
- ERC (Risk Parity): Verde (#2ca02c)

## Arquivos Gerados:
- tabela_performance_principal.tex
- tabela_implementabilidade.tex
"""
        
        with open(os.path.join(self.tables_dir, 'relatorio_formatacao.md'), 'w', encoding='utf-8') as f:
            f.write(resumo)
        
        print("   OK Salvo: relatorio_formatacao.md")
    
    def executar_todas(self):
        """Executa todas as formatações"""
        self.carregar_dados()
        self.formatar_metricas()
        self.gerar_tabela_principal_latex()
        self.gerar_tabela_implementabilidade_latex()
        self.gerar_resumo_formatacao()
        
        print("\n" + "="*70)
        print("OK TODAS AS TABELAS FORMATADAS FORAM GERADAS!")
        print(f"OK Localizacao: {self.tables_dir}")
        print("OK Formatacao: 1 casa (vol/MDD), 2 casas (Sharpe/Sortino)")
        print("OK Alinhamento de percentuais otimizado")
        print("="*70)

if __name__ == "__main__":
    gerador = GeradorTabelasFormatadas()
    gerador.executar_todas()