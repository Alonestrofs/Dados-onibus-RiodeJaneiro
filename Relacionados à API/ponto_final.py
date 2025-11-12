import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def pontos_finais(route_name_input):
    """
    Encontra os dois pontos terminais de uma linha de ônibus com base no seu 'route_short_name' (ou 'route_desc' como fallback).
    Trabalha com arquivos GTFS presentes na raiz do conjunto de dados (stops.txt, stop_times.txt, trips.txt, routes.txt).
    Retorno: lista de coordenadas (lat, lon) dos terminais encontrados (uma entrada por direção encontrada).
    """
    try:
        # Lê os arquivos GTFS esperados no workspace.
        # Esses arquivos fazem parte do dataset "Dados-onibus-RiodeJaneiro".
        stops_df = pd.read_csv("stops.txt")
        stop_times_df = pd.read_csv("stop_times.txt")
        trips_df = pd.read_csv("trips.txt")
        routes_df = pd.read_csv("routes.txt")
    except FileNotFoundError as e:
        print(f"Erro 1º Arquivo não encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro ao ler os arquivos: {e}")
        return

    try:
        # Tenta localizar a rota pelo campo route_short_name (ex.: número da linha).
        route_info = routes_df[routes_df['route_short_name'].astype(str) == str(route_name_input)]

        # Se não encontrou por short_name, tenta pelo campo route_desc (descrição textual).
        if route_info.empty:
            route_info = routes_df[routes_df['route_desc'].astype(str) == str(route_name_input)]
        
        # Se ainda não encontrou, retorna sem erro (linha não cadastrada).
        if route_info.empty:
            return

        # Usa o primeiro match para route_id.
        my_route_id = route_info.iloc[0]['route_id']

        # Filtra viagens (trips) que pertencem à rota encontrada.
        viagens_da_linha = trips_df[trips_df['route_id'] == my_route_id]

        if viagens_da_linha.empty:
            print(f"Erro 3º nenhuma viagem encontrada para o route_id {my_route_id}.")
            return

        # Separa viagens por direção (direction_id típicos: 0 e 1 em GTFS).
        viagens_dir_0 = viagens_da_linha[viagens_da_linha['direction_id'] == 0]
        viagens_dir_1 = viagens_da_linha[viagens_da_linha['direction_id'] == 1]

        terminais = {}

        # Para cada direção encontrada, obtém um exemplo de viagem e extrai sua primeira parada
        # Observação: o código assume que a primeira parada (menor stop_sequence) corresponde ao terminal daquela direção.
        for direction_label, trips_in_direction in [("Direção 0", viagens_dir_0), ("Direção 1", viagens_dir_1)]:
            
            if trips_in_direction.empty:
                # Não há viagens registradas nessa direção — pula.
                continue

            sample_trip = trips_in_direction.iloc[0]
            sample_trip_id = sample_trip['trip_id']
            
            # Extrai stop_times da viagem de amostra.
            trip_stops = stop_times_df[stop_times_df['trip_id'] == sample_trip_id]

            if trip_stops.empty:
                # Viagem sem registros em stop_times.txt — informa e segue para próxima direção.
                print(f"Viagem {sample_trip_id} (para {direction_label}) não tem paradas em stop_times.txt.")
                continue

            # Ordena por stop_sequence para garantir que a primeira linha corresponda ao início da viagem.
            trip_stops_sorted = trip_stops.sort_values('stop_sequence', ascending=True).copy()
            
            # Pega a primeira parada (terminal presumido para esta direção).
            first_stop_entry = trip_stops_sorted.iloc[0]
            first_stop_id = first_stop_entry['stop_id']

            # Busca os detalhes da parada em stops.txt (nome, latitude, longitude).
            terminal_stop_info = stops_df[stops_df['stop_id'] == first_stop_id]

            if terminal_stop_info.empty:
                print(f"Não foi possível encontrar os detalhes da parada {first_stop_id} em stops.txt.")
                continue

            stop_details = terminal_stop_info.iloc[0]
            terminais[direction_label] = {
                'nome': stop_details['stop_name'],
                'lat': stop_details['stop_lat'],
                'lon': stop_details['stop_lon'],
                'headsign_destino': sample_trip.get('trip_headsign', 'N/A')
            }

        if not terminais:
            print("Não foi possível encontrar nenhum ponto terminal para esta linha.")
            return

        ret = []
        for direction, details in terminais.items():
            ret.append((details['lat'], details['lon']))
        return ret

    except (IndexError, KeyError) as e:
        print(f"Erro ao processar os dados.")
        print(f"Detalhe do erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


