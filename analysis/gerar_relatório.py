"""
Código python para:
- carregar viagens.xlsx ou viagens.csv
- padronizar/renomear colunas
- limpar Velocidade (remover " km/h" e converter)
- converter/limpar Duração para segundos (Duracao_s)
- aplicar filtros básicos
- remover outliers por Linha usando IQR (Quilometragem e Duracao_s)
- gerar relatório analise_viagens.txt com as seções solicitadas
"""

from pathlib import Path
import re
import math
import numpy as np
import pandas as pd
from datetime import timedelta

# --- Configuração / constantes ---
INPUT_FILES = ["viagens.csv", "viagens.xlsx", "viagens.xls"]
OUTPUT_TXT = "analise_viagens2.txt"

# Nomes padrão desejados
STANDARD_COLS = {
    # pode ajustar mapeamentos se a planilha tiver nomes diferentes:
    "Viação": "Viacao",
    "Viacao": "Viacao",
    "Viação ": "Viacao",
    "Linha": "Linha",
    "Carro": "Carro",
    "Quilometragem": "Quilometragem",
    "QuilômetraGem": "Quilometragem",
    "Duração": "Duracao",
    "Duracao": "Duracao",
    "Duracao_s": "Duracao_s",
    "Velocidade Média": "Velocidade_Media",
    "Velocidade Média ": "Velocidade_Media",
    "Velocidade Media": "Velocidade_Media",
    "Velocidade": "Velocidade_Media",
    "Velocidade Média (km/h)": "Velocidade_Media",
    "Velocidade Média_km/h": "Velocidade_Media",
}

def find_input_file():
    for name in INPUT_FILES:
        p = Path(name)
        if p.exists():
            return p
    raise FileNotFoundError("Nenhum dos arquivos de entrada foi encontrado na pasta atual: " + ", ".join(INPUT_FILES))

def safe_read(file_path: Path):
    """Lê CSV ou Excel automaticamente."""
    if file_path.suffix.lower() in [".xls", ".xlsx"]:
        return pd.read_excel(file_path)
    else:
        # tenta autodetectar separador comum
        return pd.read_csv(file_path)

def standardize_columns(df: pd.DataFrame):
    new_cols = {}
    for col in df.columns:
        col_norm = col.strip()
        # tenta mapear direto
        if col_norm in STANDARD_COLS:
            new_cols[col] = STANDARD_COLS[col_norm]
            continue
        col_ascii = (col_norm
                     .replace("á","a").replace("ã","a").replace("â","a").replace("à","a")
                     .replace("é","e").replace("ê","e")
                     .replace("í","i")
                     .replace("ó","o").replace("ô","o").replace("õ","o")
                     .replace("ú","u").replace("ç","c"))
        col_ascii = re.sub(r"[^0-9A-Za-z_ ]+", "", col_ascii).strip()
        if re.search(r"via(ç|c)a|empresa", col_ascii, re.IGNORECASE):
            new_cols[col] = "Viacao"
        elif re.search(r"linh", col_ascii, re.IGNORECASE):
            new_cols[col] = "Linha"
        elif re.search(r"carro|veiculo", col_ascii, re.IGNORECASE):
            new_cols[col] = "Carro"
        elif re.search(r"quilom|km\b|quil", col_ascii, re.IGNORECASE):
            new_cols[col] = "Quilometragem"
        elif re.search(r"dura|tempo", col_ascii, re.IGNORECASE):
            new_cols[col] = "Duracao"
        elif re.search(r"veloc|km/h|kmh", col_ascii, re.IGNORECASE):
            new_cols[col] = "Velocidade_Media"
        else:
            new_cols[col] = col_ascii.replace(" ", "_")
    df = df.rename(columns=new_cols)
    return df

def parse_speed_to_float(s):
    """Recebe '30 km/h' ou '30km/h' ou '30' ou numeric e retorna float (km/h) ou np.nan"""
    if pd.isna(s):
        return np.nan
    if isinstance(s, (int, float, np.floating, np.integer)):
        return float(s)
    ss = str(s).strip()
    # remove spaces e 'km/h' e vírgulas
    ss = ss.replace(" ", "").lower()
    ss = ss.replace("km/h", "")
    # se contiver virgula decimal, troca por ponto
    ss = ss.replace(",", ".")
    # remove tudo que nao numero ou ponto ou - 
    ss = re.sub(r"[^0-9\.\-]", "", ss)
    if ss == "":
        return np.nan
    try:
        return float(ss)
    except Exception:
        return np.nan

