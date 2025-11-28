import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SWS - Dashboard", layout="wide")

st.title("Dashboard Streamlit para análise e filtragem dos arquivos SWS")
st.caption("Responsável Técnico: **Silva Adenilton (Denis) - Analista**")
st.markdown("---")

# ===============================
# UPLOAD DO ARQUIVO
# ===============================
uploaded_file = st.file_uploader("Envie o arquivo SWS (com abas SWS1 e SWS2)", type=["xlsx"])

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    xls = pd.ExcelFile(uploaded_file)

    # ===============================
    # SELETOR PRINCIPAL DE BASE
    # ===============================
    st.subheader("Selecione a Base de Análise")
    escolha = st.radio("Escolha a base:", ["SWS1", "SWS2"], horizontal=True)

    df = pd.read_excel(uploaded_file, sheet_name=escolha)

    st.success(f"Base selecionada: {escolha}")

    # ===============================
    # FILTROS
    # ===============================
    st.markdown("---")
    st.header("Filtros")

    # → FILTRO: serial_number
    serial_list = sorted(df["serial_number"].dropna().unique())
    serial_sel = st.multiselect("Filtrar por Serial Number:", serial_list)

    # → FILTRO: prestador
    prestador_list = sorted(df["prestador"].dropna().unique())
    prestador_sel = st.multiselect("Filtrar por Prestador:", prestador_list)

    # → FILTRO: Status
    status_list = sorted(df["Status"].dropna().unique())
    status_sel = st.multiselect("Filtrar por Status:", status_list)

    # → FILTRO: error_msg
    error_list = sorted(df["error_msg"].dropna().unique())
    error_sel = st.multiselect("Filtrar por Erros:", error_list)

    # → FILTRO: intervalo de datas
    if "work_date" in df.columns:
        df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")
        start_date = df["work_date"].min()
        end_date = df["work_date"].max()

        date_range = st.date_input("Intervalo de Datas:", value=[start_date, end_date])
        dt_start, dt_end = date_range

    # ===============================
    # APLICANDO FILTROS
    # ===============================
    df_filt = df.copy()

    if serial_sel:
        df_filt = df_filt[df_filt["serial_number"].isin(serial_sel)]

    if prestador_sel:
        df_filt = df_filt[df_filt["prestador"].isin(prestador_sel)]

    if status_sel:
        df_filt = df_filt[df_filt["Status"].isin(status_sel)]

    if error_sel:
        df_filt = df_filt[df_filt["error_msg"].isin(error_sel)]

    if "work_date" in df_filt.columns:
        df_filt = df_filt[(df_filt["work_date"] >= pd.to_datetime(dt_start)) &
                          (df_filt["work_date"] <= pd.to_datetime(dt_end))]

    # ===============================
    # RESULTADOS
    # ===============================
    st.markdown("---")
    st.header("Resultados da Análise")

    if df_filt.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    st.subheader("Pré-visualização dos dados filtrados:")
    st.dataframe(df_filt, use_container_width=True)

    # SOMATÓRIOS
    total_effective = df_filt["over_effective_area"].sum()
    total_not_effective = df_filt["over_not_effective_area"].sum()

    st.subheader("Somatórios")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Área Efetiva Total", f"{total_effective:,.2f}")

    with col2:
        st.metric("Área Não Efetiva Total", f"{total_not_effective:,.2f}")

    # ===============================
    # GRÁFICOS
    # ===============================
    st.markdown("---")
    st.header("Gráficos")

    # Pizza de Status
    fig_status = px.pie(df_filt, names="Status", title="Distribuição por Status")
    st.plotly_chart(fig_status, use_container_width=True)

    # Pizza de Prestadores
    fig_prestador = px.pie(df_filt, names="prestador", title="Distribuição por Prestador")
    st.plotly_chart(fig_prestador, use_container_width=True)

    # Barras por Erros
    fig_erro = px.bar(df_filt.groupby("error_msg").size().reset_index(name="count"),
                      x="error_msg", y="count", title="Erros Encontrados")
    st.plotly_chart(fig_erro, use_container_width=True)

    st.markdown("---")
    st.caption("Sistema SWS - Desenvolvido por Silva Adenilton (Denis)")
