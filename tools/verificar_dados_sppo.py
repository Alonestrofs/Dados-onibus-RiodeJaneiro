from pathlib import Path

dir = Path('sppo')

# Inicializa contadores para cada dia de outubro e novembro
oct = [0 for _ in range(0, 31)]
nov = [0 for _ in range(0, 30)]

# Conta arquivos por dia e mês
for i in dir.iterdir():
    mes = int(str(i)[20:22])
    dia = int(str(i)[23:25])
    if mes == 10:
        oct[dia - 1] += 1
    elif mes == 11:
        nov[dia - 1] += 1

# Verifica se todos os dias de outubro têm 24 arquivos (um por hora)
for i in range(0, 31):
    if oct[i] == 24:
        print('oct', i + 1)
    else:
        print('------------')
    
# Verifica se todos os dias de novembro têm 24 arquivos (um por hora)
for i in range(0, 30):
    if nov[i] == 24:
        print('nov', i + 1)
    else:
        print('------------')
