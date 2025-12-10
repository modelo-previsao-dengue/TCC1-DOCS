import pandas as pd
import numpy as np
import os
from statsmodels.tsa.stattools import grangercausalitytests
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

INPUT_FILE = "data_processed/dataset_unificado.csv"
OUTPUT_CSV = "data_processed/TABELA_CORRELACAO_SINAN_INMET_ULTIMOS3ANOS.csv"
OUTPUT_MD = "data_processed/TABELA_CORRELACAO_SINAN_INMET_ULTIMOS3ANOS.md"

def interpret_correlation(r):
    """Interpreta a força da correlação baseado no valor absoluto"""
    abs_r = abs(r)
    if abs_r >= 0.7:
        return "Forte", "🔴"
    elif abs_r >= 0.4:
        return "Moderada", "🟡"
    elif abs_r >= 0.2:
        return "Fraca", "🟢"
    else:
        return "Muito Fraca", "⚪"

def interpret_direction(r):
    """Interpreta a direção da correlação"""
    if r > 0:
        return "Positiva", "↑"
    elif r < 0:
        return "Negativa", "↓"
    else:
        return "Neutra", "→"

def analyze_correlations():
    print("--- STEP 3: STATISTICAL ANALYSIS ---")
    
    df = pd.read_csv(INPUT_FILE)
    df['data'] = pd.to_datetime(df['data'])
    df = df.sort_values('data')
    
    # Informações sobre o período
    data_inicio = df['data'].min()
    data_fim = df['data'].max()
    n_semanas = len(df)
    total_casos = df['casos_dengue'].sum()
    
    variables = {
        'chuva': {
            'nome': 'Precipitação (mm)',
            'unidade': 'mm/semana',
            'descricao': 'Quantidade total de chuva acumulada na semana'
        },
        'umidade': {
            'nome': 'Umidade Relativa do Ar (%)',
            'unidade': '%',
            'descricao': 'Umidade relativa média do ar durante a semana'
        },
        'temperatura_media': {
            'nome': 'Temperatura Média (°C)',
            'unidade': '°C',
            'descricao': 'Temperatura média do ar durante a semana'
        },
        'pressao': {
            'nome': 'Pressão Atmosférica (hPa)',
            'unidade': 'hPa',
            'descricao': 'Pressão atmosférica média na semana'
        }
    }
    
    results = []
    
    for var_col, var_info in variables.items():
        if var_col not in df.columns: 
            continue
        
        print(f"    Analisando {var_info['nome']}...")
        
        # Estatísticas descritivas da variável climática
        media_var = df[var_col].mean()
        desvio_var = df[var_col].std()
        min_var = df[var_col].min()
        max_var = df[var_col].max()
        
        # Correlações
        pearson = df['casos_dengue'].corr(df[var_col], method='pearson')
        spearman = df['casos_dengue'].corr(df[var_col], method='spearman')
        
        # Interpretações
        forca_pearson, emoji_forca = interpret_correlation(pearson)
        direcao_pearson, emoji_dir = interpret_direction(pearson)
        
        # Para interpretação geral, considerar também Spearman se for mais forte
        forca_spearman, _ = interpret_correlation(spearman)
        
        row = {
            'Variável Climática': var_info['nome'],
            'Descrição': var_info['descricao'],
            'Média': f"{media_var:.2f} {var_info['unidade']}",
            'Desvio Padrão': f"{desvio_var:.2f} {var_info['unidade']}",
            'Valor Mínimo': f"{min_var:.2f} {var_info['unidade']}",
            'Valor Máximo': f"{max_var:.2f} {var_info['unidade']}",
            'Correlação de Pearson (r)': f"{pearson:.4f}",
            'Força da Correlação': f"{forca_pearson} {emoji_forca}",
            'Direção': f"{direcao_pearson} {emoji_dir}",
            'Correlação de Spearman (ρ)': f"{spearman:.4f}",
            'Força Spearman': forca_spearman,
            'Interpretação': f"Correlação {forca_pearson.lower()} {direcao_pearson.lower()} (Pearson) / {forca_spearman.lower()} (Spearman) entre {var_info['nome'].lower()} e casos de dengue"
        }
        
        # Teste de Causalidade de Granger (Climate -> Dengue)
        data_gc = df[['casos_dengue', var_col]].dropna()
        
        max_lag = 4
        melhor_lag = None
        melhor_p_val = 1.0
        
        try:
            gc_res = grangercausalitytests(data_gc, maxlag=max_lag, verbose=False)
            
            lags_significativos = []
            
            for lag in range(1, max_lag + 1):
                # F-test p-value
                p_val = gc_res[lag][0]['ssr_ftest'][1]
                
                if p_val < melhor_p_val:
                    melhor_p_val = p_val
                    melhor_lag = lag
                
                if p_val < 0.05:
                    lags_significativos.append(lag)
                
                row[f'Causalidade Lag {lag} (p-valor)'] = f"{p_val:.4f}"
                row[f'Significativo Lag {lag}?'] = "✅ SIM" if p_val < 0.05 else "❌ NÃO"
                
            # Resumo de causalidade
            if lags_significativos:
                row['Melhor Lag Causal'] = f"Lag {melhor_lag} (p={melhor_p_val:.4f})"
                row['Conclusão Causalidade'] = f"✅ Há evidência de causalidade (melhor lag: {melhor_lag} semana{'s' if melhor_lag > 1 else ''})"
            else:
                row['Melhor Lag Causal'] = "Nenhum"
                row['Conclusão Causalidade'] = "❌ Não há evidência estatística de causalidade temporal"
                
        except Exception as e:
            print(f"    ⚠️ Granger failed for {var_info['nome']}: {e}")
            row['Conclusão Causalidade'] = f"⚠️ Erro no teste: {str(e)[:50]}"
            
        results.append(row)
        
    # Criar DataFrame
    res_df = pd.DataFrame(results)
    
    # Reordenar colunas para melhor legibilidade
    col_order = [
        'Variável Climática',
        'Descrição',
        'Média',
        'Desvio Padrão',
        'Valor Mínimo',
        'Valor Máximo',
        'Correlação de Pearson (r)',
        'Força da Correlação',
        'Direção',
        'Correlação de Spearman (ρ)',
        'Força Spearman',
        'Interpretação',
        'Causalidade Lag 1 (p-valor)',
        'Significativo Lag 1?',
        'Causalidade Lag 2 (p-valor)',
        'Significativo Lag 2?',
        'Causalidade Lag 3 (p-valor)',
        'Significativo Lag 3?',
        'Causalidade Lag 4 (p-valor)',
        'Significativo Lag 4?',
        'Melhor Lag Causal',
        'Conclusão Causalidade'
    ]
    
    # Garantir que todas as colunas existam
    for col in col_order:
        if col not in res_df.columns:
            res_df[col] = '-'
    
    # Selecionar apenas as colunas que existem
    col_order = [col for col in col_order if col in res_df.columns]
    res_df = res_df[col_order]
    
    # Salvar CSV
    res_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')
    print(f"✔ Tabela salva em {OUTPUT_CSV}")
    
    # Criar Markdown completo e didático
    md_content = generate_markdown_table(res_df, data_inicio, data_fim, n_semanas, total_casos)
    
    with open(OUTPUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"✔ Markdown salvo em {OUTPUT_MD}")
    
    return res_df

