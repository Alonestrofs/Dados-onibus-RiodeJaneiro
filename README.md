# 🚌 Análise de Dados dos Ônibus do Rio de Janeiro

Este repositório contém uma **pipeline completa em Python** para **coletar, processar e analisar dados de performance dos ônibus** da cidade do **Rio de Janeiro**, utilizando informações públicas da **API Data.Rio (SPPO)** e **feeds GTFS**.

---

## 📁 Estrutura do Repositório

A organização segue uma arquitetura modular, separando claramente as etapas da pipeline de dados:

```
.
├── gtfs/           # Arquivos estáticos do feed GTFS (routes.txt, stops.txt, etc.)
├── data_inputs/    # Arquivos manuais ou auxiliares (ex: mapeamentos, equivalências de linhas)
├── src/            # Código-fonte principal da pipeline ETL (Extração, Transformação e Carga)
├── analysis/       # Scripts de análise exploratória e geração de relatórios
├── reports/        # Relatórios finais gerados após a análise (ex: analise_viagens.txt)
└── tools/          # Scripts utilitários para verificação e monitoramento dos dados brutos
```

---

## ⚙️ Requisitos e Instalação

### 🐍 Pré-requisitos

* Python 3.8 ou superior
* Acesso à API, caso queira apenas usar o codigo para extrair a API

### 📦 Instalação das Dependências

Instale todas as bibliotecas necessárias com um único comando:

```bash
pip install pandas numpy openpyxl geopy tqdm ijson
```

---

## 📚 Bibliotecas Utilizadas

| Biblioteca   | Função Principal                                           |
| ------------ | ---------------------------------------------------------- |
| **pandas**   | Manipulação e processamento de dados tabulares (GTFS, CSV) |
| **numpy**    | Cálculos estatísticos e numéricos (análise de performance) |
| **openpyxl** | Leitura e escrita de planilhas `.xlsx` pelo pandas         |
| **geopy**    | Cálculo de distâncias geográficas (great-circle)           |
| **tqdm**     | Exibição de barras de progresso durante o processamento    |
| **ijson**    | Leitura eficiente de grandes arquivos JSON em streaming    |

---

## 🔄 Pipeline de Dados (ETL)

A pipeline é composta por scripts numerados localizados em `/src/`, representando as etapas clássicas de **Extração**, **Transformação** e **Carga**:

1. **Extração**
   Coleta dados do feed GTFS e da API SPPO.

2. **Transformação**
   Processa, filtra e cruza as informações das viagens e veículos.

3. **Carga**
   Gera o arquivo consolidado `viagens.csv` com os dados limpos e prontos para análise.

---

## 📊 Análise de Performance

Após a execução completa da pipeline, o arquivo final `viagens.csv` é gerado na pasta raiz ou em `/data_outputs/`.

### ▶️ Execução da Análise

Use o script principal da pasta `analysis/`:

```bash
python analysis/analisar_performance_viagens.py
```

### 🔍 O que ele faz

* Lê o arquivo `viagens.csv`
* Aplica filtros estatísticos (como **IQR** para outliers)
* Calcula métricas de desempenho por linha, empresa e horário
* Gera um relatório detalhado de performance

### 📁 Saída

O resultado é salvo em:

```
reports/analise_viagens.txt
```

---

## 🧰 Ferramentas Auxiliares

A pasta `/tools/` contém utilitários de suporte, como:

* `verificar_dados_sppo.py`: Verifica a integridade e consistência dos dados brutos obtidos da API SPPO.
* Scripts adicionais para depuração e monitoramento dos feeds GTFS.

---

## 🚀 Próximos Passos

* Implementar visualizações gráficas com **Matplotlib** ou **Plotly**
* Automatizar a atualização dos dados via **cron job**
* Publicar dashboards no **Data Studio** ou **Power BI**

---

## 🏙️ Fontes dos Dados

* API Data.Rio – SPPO
* Feed GTFS – Mobilidade Urbana RJ

---
