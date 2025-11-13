from pathlib import Path
import json
from datetime import datetime
from geopy.distance import great_circle
from tqdm import tqdm
import statistics

# Distância máxima para considerar chegada em ponto final (em km)
distponto = 0.5

# Carrega equivalências de nomes de linhas
with open('equivalencias.json', 'r') as f:
    equivalencias = json.load(f)

# Função para obter nome equivalente de linha
def outronome(n):
    for eq in equivalencias:
        if n == eq[0]:
            return eq[1]
        if n == eq[1]:
            return eq[0]
    return n

def verdnome(n):
    # Se for linha especial, retorna nome equivalente
    if n[:4] == 'LECD':
        return outronome(n)
    return n

# Carrega coordenadas dos pontos finais das linhas
with open('terminais_coordenadas.json', 'r') as f:
    pontos_finais = json.load(f)

# Analisa os registros de um carro e segmenta viagens
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
        # Calcula distância e velocidade entre pontos
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

        # Atualiza ponto final se linha mudou
        if i['linha'] != llinha:
            if i['linha'] in pontos_finais:
                pf = pontos_finais[i['linha']]
            elif outronome(i['linha']) in pontos_finais:
                pf = pontos_finais[outronome(i['linha'])]
            else:
                pf = []

        # Calcula distância até pontos finais conhecidos
        d_pontos = []
        for p in pf:
            d_pontos.append(great_circle(p, (lat, lon)).kilometers)

        if len(d_pontos) == 0:
            mindist = 0.0
        else:
            mindist = min(d_pontos)

        # Detecta fim de viagem
        if len(viagem) > 0 and ((vel == 0.0 and mindist < distponto) or len(d_pontos) == 0):
            viagens.append((verdnome(llinha), prefixo, viagem))
            viagem = []

        # Adiciona registro à viagem se válido
        if len(viagem) > 0 or (vel > 0.0 and mindist > distponto):
            viagem.append({
                'datahora': int(i['datahora']),
                'latitude': float(i['latitude'].replace(',', '.')),
                'longitude': float(i['longitude'].replace(',', '.')),
                'vel': vel,
            })

        # Atualiza variáveis para próximo registro
        llat, llon = lat, lon
        lt = t
        llinha = i['linha']

    # Remove primeira e última viagem (artefato do algoritmo)
    return viagens[1:]

# Calcula duração da viagem em milissegundos
def duracao_viagem(v):
    t0 = v[2][0]['datahora']
    tn = v[2][-1]['datahora']

    return tn - t0

# Calcula distância da viagem em km
def dist_viagem(v):
    s0 = (v[2][0]['latitude'], v[2][0]['longitude'])
    sn = (v[2][-1]['latitude'], v[2][-1]['longitude'])

    return great_circle(s0, sn).kilometers

# Gera resumo de cada viagem
def resumo_viagem(v):
    return (v[0], v[1], duracao_viagem(v), dist_viagem(v))
    
def dados_linhas(resumos):
    linhas = {}
    for i in resumos:
        if not i[0] in linhas:
            linhas[i[0]] = ()
    # Calcula intervalos de duração e distância típicos por linha
    for linha in tqdm(linhas.keys(), desc='Linhas'):
        tempos = [r[2] for r in resumos if r[0] == linha]
        dists = [r[3] for r in resumos if r[0] == linha]
        # Usa quartis para definir limites de aceitação
        t_qs = statistics.quantiles(tempos, n=4)
        d_qs = statistics.quantiles(dists, n=4)
        t_r = (t_qs[0] - (0.5 * (t_qs[2] - t_qs[0])), t_qs[2] + (0.5 * (t_qs[2] - t_qs[0])))
        d_r = (d_qs[0] - (0.3 * (d_qs[2] - d_qs[0])), d_qs[2] + (0.3 * (d_qs[2] - d_qs[0])))
        linhas[linha] = (t_r, d_r)
    return linhas

# Filtra viagens fora dos intervalos típicos de cada linha
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

# Percorre todos os arquivos de carros, processa viagens e gera resumos
for i in tqdm(prefixos, desc='Carros'):
    prefixo = i[7:][:-5]

    with open(i, 'r') as f:
        viagens = analisar_carro(json.load(f), prefixo)

    resumo_tudo += [resumo_viagem(v) for v in viagens]

# Calcula intervalos típicos por linha
d_linhas = dados_linhas(resumo_tudo)

print(d_linhas)

todas_viagens = []

# Processa e filtra todas as viagens válidas
for i in tqdm(prefixos, desc='Carros'):
    prefixo = i[7:][:-5]

    with open(i, 'r') as f:
        viagens = analisar_carro(json.load(f), prefixo)

    resumos = [resumo_viagem(v) for v in viagens]

    todas_viagens += filtrar_viagens(viagens, resumos, d_linhas)

    #for v in viagens:
    #    print('Linha', v[0], 'carro', v[1], 'demorou', duracao_viagem(v) / 60000, 'min e andou', dist_viagem(v))

# Salva todas as viagens processadas em arquivo JSON
with open('viagens_processadas.json', 'w') as f:
    json.dump(todas_viagens, f)