def parse_duration_to_seconds(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float, np.integer, np.floating)):
        return float(x)
    s = str(x).strip()
    if s == "":
        return np.nan
    s = s.replace(",", ".")
    # caso padrão HH:MM:SS ou MM:SS
    if re.match(r"^\d+:\d{1,2}(:\d{1,2})?$", s):
        parts = s.split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            h, m, sec = parts
        elif len(parts) == 2:
            h = 0
            m, sec = parts
        else:
            return np.nan
        return h*3600 + m*60 + sec
    # unidades explícitas
    # ex: "1h 20m 30s", "2h", "45m", "120s", "1.5h"
    # procura números seguidos de unidade
    m = re.findall(r"(\d+(\.\d+)?)(\s*)(h|hr|hrs|hora|horas|m|min|mins|minuto|minutos|s|sec|segs|segundo|segundos)\b", s, flags=re.IGNORECASE)
    if m:
        total_s = 0.0
        for group in m:
            val = float(group[0])
            unit = group[3].lower()
            if unit.startswith("h"):
                total_s += val * 3600
            elif unit.startswith("m"):
                total_s += val * 60
            else:
                total_s += val
        return total_s
    # se for número simples, assume segundos (ou minutos? escolhi segundos)
    digits = re.sub(r"[^\d\.\-]", "", s)
    if digits != "":
        try:
            return float(digits)
        except:
            return np.nan
    return np.nan

def iqr_filter_groupwise(df, group_col, cols_to_check, k=1.5):
    df = df.copy()
    mask_keep = pd.Series(True, index=df.index)
    grouped = df.groupby(group_col)
    for name, group in grouped:
        idx = group.index
        for col in cols_to_check:
            # se a coluna não existir ou tiver poucos valores, pule
            series = group[col].dropna().astype(float)
            if series.shape[0] < 4:
                # se poucos dados, não remover por IQR (evita apagar quase tudo)
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            low = q1 - k * iqr
            high = q3 + k * iqr
            # marcar como keep False para outliers
            outlier_idx = series[(series < low) | (series > high)].index
            mask_keep.loc[outlier_idx] = False
    return df[mask_keep].copy()

def top_n_series(s: pd.Series, n=10, ascending=False):
    """Retorna tuplas (index, valor) do top n da série (ordenada por valor)"""
    if ascending:
        res = s.nsmallest(n)
    else:
        res = s.nlargest(n)
    return list(zip(res.index.astype(str), res.values))

def format_top_list(pairs):
    lines = []
    for i, (k, v) in enumerate(pairs, 1):
        lines.append(f"{i:2d}. {k} — {v}")
    return "\n".join(lines)

