import pandas as pd
import json
import time
import warnings

def criar_mapeamento_desc():
    """
    Analisa o 'routes.txt' e cria um mapeamento (lista de listas)
    entre 'route_short_name' e 'route_desc' para todas as linhas
    onde 'route_desc' não é uma string vazia.
    """
    # Inicia timer para medir tempo de execução
    inicio_script = time.perf_counter()
    
    warnings.simplefilter(action='ignore', category=FutureWarning)
    
    output_filename = "mapeamento_route_desc.json"
    
    try:
        # Carrega o arquivo de rotas do GTFS
        print("Carregando 'gtfs/routes.txt'...")
        # Carregamos tudo como string para evitar problemas de tipo
        routes_df = pd.read_csv("routes.txt", low_memory=False, dtype=str)
        print(f"Total de rotas carregadas: {len(routes_df)}")

    except FileNotFoundError:
        print("Erro: Arquivo 'gtfs/routes.txt' não encontrado.")
        print("Verifique se o arquivo está na subpasta 'gtfs/'.")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo: {e}")
        return

    try:
        # Preenche valores ausentes em 'route_desc' com string vazia
        routes_df['route_desc'] = routes_df['route_desc'].fillna('')

        # Filtra apenas linhas com 'route_desc' preenchido
        mask = (routes_df['route_desc'] != '') & (routes_df['route_desc'] != '""')
        filtered_df = routes_df[mask]

        print(f"Encontradas {len(filtered_df)} rotas com 'route_desc' preenchido.")

        if filtered_df.empty:
            print("Nenhuma rota com 'route_desc' não-vazio foi encontrada.")
            lista_de_mapeamento = []
        else:
            # Seleciona colunas de interesse e converte para lista de listas
            mappings_df = filtered_df[['route_short_name', 'route_desc']]
            lista_de_mapeamento = mappings_df.values.tolist()

        # Salva resultado em arquivo JSON
        print(f"Salvando resultados em '{output_filename}'...")
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(lista_de_mapeamento, f, indent=2, ensure_ascii=False)
        print(f"Sucesso! Mapeamento salvo.")
        
        # Mostra amostra dos primeiros resultados
        if lista_de_mapeamento:
            print(f"\nExemplo dos primeiros 5 itens encontrados:")
            for item in lista_de_mapeamento[:5]:
                print(f"  {item}")

    except Exception as e:
        print(f"Ocorreu um erro durante o processamento: {e}")

    # Finaliza timer e mostra tempo total
    fim_script = time.perf_counter()
    tempo_total = fim_script - inicio_script
    print("\n" + "="*40)
    print(f"Tempo total de execução: {tempo_total:.4f} segundos")
    print("="*40)

# Executa a função principal quando o script é rodado
def main():
    criar_mapeamento_desc()

if __name__ == "__main__":
    main()