import ijson
from datetime import datetime
from tqdm import tqdm
from geopy.distance import great_circle
import csv
from pegar_viacao import achar_viacao

outputf = 'viagens.csv'

with open(outputf, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['viacao', 'linha', 'carro', 'kilometragem', 'duracao', 'velocidade media'])

with open('viagens_processadas.json', 'r') as f:
    viagens = ijson.items(f, 'item')

    for viagem in tqdm(viagens, desc='Viagens', total=220000):
        if len(viagem[2]) < 20:
            continue

        ii = 5
        kil = 0
        for i in range(0, len(viagem[2]) - ii, ii):
            # t = viagem[2][i + ii]['datahora'] - viagem[2][i]['datahora']
            d = great_circle(
                (viagem[2][i + ii]['latitude'], viagem[2][i + ii]['longitude']),
                (viagem[2][i]['latitude'], viagem[2][i]['longitude'])
            ).kilometers

            #if d * 3600000 / t > velmax:
            #    velmax = d * 3600000 / t

            kil += d

        tempotot = viagem[2][-1]['datahora'] - viagem[2][0]['datahora']
        velmed = kil * 3600000 / tempotot

        viacao = achar_viacao(viagem[0], viagem[1])

        with open(outputf, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([viacao, viagem[0], viagem[1], round(kil), round(tempotot / 1000), round(velmed)])

