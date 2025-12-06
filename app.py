import streamlit as st
import pandas as pd
import plotly.express as px

# =====================
# CONFIGURAÇÃO GERAL
# =====================
st.set_page_config(page_title="Análise Técnica – SWS", layout="wide", page_icon="📊")

st.markdown("""
<style>
section[data-testid="stSidebar"] * {
    color: white !important;
}
.stSelectbox label, .stSelectbox div, .stSelectbox span {
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

    excel = pd.ExcelFile(uploaded_file)
    sheets = [s for s in excel.sheet_names if str(s).lower().startswith("sws")]

    if not sheets:
        st.error("❌ Nenhuma aba começando com 'SWS' encontrada no arquivo.")
        st.stop()

    df_all = pd.read_excel(uploaded_file, sheet_name=None)
    chosen_sheet = st.selectbox("⭐ Selecione a aba para análise", sheets)
    df = df_all[chosen_sheet]

    df.columns = [str(c).strip().lower() for c in df.columns]

    if "work_date" in df.columns:
        df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")

    # =====================
    # SIDEBAR – FILTROS
    # =====================
    st.sidebar.header("🎛️ Filtros")

    prestadores = ["Todos"] + sorted(df["prestador"].dropna().unique())
    prestador_filtro = st.sidebar.selectbox("Prestador", prestadores)

    serials = ["Todos"] + sorted(df["serial_number"].dropna().unique())
    serial_filtro = st.sidebar.selectbox("Serial Number", serials)

    status_list = ["Todos"] + sorted(df["status"].dropna().unique())
    status_filtro = st.sidebar.selectbox("Status", status_list)

    if "work_date" in df.columns:
        min_date, max_date = df["work_date"].min(), df["work_date"].max()
        work_date_filter = st.sidebar.date_input(
            "Período de Trabalho",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        start_date, end_date = pd.to_datetime(work_date_filter[0]), pd.to_datetime(work_date_filter[1])

    area_min = st.sidebar.number_input("Área Efetiva Mínima", min_value=0.0, value=0.0)

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

    df_filtered = df_filtered[df_filtered["over_effective_area"] >= area_min]

    # =====================
    # KPIs
    # =====================
    total_effective = df_filtered.get("over_effective_area", pd.Series([0])).sum()
    total_not_effective = df_filtered.get("over_not_effective_area", pd.Series([0])).sum()

    total_registros = len(df_filtered)
    total_prestadores = df_filtered["prestador"].nunique()
    total_serials = df_filtered["serial_number"].nunique()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Área Efetiva", f"{total_effective:,.2f}")
    col2.metric("Área Não Efetiva", f"{total_not_effective:,.2f}")
    col3.metric("Registros", total_registros)
    col4.metric("Prestadores", total_prestadores)
    col5.metric("Seriais", total_serials)

    # =====================
    # GRÁFICOS
    # =====================
    st.markdown("## 📊 Análises Gráficas")

    # Barras áreas
    areas_df = pd.DataFrame({
        "Tipo": ["Área Efetiva", "Área Não Efetiva"],
        "Valor": [total_effective, total_not_effective]
    })

    fig_areas = px.bar(areas_df, x="Tipo", y="Valor", text="Valor", title="Somatória das Áreas")
    st.plotly_chart(fig_areas, use_container_width=True)

    # Evolução Temporal
    if "work_date" in df_filtered.columns:
        evolucao = df_filtered.groupby("work_date")[["over_effective_area", "over_not_effective_area"]].sum().reset_index()
        fig_evo = px.line(evolucao, x="work_date", y=["over_effective_area", "over_not_effective_area"], title="Evolução ao Longo do Tempo")
        st.plotly_chart(fig_evo, use_container_width=True)

    # Ranking
    ranking = df_filtered.groupby("prestador")["over_effective_area"].sum().sort_values(ascending=False).reset_index()
    fig_rank = px.bar(ranking, x="prestador", y="over_effective_area", title="Ranking de Prestadores")
    st.plotly_chart(fig_rank, use_container_width=True)

    # Pizza Status
    status_dist = df_filtered["status"].value_counts().reset_index()
    status_dist.columns = ["Status", "Quantidade"]
    fig_status = px.pie(status_dist, names="Status", values="Quantidade", title="Distribuição por Status")
    st.plotly_chart(fig_status, use_container_width=True)

    # Heatmap
    if "work_date" in df_filtered.columns:
        heatmap_df = df_filtered.pivot_table(index="prestador", columns="work_date", values="over_effective_area", aggfunc="sum", fill_value=0)
        fig_heatmap = px.imshow(heatmap_df, aspect="auto", title="Mapa de Calor de Produtividade")
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Top 10 Seriais
    top_serials = df_filtered.groupby("serial_number")["over_effective_area"].sum().sort_values(ascending=False).head(10).reset_index()
    fig_serial = px.bar(top_serials, x="serial_number", y="over_effective_area", title="Top 10 Seriais")
    st.plotly_chart(fig_serial, use_container_width=True)

    # Área acumulada
    if "work_date" in df_filtered.columns:
        acumulado = df_filtered.sort_values("work_date")
        acumulado["area_acumulada"] = acumulado["over_effective_area"].cumsum()
        fig_acum = px.line(acumulado, x="work_date", y="area_acumulada", title="Área Efetiva Acumulada")
        st.plotly_chart(fig_acum, use_container_width=True)

    # Erros
    if "error_msg" in df_filtered.columns:
        error_counts = df_filtered["error_msg"].fillna("Sem Erro").value_counts().reset_index()
        error_counts.columns = ["Erro", "Quantidade"]
        fig_erros = px.bar(error_counts, x="Erro", y="Quantidade", title="Ocorrências de Erros")
        st.plotly_chart(fig_erros, use_container_width=True)

    # =====================
    # TABELA FINAL
    # =====================
    st.markdown("## 📄 Registros Filtrados")
    st.dataframe(df_filtered, use_container_width=True)

else:
    st.info("⬆️ Envie um arquivo para iniciar a análise.")
