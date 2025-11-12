Análise de Dados dos Ônibus do Rio de Janeiro

Este repositório contém uma pipeline de scripts em Python para coletar, processar e analisar dados de performance dos ônibus da cidade do Rio de Janeiro, utilizando dados públicos da API Data.Rio (SPPO) e feeds GTFS.

Estrutura do Repositório

O projeto é organizado em pastas que separam as etapas da pipeline de dados:

/gtfs/: Contém os arquivos estáticos do feed GTFS (routes.txt, stops.txt, etc.), usados como base para mapeamento.

/data_inputs/: Contém arquivos de dados manuais ou auxiliares que servem de input para os scripts (ex: mapeamento de viações, equivalências de linhas).

/src/: Contém o código-fonte principal da pipeline de ETL (Extração, Transformação e Carga). Os scripts são numerados na ordem de execução.

/analysis/: Contém scripts de análise exploratória (EDA) e geração de relatórios, que consomem os dados processados pela pipeline src/.

/reports/: Contém os relatórios finais gerados pelos scripts de análise (ex: analise_viagens.txt).

/tools/: Contém scripts utilitários para monitoramento e verificação dos dados brutos (ex: verificar_dados_sppo.py).

Requisitos e Instalação

Para executar os scripts deste repositório, é necessário ter o Python 3 instalado e as seguintes bibliotecas.

Você pode instalar todas de uma vez com o seguinte comando:

pip install pandas numpy openpyxl geopy tqdm ijson


Bibliotecas Utilizadas:

pandas: Usada extensivamente para carregar e processar os arquivos GTFS e o CSV final.

numpy: Usada pelo analisar_performance_viagens.py para cálculos estatísticos.

openpyxl: Necessário para que o pandas possa ler os arquivos .xlsx.

geopy: Usada nos scripts src/03_processar_viagens_carro.py e src/04_converter_para_csv.py para calcular distâncias (great_circle).

tqdm: Usada em múltiplos scripts para exibir barras de progresso durante o processamento de dados.

ijson: Usada pelo src/04_converter_para_csv.py para ler o viagens_processadas.json sem carregar tudo na memória.

Análise

Após a pipeline ser executada e o viagens.csv ser gerado, você pode executar os scripts da pasta analysis/.

analysis/analisar_performance_viagens.py

O que faz: Lê o viagens.csv, aplica filtros estatísticos (IQR, etc.) e gera um relatório de performance.

Gera: reports/analise_viagens.txt.