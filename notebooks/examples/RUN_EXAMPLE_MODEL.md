# Como Executar o Notebook XGBoost

Guia passo a passo para configurar o ambiente virtual e executar o notebook de análise de dengue com XGBoost.

## Pré-requisitos

- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes do Python)
- Git (opcional, para clonar o repositório)
- Leia o arquivo XGBoost_README.md para entender os detalhes do modelo e análise

Verifique a instalação do Python com:
```bash
python --version
```

---

## 1. Criar o Ambiente Virtual

### No Windows (PowerShell ou CMD):

```bash
# Navegue até a pasta do projeto
cd C:\Users\Thiago\Documents\GitHub\TCC1

# Crie o ambiente virtual
python -m venv venv

# Ative o ambiente virtual
venv\Scripts\activate
```

### No Linux/macOS:

```bash
# Navegue até a pasta do projeto
cd ~/GitHub/TCC1

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate
```

Após ativar, você verá `(venv)` no início da linha de comando.

---

## 2. Instalar Dependências

Com o ambiente virtual ativado, instale os pacotes necessários:

```bash
# Use o arquivo requirements_xgboost.txt
pip install -r requirements_xgboost.txt
```

**Pacotes que serão instalados:**
- `pandas` - Manipulação de dados
- `numpy` - Computação numérica
- `matplotlib` - Visualização de gráficos
- `seaborn` - Visualização avançada
- `xgboost` - Modelo de machine learning
- `scikit-learn` - Ferramentas de ML
- `shap` - Interpretabilidade do modelo
- `joblib` - Serialização de objetos

A instalação pode levar alguns minutos na primeira vez.

---

## 3. Executar o Jupyter Notebook

### Opção A: Via Linha de Comando (Recomendado)

```bash
# Entre no diretório notebooks
cd notebooks

# Inicie o Jupyter Notebook
jupyter notebook 02_xgboost_model_educativo.ipynb
```

Isso abrirá o navegador automaticamente na URL `http://localhost:8888`.

### Opção B: Via VS Code

Se estiver usando VS Code com a extensão Jupyter:

1. Abra o arquivo `02_xgboost_model_educativo.ipynb` no VS Code
2. Clique em "Select Kernel" no canto superior direito
3. Escolha `./venv/Scripts/python.exe` (Windows) ou `./venv/bin/python` (Linux/macOS)
4. Execute as células com Shift+Enter

---

## 4. Estrutura do Projeto

```
TCC1/
├── HOW_TO_RUN.md                          # Este arquivo
├── README.md                              # Descritores gerais
├── requirements_xgboost.txt               # Dependências
├── requirements.txt                       # Alternativo
├── run_pipeline.py                        # Script principal
│
├── notebooks/
│   ├── 02_xgboost_model_educativo.ipynb  # Notebook da análise
│   └── 01_analise_dados_inmet.ipynb
│
├── scripts/
│   ├── download_data.py
│   ├── process_data.py
│   ├── xgboost_model.py
│   └── ...
│
├── data_processed/
│   ├── dataset_unificado.csv
│   ├── inmet_sinan_merged.csv
│   └── ...
│
├── models/
│   └── train_sarima.py
│
└── venv/                                  # Ambiente virtual (criado automaticamente)
    ├── Scripts/                           # Windows
    ├── bin/                               # Linux/macOS
    └── lib/
```

---

## 5. Verificar Instalação

Para verificar se tudo foi instalado corretamente, execute no ambiente virtual:

```bash
python -c "import xgboost; import shap; import pandas; print('✅ Todas as bibliotecas instaladas com sucesso!')"
```

---

## 6. Desativar o Ambiente Virtual

Quando terminar, desative o ambiente virtual com:

```bash
# Windows
deactivate

# Linux/macOS
deactivate
```

---

## 7. Troubleshooting

### Problema: "python: command not found" (Linux/macOS)

**Solução:** Use `python3` em vez de `python`:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Problema: Erro ao instalar SHAP

Se SHAP falhar na instalação, instale dependências de compilação primeiro:

**Windows:**
```bash
# Instale Visual Studio Build Tools
# Ou use o Python com pre-compiled wheels
pip install --upgrade setuptools wheel
pip install -r requirements_xgboost.txt
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev build-essential
pip install -r requirements_xgboost.txt
```

**macOS:**
```bash
brew install gcc
pip install -r requirements_xgboost.txt
```

### Problema: Jupyter não encontrado

**Solução:** Instale Jupyter separadamente:
```bash
pip install jupyter jupyterlab
```

### Problema: Porta 8888 já está em uso

**Solução:** Use uma porta diferente:
```bash
jupyter notebook --port 8889 02_xgboost_model_educativo.ipynb
```

---

## 8. Conteúdo do Notebook

O notebook `02_xgboost_model_educativo.ipynb` contém:

1. **Fundamentos Teóricos**
   - Árvores de decisão para regressão
   - Conceito de boosting sequencial
   - XGBoost vs. outros algoritmos

2. **Preparação de Dados**
   - Carregamento e exploração
   - Limpeza e tratamento de outliers
   - Engenharia de features com lags temporais

3. **Modelagem**
   - Split temporal (train/val/test)
   - Treinamento do XGBoost
   - Otimização de hiperparâmetros

4. **Avaliação**
   - Cálculo de métricas (RMSE, MAE, R²)
   - Visualização de predições
   - Análise de importância de features com SHAP

5. **Escalabilidade**
   - Classe modular `ModeloPreditoXGBoost`
   - Aplicação a múltiplos municípios

---

## 9. Dataset

O notebook utiliza o arquivo:
- `data_processed/dataset_unificado.csv`

Que contém dados de:
- **Período:** 2022-2024
- **Localidade:** Brasília/DF
- **Granularidade:** Semanal (semana epidemiológica)
- **Variáveis:** Casos de dengue, precipitação, temperatura, umidade, pressão

---

## 10. Próximos Passos

Após executar o notebook com sucesso:

1. Explore diferentes hiperparâmetros
2. Compare com outros modelos (SARIMA, Prophet)
3. Teste em outros municípios
4. Implemente validação walk-forward
5. Crie um sistema de alertas

---

## 11. Referências

- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Scikit-learn Guide](https://scikit-learn.org/)
- [Matplotlib & Seaborn](https://matplotlib.org/)

---

## Suporte

Se encontrar problemas:

1. Verifique se está no ambiente virtual ativado: `(venv)` deve aparecer no terminal
2. Atualize pip: `pip install --upgrade pip`
3. Limpe cache: `pip cache purge`
4. Recrie o ambiente se necessário:
   ```bash
   deactivate
   rmdir /s venv  (Windows) ou rm -rf venv (Linux/macOS)
   python -m venv venv
   # Reative e instale de novo
   ```

---

**Última atualização:** 25 de março de 2026

