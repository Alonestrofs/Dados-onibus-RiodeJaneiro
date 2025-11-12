from pathlib import Path

dir = Path('sppo')

oct = [0 for _ in range(0, 31)]
nov = [0 for _ in range(0, 30)]

for i in dir.iterdir():
    mes = int(str(i)[20:22])
    dia = int(str(i)[23:25])
    if mes == 10:
        oct[dia - 1] += 1
    elif mes == 11:
        nov[dia - 1] += 1

for i in range(0, 31):
    if oct[i] == 24:
        print('oct', i + 1)
    else:
        print('------------')
    
for i in range(0, 30):
    if nov[i] == 24:
        print('nov', i + 1)
    else:
        print('------------')
