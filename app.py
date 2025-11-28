import streamlit as st
import pandas as pd
import plotly.express as px

# ===============================
# CABEÇALHO DO APP
# ===============================

st.set_page_config(page_title="SWS Dashboard 2025", layout="wide")

st.markdown("""
## Dashboard Streamlit para análise e filtragem dos arquivos SWS  
### 👨‍🔧 Responsável Técnico: **Silva Adenilton (Denis) – Analista**
---
""")

# ===============================
# UPLOAD DO ARQUIVO
# ===============================

uploaded_file = st.file_uploader("Envie o arquivo SWS (xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.warning("Envie um arquivo para iniciar a análise.")
    st.stop()

df = pd.read_excel(uploaded_file)

st.success("Arquivo carregado com sucesso!")

# ===============================
# SELEÇÃO DA BASE
# ===============================

st.subheader("Selecione a Base de Análise")

base_escolhida = st.radio("Escolha:", ["SWS1", "SWS2"], horizontal=True)

st.success(f"Base selecionada: **{base_escolhida}**")

# Filtra somente linhas da base selecionada
df_base = df[df["name"] == base_escolhida].copy()

# ===============================
# TRATAMENTO E LIMPEZA
# ===============================

# Remove colunas inúteis quando existirem
colunas_remover = ["name.1", "path", "mac_address", "name"]
df_base = df_base[[c for c in df_base.columns if c not in colunas_remover]]

# Garantir tipos corretos
if "work_date" in df_base.columns:
    df_base["work_date"] = pd.to_datetime(df_base["work_date"], errors="coerce")

# ===============================
# FILTROS
# ===============================

st.subheader("Filtros")

# ---- Serial Number ----
if "serial_number" in df_base.columns:
    serial_list = sorted(df_base["serial_number"].dropna().unique())
    serial_filter = st.multiselect("Filtrar por Serial Number:", serial_list)
    if serial_filter:
        df_base = df_base[df_base["serial_number"].isin(serial_filter)]

# ---- Prestador ----
if "prestador" in df_base.columns:
    prestador_list = sorted(df_base["prestador"].dropna().unique())
    prestador_filter = st.multiselect("Filtrar por Prestador:", prestador_list)
    if prestador_filter:
        df_base = df_base[df_base["prestador"].isin(prestador_filter)]

# ---- Filtro por Data ----
if "work_date" in df_base.columns:
    min_date = df_base["work_date"].min()
    max_date = df_base["work_date"].max()

    date_range = st.date_input(
        "Filtrar por período (work_date):",
        (min_date, max_date)
    )

    if isinstance(date_range, tuple):
        df_base = df_base[
            (df_base["work_date"] >= pd.to_datetime(date_range[0])) &
            (df_base["work_date"] <= pd.to_datetime(date_range[1]))
        ]

# ---- Status ----
if "Status" in df_base.columns:
    status_list = sorted(df_base["Status"].dropna().unique())
    status_filter = st.multiselect("Filtrar por Status:", status_list)
    if status_filter:
        df_base = df_base[df_base["Status"].isin(status_filter)]

# ---- Errors ----
if "error_msg" in df_base.columns:
    error_list = sorted(df_base["error_msg"].dropna().unique())
    error_filter = st.multiselect("Filtrar por Erros:", error_list)
    if error_filter:
        df_base = df_base[df_base["error_msg"].isin(error_filter)]

# ===============================
# SOMATÓRIOS
# ===============================

st.markdown("---")
st.subheader("Somatórios de Áreas")

col1, col2 = st.columns(2)

with col1:
    soma_efetiva = df_base["over_effective_area"].sum()
    st.metric("Área Efetiva Total", f"{soma_efetiva:,.2f}")

with col2:
    soma_nao_efetiva = df_base["over_not_effective_area"].sum()
    st.metric("Área Não Efetiva Total", f"{soma_nao_efetiva:,.2f}")

# ===============================
# GRÁFICOS
# ===============================

st.markdown("---")
st.subheader("Gráficos de Distribuição")

# ---- Status ----
if "Status" in df_base.columns:
    fig_status = px.pie(
        df_base,
        names="Status",
        title="Distribuição por Status",
        hole=0.45
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ---- Prestador ----
if "prestador" in df_base.columns:
    fig_prestador = px.bar(
        df_base,
        x="prestador",
        title="Quantidade por Prestador"
    )
    st.plotly_chart(fig_prestador, use_container_width=True)

# ===============================
# ANÁLISE DE ERROS
# ===============================

st.markdown("---")
st.subheader("Erros Encontrados")

df_erros = df_base[df_base["error_msg"].notna() & (df_base["error_msg"] != "")]
st.dataframe(df_erros)

# ===============================
# TABELA FINAL
# ===============================

st.markdown("---")
st.subheader("Tabela Final Filtrada")

st.dataframe(df_base, use_container_width=True)

# Rodapé
st.caption("Sistema SWS - Análise 2025 • Desenvolvido com Streamlit")
