# Como Executar o Notebook SARIMA

Guia passo a passo para configurar o ambiente virtual e executar o notebook de análise de dengue com SARIMA.

## Pré-requisitos

- Python 3.8 ou superior instalado
- pip (gerenciador de pacotes do Python)
- Git (opcional, para clonar o repositório)
- Leia o arquivo SARIMA_README.md para entender os detalhes do modelo e análise

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
# Use o arquivo requirements_sarima.txt
pip install -r requirements_sarima.txt
```

**Pacotes que serão instalados:**
- `pandas` - Manipulação de dados
- `numpy` - Computação numérica
- `matplotlib` - Visualização de gráficos
- `seaborn` - Visualização avançada
- `statsmodels` - Modelo SARIMA/SARIMAX
- `scikit-learn` - Ferramentas de ML (métricas)
- `scipy` - Testes estatísticos
- `joblib` - Serialização de objetos

A instalação pode levar alguns minutos na primeira vez.

---

## 3. Executar o Jupyter Notebook

### Opção A: Via Linha de Comando (Recomendado)

```bash
# Entre no diretório notebooks
cd notebooks/examples

# Inicie o Jupyter Notebook
jupyter notebook 03_sarima_model_educativo.ipynb
```

Isso abrirá o navegador automaticamente na URL `http://localhost:8888`.

### Opção B: Via VS Code

Se estiver usando VS Code com a extensão Jupyter:

1. Abra o arquivo `03_sarima_model_educativo.ipynb` no VS Code
2. Clique em "Select Kernel" no canto superior direito
3. Escolha `./venv/Scripts/python.exe` (Windows) ou `./venv/bin/python` (Linux/macOS)
4. Execute as células com Shift+Enter

---

## 4. Estrutura do Projeto

```
TCC1/
├── RUN_SARIMA_MODEL.md                   # Este arquivo
├── SARIMA_README.md                      # Documentação do modelo
├── requirements_sarima.txt               # Dependências
│
├── notebooks/examples/
│   ├── 03_sarima_model_educativo.ipynb   # Notebook da análise
│   └── 02_xgboost_model_educativo.ipynb  # Notebook XGBoost (comparação)
│
├── data_processed/
│   ├── dataset_unificado.csv
│   └── ...
│
├── models/
│   └── sarima_brasilia.pkl
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
python -c "import statsmodels; import pandas; import sklearn; print('✅ Todas as bibliotecas instaladas com sucesso!')"
```

---

## 6. Desativar o Ambiente Virtual

Quando terminar, desative o ambiente virtual com:

```bash
# Windows e Linux/macOS
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

### Problema: Erro ao instalar statsmodels

Se statsmodels falhar na instalação:

**Windows:**
```bash
pip install --upgrade setuptools wheel
pip install -r requirements_sarima.txt
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-dev build-essential gfortran
pip install -r requirements_sarima.txt
```

**macOS:**
```bash
brew install gcc
pip install -r requirements_sarima.txt
```

### Problema: "ConvergenceWarning" durante treinamento do SARIMA

**Solução:** Aumente o número máximo de iterações:
```python
resultado = modelo.fit(maxiter=500, disp=False)
```

### Problema: Jupyter não encontrado

**Solução:** Instale Jupyter separadamente:
```bash
pip install jupyter jupyterlab
```

### Problema: Porta 8888 já está em uso

**Solução:** Use uma porta diferente:
```bash
jupyter notebook --port 8889 03_sarima_model_educativo.ipynb
```

---

## 8. Conteúdo do Notebook

O notebook `03_sarima_model_educativo.ipynb` contém:

1. **Fundamentos Teóricos**
   - Séries temporais e estacionariedade
   - Componentes AR, I, MA
   - Extensão sazonal (SARIMA)
   - SARIMAX com variáveis exógenas

2. **Análise Exploratória**
   - Decomposição STL da série
   - Testes de estacionariedade (ADF, KPSS)
   - Gráficos ACF e PACF

3. **Preparação de Dados**
   - Carregamento e exploração
   - Limpeza e tratamento de outliers
   - Split temporal sem vazamento

4. **Modelagem**
   - Seleção automática de parâmetros (Grid AIC/BIC)
   - Treinamento SARIMA e SARIMAX
   - Diagnóstico de resíduos

5. **Avaliação**
   - Cálculo de métricas (RMSE, MAE, R²)
   - Visualização de predições com intervalos de confiança
   - Testes estatísticos (Ljung-Box, Jarque-Bera)

6. **Escalabilidade**
   - Classe modular `ModeloPreditoSARIMA`
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

1. Compare métricas com o modelo XGBoost
2. Experimente diferentes ordens (p,d,q)(P,D,Q,s)
3. Teste em outros municípios
4. Implemente validação walk-forward
5. Combine SARIMA + XGBoost em ensemble

---

## 11. Referências

- [statsmodels SARIMAX](https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html)
- [Forecasting: Principles and Practice](https://otexts.com/fpp3/)
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

**Última atualização:** 02 de abril de 2026
