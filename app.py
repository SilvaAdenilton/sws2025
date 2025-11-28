import streamlit as st
import pandas as pd
import plotly.express as px

# ======================================
# CONFIGURAÇÃO INICIAL
# ======================================
st.set_page_config(page_title="Dashboard SWS", layout="wide")

st.title("📊 Dashboard SWS - Análise 2025")
st.markdown("### Responsável Técnico: **Silva Adenilton (Denis) - Analista**")
st.markdown("---")

# ======================================
# UPLOAD DO ARQUIVO
# ======================================
uploaded_file = st.file_uploader(
    "Envie a planilha SWS (xlsx)", type=["xlsx"], help="Somente arquivos .xlsx"
)

if not uploaded_file:
    st.warning("Envie um arquivo para iniciar a análise...")
    st.stop()

# Carregar arquivo
df = pd.read_excel(uploaded_file)

# Garantir que work_date é data
if "work_date" in df.columns:
    df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")

# ======================================
# BOTÕES PARA SELEÇÃO DE BASE (SWS1 / SWS2)
# ======================================
st.subheader("Selecione a Base de Análise")

colA, colB = st.columns(2)
with colA:
    base = st.radio("Escolha:", ["SWS1", "SWS2"], horizontal=True)

# Filtrar automaticamente pela coluna correspondente
df_base = df[df["BASE"] == base] if "BASE" in df.columns else df

st.success(f"Base selecionada: **{base}**")

st.markdown("---")

# ======================================
# FILTROS PRINCIPAIS
# ======================================
st.subheader("Filtros")

col1, col2, col3 = st.columns(3)

# Serial Number
serial_list = sorted(df_base["serial_number"].dropna().unique())
serial_filter = col1.multiselect("Filtrar por Serial Number:", serial_list)

# Prestador
prest_list = sorted(df_base["prestador"].dropna().unique())
prest_filter = col2.multiselect("Filtrar por Prestador:", prest_list)

# Data
if "work_date" in df_base.columns:
    min_date = df_base["work_date"].min()
    max_date = df_base["work_date"].max()
    date_filter = col3.date_input("Filtrar por Data de Trabalho:", [min_date, max_date])
else:
    date_filter = None


# Aplicar filtros
df_filt = df_base.copy()

if serial_filter:
    df_filt = df_filt[df_filt["serial_number"].isin(serial_filter)]

if prest_filter:
    df_filt = df_filt[df_filt["prestador"].isin(prest_filter)]

if date_filter:
    start, end = date_filter
    df_filt = df_filt[(df_filt["work_date"] >= pd.to_datetime(start)) &
                      (df_filt["work_date"] <= pd.to_datetime(end))]

st.markdown("---")

# ======================================
# SOMATÓRIOS DAS ÁREAS
# ======================================
st.subheader("Somatórios de Áreas")

col4, col5 = st.columns(2)

eff = df_filt["over_effective_area"].sum()
not_eff = df_filt["over_not_effective_area"].sum()

col4.metric("Área Efetiva (Soma)", f"{eff:,.2f}")
col5.metric("Área Não Efetiva (Soma)", f"{not_eff:,.2f}")

# Gráfico Pizza
fig_pizza = px.pie(
    names=["Efetiva", "Não Efetiva"],
    values=[eff, not_eff],
    title="Distribuição das Áreas",
    color_discrete_sequence=px.colors.qualitative.Prism
)
st.plotly_chart(fig_pizza, use_container_width=True)

st.markdown("---")

# ======================================
# GRÁFICOS POR PRESTADOR
# ======================================
st.subheader("Distribuição por Prestador")

if "prestador" in df_filt.columns:
    df_prest = df_filt.groupby("prestador")[["over_effective_area", "over_not_effective_area"]].sum().reset_index()

    fig_prest = px.bar(
        df_prest,
        x="prestador",
        y=["over_effective_area", "over_not_effective_area"],
        barmode="group",
        title="Áreas por Prestador",
        labels={"value": "Área Total", "prestador": "Prestador"}
    )
    st.plotly_chart(fig_prest, use_container_width=True)

st.markdown("---")

# ======================================
# STATUS E ERROS
# ======================================
st.subheader("Status e Erros por Serial Number")

col8, col9 = st.columns(2)

with col8:
    if "STATUS_SCHEDULED" in df_filt.columns:
        fig_status = px.histogram(df_filt, x="STATUS_SCHEDULED", title="Status dos Equipamentos")
        st.plotly_chart(fig_status, use_container_width=True)

with col9:
    if "error_msg" in df_filt.columns:
        fig_error = px.histogram(df_filt, x="error_msg", title="Erros Encontrados")
        st.plotly_chart(fig_error, use_container_width=True)

# Mostrar tabela final
st.markdown("### Dados Filtrados")
st.dataframe(df_filt)

st.markdown("---")
st.caption("Sistema SWS - Desenvolvido por Silva Adenilton (Denis) • 2025")

