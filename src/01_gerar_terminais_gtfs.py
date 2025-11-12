import pandas as pd
import warnings
import json
import time
from tqdm import tqdm

def analisar_terminais_da_linha(route_name, routes_df, trips_df, stop_times_df, stops_df):
    """
    Função interna que analisa uma única linha.
    
    Retorna:
        - Uma lista de listas com coordenadas (ex: [[lat1, lon1], [lat2, lon2]])
        - Uma lista vazia [] se a linha não for encontrada ou der erro.
    """
    
    # Lista para armazenar as coordenadas [[lat, lon], [lat, lon]]
    coordenadas_terminais = []
    
    try:
        # 1. Encontrar o route_id
        route_info = routes_df[routes_df['route_short_name'].astype(str) == str(route_name)]
        if route_info.empty:
            route_info = routes_df[routes_df['route_desc'].astype(str) == str(route_name)]
        
        if route_info.empty:
            return []  # <--- Retorna lista vazia se não achar a rota

        my_route_id = route_info.iloc[0]['route_id']
        
        # 2. Encontrar viagens
        viagens_da_linha = trips_df[trips_df['route_id'] == my_route_id]
        if viagens_da_linha.empty:
            return []  # <--- Retorna lista vazia se não achar viagens

        viagens_dir_0 = viagens_da_linha[viagens_da_linha['direction_id'] == 0]
        viagens_dir_1 = viagens_da_linha[viagens_da_linha['direction_id'] == 1]

        # 3. Processar cada direção
        for trips_in_direction in [viagens_dir_0, viagens_dir_1]:
            
            if trips_in_direction.empty:
                continue 

            sample_trip = trips_in_direction.iloc[0]
            sample_trip_id = sample_trip['trip_id']
            
            trip_stops = stop_times_df[stop_times_df['trip_id'] == sample_trip_id]
            if trip_stops.empty:
                continue

            # Encontra a *primeira* parada (menor stop_sequence)
            trip_stops_sorted = trip_stops.sort_values('stop_sequence', ascending=True)
            first_stop_entry = trip_stops_sorted.iloc[0]
            first_stop_id = first_stop_entry['stop_id']
            
            terminal_stop_info = stops_df[stops_df['stop_id'] == first_stop_id]
            if terminal_stop_info.empty:
                continue

            stop_details = terminal_stop_info.iloc[0]
            
            # Adiciona a lista [lat, lon] à lista principal
            coordenadas_terminais.append([
                stop_details['stop_lat'], 
                stop_details['stop_lon']
            ])

        return coordenadas_terminais

    except Exception as e:
        print(f"Erro ao processar a linha {route_name}: {e}")
        return []

def main():
    """
    Função principal para carregar dados, iterar por todas as linhas
    e salvar o resultado em JSON.
    """
    
    # --- 2. Timer iniciado ---
    inicio_script = time.perf_counter()
    
    warnings.simplefilter(action='ignore', category=FutureWarning)
    
    try:
        # 1. Carregar todos os DataFrames UMA VEZ
        print("Carregando arquivos GTFS (pode levar um momento)...")
        stops_df = pd.read_csv("../gtfs/stops.txt", low_memory=False)
        stop_times_df = pd.read_csv("../gtfs/stop_times.txt", low_memory=False)
        trips_df = pd.read_csv("../gtfs/trips.txt", low_memory=False)
        routes_df = pd.read_csv("../gtfs/routes.txt", low_memory=False)
        print("Arquivos carregados com sucesso.")
    
    except FileNotFoundError as e:
        print(f"Erro 1º Arquivo não encontrado.")
        print(f"Verifique se seus arquivos .txt estão dentro de uma pasta chamada 'gtfs'.")
        print(f"Detalhe: {e}")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao ler os arquivos: {e}")
        return

    # 2. Pegar a lista de todas as linhas únicas
    lista_de_linhas = routes_df['route_short_name'].dropna().unique()
    print(f"Encontradas {len(lista_de_linhas)} linhas únicas para analisar.")
    
    # O resultado final será um grande dicionário
    todos_os_resultados = {}

    # 3. Iterar por todas as linhas com uma barra de progresso (tqdm)
    for linha in tqdm(lista_de_linhas, desc="Processando linhas"):
        
        resultado_da_linha = analisar_terminais_da_linha(
            linha, routes_df, trips_df, stop_times_df, stops_df
        )
        
        # Adiciona o resultado ao dicionário principal.
        # Se 'resultado_da_linha' for [], o JSON ficará "linha": []
        todos_os_resultados[linha] = resultado_da_linha

    # 4. Verificar se algum resultado foi gerado
    if not todos_os_resultados:
        print("Processamento concluído, mas nenhum resultado foi gerado.")
        return

    print("\nProcessamento concluído. Gerando JSON...")

    # 5. Salvar em JSON
    output_filename = "terminais_coordenadas.json" # Mudei o nome
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            # indent=2 cria um arquivo "bonito" (formatado)
            # ensure_ascii=False garante que acentos saiam corretos
            json.dump(todos_os_resultados, f, indent=2, ensure_ascii=False)
            
        print(f"Sucesso! Os resultados foram salvos em: {output_filename}")
        
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")

    # --- 3. Timer finalizado e impresso ---
    fim_script = time.perf_counter()
    tempo_total = fim_script - inicio_script
    print("\n" + "="*40)
    print(f"Tempo total de execução: {tempo_total:.2f} segundos")
    print("="*40)


# Executa a função principal quando o script é rodado
if __name__ == "__main__":
    main()