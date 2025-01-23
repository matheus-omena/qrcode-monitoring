import streamlit as st
import pandas as pd
import json

# Caminhos dos arquivos gerados
json_file = "csv_files/combinated_data/processed_data.json"
csv_file = "csv_files/combinated_data/invalid_links.csv"

# Título do Dashboard
st.title("Dashboard de Validação de QRCodes")

# Exibir informações do JSON
st.header("Resumo dos Dados (JSON)")
try:
    with open(json_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        # Exibir os dados formatados
        st.json(json_data)

        # Exibir métricas
        st.metric("Total de Links", json_data["totalLinks"])
        st.metric("Links Válidos", json_data["validLinks"])
        st.metric("Links Inválidos", json_data["invalidLinks"]["total"])
except FileNotFoundError:
    st.error(f"Arquivo JSON não encontrado: {json_file}")

# Exibir tabela do CSV
st.header("Links Inválidos (CSV)")
try:
    df = pd.read_csv(csv_file, sep=";")
    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.error(f"Arquivo CSV não encontrado: {csv_file}")
