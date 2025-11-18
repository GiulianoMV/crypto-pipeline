# ETL para Dados Financeiros

![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Em%20Desenvolvimento-yellow.svg)
![Tests](https://img.shields.io/badge/tests-Pytest-orange.svg)

Pipeline **ETL** desenvolvido em **Python** para **extração, transformação e análise de ativos financeiros**.

---

## Objetivo

Extrair e processar dados de ativos financeiros (ações, ETFs, criptomoedas e similares) via [Yahoo Finance](https://pypi.org/project/yfinance/), aplicar transformações e indicadores técnicos para análise, gerar gráficos e enviar alertas automatizados via **Telegram** e **E-mail** com **recomendações de compra/venda**.

---

## Tecnologias Principais

- **Python 3.11+**
- **Polars** – Manipulação de dados em alta performance
- **yfinance** – Extração de dados do Yahoo Finance
- **PyYAML** – Gerenciamento de configurações *(em desenvolvimento)*
- **matplotlib / plotly** – Visualização de dados
- **pytest** – Testes automatizados *(em desenvolvimento)*
- **Telegram API / SMTP** – Notificações *(em desenvolvimento)*

---

## Estrutura do Projeto
```
finpipe/
│
├── data/
│   ├── raw/ # Dados brutos obtidos da API
│   ├── processed/ # Dados após transformação
│   └── logs/ # Logs de execução
│
├── src/
│   ├── core/ # Extração, transformação e carga
│   ├── notifications/ # Envio de notificações
│   ├── visualization/ # Geração de gráficos e relatórios
│   ├── config/ # Carregamento de configurações YAML
│   └── utils/ # Funções auxiliares e validações
│
├── config/ # Parâmetros de execução e credenciais
│
├── tests/ # Testes unitários e de integração
└── run_pipeline.py # Script principal
```

---

## Funcionalidades implementadas

1. Extração
- Coleta de dados históricos de qualquer ativo disponível via yfinance.
- Normalização e conversão para formato Polars.

2. Transformação
- Cálculo de indicadores técnicos para análise (EMA, RSI, Bandas de Bollinger, etc).
- Criação de colunas derivadas para análise de compra e venda.

3. Visualização
- Plotagem de gráficos com indicadores técnicos.
- Integração futura com relatórios automáticos (gráficos + análises).

4. Notificações (em desenvolvimento)
- Envio automático de relatórios e gráficos via Telegram e E-mail.
- Resumo indicando quais indicadores apontam sinal de compra ou venda.

5. Persistência de dados
- Histórico consolidado via arquivos parquet devido a baixa complexidade de dados.
- Suporte futuro a particionamento de tabelas por ativo.

---

## Como Executar

### Clonar o repositório
```bash
git clone https://github.com/GiulianoMV/finpipe.git
cd finpipe
```

### Criar e ativar o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Executar pipeline
```bash
python run_pipeline.py
```

### Testes
```bash
pytest -v
```

---

## Visualizações e Notificações (planejadas)

O pipeline irá gerar gráficos e enviar relatórios automáticos via Telegram e E-mail, contendo:
- Gráfico de preços com indicadores técnicos;
- Sinalizações de compra/venda com base nos indicadores;
- Resumo textual do status do ativo.

(Uma prévia do gráfico será incluída aqui quando o módulo de visualização estiver completo.)

---

## Roadmap

|Etapa|Descrição|Status|
|---|---|---|
|Extract|Coleta de dados via yfinance|✅ Concluído|
|Transform|Cálculo de indicadores técnicos|✅ Concluído|
|Load|Persistência de dados via parquet|🔄 MVP OK|
|Visualization|Gráficos e relatórios visuais|✅ Concluído|
|Notifications|Envio via Telegram e E-mail|🔄 Em desenvolvimento|
|Testes de integração|Cobertura de pipeline completo|🔜 Planejado|

---
