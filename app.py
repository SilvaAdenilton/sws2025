import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ============================================================
# ESTILO CLEAN COM BANNER NO TOPO
# ============================================================
def load_banner(image_path):
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <div style='width:100%;height:180px;overflow:hidden;margin-bottom:15px;border-radius:8px;'>
                <img src='data:image/png;base64,{encoded}' 
                     style='width:100%;object-fit:cover;'>
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.warning("⚠ Não foi possível carregar o banner superior.")


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Análise Técnica — SWS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS clean e sidebar estreita
st.markdown("""
<style>

.stApp {
    background-color: #FFFFFF !important;
}

/* Sidebar mais fina */
section[data-testid="stSidebar"] {
    background-color: #F5F6FA !important;
    width: 260px !important;
}

/* Labels de filtros */
label, .stSelectbox label, .stMultiSelect label {
    color: #333 !important;
    font-weight: 600 !important;
}

/* Títulos */
h1, h2, h3, h4 {
    color: #222 !important;
    font-weight: 800 !important;
}

/* Cards (metric) */
[data-testid="stMetricLabel"] {
    font-size: 15px;
    color: #555;
}
[data-testid="stMetricValue"] {
    font-size: 24px;
    font-weight: 900;
    color: #000;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# EXIBE BANNER NO TOPO
# ============================================================
load_banner("images/baixados.png")

# ============================================================
# TÍTULO
# ============================================================
st.markdown("""
<h1>📊 Análise Técnica — Arquivos Enviados (SWS)</h1>
<h4 style='color:#555;'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# UPLOAD DO ARQUIVO
# ============================================================
uploaded_file = st.file_uploader(
    "📂 Envie o arquivo SWS (.xlsx/.xls)",
    type=["xlsx","xls"]
)

def read_first_sheet(file):
    xls = pd.ExcelFile(file)
    return pd.read_excel(file, sheet_name=xls.sheet_names[0])

# ============================================================
# PROCESSAMENTO DO ARQUIVO
# ============================================================
if uploaded_file:

    try:
        excel = pd.ExcelFile(uploaded_file)
        sheets = [s for s in excel.sheet_names if "CDG" not in s.upper()]  # remove CDG

        selected_sheet = st.selectbox("📌 Selecione a aba para análise", sheets)
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

        st.success("Arquivo carregado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")
        st.stop()

    # Normaliza colunas
    df.columns = [str(c).strip() for c in df.columns]

    # Detectar colunas automaticamente
    date_col = next((c for c in ["work_date","date","data"] if c in df.columns), None)
    code_col = next((c for c in ["code","codigo","cod"] if c in df.columns), None)
    eff_col  = next((c for c in ["over_effective_area","effective_area"] if c in df.columns), None)
    not_col  = next((c for c in ["over_not_effective_area","not_effective_area"] if c in df.columns), None)
    prest_col = next((c for c in ["prestador","provider"] if c in df.columns), None)
    status_col = next((c for c in ["Status","status"] if c in df.columns), None)

    # ================= SIDEBAR =================
    st.sidebar.header("Filtros")

    def sidebar_filter(col):
        if col:
            options = ["Todos"] + sorted(df[col].dropna().astype(str).unique())
            return st.sidebar.multiselect(col, options, ["Todos"])
        return ["Todos"]

    f_prest = sidebar_filter(prest_col)
    f_status = sidebar_filter(status_col)
    f_code = sidebar_filter(code_col)

    if date_col:
        min_d, max_d = df[date_col].min(), df[date_col].max()
        f_dates = st.sidebar.date_input("Datas", (min_d, max_d))

    # Aplicar filtros
    df_f = df.copy()

    if prest_col and "Todos" not in f_prest:
        df_f = df_f[df_f[prest_col].astype(str).isin(f_prest)]

    if status_col and "Todos" not in f_status:
        df_f = df_f[df_f[status_col].astype(str).isin(f_status)]

    if code_col and "Todos" not in f_code:
        df_f = df_f[df_f[code_col].astype(str).isin(f_code)]

    if date_col:
        ini, fim = pd.to_datetime(f_dates[0]), pd.to_datetime(f_dates[1])
        df_f = df_f[(df_f[date_col] >= ini) & (df_f[date_col] <= fim)]

    if df_f.empty:
        st.warning("Nenhum dado encontrado com os filtros.")
        st.stop()

    # ================= KPIs =================
    k1, k2, k3 = st.columns(3)

    k1.metric("Registros filtrados", len(df_f))
    if eff_col:
        k2.metric("Área efetiva", f"{df_f[eff_col].sum():,.2f}")
    if not_col:
        k3.metric("Área não efetiva", f"{df_f[not_col].sum():,.2f}")

    st.markdown("---")

    # ================= GRÁFICOS =================
    if code_col:
        st.subheader("🏷 Top 10 códigos")
        vc = df_f[code_col].astype(str).value_counts().head(10)
        st.plotly_chart(px.bar(vc, title="Top códigos"), use_container_width=True)

    if date_col and eff_col:
        st.subheader("📈 Evolução diária")
        df_time = df_f.groupby(date_col)[eff_col].sum().reset_index()
        st.plotly_chart(px.line(df_time, x=date_col, y=eff_col), use_container_width=True)

else:
    st.info("Envie um arquivo Excel para iniciar a análise.")
