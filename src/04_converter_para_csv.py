import ijson
from datetime import datetime
from tqdm import tqdm
from geopy.distance import great_circle
import csv
from pegar_viacao import achar_viacao

outputf = 'viagens.csv'

# Cria arquivo CSV de saída e escreve cabeçalho
with open(outputf, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['viacao', 'linha', 'carro', 'kilometragem', 'duracao', 'velocidade media'])

# Lê viagens processadas do JSON e converte para linhas do CSV
with open('viagens_processadas.json', 'r') as f:
    viagens = ijson.items(f, 'item')

    for viagem in tqdm(viagens, desc='Viagens', total=220000):
        # Ignora viagens muito curtas
        if len(viagem[2]) < 20:
            continue

        ii = 5
        kil = 0
        # Calcula quilometragem total da viagem somando trechos
        for i in range(0, len(viagem[2]) - ii, ii):
            d = great_circle(
                (viagem[2][i + ii]['latitude'], viagem[2][i + ii]['longitude']),
                (viagem[2][i]['latitude'], viagem[2][i]['longitude'])
            ).kilometers
            kil += d

        tempotot = viagem[2][-1]['datahora'] - viagem[2][0]['datahora']
        velmed = kil * 3600000 / tempotot

        # Determina a viação a partir da linha e prefixo
        viacao = achar_viacao(viagem[0], viagem[1])

        # Escreve linha no CSV
        with open(outputf, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([viacao, viagem[0], viagem[1], round(kil), round(tempotot / 1000), round(velmed)])

