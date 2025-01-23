import pandas as pd
import requests
import json
from datetime import datetime

# Função para verificar o status de uma URL
def check_url_status(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code
    except requests.RequestException:
        return None

# Caminho do arquivo CSV final
csv_path = "csv_files/combinated_data/combined_data.csv"

print(f"Iniciando validação dos QRCodes (", datetime.now(), ")")

# Lê o CSV
df = pd.read_csv(csv_path, sep=";")

# Inicializa contadores e coleções
total_links = len(df)
total_valid_links = 0
invalid_links = {
    "total": 0,
    "blankLinks": 0,
    "youtubeLinks": 0,
    "notSaraLinks": 0,
    "saraHomeLinks": 0,
    "404Links": 0
}

# Lista para armazenar registros classificados como invalidLinks
invalid_records = []

print(f"Total de registros no CSV: {total_links}")
print(f"Iterando pelos registros...")

# Itera pelos registros do CSV
for index, row in df.iterrows():
    print(f"Processando registro {index + 1}/{total_links}...")
    qr_id = row["QR ID"]
    qr_description = row["QR Description"]
    permalink = row["Permalink"]
    redirection = row["Redirection"]

    # 1. Links vazios
    if pd.isna(redirection) or redirection.strip() == "":
        invalid_links["blankLinks"] += 1
        invalid_records.append({
            "Situation": "Links vazios",
            "QR ID": qr_id,
            "QR Description": qr_description,
            "Permalink": permalink,
            "Redirection": redirection
        })
        continue

    # 2. Links que não começam com "https://www.sara.com.br/produto/" ou "https://www.sara.com.br/buscar/" ou levam para a home do SARA
    if not (redirection.startswith("https://www.sara.com.br/produto/") or redirection.startswith("https://www.sara.com.br/buscar/")):
        if redirection in ["https://www.sara.com.br", "https://www.sara.com.br/"]:
            invalid_links["saraHomeLinks"] += 1
            invalid_records.append({
                "Situation": "Links para a home do SARA",
                "QR ID": qr_id,
                "QR Description": qr_description,
                "Permalink": permalink,
                "Redirection": redirection
            })
        elif "youtu" in redirection:
            invalid_links["youtubeLinks"] += 1
            invalid_records.append({
                "Situation": "Links do YouTube",
                "QR ID": qr_id,
                "QR Description": qr_description,
                "Permalink": permalink,
                "Redirection": redirection
            })
        else:
            invalid_links["notSaraLinks"] += 1
            invalid_records.append({
                "Situation": "Links não-relacionados ao SARA",
                "QR ID": qr_id,
                "QR Description": qr_description,
                "Permalink": permalink,
                "Redirection": redirection
            })
        continue

    # 3. Valida o status HTTP para URLs que começam com "https://www.sara.com.br/produto/" ou "https://www.sara.com.br/buscar/"
    status_code = check_url_status(redirection)
    if status_code == 200:
        total_valid_links += 1
    elif status_code == 404:
        invalid_links["404Links"] += 1
        invalid_records.append({
            "Situation": "Produtos não encontrados",
            "QR ID": qr_id,
            "QR Description": qr_description,
            "Permalink": permalink,
            "Redirection": redirection
        })

# Totaliza os links inválidos
invalid_links["total"] = sum(invalid_links.values())

# Monta o JSON final
output_data = {
    "totalLinks": total_links,
    "validLinks": total_valid_links,
    "invalidLinks": invalid_links
}

# Salva o JSON em um arquivo
output_json_path = "csv_files/combinated_data/processed_data.json"
with open(output_json_path, "w", encoding="utf-8") as json_file:
    json.dump(output_data, json_file, indent=4, ensure_ascii=False)
print(f"JSON salvo em {output_json_path}")

# Exporta os registros classificados como invalidLinks para um CSV
invalid_links_csv_path = "csv_files/combinated_data/invalid_links.csv"
invalid_df = pd.DataFrame(invalid_records)

# Ordena os registros por Situation
invalid_df = invalid_df.sort_values(by="Situation")
invalid_df.to_csv(invalid_links_csv_path, index=False, sep=";")
print(f"CSV de links inválidos salvo em {invalid_links_csv_path}")

print(f"Validação dos QRCodes finalizada")