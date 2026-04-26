# Clusterizacao de atributos INMET e correlacao espacial com SINAN

## Objetivo

Documentar o processo de reducao de redundancia dos atributos climaticos, responder sobre correlacao por localizacao (Estado, UF, Municipio) e definir como os atributos selecionados serao usados no modelo preditivo final.

## Pergunta 1: E possivel correlacionar localizacao (Estado, UF, Municipio) com ocorrencias de dengue do SINAN?

Sim, e possivel e recomendavel, desde que a base esteja em painel espaco-temporal com chaves consistentes.

### Chaves de correlacao recomendadas

- Chave espacial primaria: `ibge_mun` (codigo do municipio IBGE)
- Chave espacial de apoio: `uf` + `municipio` normalizados
- Chave temporal: `iso_year` + `iso_week` (ou `sem_not`)

### Evidencia no projeto atual

- A base [data_processed/2024_inmet_dengue_weekly_by_mun.csv](../data_processed/2024_inmet_dengue_weekly_by_mun.csv) ja esta no nivel semanal por municipio (`ibge_mun`, `iso_year`, `iso_week`) e e a melhor estrutura para o merge espacial com SINAN.
- A base [data_processed/inmet_sinan_merged.csv](../data_processed/inmet_sinan_merged.csv) atualmente aparece concentrada em um unico par `UF/municipio` (DF/Brasilia), entao ela nao representa ainda um painel nacional.
- A base [data_processed/sinan_2022_2024.csv](../data_processed/sinan_2022_2024.csv) esta agregada por semana e sem chave espacial explicita.

### Estrategia de correlacao espacial-temporal

1. Padronizar o municipio via `ibge_mun` em INMET e SINAN.
2. Agregar tudo para periodicidade semanal epidemiologica.
3. Fazer merge por (`ibge_mun`, `iso_year`, `iso_week`).
4. Gerar lags climaticos por municipio (1, 2, 4, 8, 12 semanas).
5. Calcular correlacoes por municipio e por UF (Pearson/Spearman) e salvar tabelas de ranking.
6. Treinar modelo final com validacao temporal em blocos e avaliacao por recorte geografico.

## Pergunta 2: Existem mais atributos do INMET que podem enriquecer o modelo?

Sim. A base usada no script atual contem 7 variaveis nucleares (temperatura, chuva, umidade, pressao e vento), mas o INMET permite extrair mais sinais relevantes para dengue.

### Atributos adicionais recomendados

- Umidade minima e maxima diaria/semanal.
- Ponto de orvalho (medio/min/max).
- Radiacao global e insolacao.
- Evaporacao/evapotranspiracao (quando disponivel).
- Rajada maxima de vento e direcao predominante do vento.
- Indicadores de extremos climaticos:
  - dias com chuva acima de limiar (ex.: >= 10 mm),
  - sequencia de dias secos,
  - numero de dias com temperatura acima de limiar biologico.
- Interacoes climaticas:
  - amplitude termica (`temp_max - temp_min`),
  - chuva acumulada x temperatura media,
  - temperatura x umidade.

### Prioridade pratica

Para o proximo ciclo de engenharia de atributos, priorizar:

1. umidade minima/maxima,
2. ponto de orvalho,
3. radiacao/insolacao,
4. indicadores de extremos (dias de chuva intensa e sequencia seca).

Esses atributos costumam melhorar a capacidade de capturar condicoes favoraveis a reproducao do vetor com defasagem temporal.
 
### Status de implementacao deste ciclo

O pipeline em [scripts/cluster_inmet_attributes.py](../scripts/cluster_inmet_attributes.py) foi atualizado para incluir:

- suporte a umidade minima/maxima quando essas colunas existirem na base;
- calculo de ponto de orvalho medio semanal (com fallback por formula de Magnus-Tetens quando nao houver coluna explicita);
- suporte a radiacao media e insolacao acumulada quando disponiveis;
- indicadores de extremos climaticos:
  - quantidade semanal de dias com chuva intensa (`rain >= 10 mm`),
  - maior sequencia semanal de dias secos (`rain <= 1 mm`).

