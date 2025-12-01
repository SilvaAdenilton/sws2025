import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ============================================================
#  FUNÇÃO: Fundo Profissional Moderno
# ============================================================
def add_bg_from_local(image_file: str, opacity: float = 0.25):
    try:
        with open(image_file, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
    except Exception:
        return

    css = f"""
    <style>
    .stApp {{
        background: url("data:image/png;base64,{encoded}") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        filter: brightness(1.03);
    }}

    /* Camada escura suave */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,{opacity});
        backdrop-filter: blur(2px);
        z-index: 0;
    }}

    .stApp > * {{
        position: relative;
        z-index: 1;
    }}

    /* Painéis */
    .css-1d391kg, .css-12oz5g7 {{
        background: rgba(18,18,18,0.35) !important;
        backdrop-filter: blur(5px);
        border-radius: 12px;
        padding: 10px !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Aplica imagem panorâmica como fundo
add_bg_from_local("/mnt/data/imagesbackground.png", opacity=0.28)

# ============================================================
# Configuração
# ============================================================
st.set_page_config(page_title="Analise Técnica SWS", layout="wide")

st.markdown("<h1>📊 Analise Técnica — Arquivos Enviados (SWS)</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color:#ccc'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# Cache de leitura
# ============================================================
@st.cache_data
def load_excel(file):
    return pd.read_excel(file, sheet_name=None)

# ============================================================
# Upload
# ============================================================
uploaded = st.file_uploader("📂 Envie arquivo SWS (xlsx/xls)", type=["xlsx", "xls"])

if uploaded:

    with st.spinner("⏳ Processando arquivo, aguarde..."):
        sheets_dict = load_excel(uploaded)

    st.success("Arquivo carregado com sucesso!")

    # Remove planilha CDG
    valid_sheets = [s for s in sheets_dict if s.lower() != "alarmes - cdg".lower()]

    # Seleção destacada
    st.markdown("""
    <div style="
        background: rgba(255,255,255,0.1);
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #00c3ff;
        margin-bottom: 8px;">
        <span style="font-size:18px;color:white;">🔎 <b>Selecione a aba para análise</b></span>
    </div>
    """, unsafe_allow_html=True)

    priority = [s for s in ["SWS1", "SWS2"] if s in valid_sheets]
    others = [s for s in valid_sheets if s not in priority]

    selected_sheet = st.selectbox("", priority + others)
    df = sheets_dict[selected_sheet]

    # ============================================================
    # LIMPEZA DE COLUNAS
    # ============================================================
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Mapear possíveis colunas
    date_col = next((c for c in ["date", "work_date", "data"] if c in df.columns), None)
    code_col = next((c for c in ["code", "codigo"] if c in df.columns), None)
    eff_col = next((c for c in ["over_effective_area","effective_area"] if c in df.columns), None)
    not_eff_col = next((c for c in ["over_not_effective_area","not_effective_area"] if c in df.columns), None)
    serial_col = "serial_number" if "serial_number" in df.columns else None
    prestador_col = "prestador" if "prestador" in df.columns else None
    status_col = "status" if "status" in df.columns else None
    error_col = "error_msg" if "error_msg" in df.columns else None

    # Conversões
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if eff_col:
        df[eff_col] = pd.to_numeric(df[eff_col], errors="coerce").fillna(0)
    if not_eff_col:
        df[not_eff_col] = pd.to_numeric(df[not_eff_col], errors="coerce").fillna(0)

    # ============================================================
    # FILTROS
    # ============================================================
    st.sidebar.header("Filtros")

    def clear(val): return [] if "Todos" in val else val

    # Serial
    if serial_col:
        ops = ["Todos"] + sorted(df[serial_col].dropna().astype(str).unique())
        serial_sel = clear(st.sidebar.multiselect("Serial Number", ops, default=["Todos"]))
    else:
        serial_sel = []

    # Prestador
    if prestador_col:
        ops = ["Todos"] + sorted(df[prestador_col].dropna().astype(str).unique())
        prestador_sel = clear(st.sidebar.multiselect("Prestador", ops, default=["Todos"]))
    else:
        prestador_sel = []

    # Status
    if status_col:
        ops = ["Todos"] + sorted(df[status_col].dropna().astype(str).unique())
        status_sel = clear(st.sidebar.multiselect("Status", ops, default=["Todos"]))
    else:
        status_sel = []

    # Erros
    if error_col:
        ops = ["Todos"] + sorted([e for e in df[error_col].unique() if str(e).strip()!=""])
        error_sel = clear(st.sidebar.multiselect("Erros", ops, default=["Todos"]))
    else:
        error_sel = []

    # Código
    if code_col:
        ops = ["Todos"] + sorted(df[code_col].astype(str).unique())
        code_sel = clear(st.sidebar.multiselect("Código", ops, default=["Todos"]))
    else:
        code_sel = []

    # Data
    if date_col:
        min_dt, max_dt = df[date_col].min(), df[date_col].max()
        date_sel = st.sidebar.date_input("Intervalo de Datas", (min_dt, max_dt))
    else:
        date_sel = None

    st.sidebar.markdown("---")
    st.sidebar.caption("Selecione 'Todos' para desativar filtros.")

    # ============================================================
    # Aplicar Filtros
    # ============================================================
    df_f = df.copy()

    if serial_sel:
        df_f = df_f[df_f[serial_col].astype(str).isin(serial_sel)]
    if prestador_sel:
        df_f = df_f[df_f[prestador_col].astype(str).isin(prestador_sel)]
    if status_sel:
        df_f = df_f[df_f[status_col].astype(str).isin(status_sel)]
    if error_sel:
        df_f = df_f[df_f[error_col].astype(str).isin(error_sel)]
    if code_sel:
        df_f = df_f[df_f[code_col].astype(str).isin(code_sel)]
    if date_sel and date_col:
        start, end = pd.to_datetime(date_sel[0]), pd.to_datetime(date_sel[1])
        df_f = df_f[(df_f[date_col] >= start) & (df_f[date_col] <= end)]

    # ============================================================
    # KPIs
    # ============================================================
    st.markdown("### 📌 Indicadores Gerais")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros", f"{len(df_f)}")
    c2.metric("Área Efetiva Total", f"{df_f[eff_col].sum():,.2f}" if eff_col else "0")
    c3.metric("Área Não Efetiva", f"{df_f[not_eff_col].sum():,.2f}" if not_eff_col else "0")
    c4.metric("Efetiva Média", f"{df_f[eff_col].mean():,.2f}" if eff_col else "0")

    st.markdown("---")

    # ============================================================
    # Gráficos
    # ============================================================

    # Top códigos
    if code_col:
        st.subheader("🏷️ Top 10 Códigos")
        df_codes = df_f[code_col].astype(str).value_counts().head(10).reset_index()
        df_codes.columns = ["Código", "Quantidade"]
        st.plotly_chart(px.bar(df_codes, x="Código", y="Quantidade"), use_container_width=True)

    # Evolução
    if date_col and eff_col:
        st.subheader("📈 Evolução da Área Efetiva")
        df_time = df_f.groupby(date_col)[eff_col].sum().reset_index()
        st.plotly_chart(px.line(df_time, x=date_col, y=eff_col, markers=True), use_container_width=True)

    # Erros
    if error_col:
        st.subheader("🧭 Distribuição de Erros")
        df_err = df_f[error_col].replace({"":"Sem erro"}).value_counts().head(10).reset_index()
        df_err.columns = ["Erro","Total"]
        st.plotly_chart(px.pie(df_err, names="Erro", values="Total"), use_container_width=True)

    # Prestadores
    if prestador_col and eff_col and not_eff_col:
        st.subheader("🔁 Efetiva x Não Efetiva por Prestador")
        df_p = df_f.groupby(prestador_col)[[eff_col,not_eff_col]].sum().reset_index()
        df_p = df_p.sort_values(eff_col, ascending=False).head(10)
        df_m = df_p.melt(id_vars=prestador_col, var_name="Tipo", value_name="Área")
        st.plotly_chart(px.bar(df_m, x="Área", y=prestador_col, color="Tipo", orientation="h"), use_container_width=True)

    st.markdown("---")
    st.caption("Sistema SWS — Desenvolvido por Silva Adenilton (Denis)")

else:
    st.info("Envie um arquivo Excel para começar.")
