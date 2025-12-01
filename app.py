import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO

# ============================================================
#  FUNÇÃO: Inserir imagem de fundo otimizada (WEB / GitHub)
# ============================================================
def add_bg_from_local(image_path: str, opacity: float = 0.28):
    """
    Insere imagem de fundo carregada do repositório (pasta /images).
    Aplicada via CSS com overlay escuro suave.
    """
    try:
        with open(image_path, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode()

        css = f"""
        <style>
        .stApp {{
            background: url("data:image/png;base64,{encoded_string}");
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}

        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,{opacity});
            z-index: 0;
        }}

        .stApp > * {{
            position: relative;
            z-index: 1;
        }}
        </style>
        """

        st.markdown(css, unsafe_allow_html=True)

    except Exception as e:
        st.warning(f"⚠ Não foi possível carregar a imagem de fundo.\nCaminho: {image_path}")
        st.write("Erro:", e)


# ============================================================
#  APLICAR FUNDO
# ============================================================
add_bg_from_local("images/background.png", opacity=0.30)

# ============================================================
#  CONFIGURAÇÕES DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Analise Técnica — Arquivos Enviados (SWS)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título
st.markdown("""
<h1 style='margin-bottom:4px;'>📊 Analise Técnica — Arquivos Enviados (SWS)</h1>
<h4 style='color:#e0e0e0;margin-top:0px;'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>
<br>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
#  UPLOAD DO ARQUIVO
# ============================================================
uploaded_file = st.file_uploader(
    "📂 Envie arquivo SWS (xlsx/xls):",
    type=["xlsx", "xls"]
)

def read_first_sheet(xl_file):
    try:
        xls = pd.ExcelFile(xl_file)
        first_sheet = xls.sheet_names[0]
        return pd.read_excel(xl_file, sheet_name=first_sheet)
    except:
        return pd.read_excel(xl_file)

# ============================================================
#  PROCESSAMENTO APÓS UPLOAD
# ============================================================
if uploaded_file:

    try:
        df_all = pd.ExcelFile(uploaded_file)

        sheet_names = df_all.sheet_names
        sheet_names = [s for s in sheet_names if "CDG" not in s.upper()]  # REMOVE CDG

        # Se tiver SWS1 e SWS2 → opção de escolha
        if "SWS1" in sheet_names or "SWS2" in sheet_names:
            selected_sheet = st.selectbox("📌 Selecione a aba para análise:", sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        else:
            df = read_first_sheet(uploaded_file)

        st.success("✅ Arquivo carregado com sucesso!")

    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        st.stop()

    # ============================================================
    #  NORMALIZAÇÃO DAS COLUNAS
    # ============================================================
    df.columns = [str(c).strip() for c in df.columns]

    # Detectar possíveis nomes
    date_col = next((c for c in ["work_date", "date", "data", "workdate"] if c in df.columns), None)
    code_col = next((c for c in ["code", "codigo", "cod", "codigo_id"] if c in df.columns), None)
    eff_col = next((c for c in ["over_effective_area", "effective_area", "area_efetiva"] if c in df.columns), None)
    not_eff_col = next((c for c in ["over_not_effective_area", "not_effective_area", "area_nao_efetiva"] if c in df.columns), None)
    serial_col = next((c for c in ["serial_number", "serial"] if c in df.columns), None)
    prestador_col = next((c for c in ["prestador", "provider"] if c in df.columns), None)
    status_col = next((c for c in ["Status", "status"] if c in df.columns), None)
    error_col = next((c for c in ["error_msg", "error"] if c in df.columns), None)

    # ============================================================
    #  LIMPEZA E TRATAMENTO
    # ============================================================
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    if eff_col:
        df[eff_col] = pd.to_numeric(df[eff_col], errors="coerce").fillna(0)

    if not_eff_col:
        df[not_eff_col] = pd.to_numeric(df[not_eff_col], errors="coerce").fillna(0)

    if error_col:
        df[error_col] = df[error_col].astype(str).str.strip()
        df[error_col] = df[error_col].replace({"nan": "", "None": ""})
    else:
        df["error_msg_clean"] = ""
        error_col = "error_msg_clean"

    # ============================================================
    #  SIDEBAR — FILTROS
    # ============================================================
    st.sidebar.header("Filtros")

    # Função auxiliar para montar multiselect
    def build_filter(col):
        options = ["Todos"] + sorted(df[col].dropna().astype(str).unique().tolist())
        return st.sidebar.multiselect(col, options, default=["Todos"])

    # Filtros dinâmicos
    serial_sel = build_filter(serial_col) if serial_col else ["Todos"]
    prestador_sel = build_filter(prestador_col) if prestador_col else ["Todos"]
    status_sel = build_filter(status_col) if status_col else ["Todos"]
    error_sel = build_filter(error_col) if error_col else ["Todos"]
    code_sel = build_filter(code_col) if code_col else ["Todos"]

    if date_col:
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.sidebar.date_input("Intervalo de Datas", (min_date, max_date))
    else:
        date_range = (None, None)

    st.sidebar.markdown("---")
    st.sidebar.caption("🛈 Use 'Todos' para não filtrar.")

    # ============================================================
    #  APLICAÇÃO DOS FILTROS
    # ============================================================
    df_filt = df.copy()

    def apply_filter(col, selected):
        if col and "Todos" not in selected:
            df_filt[col] = df_filt[col].astype(str)
            return df_filt[df_filt[col].isin(selected)]
        return df_filt

    df_filt = apply_filter(serial_col, serial_sel)
    df_filt = apply_filter(prestador_col, prestador_sel)
    df_filt = apply_filter(status_col, status_sel)
    df_filt = apply_filter(error_col, error_sel)
    df_filt = apply_filter(code_col, code_sel)

    if date_col and date_range:
        start, end = map(pd.to_datetime, date_range)
        df_filt = df_filt[(df_filt[date_col] >= start) & (df_filt[date_col] <= end)]

    if df_filt.empty:
        st.warning("Nenhum dado encontrado com os filtros.")
        st.stop()

    # ============================================================
    #  KPI's
    # ============================================================
    total_records = len(df_filt)
    total_eff = df_filt[eff_col].sum() if eff_col else 0
    total_not_eff = df_filt[not_eff_col].sum() if not_eff_col else 0
    avg_eff = df_filt[eff_col].mean() if eff_col else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros Filtrados", total_records)
    k2.metric("Área Efetiva Total", f"{total_eff:,.2f}")
    k3.metric("Área Não Efetiva Total", f"{total_not_eff:,.2f}")
    k4.metric("Média Área Efetiva", f"{avg_eff:,.2f}")

    st.markdown("---")

    # ============================================================
    #  GRÁFICOS
    # ============================================================

    # Top 10 códigos
    if code_col:
        st.subheader("🏷 Top 10 Códigos")
        df_codes = df_filt[code_col].astype(str).value_counts().head(10)
        st.plotly_chart(px.bar(df_codes, title="Top Códigos"), use_container_width=True)

    # Linha temporal área efetiva
    if date_col and eff_col:
        st.subheader("📈 Evolução Área Efetiva")
        df_time = df_filt.groupby(date_col)[eff_col].sum().reset_index()
        st.plotly_chart(px.line(df_time, x=date_col, y=eff_col, markers=True), use_container_width=True)

    # Erros
    st.subheader("🧭 Distribuição de Erros")
    df_err = df_filt[error_col].replace({"": "Sem erro"}).value_counts().head(10)
    st.plotly_chart(px.pie(df_err, names=df_err.index, values=df_err.values), use_container_width=True)

    # Prestador
    if prestador_col and eff_col:
        st.subheader("🔁 Efetiva vs Não Efetiva por Prestador")
        df_prest = df_filt.groupby(prestador_col)[[eff_col, not_eff_col]].sum().reset_index()
        df_prest["total"] = df_prest[eff_col] + df_prest[not_eff_col]
        df_top = df_prest.nlargest(10, "total")
        st.plotly_chart(
            px.bar(
                df_top.melt(id_vars=prestador_col, value_vars=[eff_col, not_eff_col]),
                x="value", y=prestador_col, color="variable", orientation="h"
            ),
            use_container_width=True
        )

else:
    st.info("Envie um arquivo Excel para iniciar a análise.")
