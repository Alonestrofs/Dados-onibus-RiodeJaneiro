from pathlib import Path
import json
from datetime import datetime
from geopy.distance import great_circle
from tqdm import tqdm
import statistics

distponto = 0.5

with open('equivalencias.json', 'r') as f:
    equivalencias = json.load(f)

def outronome(n):
    for eq in equivalencias:
        if n == eq[0]:
            return eq[1]
        if n == eq[1]:
            return eq[0]
    return n

def verdnome(n):
    if n[:4] == 'LECD':
        return outronome(n)
    return n

with open('terminais_coordenadas.json', 'r') as f:
    pontos_finais = json.load(f)

def analisar_carro(carro, prefixo):
    llat = float(carro[0]['latitude'].replace(',', '.'))
    llon = float(carro[0]['longitude'].replace(',', '.'))
    lt = int(carro[0]['datahora'])
    llinha = carro[0]['linha']

    if llinha in pontos_finais:
        pf = pontos_finais[llinha]
    elif outronome(llinha) in pontos_finais:
        pf = pontos_finais[outronome(llinha)]
    else:
        pf = []

    viagens = []
    
    viagem = []

    for i in tqdm(carro, desc='Registros', position=1, leave=False):
        lat = float(i['latitude'].replace(',', '.'))
        lon = float(i['longitude'].replace(',', '.'))
        t = int(i['datahora'])

        dist = great_circle((llat, llon), (lat, lon)).kilometers
        if t != lt:
            vel = dist * 3600000 / (t - lt)
        else:
            vel = 0.0
        if vel < 2 or vel > 200:
            vel = 0.0



        if i['linha'] != llinha:
            if i['linha'] in pontos_finais:
                pf = pontos_finais[i['linha']]
            elif outronome(i['linha']) in pontos_finais:
                pf = pontos_finais[outronome(i['linha'])]
            else:
                pf = []

        d_pontos = []
        for p in pf:
            d_pontos.append(great_circle(p, (lat, lon)).kilometers)

        if len(d_pontos) == 0:
            mindist = 0.0
        else:
            mindist = min(d_pontos)

        if len(viagem) > 0 and ((vel == 0.0 and mindist < distponto) or len(d_pontos) == 0):
            viagens.append((verdnome(llinha), prefixo, viagem))
            viagem = []

        if len(viagem) > 0 or (vel > 0.0 and mindist > distponto):
            viagem.append({
                'datahora': int(i['datahora']),
                'latitude': float(i['latitude'].replace(',', '.')),
                'longitude': float(i['longitude'].replace(',', '.')),
                'vel': vel,
            })

        #print(
        #    i['linha'],
        #    vel,
        #    d_pontos,
        #    datetime.fromtimestamp(int(i['datahora']) / 1000).strftime("%Y-%m-%d %H:%M:%S")
        #)

        llat, llon = lat, lon
        lt = t
        llinha = i['linha']

    
    # Deixamos a última viagem fora do array e removemos a primeira
    return viagens[1:]

def duracao_viagem(v):
    t0 = v[2][0]['datahora']
    tn = v[2][-1]['datahora']

    return tn - t0

def dist_viagem(v):
    s0 = (v[2][0]['latitude'], v[2][0]['longitude'])
    sn = (v[2][-1]['latitude'], v[2][-1]['longitude'])

    return great_circle(s0, sn).kilometers

def resumo_viagem(v):
    return (v[0], v[1], duracao_viagem(v), dist_viagem(v))
    
def dados_linhas(resumos):
    linhas = {}
    for i in resumos:
        if not i[0] in linhas:
            linhas[i[0]] = ()

    for linha in tqdm(linhas.keys(), desc='Linhas'):
        tempos = [r[2] for r in resumos if r[0] == linha]
        dists = [r[3] for r in resumos if r[0] == linha]

        t_qs = statistics.quantiles(tempos, n=4)
        d_qs = statistics.quantiles(dists, n=4)

        t_r = (t_qs[0] - (0.5 * (t_qs[2] - t_qs[0])), t_qs[2] + (0.5 * (t_qs[2] - t_qs[0])))
        d_r = (d_qs[0] - (0.3 * (d_qs[2] - d_qs[0])), d_qs[2] + (0.3 * (d_qs[2] - d_qs[0])))

        linhas[linha] = (t_r, d_r)
    
    return linhas

def filtrar_viagens(viagens, resumos, d_linhas):
    ret = []
    for i in range(len(viagens)):
        t_r, d_r = d_linhas[resumos[i][0]]
        if resumos[i][2] > t_r[0] and resumos[i][2] < t_r[1] and resumos[i][3] > d_r[0] and resumos[i][3] < d_r[1]:
            ret.append(viagens[i])
    return ret


dir = Path('carros')
prefixos = [str(i) for i in dir.iterdir()]

resumo_tudo = []

for i in tqdm(prefixos, desc='Carros'):
    prefixo = i[7:][:-5]

    with open(i, 'r') as f:
        viagens = analisar_carro(json.load(f), prefixo)

    resumo_tudo += [resumo_viagem(v) for v in viagens]

d_linhas = dados_linhas(resumo_tudo)

print(d_linhas)

todas_viagens = []

for i in tqdm(prefixos, desc='Carros'):
    prefixo = i[7:][:-5]

    with open(i, 'r') as f:
        viagens = analisar_carro(json.load(f), prefixo)

    resumos = [resumo_viagem(v) for v in viagens]

    todas_viagens += filtrar_viagens(viagens, resumos, d_linhas)

    #for v in viagens:
    #    print('Linha', v[0], 'carro', v[1], 'demorou', duracao_viagem(v) / 60000, 'min e andou', dist_viagem(v))

with open('viagens_processadas.json', 'w') as f:
    json.dump(todas_viagens, f)




