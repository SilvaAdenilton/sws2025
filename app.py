import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================
#  CONFIGURAÇÃO DA PÁGINA (FUNDO BRANCO)
# ============================================================
st.set_page_config(
    page_title="Análise Técnica — SWS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
#  ESTILO CLEAN (função)
# ============================================================
def set_clean_style():
    clean_css = """
    <style>
    
    /* Fundo totalmente branco */
    .stApp {
        background-color: #FFFFFF !important;
    }

    /* Títulos */
    h1, h2, h3, h4, h5 {
        color: #1A1A1A !important;
        font-weight: 700 !important;
    }

    /* Sidebar com destaque */
    section[data-testid="stSidebar"] {
        background-color: #F5F7FA !important;
        padding: 15px;
        border-right: 1px solid #DDD;
    }

    /* Labels dos filtros */
    .css-17eq0hr, .stSelectbox label, .stSlider label {
        color: #333 !important;
        font-weight: 600;
    }

    /* Caixas e widgets */
    .stSelectbox, .stMultiSelect, .stSlider, .stDateInput {
        background-color: white !important;
    }

    /* Métricas mais visíveis */
    [data-testid="stMetricLabel"] {
        font-size: 17px;
        color: #555 !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px;
        font-weight: 800;
        color: #111 !important;
    }

    </style>
    """
    st.markdown(clean_css, unsafe_allow_html=True)


# Ativar estilo clean
set_clean_style()

# ============================================================
#  CABEÇALHO
# ============================================================
st.markdown("""
<h1>📊 Análise Técnica — Arquivos Enviados (SWS)</h1>
<h4 style='color:#555;'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
#  UPLOAD ARQUIVO
# ============================================================
uploaded_file = st.file_uploader("📂 Envie o arquivo SWS (.xlsx ou .xls)", type=["xlsx", "xls"])

def read_first_sheet(file):
    try:
        xls = pd.ExcelFile(file)
        return pd.read_excel(file, sheet_name=xls.sheet_names[0])
    except:
        return pd.read_excel(file)

# ============================================================
#  PROCESSAMENTO DO ARQUIVO
# ============================================================
if uploaded_file:

    try:
        excel = pd.ExcelFile(uploaded_file)
        sheets = [s for s in excel.sheet_names if "CDG" not in s.upper()]  # EXCLUI CDG

        # Se houver SWS1 e SWS2 → escolher
        selected = st.selectbox("📌 Selecione a aba para análise", sheets)
        df = pd.read_excel(uploaded_file, sheet_name=selected)
        st.success("✅ Arquivo carregado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        st.stop()

    # Normalização
    df.columns = [str(c).strip() for c in df.columns]

    # Detectar colunas automaticamente
    date_col = next((c for c in ["work_date", "date", "data"] if c in df.columns), None)
    code_col = next((c for c in ["code", "codigo", "cod"] if c in df.columns), None)
    eff_col = next((c for c in ["over_effective_area", "effective_area"] if c in df.columns), None)
    not_eff_col = next((c for c in ["over_not_effective_area", "not_effective_area"] if c in df.columns), None)
    prestador_col = next((c for c in ["prestador", "provider"] if c in df.columns), None)
    status_col = next((c for c in ["Status", "status"] if c in df.columns), None)
    error_col = next((c for c in ["error_msg", "error"] if c in df.columns), None)

    # ----------------------------------------------------------
    # Sidebar filtros
    # ----------------------------------------------------------
    st.sidebar.header("Filtros")

    def filter_option(colname):
        if colname:
            vals = ["Todos"] + sorted(df[colname].dropna().astype(str).unique().tolist())
            return st.sidebar.multiselect(colname, vals, ["Todos"])
        return ["Todos"]

    prest_filter = filter_option(prestador_col)
    status_filter = filter_option(status_col)
    code_filter = filter_option(code_col)

    if date_col:
        min_d, max_d = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input("Datas", (min_d, max_d))

    st.sidebar.markdown("---")

    # ----------------------------------------------------------
    # Aplicar filtros
    # ----------------------------------------------------------
    df_filt = df.copy()

    if prestador_col and "Todos" not in prest_filter:
        df_filt = df_filt[df_filt[prestador_col].astype(str).isin(prest_filter)]

    if status_col and "Todos" not in status_filter:
        df_filt = df_filt[df_filt[status_col].astype(str).isin(status_filter)]

    if code_col and "Todos" not in code_filter:
        df_filt = df_filt[df_filt[code_col].astype(str).isin(code_filter)]

    if date_col:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filt = df_filt[(df_filt[date_col] >= start) & (df_filt[date_col] <= end)]

    if df_filt.empty:
        st.warning("Nenhum dado com os filtros aplicados.")
        st.stop()

    # ----------------------------------------------------------
    # KPIs
    # ----------------------------------------------------------
    k1, k2, k3 = st.columns(3)

    k1.metric("Registros filtrados", len(df_filt))
    if eff_col:
        k2.metric("Área efetiva total", f"{df_filt[eff_col].sum():,.2f}")
    if not_eff_col:
        k3.metric("Área não efetiva total", f"{df_filt[not_eff_col].sum():,.2f}")

    st.markdown("---")

    # ----------------------------------------------------------
    # Gráficos
    # ----------------------------------------------------------
    if code_col:
        st.subheader("📌 Top códigos")
        vc = df_filt[code_col].astype(str).value_counts().head(10)
        st.plotly_chart(px.bar(vc, title="Top 10 códigos"), use_container_width=True)

    if date_col and eff_col:
        st.subheader("📈 Evolução diária (Área efetiva)")
        df_time = df_filt.groupby(date_col)[eff_col].sum().reset_index()
        st.plotly_chart(px.line(df_time, x=date_col, y=eff_col), use_container_width=True)

else:
    st.info("Envie um arquivo Excel para iniciar a análise.")