Tambem foram adicionadas medias moveis e lags para esses novos atributos, mantendo compatibilidade com bases antigas que nao tenham todas as colunas opcionais.

## Algoritmo de clusterizacao selecionado

Implementado em [scripts/cluster_inmet_attributes.py](../scripts/cluster_inmet_attributes.py).

### Etapas

1. Leitura da base diaria consolidada.
2. Agregacao semanal.
3. Expansao de atributos (lags, medias moveis, acumulados e amplitude termica).
4. Padronizacao (`StandardScaler`).
5. Matriz de correlacao absoluta entre atributos.
6. Distancia por `1 - |corr|`.
7. Clusterizacao hierarquica (`linkage` metodo `average`).
8. Corte por limiar de distancia (`distance_threshold`).
9. Escolha de representantes por score de prioridade e balanceamento por familia de variaveis.

## Criterios de escolha dos representantes

- Reducao de redundancia: evitar manter variaveis altamente correlacionadas no mesmo cluster.
- Prioridade epidemiologica: precipitação, umidade e temperatura com maior peso.
- Janela temporal: valorizar lags curtos e intermediarios (2, 4, 8 semanas).
- Balanceamento por familia: garantir cobertura minima de precipitacao, temperatura, umidade, radiacao (quando disponivel), pressao e vento.

## Resultado atual da selecao

Com os artefatos atuais em [data_processed/inmet_feature_selection](../data_processed/inmet_feature_selection):

- 10 clusters climaticos identificados.
- 7 atributos recomendados:
  - `rain_heavy_days_lag2`
  - `rain_heavy_days_lag4`
  - `humidity_mean_lag2`
  - `temp_mean_lag2`
  - `temp_mean_lag4`
  - `pressure_lag2`
  - `wind_speed_lag2`

Observacao: nesta execucao, os atributos de radiacao/insolacao nao foram selecionados porque nao estavam presentes na base de entrada utilizada (`data_processed/inmet_2022_2024.csv`). O pipeline ja esta preparado para incorporá-los automaticamente quando essas colunas estiverem disponiveis.

Arquivos de suporte:

- [data_processed/inmet_feature_selection/clusters_inmet.csv](../data_processed/inmet_feature_selection/clusters_inmet.csv)
- [data_processed/inmet_feature_selection/selected_features_inmet.csv](../data_processed/inmet_feature_selection/selected_features_inmet.csv)
- [data_processed/inmet_feature_selection/report.md](../data_processed/inmet_feature_selection/report.md)

## Como usar no modelo final

1. Montar painel final por (`ibge_mun`, `iso_year`, `iso_week`) com casos SINAN + clima INMET.
2. Incluir os 7 atributos selecionados como base exogena.
3. Acrescentar incrementalmente os atributos adicionais sugeridos e repetir a selecao por clusterizacao.
4. Treinar modelos candidatos (SARIMAX, XGBoost, LSTM temporal) com validacao temporal.
5. Reportar metricas globais e por UF/municipio para detectar ganho real de generalizacao.

## Riscos e controles

- Risco de cobertura desigual de estacoes por municipio.
  - Controle: usar `n_stations` como atributo de qualidade e filtro minimo.
- Risco de leak temporal em engenharia de atributos.
  - Controle: gerar lags somente com historico disponivel ate a semana t-1.
- Risco de confundimento espacial.
  - Controle: avaliar desempenho por estratos regionais e incluir efeitos fixos por UF/municipio, se necessario.

## Conclusao

A correlacao espacial entre clima e dengue e tecnicamente viavel e deve usar `ibge_mun` como chave principal. O pipeline de clusterizacao atual e adequado para reduzir colinearidade, e o proximo ganho esperado esta na ampliacao de atributos climaticos (principalmente umidade detalhada, ponto de orvalho, radiacao e extremos), sempre com validacao temporal e recorte geografico.
