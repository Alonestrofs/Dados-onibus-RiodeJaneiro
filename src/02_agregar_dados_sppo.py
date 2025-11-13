from pathlib import Path
import json
from tqdm import tqdm

dir = Path('sppo')

# Cria matriz para armazenar arquivos por dia e hora
dias = [[None for _ in range(0, 24)] for _ in range(0, 7)]

# Preenche a matriz dias com os arquivos correspondentes a cada dia/hora
for i in dir.iterdir():
    mes = int(str(i)[20:22])
    dia = int(str(i)[23:25])
    if mes != 11 or dia > 7:
        continue
    
    hora = int(str(i)[26:28])

    dias[dia - 1][hora] = i

# Para cada consórcio, agrega dados dos carros
for consorcio in tqdm(['A', 'B', 'C', 'D', 'E'], desc='Consórcio', position=0):
    carros = {}

    # Itera sobre dias e horas disponíveis
    for dia in tqdm(range(1, 8), desc="Dias", position=1, leave=False):
        for hora in tqdm(range(0, 24), desc='Horas do Dia', position=2, leave=False):
            with open(dias[dia - 1][hora], 'r') as f:
                dados = json.load(f)
            for i in dados:
                # Filtra por consórcio usando a primeira letra da ordem
                if i['ordem'][0] == consorcio:
                    if not i['ordem'] in carros:
                        carros[i['ordem']] = []
                    carros[i['ordem']].append({
                        'latitude': i['latitude'],
                        'longitude': i['longitude'],
                        'linha': i['linha'],
                        'datahora': i['datahora'],
                    })

    # Salva os dados agregados de cada carro em arquivos separados
    for carro, d in tqdm(carros.items(), desc='Carros', leave=False):
        d.sort(key=lambda x: x['datahora'])  # Ordena por data/hora
        with open(f'carros/{carro}.json', 'w') as f:
            json.dump(d, f)

