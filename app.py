import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# ============================================================
#  FUNÇÃO: Inserir imagem de fundo otimizada (nitidez)
# ============================================================
def add_bg_from_local(image_file: str, overlay_opacity: float = 0.30):
    try:
        with open(image_file, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode()
    except Exception:
        return

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        filter: brightness(1.07);
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,{overlay_opacity});
        backdrop-filter: blur(1.5px);
        z-index: 0;
    }}

    .stApp > * {{
        position: relative;
        z-index: 1;
    }}

    .stCard, .css-1d391kg, .css-12oz5g7 {{
        background: rgba(18,18,18,0.48) !important;
        border-radius: 10px;
        padding: 12px;
        backdrop-filter: blur(4px);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

add_bg_from_local("/mnt/data/imagesbackground.png", overlay_opacity=0.30)

# ============================================================
#  Configuração Streamlit
# ============================================================
st.set_page_config(page_title="Analise_Dados_SWS2", layout="wide", initial_sidebar_state="expanded")

st.markdown("<h1 style='margin-bottom:6px'>📊 Analise Técnica  Arquivos Enviados — SWS</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color:lightgray;margin-top:0px'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
#  CACHE DE LEITURA
# ============================================================
@st.cache_data
def load_excel(file):
    return pd.read_excel(file, sheet_name=None)

# ============================================================
#  Upload do arquivo
# ============================================================
uploaded_file = st.file_uploader(
    "📂 Envie o arquivo SWS (.xlsx) — contendo SWS1/SWS2",
    type=["xlsx", "xls"]
)

if uploaded_file:
    with st.spinner("⏳ Processando arquivo, aguarde..."):
        try:
            sheets_dict = load_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()

    st.success("Arquivo carregado com sucesso!")

    # ============================================================
    #  REMOVER ABA "Alarmes - CDG"
    # ============================================================
    abas_validas = [
        s for s in sheets_dict.keys()
        if s.lower().strip() != "alarmes - cdg".lower().strip()
    ]

    if not abas_validas:
        st.error("Nenhuma planilha válida encontrada (SWS1 / SWS2).")
        st.stop()

    prioridade = [s for s in ["SWS1", "SWS2"] if s in abas_validas]
    outras = [s for s in abas_validas if s not in prioridade]

    # ============================================================
    #  SELETOR DESTACADO
    # ============================================================
    st.markdown("""
    <div style="
        background-color: rgba(255, 255, 255, 0.08);
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #00c3ff;
        margin-bottom: 10px;
    ">
        <h4 style="margin: 0; color: #ffffff; font-size: 18px;">
            🔎 <b>Selecione a aba para análise</b>
        </h4>
    </div>
    """, unsafe_allow_html=True)

    escolha = st.selectbox("", prioridade + outras)
    df = sheets_dict[escolha]

    # ============================================================
    # NORMALIZAR COLUNAS
    # ============================================================
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Detectar colunas
    date_col = next((c for c in ["work_date","date","data","workdate"] if c in df.columns), None)
    code_col = next((c for c in ["code","codigo","cod","codigo_id"] if c in df.columns), None)
    eff_col = next((c for c in ["over_effective_area","overeffectivearea","effective_area","area_efetiva"] if c in df.columns), None)
    not_eff_col = next((c for c in ["over_not_effective_area","overnoteffectivearea","not_effective_area","area_nao_efetiva"] if c in df.columns), None)
    serial_col = "serial_number" if "serial_number" in df.columns else ("serial" if "serial" in df.columns else None)
    prestador_col = "prestador" if "prestador" in df.columns else ("provider" if "provider" in df.columns else None)
    status_col = "status" if "status" in df.columns else None
    error_col = "error_msg" if "error_msg" in df.columns else None

    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if eff_col:
        df[eff_col] = pd.to_numeric(df[eff_col], errors="coerce").fillna(0)

    if not_eff_col:
        df[not_eff_col] = pd.to_numeric(df[not_eff_col], errors="coerce").fillna(0)

    if error_col:
        df[error_col] = df[error_col].astype(str).replace({"nan":"", "None":""})
    else:
        df["error_msg_clean"] = ""
        error_col = "error_msg_clean"

    # ============================================================
    #  FILTROS
    # ============================================================
    st.sidebar.header("Filtros rápidos")

    def clean_filter(values):
        return [] if ("Todos" in values) else values

    # Serial
    if serial_col:
        ops = ["Todos"] + sorted(df[serial_col].dropna().astype(str).unique())
        serial_sel = clean_filter(st.sidebar.multiselect("Serial Number", ops, default=["Todos"]))
    else:
        serial_sel = []

    # Prestador
    if prestador_col:
        ops = ["Todos"] + sorted(df[prestador_col].dropna().astype(str).unique())
        prestador_sel = clean_filter(st.sidebar.multiselect("Prestador", ops, default=["Todos"]))
    else:
        prestador_sel = []

    # Status
    if status_col:
        ops = ["Todos"] + sorted(df[status_col].dropna().astype(str).unique())
        status_sel = clean_filter(st.sidebar.multiselect("Status", ops, default=["Todos"]))
    else:
        status_sel = []

    # Erros
    ops = ["Todos"] + sorted([e for e in df[error_col].unique() if str(e).strip()!=""])
    error_sel = clean_filter(st.sidebar.multiselect("Erros (error_msg)", ops, default=["Todos"]))

    # Código
    if code_col:
        ops = ["Todos"] + sorted(df[code_col].dropna().astype(str).unique())
        code_sel = clean_filter(st.sidebar.multiselect("Código", ops, default=["Todos"]))
    else:
        code_sel = []

    # Data
    if date_col:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            date_range = st.sidebar.date_input("Intervalo de datas", (min_date.date(), max_date.date()))
        else:
            date_range = (None, None)
    else:
        date_range = (None, None)

    st.sidebar.markdown("---")
    st.sidebar.markdown("🛈 Dica: selecione 'Todos' para desativar o filtro correspondente.")

    # ============================================================
    #  APLICAR FILTROS
    # ============================================================
    df_filt = df.copy()

    if serial_sel:
        df_filt = df_filt[df_filt[serial_col].astype(str).isin(serial_sel)]

    if prestador_sel:
        df_filt = df_filt[df_filt[prestador_col].astype(str).isin(prestador_sel)]

    if status_sel:
        df_filt = df_filt[df_filt[status_col].astype(str).isin(status_sel)]

    if error_sel:
        df_filt = df_filt[df_filt[error_col].astype(str).isin(error_sel)]

    if code_sel:
        df_filt = df_filt[df_filt[code_col].astype(str).isin(code_sel)]

    if date_col and None not in date_range:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        df_filt = df_filt[(df_filt[date_col] >= start) & (df_filt[date_col] <= end)]

    if df_filt.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    # ============================================================
    #  KPIs
    # ============================================================
    total_records = len(df_filt)
    total_effective = df_filt[eff_col].sum() if eff_col else 0
    total_not_effective = df_filt[not_eff_col].sum() if not_eff_col else 0
    avg_effective = df_filt[eff_col].mean() if eff_col else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registros (filtrados)", f"{total_records}")
    c2.metric("Área Efetiva Total", f"{total_effective:,.2f}")
    c3.metric("Área Não Efetiva Total", f"{total_not_effective:,.2f}")
    c4.metric("Área Efetiva Média", f"{avg_effective:,.2f}")

    st.markdown("---")

    # ============================================================
    #  GRÁFICOS
    # ============================================================

    # Top códigos
    st.subheader("🏷️ Top 10 Códigos")
    if code_col:
        df_codes = df_filt[code_col].astype(str).value_counts().reset_index()
        df_codes.columns = ["code","count"]
        fig = px.bar(df_codes.head(10), x="code", y="count")
        st.plotly_chart(fig, use_container_width=True)

    # Série temporal
    st.subheader("📈 Evolução Temporal — Área Efetiva")
    if date_col and eff_col:
        df_time = df_filt.groupby(pd.Grouper(key=date_col, freq="D"))[eff_col].sum().reset_index()
        fig = px.line(df_time, x=date_col, y=eff_col, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # Erros
    st.subheader("🧭 Distribuição por Erros")
    df_err = df_filt[error_col].replace({"": "Sem erro"})
    df_err = df_err.value_counts().reset_index()
    df_err.columns = ["erro","count"]
    fig = px.pie(df_err.head(10), names="erro", values="count")
    st.plotly_chart(fig, use_container_width=True)

    # Prestadores
    st.subheader("🔁 Área Efetiva vs Não Efetiva — Top Prestadores")
    if prestador_col and eff_col and not_eff_col:
        df_p = df_filt.groupby(prestador_col).agg({
            eff_col: "sum",
            not_eff_col: "sum"
        }).reset_index()
        df_p["total"] = df_p[eff_col] + df_p[not_eff_col]
        df_p = df_p.sort_values("total", ascending=False).head(10)

        df_melt = df_p.melt(id_vars=prestador_col,
                            value_vars=[eff_col, not_eff_col],
                            var_name="tipo", value_name="valor")
        fig = px.bar(df_melt, x="valor", y=prestador_col, color="tipo", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.caption("Sistema SWS - Desenvolvido por Silva Adenilton (Denis) — Dashboard profissional")

else:
    st.info("Envie um arquivo Excel para começar.")
