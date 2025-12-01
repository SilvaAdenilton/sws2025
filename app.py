import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# -------------------------------------------------------------
# Função: Carregar logo no topo (IMAGEM PEQUENA)
# -------------------------------------------------------------
def load_logo(image_path):
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:15px; margin-bottom:25px;'>
                <img src='data:image/png;base64,{encoded}'
                     style='width:110px; height:auto; border-radius:6px;'>

                <div>
                    <h1 style='margin:0; padding:0; font-size:40px; color:#000;'>
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
        st.warning("⚠ Não foi possível carregar o logo (imagem não encontrada no GitHub).")


# -------------------------------------------------------------
# Configurações gerais da página
# -------------------------------------------------------------
st.set_page_config(
    page_title="Análise SWS",
    layout="wide",
)

# Fundo branco TOTAL
st.markdown(
    """
    <style>
        body, .stApp {
            background-color: white !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Carrega LOGO DO TOPO
load_logo("images/baixados.png")

# -------------------------------------------------------------
# UPLOAD DO ARQUIVO
# -------------------------------------------------------------
st.markdown("### 📂 Envie o arquivo SWS (.xlsx/.xls)")

uploaded_file = st.file_uploader(
    "Drag and drop ou selecione o arquivo",
    type=["xlsx", "xls"]
)

if not uploaded_file:
    st.info("📘 Envie um arquivo Excel para iniciar a análise.")
    st.stop()

# -------------------------------------------------------------
# CARREGAR PLANILHA
# -------------------------------------------------------------
try:
    df_excel = pd.ExcelFile(uploaded_file)
except:
    st.error("Erro ao carregar o arquivo. Verifique se é um Excel válido.")
    st.stop()

abas = [a for a in df_excel.sheet_names if "CDG" not in a.upper()]

st.markdown("### ⭐ Selecione a aba para análise")
selected_sheet = st.selectbox("", abas)

df = df_excel.parse(selected_sheet)

st.success("Arquivo carregado com sucesso!")

# -------------------------------------------------------------
# FILTROS LATERAIS
# -------------------------------------------------------------
st.sidebar.title("Filtros")

col_filtros = {}

for col in df.columns:
    if df[col].dtype == "object":
        valores = sorted([v for v in df[col].unique() if str(v).strip() != ""])
        valores.insert(0, "Todos")

        col_filtros[col] = st.sidebar.multiselect(
            col,
            valores,
            default="Todos"
        )

# APLICAR FILTROS
df_filtrado = df.copy()

for col, escolhas in col_filtros.items():
    if "Todos" not in escolhas:
        df_filtrado = df_filtrado[df_filtrado[col].isin(escolhas)]

# -------------------------------------------------------------
# EXIBIR RESULTADOS
# -------------------------------------------------------------
st.markdown("### 📊 Visualização dos Dados Filtrados")

if df_filtrado.empty:
    st.warning("⚠ Nenhum dado encontrado com os filtros selecionados.")
else:
    st.dataframe(df_filtrado, use_container_width=True)

    num_cols = df_filtrado.select_dtypes(include=["number"]).columns

    if len(num_cols) >= 2:
        st.markdown("### 📈 Gráfico Interativo")
        x_axis = st.selectbox("Selecione o eixo X", num_cols)
        y_axis = st.selectbox("Selecione o eixo Y", num_cols)

        fig = px.scatter(df_filtrado, x=x_axis, y=y_axis, color=num_cols[0])
        st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# RODAPÉ
# -------------------------------------------------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:#666; font-size:14px;'>
        © 2025 — Desenvolvido por Silva Adenilton (Denis) | Hexagon<br>
        Dashboard profissional para análise de dados SWS.
    </p>
    """,
    unsafe_allow_html=True
)
