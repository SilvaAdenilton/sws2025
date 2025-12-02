import streamlit as st
import pandas as pd
import plotly.express as px

# =====================
# CONFIGURAÇÃO GERAL
# =====================
st.set_page_config(page_title="Análise Técnica – SWS", layout="wide", page_icon="📊")

st.markdown("""
<style>
/*****************************/
/* Sidebar */
/*****************************/
section[data-testid="stSidebar"] * {
    color: white !important;
}

/*****************************/
/* Selectbox e inputs */
/*****************************/
.stSelectbox label, .stSelectbox div, .stSelectbox span {
    color: white !important;
}
.css-16huue1, .css-1d391kg, .st-b7, .st-bs {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =====================
# TÍTULO
# =====================
st.title("📊 Análise Técnica — Arquivos Enviados (SWS)")
st.subheader("Dashboard interativa | Desenvolvido por Adenilton Silva (Denis)")

# =====================
# UPLOAD DO ARQUIVO
# =====================
st.markdown("### 📁 Envie o arquivo SWS (.xlsx / .xls)")
uploaded_file = st.file_uploader("Arraste ou selecione o arquivo", type=["xlsx", "xls"])

if uploaded_file:
    # Ler sheets
    excel = pd.ExcelFile(uploaded_file)
    sheets = excel.sheet_names

    # Filtrar apenas abas SWS
    sheets = [s for s in sheets if str(s).strip().lower().startswith("sws")]

    if not sheets:
        st.error("❌ Nenhuma aba começando com 'SWS' encontrada no arquivo.")
        st.stop()

    df_all = pd.read_excel(uploaded_file, sheet_name=None)

    # Select aba
    chosen_sheet = st.selectbox("⭐ Selecione a aba para análise", sheets)

    df = df_all[chosen_sheet]

    # Normalização das colunas
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Conversão work_date
    if "work_date" in df.columns:
        df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")

    # =====================
    # SIDEBAR – FILTROS
    # =====================
    st.sidebar.header("Filtros")

    # Prestador
    prestadores = ["Todos"] + sorted(df["prestador"].dropna().unique().tolist())
    prestador_filtro = st.sidebar.selectbox("Prestador", prestadores)

    # Serial Number
    serials = ["Todos"] + sorted(df["serial_number"].dropna().unique().tolist())
    serial_filtro = st.sidebar.selectbox("Serial Number", serials)

    # Status
    status_list = ["Todos"] + sorted(df["status"].dropna().unique().tolist())
    status_filtro = st.sidebar.selectbox("Status", status_list)

    # Work_date
    if "work_date" in df.columns:
        min_date = df["work_date"].min()
        max_date = df["work_date"].max()

        work_date_filter = st.sidebar.date_input(
            "Work Date",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        start_date, end_date = pd.to_datetime(work_date_filter[0]), pd.to_datetime(work_date_filter[1])

    # =====================
    # APLICAR FILTROS
    # =====================
    df_filtered = df.copy()

    if prestador_filtro != "Todos":
        df_filtered = df_filtered[df_filtered["prestador"] == prestador_filtro]

    if serial_filtro != "Todos":
        df_filtered = df_filtered[df_filtered["serial_number"] == serial_filtro]

    if status_filtro != "Todos":
        df_filtered = df_filtered[df_filtered["status"] == status_filtro]

    if "work_date" in df.columns:
        df_filtered = df_filtered[
            (df_filtered["work_date"] >= start_date) &
            (df_filtered["work_date"] <= end_date)
        ]

    # =====================
    # SOMATÓRIAS
    # =====================
    total_effective = df_filtered.get("over_effective_area", pd.Series([0])).sum()
    total_not_effective = df_filtered.get("over_not_effective_area", pd.Series([0])).sum()

    col1, col2 = st.columns(2)
    col1.metric("Área Efetiva Total (Filtro Aplicado)", f"{total_effective:,.2f}")
    col2.metric("Área Não Efetiva Total (Filtro Aplicado)", f"{total_not_effective:,.2f}")

    # =====================
    # GRÁFICOS
    # =====================
    st.markdown("## 📊 Gráficos da Análise")

    # Gráfico das áreas
    areas_df = pd.DataFrame({
        "Tipo": ["Área Efetiva", "Área Não Efetiva"],
        "Valor": [total_effective, total_not_effective]
    })

    fig_areas = px.bar(
        areas_df,
        x="Tipo",
        y="Valor",
        title="Somatória das Áreas (Filtro Aplicado)",
        text="Valor",
    )
    st.plotly_chart(fig_areas, use_container_width=True)

    # Gráfico dos erros
    if "error_msg" in df_filtered.columns:
        error_counts = df_filtered["error_msg"].fillna("SEM ERRO").value_counts().reset_index()
        error_counts.columns = ["Erro", "Quantidade"]

        fig_erros = px.bar(
            error_counts,
            x="Erro",
            y="Quantidade",
            title="Ocorrências de Erros",
            text="Quantidade"
        )
        st.plotly_chart(fig_erros, use_container_width=True)

    # =====================
    # TABELA FINAL
    # =====================
    st.markdown("## 📄 Registros filtrados")
    st.dataframe(df_filtered, use_container_width=True)

else:
    st.info("⬆️ Envie um arquivo para iniciar a análise.")