# --- Pipeline principal ---
def main():
    try:
        input_path = find_input_file()
    except FileNotFoundError as e:
        print(str(e))
        return

    print(f"Lendo arquivo: {input_path}")
    df = safe_read(input_path)

    # Padroniza nomes de colunas
    df = standardize_columns(df)

    # Verifica presença das colunas esperadas
    expected = ["Viacao", "Linha", "Carro", "Quilometragem", "Duracao", "Velocidade_Media"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        print("Aviso: as seguintes colunas esperadas não foram encontradas automaticamente:", missing)
        print("Colunas detectadas:", list(df.columns))
        # Continuar mesmo assim (usuário pode ter diferentes nomes); o script tentará seguir com o que houver

    # Normaliza e cria as colunas desejadas
    # Quilometragem
    if "Quilometragem" in df.columns:
        # tentar converter limpando vírgulas e pontos
        df["Quilometragem"] = pd.to_numeric(df["Quilometragem"].astype(str).str.replace(",", ".").str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce")
    else:
        df["Quilometragem"] = np.nan

    # Velocidade_Media (limpar " km/h")
    if "Velocidade_Media" in df.columns:
        df["Velocidade_Media"] = df["Velocidade_Media"].apply(parse_speed_to_float)
    else:
        df["Velocidade_Media"] = np.nan

    # Duracao -> Duracao_s em segundos
    if "Duracao" in df.columns:
        df["Duracao_s"] = df["Duracao"].apply(parse_duration_to_seconds)
    elif "Duracao_s" in df.columns:
        df["Duracao_s"] = pd.to_numeric(df["Duracao_s"], errors="coerce")
    else:
        df["Duracao_s"] = np.nan

    # Remover linhas totalmente vazias essenciais
    df = df.dropna(subset=["Linha", "Carro"], how="all")

    # Requisito: não filtrar BRT - pois você já removeu manualmente no Excel
    # Aplicar filtros básicos (descartar)
    before_count = len(df)
    filt_basic = (
        (df["Quilometragem"].fillna(-1) > 1) &
        (df["Duracao_s"].fillna(-1) > 60) &
        (df["Velocidade_Media"].fillna(-1) >= 10)
    )
    df = df[filt_basic].copy()
    after_basic_count = len(df)
    print(f"Linhas antes dos filtros básicos: {before_count}, após filtros básicos: {after_basic_count}")

    # Remoção de outliers por Linha (IQR) nas colunas Quilometragem e Duracao_s
    cols_for_iqr = ["Quilometragem", "Duracao_s"]
    df_clean = iqr_filter_groupwise(df, group_col="Linha", cols_to_check=cols_for_iqr, k=1.5)
    after_iqr_count = len(df_clean)
    print(f"Linhas após remoção de outliers por Linha (IQR): {after_iqr_count}")

    # A partir daqui, todos os cálculos são feitos em df_clean
    dfc = df_clean.copy()

    # Funções para gerar rankings por mediana / soma / count
    def group_stats(groupby_cols, value_col, agg="median"):
        g = dfc.groupby(groupby_cols)[value_col]
        if agg == "median":
            return g.median().sort_values(ascending=False)
        elif agg == "sum":
            return g.sum().sort_values(ascending=False)
        elif agg == "count":
            return g.count().sort_values(ascending=False)
        elif agg == "median_asc":
            return g.median().sort_values(ascending=True)
        else:
            raise ValueError("agg unknown")

    # Seção 1: Análise de Linhas (por mediana)
    linha_med_quil = group_stats("Linha", "Quilometragem", agg="median")
    linha_med_quil_min = linha_med_quil.sort_values(ascending=True)
    linha_med_vel = group_stats("Linha", "Velocidade_Media", agg="median")
    linha_med_vel_min = linha_med_vel.sort_values(ascending=True)

    # Seção 2: Análise de Viações (Viacao)
    viac_med_quil = group_stats("Viacao", "Quilometragem", agg="median")
    viac_med_quil_min = viac_med_quil.sort_values(ascending=True)
    viac_med_vel = group_stats("Viacao", "Velocidade_Media", agg="median")
    viac_med_vel_min = viac_med_vel.sort_values(ascending=True)

    # Seção 3: Total de Viagens (Contagem)
    linha_count = group_stats("Linha", "Carro", agg="count")  # contar pelo Carro dentro de Linha é equivalente a contar viagens por linha
    linha_count_min = linha_count.sort_values(ascending=True)
    viac_count = group_stats("Viacao", "Carro", agg="count")
    viac_count_min = viac_count.sort_values(ascending=True)

    # Seção 4: Quilometragem Total (Soma)
    linha_sum_km = group_stats("Linha", "Quilometragem", agg="sum")
    linha_sum_km_min = linha_sum_km.sort_values(ascending=True)
    viac_sum_km = group_stats("Viacao", "Quilometragem", agg="sum")
    viac_sum_km_min = viac_sum_km.sort_values(ascending=True)

    # Seção 5: Análise de Carro (mediana da velocidade) com condição >=10 viagens
    carro_counts = dfc.groupby("Carro").size()
    carros_validos = carro_counts[carro_counts >= 10].index
    carro_med_vel = dfc[dfc["Carro"].isin(carros_validos)].groupby("Carro")["Velocidade_Media"].median().sort_values(ascending=False)
    carro_med_vel_min = dfc[dfc["Carro"].isin(carros_validos)].groupby("Carro")["Velocidade_Media"].median().sort_values(ascending=True)

    # Também top10 de carros mais lentos independentemente? Pediste "da mesma forma apontar os carros mais lentos" — vou usar mesma condição de >=10 viagens.
    # Prepara conteúdo do relatório
    def top_to_text(series, n=10, reverse=False, fmt_val="{:.3f}"):
        # series: pandas Series index -> value
        if series.empty:
            return "(sem dados)\n"
        if reverse:
            s = series.nsmallest(n)
        else:
            s = series.nlargest(n)
        lines = []
        for i, (idx, val) in enumerate(zip(s.index, s.values), 1):
            try:
                val_str = fmt_val.format(float(val))
            except:
                val_str = str(val)
            lines.append(f"{i:2d}. {idx} — {val_str}")
        return "\n".join(lines) + "\n"

    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write("ANÁLISE DE VIAGENS (APÓS LIMPEZA)\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total de viagens após limpeza: {len(dfc)}\n")
        f.write(f"Linhas antes dos filtros: {before_count}; após filtros básicos: {after_basic_count}; após IQR: {after_iqr_count}\n\n")

        f.write("SEÇÃO 1 — ANÁLISE DE LINHAS (POR MEDIANA)\n")
        f.write("- Top 10 Linhas com MAIOR Mediana de Quilometragem\n")
        f.write(top_to_text(linha_med_quil, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Linhas com MENOR Mediana de Quilometragem\n")
        f.write(top_to_text(linha_med_quil_min, 10, reverse=True, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Linhas com MAIOR Mediana de Velocidade Média\n")
        f.write(top_to_text(linha_med_vel, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Linhas com MENOR Mediana de Velocidade Média\n")
        f.write(top_to_text(linha_med_vel_min, 10, reverse=True, fmt_val="{:.3f}"))

        f.write("\nSEÇÃO 2 — ANÁLISE DE VIAÇÕES (POR MEDIANA)\n")
        f.write("- Top 10 Viações com MAIOR Mediana de Quilometragem\n")
        f.write(top_to_text(viac_med_quil, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Viações com MENOR Mediana de Quilometragem\n")
        f.write(top_to_text(viac_med_quil_min, 10, reverse=True, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Viações com MAIOR Mediana de Velocidade Média\n")
        f.write(top_to_text(viac_med_vel, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Viações com MENOR Mediana de Velocidade Média\n")
        f.write(top_to_text(viac_med_vel_min, 10, reverse=True, fmt_val="{:.3f}"))

        f.write("\nSEÇÃO 3 — TOTAL DE VIAGENS (CONTAGEM)\n")
        f.write("- Top 10 Linhas com MAIOR número de viagens\n")
        f.write(top_to_text(linha_count, 10, reverse=False, fmt_val="{:.0f}"))
        f.write("\n- Top 10 Linhas com MENOR número de viagens\n")
        f.write(top_to_text(linha_count_min, 10, reverse=True, fmt_val="{:.0f}"))
        f.write("\n- Top 10 Viações com MAIOR número de viagens\n")
        f.write(top_to_text(viac_count, 10, reverse=False, fmt_val="{:.0f}"))
        f.write("\n- Top 10 Viações com MENOR número de viagens\n")
        f.write(top_to_text(viac_count_min, 10, reverse=True, fmt_val="{:.0f}"))

        f.write("\nSEÇÃO 4 — QUILOMETRAGEM TOTAL (SOMA)\n")
        f.write("- Top 10 Linhas com MAIOR soma de quilometragem\n")
        f.write(top_to_text(linha_sum_km, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Linhas com MENOR soma de quilometragem\n")
        f.write(top_to_text(linha_sum_km_min, 10, reverse=True, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Viações com MAIOR soma de quilometragem\n")
        f.write(top_to_text(viac_sum_km, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Viações com MENOR soma de quilometragem\n")
        f.write(top_to_text(viac_sum_km_min, 10, reverse=True, fmt_val="{:.3f}"))

        f.write("\nSEÇÃO 5 — CARROS (mediana da velocidade), condição: >= 10 viagens\n")
        f.write("- Top 10 Carros MAIS RÁPIDOS (>=10 viagens)\n")
        f.write(top_to_text(carro_med_vel, 10, reverse=False, fmt_val="{:.3f}"))
        f.write("\n- Top 10 Carros MAIS LENTOS (>=10 viagens)\n")
        f.write(top_to_text(carro_med_vel_min, 10, reverse=True, fmt_val="{:.3f}"))

    print(f"Relatório gerado: {OUTPUT_TXT}")

if __name__ == "__main__":
    main()
