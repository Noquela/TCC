"""
SISTEMA TCC RISK PARITY - v3.0
Script 10: Gerador de Resultados Essenciais para TCC

Autor: Bruno Gasparoni Ballerini
Data: 2025-09-23

Gera as 5 visualizações e tabelas mais importantes para a seção de Resultados:
1. Tabela Resumo de Performance Completa
2. Gráfico de Retornos Acumulados (evolução temporal)
3. Gráfico de Drawdowns (análise de risco)
4. Tabela de Significância Estatística (Jobson-Korkie)
5. Análise de Composição das Carteiras
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy.stats import t
import warnings
import sys
from pathlib import Path

# Adicionar src ao path e importar configuração global
sys.path.append(str(Path(__file__).parent))
import importlib.util
spec = importlib.util.spec_from_file_location("configuracao_global", Path(__file__).parent / "00_configuracao_global.py")
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
get_logger = config_module.get_logger
get_path = config_module.get_path
get_config = config_module.get_config

warnings.filterwarnings('ignore')

class GeradorResultadosEssenciais:
    """
    Gera as visualizações e tabelas mais importantes para a seção de Resultados
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.config = get_config()

        # Configurar matplotlib
        plt.style.use('default')
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 11,
            'lines.linewidth': 2.5,
            'figure.dpi': 300,
            'savefig.dpi': 300
        })

        # Cores contrastantes para impressão
        self.cores_melhoradas = {
            'Equal Weight': '#2E5BBA',           # Azul forte
            'Mean-Variance Optimization': '#D63384',  # Rosa/Vermelho
            'Equal Risk Contribution': '#28A745'     # Verde forte
        }
        print("="*80)
        print("GERADOR DE RESULTADOS ESSENCIAIS - TCC RISK PARITY")
        print("="*80)
        print("OK 5 visualizacoes principais para secao de Resultados")
        print("OK Tabelas formatadas para inclusao direta no LaTeX")
        print("OK Graficos otimizados para impressao academica")
        print()

    def carregar_dados(self):
        """Carrega todos os dados necessários"""

        try:
            # Carregar dados principais usando paths do config
            self.retornos_portfolios = pd.read_csv(
                self.config.results_dir / "03_retornos_portfolios.csv",
                index_col=0, parse_dates=True
            )

            self.pesos_portfolios = pd.read_csv(
                self.config.results_dir / "03_pesos_portfolios.csv"
            )

            self.comparacao_estrategias = pd.read_csv(
                self.config.results_dir / "03_comparacao_estrategias.csv"
            )

            self.ativos_selecionados = pd.read_csv(
                self.config.results_dir / "01_ativos_selecionados.csv"
            )

            print("OK Dados carregados com sucesso")
            print(f"  - {len(self.retornos_portfolios)} períodos mensais")
            print(f"  - {len(self.retornos_portfolios.columns)} estratégias")
            print(f"  - Período: {self.retornos_portfolios.index[0].strftime('%m/%Y')} a {self.retornos_portfolios.index[-1].strftime('%m/%Y')}")

        except Exception as e:
            self.logger.error(f"Erro ao carregar dados: {e}")
            raise

    def gerar_tabela_performance_completa(self):
        """
        Resultado 1: Tabela resumo de performance com todas as métricas essenciais
        """
        self.logger.info("Gerando tabela de performance completa")
        print("\n1. TABELA DE PERFORMANCE COMPLETA")
        print("-" * 50)

        rf_mensal = self.config.TAXA_LIVRE_RISCO['mensal']

        # Calcular métricas para cada estratégia
        resultados = []

        for estrategia in self.retornos_portfolios.columns:
            retornos = self.retornos_portfolios[estrategia]

            # Métricas básicas
            ret_mensal_medio = retornos.mean()
            ret_anual = ret_mensal_medio * 12 * 100
            vol_mensal = retornos.std()
            vol_anual = vol_mensal * np.sqrt(12) * 100

            # Sharpe Ratio - anualizado corretamente
            excess_ret = retornos - rf_mensal
            sharpe_mensal = excess_ret.mean() / excess_ret.std()
            sharpe = sharpe_mensal * np.sqrt(12)  # Anualizar multiplicando por √12

            # Sortino Ratio - anualizado corretamente
            downside_ret = excess_ret[excess_ret < 0]
            if len(downside_ret) > 0:
                downside_dev = np.sqrt(np.mean(downside_ret**2))
                sortino_mensal = excess_ret.mean() / downside_dev
                sortino = sortino_mensal * np.sqrt(12)  # Anualizar multiplicando por √12
            else:
                sortino = float('inf')

            # Maximum Drawdown
            cumret = (1 + retornos).cumprod()
            running_max = cumret.expanding().max()
            drawdown = (cumret - running_max) / running_max
            max_dd = drawdown.min() * 100

            # Estatísticas adicionais
            skewness = retornos.skew()
            kurtosis = retornos.kurtosis()

            # Probabilidade de ganho (% meses positivos)
            prob_ganho = (retornos > 0).mean() * 100

            # Retorno acumulado total
            ret_acumulado = ((1 + retornos).cumprod().iloc[-1] - 1) * 100

            resultados.append({
                'Estratégia': estrategia,
                'Retorno_Anual_pct': ret_anual,
                'Volatilidade_Anual_pct': vol_anual,
                'Sharpe_Ratio': sharpe,
                'Sortino_Ratio': sortino if sortino != float('inf') else 99.99,
                'Max_Drawdown_pct': max_dd,
                'Retorno_Acumulado_pct': ret_acumulado,
                'Prob_Ganho_pct': prob_ganho,
                'Skewness': skewness,
                'Kurtosis': kurtosis
            })

        self.tabela_performance = pd.DataFrame(resultados)

        # Salvar tabela formatada para LaTeX
        self._salvar_tabela_latex(self.tabela_performance, "tabela_performance_completa")

        print("OK Tabela de performance gerada")
        print("  Métricas incluídas: Retorno, Volatilidade, Sharpe, Sortino, MDD, etc.")

    def gerar_grafico_retornos_acumulados(self):
        """
        Resultado 2: Gráfico de evolução dos retornos acumulados
        """
        self.logger.info("Gerando gráfico de retornos acumulados")
        print("\n2. GRÁFICO DE RETORNOS ACUMULADOS")
        print("-" * 50)

        fig, ax = plt.subplots(1, 1, figsize=(14, 8))

        # Calcular retornos acumulados
        for estrategia in self.retornos_portfolios.columns:
            retornos_cum = (1 + self.retornos_portfolios[estrategia]).cumprod()

            # Nome mais limpo para o gráfico
            nome_limpo = self._limpar_nome_estrategia(estrategia)
            cor = self.cores_melhoradas.get(estrategia, 'gray')

            ax.plot(retornos_cum.index, retornos_cum.values,
                   label=nome_limpo, linewidth=3, color=cor)

        # Linha de referência (investimento inicial)
        ax.axhline(y=1.0, color='black', linestyle='--', alpha=0.5, label='Capital Inicial')

        # Formatação
        ax.set_title('Evolução dos Retornos Acumulados das Estratégias\n(Janeiro 2018 - Dezembro 2019)',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontsize=14)
        ax.set_ylabel('Valor Acumulado (Base = 1,00)', fontsize=14)
        ax.legend(fontsize=12, loc='upper left')
        ax.grid(True, alpha=0.3)

        # Formatar eixo Y para mostrar como múltiplos do capital inicial
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.2f}'))

        # Destacar eventos importantes
        eventos = [
            ('2018-05', 'Greve dos\nCaminhoneiros'),
            ('2018-10', 'Eleições\nPresidenciais')
        ]

        for data, evento in eventos:
            ax.axvline(pd.to_datetime(data), color='red', linestyle=':', alpha=0.7)
            ax.text(pd.to_datetime(data), ax.get_ylim()[1]*0.95, evento,
                   rotation=90, ha='right', va='top', fontsize=10, alpha=0.8)

        plt.tight_layout()
        plt.savefig(self.config.figures_dir / 'retornos_acumulados_essencial.png',
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print("OK Grafico de retornos acumulados salvo")

    def gerar_grafico_drawdowns(self):
        """
        Resultado 3: Gráfico de drawdowns para análise de risco
        """
        self.logger.info("Gerando gráfico de drawdowns")
        print("\n3. GRÁFICO DE DRAWDOWNS (ANÁLISE DE RISCO)")
        print("-" * 50)

        fig, ax = plt.subplots(1, 1, figsize=(14, 8))

        for estrategia in self.retornos_portfolios.columns:
            retornos = self.retornos_portfolios[estrategia]

            # Calcular drawdown
            cumret = (1 + retornos).cumprod()
            running_max = cumret.expanding().max()
            drawdown = (cumret - running_max) / running_max * 100

            nome_limpo = self._limpar_nome_estrategia(estrategia)
            cor = self.cores_melhoradas.get(estrategia, 'gray')

            ax.fill_between(drawdown.index, drawdown.values, 0,
                           alpha=0.6, color=cor, label=nome_limpo)
            ax.plot(drawdown.index, drawdown.values,
                   color=cor, linewidth=2)

        # Formatação
        ax.set_title('Evolução dos Drawdowns das Estratégias\n(Janeiro 2018 - Dezembro 2019)',
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Período', fontsize=14)
        ax.set_ylabel('Drawdown (%)', fontsize=14)
        ax.legend(fontsize=12, loc='lower right')
        ax.grid(True, alpha=0.3)

        # Eixo Y sempre negativo ou zero
        ax.set_ylim(min(ax.get_ylim()[0], -5), 2)

        # Destacar eventos importantes
        eventos = [
            ('2018-05', 'Greve dos\nCaminhoneiros'),
            ('2018-10', 'Eleições\nPresidenciais')
        ]

        for data, evento in eventos:
            ax.axvline(pd.to_datetime(data), color='red', linestyle=':', alpha=0.7)
            ax.text(pd.to_datetime(data), ax.get_ylim()[1]*0.9, evento,
                   rotation=90, ha='right', va='top', fontsize=10, alpha=0.8)

        plt.tight_layout()
        plt.savefig(self.config.figures_dir / 'drawdowns_essencial.png',
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        print("OK Grafico de drawdowns salvo")

    def gerar_tabela_significancia_estatistica(self):
        """
        Resultado 4: Tabela de significância estatística (Jobson-Korkie)
        """
        self.logger.info("Gerando tabela de significância estatística")
        print("\n4. TABELA DE SIGNIFICÂNCIA ESTATÍSTICA")
        print("-" * 50)

        rf_mensal = self.config.TAXA_LIVRE_RISCO['mensal']
        estrategias = list(self.retornos_portfolios.columns)

        # Calcular Sharpe Ratios - anualizados
        sharpe_ratios = {}
        for estrategia in estrategias:
            retornos = self.retornos_portfolios[estrategia]
            excess_ret = retornos - rf_mensal
            sharpe_mensal = excess_ret.mean() / excess_ret.std()
            sharpe_ratios[estrategia] = sharpe_mensal * np.sqrt(12)  # Anualizar

        # Teste Jobson-Korkie para todos os pares
        resultados_teste = []

        for i, est1 in enumerate(estrategias):
            for j, est2 in enumerate(estrategias):
                if i < j:  # Evitar duplicatas
                    ret1 = self.retornos_portfolios[est1] - rf_mensal
                    ret2 = self.retornos_portfolios[est2] - rf_mensal

                    # Estatística Jobson-Korkie - usar Sharpe anualizados
                    sr1 = sharpe_ratios[est1]  # Já anualizado
                    sr2 = sharpe_ratios[est2]  # Já anualizado

                    n = len(ret1)

                    # Covariância dos retornos
                    cov_ret = np.cov(ret1, ret2)[0, 1]
                    var_ret1 = np.var(ret1)
                    var_ret2 = np.var(ret2)

                    # Variância da diferença dos Sharpe Ratios
                    var_diff = (1/n) * (2 - 2*cov_ret/np.sqrt(var_ret1*var_ret2))

                    if var_diff > 0:
                        t_stat = (sr1 - sr2) / np.sqrt(var_diff)
                        p_valor = 2 * (1 - t.cdf(abs(t_stat), n-1))

                        # Nomes limpos
                        nome1 = self._limpar_nome_estrategia(est1)
                        nome2 = self._limpar_nome_estrategia(est2)

                        resultados_teste.append({
                            'Comparação': f'{nome1} vs {nome2}',
                            'Sharpe_1': sr1,
                            'Sharpe_2': sr2,
                            'Diferença': sr1 - sr2,
                            'Estatística_t': t_stat,
                            'P_valor': p_valor,
                            'Significativo_5pct': p_valor < 0.05,
                            'Significativo_1pct': p_valor < 0.01
                        })

        self.tabela_significancia = pd.DataFrame(resultados_teste)

        # Salvar tabela formatada
        self._salvar_tabela_latex(self.tabela_significancia, "tabela_significancia_estatistica")

        print("OK Tabela de significancia estatistica gerada")
        print(f"  {len(resultados_teste)} comparações par a par realizadas")

    def gerar_analise_composicao_carteiras(self):
        """
        Resultado 5: Análise da composição das carteiras
        """
        self.logger.info("Gerando análise de composição das carteiras")
        print("\n5. ANÁLISE DE COMPOSIÇÃO DAS CARTEIRAS")
        print("-" * 50)

        # Gráfico de composição média das carteiras
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Composição Média das Carteiras por Estratégia\n(Período: 2018-2019)',
                    fontsize=16, fontweight='bold')

        # Cores para ativos (palette consistente)
        cores_ativos = plt.cm.Set3(np.linspace(0, 1, len(self.ativos_selecionados)))

        for idx, estrategia in enumerate(self.retornos_portfolios.columns):
            ax = axes[idx]

            # Filtrar pesos para esta estratégia (formato longo)
            pesos_estrategia = self.pesos_portfolios[
                self.pesos_portfolios['Estratégia'] == estrategia
            ].copy()

            if not pesos_estrategia.empty:
                # Calcular peso médio por ativo (formato longo para dicionário)
                pesos_medios = {}
                for _, row in pesos_estrategia.iterrows():
                    ativo = row['Ativo']
                    peso = row['Peso_Pct'] / 100  # Converter para proporção
                    if peso > 0.01:  # Só mostrar se > 1%
                        pesos_medios[ativo] = peso

                # Ordenar por peso (maior primeiro)
                pesos_ordenados = dict(sorted(pesos_medios.items(),
                                            key=lambda x: x[1], reverse=True))

                # Criar gráfico de pizza
                labels = list(pesos_ordenados.keys())
                sizes = list(pesos_ordenados.values())

                wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                                 colors=cores_ativos[:len(labels)],
                                                 startangle=90)

                # Melhorar legibilidade
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(10)

            # Título limpo
            nome_limpo = self._limpar_nome_estrategia(estrategia)
            ax.set_title(nome_limpo, fontsize=14, fontweight='bold', pad=10)

        plt.tight_layout()
        plt.savefig(self.config.figures_dir / 'composicao_carteiras_essencial.png',
                   dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        # Tabela de concentração das carteiras
        self._gerar_tabela_concentracao()

        print("OK Analise de composicao das carteiras gerada")

    def _gerar_tabela_concentracao(self):
        """Gera tabela de concentração (HHI) das carteiras"""
        concentracao_resultados = []

        for estrategia in self.retornos_portfolios.columns:
            pesos_estrategia = self.pesos_portfolios[
                self.pesos_portfolios['Estratégia'] == estrategia
            ].copy()

            if not pesos_estrategia.empty:
                # Converter pesos para proporção
                pesos_proporcao = pesos_estrategia['Peso_Pct'] / 100

                # Calcular HHI
                hhi = sum(peso**2 for peso in pesos_proporcao if peso > 0)

                # Número efetivo de ativos (1/HHI)
                n_efetivo = 1 / hhi if hhi > 0 else 0

                # Peso máximo
                peso_max = pesos_proporcao.max()

                concentracao_resultados.append({
                    'Estratégia': self._limpar_nome_estrategia(estrategia),
                    'HHI_Médio': hhi,
                    'N_Ativos_Efetivo': n_efetivo,
                    'Peso_Máximo_Médio': peso_max
                })

        self.tabela_concentracao = pd.DataFrame(concentracao_resultados)
        self._salvar_tabela_latex(self.tabela_concentracao, "tabela_concentracao_carteiras")

    def _limpar_nome_estrategia(self, nome):
        """Limpa nomes das estratégias para visualização"""
        mapeamento = {
            'Equal Weight': 'Equal Weight',
            'Mean-Variance Optimization': 'Markowitz (MVO)',
            'Equal Risk Contribution': 'Risk Parity (ERC)'
        }
        return mapeamento.get(nome, nome)

    def _salvar_tabela_latex(self, df, nome_arquivo):
        """Salva tabela formatada para LaTeX"""
        # Formatar números e nomes das colunas
        df_formatado = df.copy()

        # Renomear colunas para formato LaTeX adequado
        rename_map = {
            'Estratégia': 'Estratégia',
            'Retorno_Anual_pct': 'Retorno Anual (\\%)',
            'Volatilidade_Anual_pct': 'Volatilidade (\\%)',
            'Sharpe_Ratio': 'Sharpe Ratio',
            'Sortino_Ratio': 'Sortino Ratio',
            'Max_Drawdown_pct': 'Max Drawdown (\\%)',
            'Retorno_Acumulado_pct': 'Retorno Total (\\%)',
            'Prob_Ganho_pct': 'Prob. Ganho (\\%)',
            'Skewness': 'Skewness',
            'Kurtosis': 'Kurtosis',
            'Comparação': 'Comparação',
            'Sharpe_1': 'Sharpe 1',
            'Sharpe_2': 'Sharpe 2',
            'Diferença': 'Diferença',
            'Estatística_t': 'Estatística t',
            'P_valor': 'P-valor',
            'Significativo_5pct': 'Signif. 5\\%',
            'Significativo_1pct': 'Signif. 1\\%',
            'HHI_Médio': 'HHI Médio',
            'N_Ativos_Efetivo': 'N Ativos Efetivo',
            'Peso_Máximo_Médio': 'Peso Máximo (\\%)'
        }

        # Aplicar renomeação
        for old_name, new_name in rename_map.items():
            if old_name in df_formatado.columns:
                df_formatado = df_formatado.rename(columns={old_name: new_name})

        # Renomear valores para nomes mais limpos
        value_map = {
            'EW_Returns': 'Equal Weight',
            'MVO_Returns': 'Markowitz',
            'ERC_Returns': 'Risk Parity',
            'True': 'Sim',
            'False': 'Não'
        }

        for col in df_formatado.columns:
            if df_formatado[col].dtype == 'object':
                df_formatado[col] = df_formatado[col].replace(value_map)

        # Formatar números
        for col in df_formatado.columns:
            if df_formatado[col].dtype in ['float64', 'int64']:
                if 'pct' in col.lower() or '%' in col:
                    df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:.2f}")
                elif 'ratio' in col.lower():
                    df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:.3f}")
                elif 'valor' in col.lower() or 'estatistica' in col.lower():
                    df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:.4f}")
                else:
                    df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:.3f}")

        # Determinar alinhamento das colunas
        n_cols = len(df_formatado.columns)
        if n_cols <= 4:
            alignment = 'l' + 'c' * (n_cols - 1)
        else:
            alignment = 'l' + 'r' * (n_cols - 1)

        # Salvar como LaTeX com formatação correta
        latex_content = df_formatado.to_latex(
            index=False,
            escape=False,
            column_format=alignment
        )

        # Remover o begin/end{table} e center, manter só tabular
        lines = latex_content.split('\n')
        start_idx = next(i for i, line in enumerate(lines) if '\\begin{tabular}' in line)
        end_idx = next(i for i, line in enumerate(lines) if '\\end{tabular}' in line) + 1

        latex_path = self.config.tables_dir / f"{nome_arquivo}.tex"
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines[start_idx:end_idx]))

        # Salvar como CSV para referência
        csv_path = self.config.results_dir / f"{nome_arquivo}.csv"
        df.to_csv(csv_path, index=False)

    def gerar_relatorio_resultados(self):
        """Gera relatório explicativo dos resultados"""
        print("\n6. GERANDO RELATÓRIO EXPLICATIVO")
        print("-" * 50)

        relatorio = f"""# RELATÓRIO DOS RESULTADOS ESSENCIAIS
**TCC Risk Parity - Gerado em:** {datetime.now().strftime('%d/%m/%Y às %H:%M')}

## Resultados Principais Gerados

### 1. Tabela de Performance Completa
- **Arquivo**: tabela_performance_completa.tex
- **Conteúdo**: Métricas de retorno, risco e performance ajustada ao risco
- **Uso no TCC**: Tabela principal da seção de Resultados

### 2. Gráfico de Retornos Acumulados
- **Arquivo**: retornos_acumulados_essencial.png
- **Conteúdo**: Evolução temporal das três estratégias (2018-2019)
- **Destaques**: Eventos importantes marcados (greve, eleições)

### 3. Gráfico de Drawdowns
- **Arquivo**: drawdowns_essencial.png
- **Conteúdo**: Análise de risco de cauda e períodos de perda
- **Importância**: Mostra resiliência das estratégias em crises

### 4. Tabela de Significância Estatística
- **Arquivo**: tabela_significancia_estatistica.tex
- **Conteúdo**: Teste Jobson-Korkie para comparações par a par
- **Uso**: Validação estatística das diferenças observadas

### 5. Análise de Composição das Carteiras
- **Arquivo**: composicao_carteiras_essencial.png
- **Conteúdo**: Distribuição de pesos por estratégia
- **Complemento**: tabela_concentracao_carteiras.tex (métricas HHI)

## Como Usar no TCC

### Ordem de Apresentação Sugerida:
1. **Introduzir** com a Tabela de Performance (visão geral)
2. **Mostrar evolução** com Gráfico de Retornos Acumulados
3. **Analisar risco** com Gráfico de Drawdowns
4. **Validar estatisticamente** com Tabela de Significância
5. **Explicar composição** com Análise de Carteiras

### Textos-Modelo para Cada Resultado:
- **Performance**: "A Tabela X apresenta as métricas de performance..."
- **Retornos**: "A Figura X ilustra a evolução dos retornos acumulados..."
- **Drawdowns**: "A análise de drawdowns (Figura X) revela..."
- **Significância**: "Os testes estatísticos (Tabela X) confirmam..."
- **Composição**: "A composição das carteiras (Figura X) demonstra..."

## Principais Insights para Discussão
(Baseado nos resultados gerados)

### Performance Relativa:
- Comparar Sharpe Ratios entre estratégias
- Analisar trade-off risco-retorno
- Destacar consistência temporal

### Comportamento em Crises:
- Reação durante greve dos caminhoneiros
- Performance durante período eleitoral
- Recuperação pós-choques

### Características de Implementação:
- Concentração vs diversificação
- Estabilidade dos pesos
- Praticidade operacional

## Próximos Passos
1. Inserir visualizações na seção de Resultados
2. Adaptar explicações ao estilo do TCC
3. Conectar com objetivos específicos estabelecidos
4. Preparar transição para seção de Discussão
"""

        # Salvar relatório
        relatorio_path = self.config.results_dir / "relatorio_resultados_essenciais.md"
        with open(relatorio_path, 'w', encoding='utf-8') as f:
            f.write(relatorio)

        print(f"OK Relatorio explicativo salvo: {relatorio_path}")

    def executar_geracao_completa(self):
        """Executa geração de todos os resultados essenciais"""
        try:
            self.carregar_dados()
            self.gerar_tabela_performance_completa()
            self.gerar_grafico_retornos_acumulados()
            self.gerar_grafico_drawdowns()
            self.gerar_tabela_significancia_estatistica()
            self.gerar_analise_composicao_carteiras()
            self.gerar_relatorio_resultados()

            print("\n" + "="*80)
            print("RESULTADOS ESSENCIAIS GERADOS COM SUCESSO!")
            print("="*80)
            print("OK 2 tabelas principais formatadas para LaTeX")
            print("OK 3 graficos otimizados para impressao academica")
            print("OK Relatorio explicativo com orientacoes de uso")
            print("OK Arquivos salvos em: tables/ e figures/")
            print("OK Proximo: incorporar na secao de Resultados do TCC")
            print("="*80)

            self.logger.info("Geração de resultados essenciais completada")

        except Exception as e:
            self.logger.error(f"Erro na geração de resultados: {e}")
            raise

def main():
    """Execução principal"""
    try:
        gerador = GeradorResultadosEssenciais()
        gerador.executar_geracao_completa()
        return 0

    except Exception as e:
        print(f"ERRO na execucao: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())