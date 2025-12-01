import streamlit as st
import pandas as pd
import base64

# ============================================================
# LOGO SUPERIOR
# ============================================================
def load_logo(image_path):
    """Exibe o logo no topo do dashboard."""
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:18px; margin-bottom:25px;'>
                <img src='data:image/png;base64,{encoded}'
                     style='width:110px; height:auto; border-radius:8px;'>
                <div>
                    <h1 style='margin:0; padding:0; font-size:36px; color:#000;'>
                        📊 Análise Técnica — Arquivos Enviados (SWS)
                    </h1>
                    <h4 style='margin:0; padding:0; color:#444;'>
                        Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b>
                    </h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.warning("⚠ Não foi possível carregar o logo.")


# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(page_title="Analise Técnica SWS", layout="wide")
load_logo("images/baixados.png")

st.markdown("### 📂 Envie o arquivo SWS (.xlsx / .xls)")
uploaded_file = st.file_uploader("Arraste ou selecione o arquivo", type=["xlsx", "xls"])

if not uploaded_file:
    st.info("Envie um arquivo Excel para iniciar a análise.")
    st.stop()

# ============================================================
# CARREGAR ARQUIVO E ABA
# ============================================================
try:
    sheets = pd.ExcelFile(uploaded_file).sheet_names
    df_all = pd.read_excel(uploaded_file, sheet_name=None)

    chosen_sheet = st.selectbox("⭐ Selecione a aba para análise", sheets)
    df = df_all[chosen_sheet]

except Exception as e:
    st.error(f"Erro ao ler arquivo: {e}")
    st.stop()

st.success("Arquivo carregado com sucesso!")

# ============================================================
# AJUSTAR NOMES DE COLUNAS
# ============================================================
df.columns = [c.strip().lower() for c in df.columns]

required_cols = [
    "prestador", "serial_number", "status",
    "over_effective_area", "over_not_effective_area"
]

missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"❌ As seguintes colunas obrigatórias não existem na aba selecionada:\n\n{missing}")
    st.stop()

# Converter áreas numéricas
df["over_effective_area"] = pd.to_numeric(df["over_effective_area"], errors="coerce").fillna(0)
df["over_not_effective_area"] = pd.to_numeric(df["over_not_effective_area"], errors="coerce").fillna(0)

# ============================================================
# SIDEBAR — FILTROS
# ============================================================
st.sidebar.header("Filtros")

prest_options = ["Todos"] + sorted(df["prestador"].dropna().astype(str).unique())
prest_sel = st.sidebar.selectbox("Prestador", prest_options)

serial_options = ["Todos"] + sorted(df["serial_number"].dropna().astype(str).unique())
serial_sel = st.sidebar.selectbox("Serial Number", serial_options)

status_options = ["Todos"] + sorted(df["status"].dropna().astype(str).unique())
status_sel = st.sidebar.selectbox("Status", status_options)

# ============================================================
# APLICAR FILTROS
# ============================================================
df_filt = df.copy()

if prest_sel != "Todos":
    df_filt = df_filt[df_filt["prestador"].astype(str) == prest_sel]

if serial_sel != "Todos":
    df_filt = df_filt[df_filt["serial_number"].astype(str) == serial_sel]

if status_sel != "Todos":
    df_filt = df_filt[df_filt["status"].astype(str) == status_sel]

if df_filt.empty:
    st.warning("⚠ Nenhum dado encontrado com os filtros aplicados.")
    st.stop()

# ============================================================
# KPIs — SOMATÓRIOS
# ============================================================
st.markdown("---")

k1, k2 = st.columns(2)

k1.metric(
    "Área Efetiva Total (Filtro Aplicado)",
    f"{df_filt['over_effective_area'].sum():,.2f}"
)

k2.metric(
    "Área Não Efetiva Total (Filtro Aplicado)",
    f"{df_filt['over_not_effective_area'].sum():,.2f}"
)

# ============================================================
# TABELA DE RESULTADOS
# ============================================================
st.markdown("### 📄 Registros filtrados")
st.dataframe(df_filt, use_container_width=True)
