import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard SWS 2025", layout="wide")

# ===========================================================
#  TÍTULO / CABEÇALHO
# ===========================================================
st.markdown("""
# 📊 Dashboard Streamlit – Análise e Filtragem dos Arquivos SWS  

### 👨‍🔧 **Responsável Técnico: Silva Adenilton (Denis) – Analista**
---
""")

# ===========================================================
#  UPLOAD DE ARQUIVO
# ===========================================================
uploaded_file = st.file_uploader(
    "Envie o arquivo SWS (XLSX)", 
    type=["xlsx"]
)

if not uploaded_file:
    st.warning("Envie um arquivo para continuar.")
    st.stop()

df = pd.read_excel(uploaded_file)

# Ajustando datas
if "work_date" in df.columns:
    df["work_date"] = pd.to_datetime(df["work_date"], errors="coerce")

# ===========================================================
#  BOTÕES DE SELEÇÃO DA BASE (SWS1 / SWS2)
# ===========================================================
st.subheader("Selecione a Base para Análise")

col1, col2 = st.columns(2)

base_selected = None
with col1:
    if st.button("🟦 SWS1", use_container_width=True):
        base_selected = "SWS1"
with col2:
    if st.button("🟩 SWS2", use_container_width=True):
        base_selected = "SWS2"

if not base_selected:
    st.info("Escolha uma base para continuar.")
    st.stop()

df_base = df[df["base"] == base_selected]

st.success(f"Base selecionada: **{base_selected}**")

# ===========================================================
#  FILTROS PRINCIPAIS
# ===========================================================

st.markdown("## 🔍 Filtros")

serial_list = sorted(df_base["serial_number"].dropna().unique())
prestador_list = sorted(df_base["prestador"].dropna().unique())

colA, colB, colC = st.columns(3)

with colA:
    serial_filter = st.multiselect(
        "Filtrar por SERIAL_NUMBER:",
        serial_list,
        default=None
    )

with colB:
    prestador_filter = st.multiselect(
        "Filtrar por PRESTADOR:",
        prestador_list,
        default=None
    )

with colC:
    dates = st.date_input(
        "Filtrar por Work Date (intervalo):",
        value=[]
    )

# Aplicar filtros
if serial_filter:
    df_base = df_base[df_base["serial_number"].isin(serial_filter)]

if prestador_filter:
    df_base = df_base[df_base["prestador"].isin(prestador_filter)]

if len(dates) == 2:
    df_base = df_base[(df_base["work_date"] >= pd.Timestamp(dates[0])) &
                      (df_base["work_date"] <= pd.Timestamp(dates[1]))]

# ===========================================================
#  SOMATÓRIOS PRINCIPAIS
# ===========================================================

area_ok = df_base["over_effective_area"].sum()
area_not_ok = df_base["over_not_effective_area"].sum()

st.markdown("## 📐 Indicadores Gerais")

col1, col2 = st.columns(2)
col1.metric("Área Efetiva Total", f"{area_ok:,.2f}")
col2.metric("Área Não Efetiva Total", f"{area_not_ok:,.2f}")

# ===========================================================
#  GRÁFICO DE PIZZA - EFETIVA x NÃO EFETIVA
# ===========================================================
st.markdown("### 🥧 Distribuição de Áreas")

pie_data = pd.DataFrame({
    "Tipo": ["Efetiva", "Não Efetiva"],
    "Valor": [area_ok, area_not_ok]
})

fig_pie = px.pie(
    pie_data,
    names="Tipo",
    values="Valor",
    color="Tipo",
    color_discrete_map={"Efetiva": "green", "Não Efetiva": "red"},
    title="Comparação de Áreas"
)

st.plotly_chart(fig_pie, use_container_width=True)

# ===========================================================
#  GRÁFICO DE BARRAS POR PRESTADOR
# ===========================================================
st.markdown("### 📊 Produção por Prestador")

df_prest = df_base.groupby("prestador")["over_effective_area"].sum().reset_index()

fig_bar = px.bar(
    df_prest,
    x="prestador",
    y="over_effective_area",
    title="Área Efetiva por Prestador",
    text_auto=True
)

st.plotly_chart(fig_bar, use_container_width=True)

# ===========================================================
#  ÁREA DE STATUS E ERROS
# ===========================================================
st.markdown("---")
st.markdown("## ⚠️ Análise de Status e Erros")

col_s1, col_s2 = st.columns(2)

with col_s1:
    serial_sel = st.selectbox("Filtrar por Serial:", serial_list)

with col_s2:
    prest_sel = st.selectbox("Filtrar por Prestador:", prestador_list)

df_status = df[(df["serial_number"] == serial_sel) &
               (df["prestador"] == prest_sel)]

if df_status.empty:
    st.info("Nenhum registro encontrado para esta combinação.")
else:
    st.dataframe(df_status[["serial_number", "prestador", "status", "error_msg"]])

    fig_status = px.histogram(
        df_status,
        x="status",
        color="status",
        title="Distribuição de Status"
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ===========================================================
#  RODAPÉ
# ===========================================================
st.markdown("---")
st.caption("Sistema SWS - Análise 2025 • Desenvolvido por Silva Adenilton (Denis) com Streamlit")
