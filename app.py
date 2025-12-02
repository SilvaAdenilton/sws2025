import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="SWS Análises", layout="wide")

st.title("📊 Análise de Dados SWS")

# Upload do arquivo
uploaded_file = st.file_uploader("📁 Envie o arquivo Excel", type=["xlsx"])

if uploaded_file:

    # 🔥 Carregar sheets
    xls = pd.ExcelFile(uploaded_file)
    sheets = [s for s in xls.sheet_names if str(s).strip().lower().startswith("sws")]

    if not sheets:
        st.error("❌ Nenhuma aba iniciando com 'SWS' encontrada.")
        st.stop()

    # Selectbox só com abas SWS
    chosen_sheet = st.selectbox("📄 Selecione a aba SWS", sheets)

    # Carregar o dataframe da aba selecionada
    df = pd.read_excel(uploaded_file, sheet_name=chosen_sheet)

    # Normalizar colunas
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Garantir colunas necessárias
    necessary_cols = [
        "prestador", "serial_number", "work_date",
        "over_effective_area", "over_not_effective_area", "error_msg"
    ]
    for col in necessary_cols:
        if col not in df.columns:
            st.error(f"❌ Coluna obrigatória ausente: {col}")
            st.stop()

    # Converter work_date
    df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")

    st.subheader("🔍 Filtros")

    col1, col2, col3 = st.columns(3)

    # Filtro prestador
    prestador_list = sorted(df["prestador"].dropna().unique())
    prestador_filter = col1.selectbox("Prestador:", ["Todos"] + prestador_list)

    # Filtro serial
    serial_list = sorted(df["serial_number"].dropna().unique())
    serial_filter = col2.selectbox("Serial Number:", ["Todos"] + list(serial_list))

    # Filtro datas
    min_date = df["work_date"].min()
    max_date = df["work_date"].max()

    work_date_filter = col3.date_input(
        "Período (work_date):",
        value=[min_date, max_date]
    )

    # Aplicando filtros
    df_filtered = df.copy()

    if prestador_filter != "Todos":
        df_filtered = df_filtered[df_filtered["prestador"] == prestador_filter]

    if serial_filter != "Todos":
        df_filtered = df_filtered[df_filtered["serial_number"] == serial_filter]

    df_filtered = df_filtered[
        (df_filtered["work_date"] >= pd.to_datetime(work_date_filter[0])) &
        (df_filtered["work_date"] <= pd.to_datetime(work_date_filter[1]))
    ]

    st.subheader("📌 Dados Filtrados")
    st.dataframe(df_filtered, use_container_width=True)

    # --- SOMATÓRIAS ---
    st.subheader("📐 Somatórios")

    soma_effective = df_filtered["over_effective_area"].sum()
    soma_not_effective = df_filtered["over_not_effective_area"].sum()

    colA, colB = st.columns(2)
    colA.metric("🔵 Total over_effective_area", f"{soma_effective:,.2f}")
    colB.metric("🟣 Total over_not_effective_area", f"{soma_not_effective:,.2f}")

    # Erros
    erro_counts = df_filtered["error_msg"].value_counts()

    st.subheader("🚨 Ocorrências de Erros")
    st.write(erro_counts)

    # --- GRÁFICO DAS SOMATÓRIAS ---
    st.subheader("📊 Gráfico: Somatória das Áreas")

    fig1, ax1 = plt.subplots(figsize=(6, 4))
    ax1.bar(["over_effective_area", "over_not_effective_area"],
            [soma_effective, soma_not_effective])
    ax1.set_ylabel("Somatória")
    ax1.set_title("Somatório das Áreas")
    st.pyplot(fig1)

    # --- GRÁFICO DE ERROS ---
    st.subheader("📉 Gráfico: Ocorrência de Erros")

    if not erro_counts.empty:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        ax2.bar(erro_counts.index.astype(str), erro_counts.values)
        ax2.set_ylabel("Quantidade")
        ax2.set_title("Quantidade de Erros por Tipo")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig2)
    else:
        st.info("Nenhum erro encontrado nos filtros aplicados.")