def generate_markdown_table(res_df, data_inicio, data_fim, n_semanas, total_casos):
    """Gera um markdown completo e didático com explicações"""
    
    # Mapeamento de meses em português
    meses_pt = {
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    }
    
    def formatar_data_pt(data):
        data_str = data.strftime('%d de %B de %Y')
        for en, pt in meses_pt.items():
            data_str = data_str.replace(en, pt)
        return data_str
    
    data_inicio_str = formatar_data_pt(data_inicio)
    data_fim_str = formatar_data_pt(data_fim)
    
    md = f"""# 📊 Tabela de Correlação e Causalidade: SINAN vs INMET
## Período: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} ({n_semanas} semanas)

---

## 📋 Informações do Período Analisado

| Métrica | Valor |
|---------|-------|
| **Data de Início** | {data_inicio_str} |
| **Data de Fim** | {data_fim_str} |
| **Total de Semanas** | {n_semanas} semanas |
| **Total de Casos de Dengue** | {total_casos:,} casos notificados |
| **Média de Casos por Semana** | {(total_casos/n_semanas):.1f} casos/semana |

---

## 📖 Glossário de Métricas

### 🔍 Correlação de Pearson (r)
- **O que é**: Mede a relação linear entre duas variáveis
- **Interpretação**: 
  - |r| ≥ 0.7 → Correlação **Forte** 🔴
  - 0.4 ≤ |r| < 0.7 → Correlação **Moderada** 🟡
  - 0.2 ≤ |r| < 0.4 → Correlação **Fraca** 🟢
  - |r| < 0.2 → Correlação **Muito Fraca** ⚪
- **Direção**: 
  - r > 0 → **Positiva** ↑ (quando uma aumenta, a outra também aumenta)
  - r < 0 → **Negativa** ↓ (quando uma aumenta, a outra diminui)

### 📈 Correlação de Spearman (ρ)
- **O que é**: Mede a relação monotônica entre duas variáveis (não necessariamente linear)
- **Vantagem**: É mais robusta a outliers do que Pearson
- **Mesma interpretação de força e direção** que Pearson

### ⏱️ Teste de Causalidade de Granger
- **O que é**: Verifica se uma variável (ex: chuva) ajuda a **prever** a outra (ex: casos de dengue)
- **Lags**: Testa se dados de 1, 2, 3 ou 4 semanas anteriores são úteis para previsão
- **Interpretação**: 
  - p-valor < 0.05 → **Significativo** ✅ (há evidência de causalidade temporal)
  - p-valor ≥ 0.05 → **Não significativo** ❌ (não há evidência de causalidade)
- **Importância**: Se significativo, a variável climática pode ser usada para prever casos futuros de dengue

---

## 📊 Resultados Detalhados

"""
    
    # Criar tabela principal com formatação melhorada
    md_table = res_df.to_markdown(index=False, tablefmt='github')
    md += md_table
    
    md += f"""

---

## 🎯 Resumo Executivo

### Principais Achados

"""
    
    # Adicionar resumo interpretativo
    for _, row in res_df.iterrows():
        var = row['Variável Climática']
        pearson = float(row['Correlação de Pearson (r)'])
        spearman = float(row['Correlação de Spearman (ρ)'])
        forca_pearson = row['Força da Correlação']
        forca_spearman = row.get('Força Spearman', '-')
        direcao = row['Direção']
        conclusao_causal = row.get('Conclusão Causalidade', '-')
        
        # Destacar quando Spearman é diferente/mais forte
        destaque_spearman = ""
        if forca_spearman != '-' and forca_spearman != forca_pearson:
            destaque_spearman = f" _(Nota: Correlação de Spearman é {forca_spearman.lower()} - ρ = {spearman:.4f})_"
        
        md += f"""
#### {var}

- **Correlação com casos de dengue**: {forca_pearson} {direcao}
- **Pearson (r)**: {pearson:.4f}{destaque_spearman}
- **Spearman (ρ)**: {spearman:.4f}
- **Causalidade Temporal**: {conclusao_causal}

"""
    
    md += f"""
---

## 📝 Notas Metodológicas

1. **Fonte dos Dados**:
   - Casos de dengue: SINAN (Sistema de Informação de Agravos de Notificação)
   - Dados climáticos: INMET (Instituto Nacional de Meteorologia)
   - Estação meteorológica: Brasília (A001)

2. **Agregação Temporal**: 
   - Dados agregados por semana epidemiológica
   - Variáveis climáticas: média semanal (temperatura, umidade, pressão) ou soma semanal (precipitação)

3. **Significância Estatística**:
   - Correlações: valores apresentados sem teste de significância adicional (valores próximos de zero indicam ausência de relação)
   - Causalidade de Granger: nível de significância de 5% (α = 0.05)

4. **Limitações**:
   - Correlação não implica causalidade direta
   - Outros fatores não considerados podem influenciar os casos de dengue
   - Atraso de notificação pode afetar a correlação temporal

---

**Data de geração**: {formatar_data_pt(datetime.now())} às {datetime.now().strftime('%H:%M:%S')}

"""
    
    return md

if __name__ == "__main__":
    analyze_correlations()

