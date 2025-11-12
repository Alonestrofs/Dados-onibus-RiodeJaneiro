import csv

sou = ['379', '383', '389', 'SP389', 'SV391', '394', '395', '731', 'SN731', '737', '741', '743', '745', '746', '753', '754', '756', '757', '764', '765', 'SV777', '790', 'SN790', 'SV790', '791', '794', 'SN794', '812', '926', '936', '841', 'SV853']

paranapuan = ['323', '327', '328', '634', '635', 'SP635', '901', 'SV901', '910', '913', '915', '922', 'SV922', '2342', 'SV2342']

pavunense = ['296', '298', 'SN298', '342', 'SR342', '384', 'SV384', 'SR384', '385', '386', 'SR386', '399', 'SR399', '687', '688', '779', 'SN779', '780', '793', 'SP795', '945', '946', '2305', '2399',
 '254', '265', 'SP265', '277', '292', '311', '349', '456', '457', '627', '650', '665', 'SVA665', 'SVB665', '799', '979']

with open('viacoes.csv', 'r') as f:
    reader = csv.reader(f)
    viacoes = list(reader)

def achar_viacao_sem_linha(prefixo):
    if prefixo[0] == 'E':
        return prefixo, 'CMTC / Mobi Rio'
    if prefixo[0] in 'ABCD' and len(prefixo) == 6:
        d = int(prefixo[3])
        if d >= 5:
            consulta = prefixo[1:3] + '500'
            consulta2 = prefixo[1:3] + '000'
        else:
            consulta = prefixo[1:3] + '000'
            consulta2 = prefixo[1:3] + '500'

        for v in viacoes:
            if v[0] == consulta:
                return consulta, v[1]

        for v in viacoes:
            if v[0] == consulta2:
                return consulta2, v[1]

        print('Desconhecido:', prefixo)
        return consulta, f'Empresa Desconhecida ({prefixo})'

    print('Desconhecido:', prefixo)
    return prefixo, f'Empresa Desconhecida ({prefixo})'

def achar_viacao(linha, prefixo):
    consulta, v = achar_viacao_sem_linha(prefixo)
    if consulta == '32500':
        if linha in paranapuan:
            return achar_viacao_sem_linha('B10000')[1]
    elif consulta in ['13000', '30000']:
        if linha in sou:
            return achar_viacao_sem_linha('B33000')[1]

    return v
        


