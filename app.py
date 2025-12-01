import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# -------------------------------------------------------------
# Função: Carregar LOGO pequeno e alinhado ao título
# -------------------------------------------------------------
def load_logo(image_path):
    try:
        with open(image_path, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()

        st.markdown(
            f"""
            <div style='display:flex; align-items:center; gap:20px; margin-bottom:30px;'>
                <img src='data:image/png;base64,{encoded}'
                     style='width:100px; height:auto;'>
                <div>
                    <h1 style='margin:0; font-size:38px; color:#000;'>
                        📊 Análise Técnica — Arquivos Enviados (SWS)
                    </h1>
                    <h4 style='margin:0; color:#444;'>
                        Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b>
                    </h4>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    except:
        st.warning("⚠ Não foi possível carregar o logo.")

# -------------------------------------------------------------
# Configurações gerais
# -------------------------------------------------------------
st.set_page_config(
    page_title="Análise Técnica SWS",
    layout="wide"
)

# Fundo branco total (limpo)
st.markdown(
    """
    <style>
        .stApp { background-color: white !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Carrega logo do topo
load_logo("images/baixados.png")


# -------------------------------------------------------------
# UPLOAD DO ARQUIVO
# -------------------------------------------------------------
st.markdown("### 📁 Envie o arquivo SWS (.xlsx / .xls)")

uploaded_file = st.file_uploader(
    "Escolha o arquivo",
    type=["xlsx", "xls"]
)

if uploaded_file is None:
    st.info("Envie um arquivo Excel para começar.")
    st.stop()

# Carrega planilha
try:
    excel = pd.ExcelFile(uploaded_file)
except:
    st.error("Erro ao ler o arquivo Excel.")
    st.stop()

# Filtra abas (removendo CDG)
abas = [a for a in excel.sheet_names if "CDG" not in a.upper()]

st.markdown("### ⭐ Selecione a aba para análise")
aba = st.selectbox("", abas)

df = excel.parse(aba)

st.success("Arquivo carregado com sucesso!")


# -------------------------------------------------------------
# FILTROS FIXOS
# -------------------------------------------------------------
st.sidebar.title("Filtros")

# Criar filtros SOMENTE das colunas desejadas
filtros_desejados = ["Prestador", "Serial_Number", "Status"]

df_filt = df.copy()

for col in filtros_desejados:
    if col in df.columns:
        valores = sorted(df[col].dropna().unique().tolist())
        valores.insert(0, "Todos")

        escolha = st.sidebar.multiselect(f"{col}", valores, default="Todos")

        if "Todos" not in escolha:
            df_filt = df_filt[df_filt[col].isin(escolha)]
    else:
        st.sidebar.warning(f"⚠ A coluna '{col}' não existe na aba selecionada.")


# -------------------------------------------------------------
# EXIBIR TABELA FILTRADA
# -------------------------------------------------------------
st.markdown("### 📊 Dados Filtrados")

if df_filt.empty:
    st.warning("⚠ Nenhum dado encontrado com os filtros aplicados.")
else:
    st.dataframe(df_filt, use_container_width=True)

# -------------------------------------------------------------
# GRÁFICO AUTOMÁTICO (se houver números)
# -------------------------------------------------------------
num_cols = df_filt.select_dtypes(include=["number"]).columns.tolist()

if len(num_cols) >= 2:
    st.markdown("### 📈 Visualização Gráfica")

    x_axis = st.selectbox("Eixo X", num_cols)
    y_axis = st.selectbox("Eixo Y", num_cols)

    fig = px.scatter(df_filt, x=x_axis, y=y_axis, color=num_cols[0])
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# Rodapé
# -------------------------------------------------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:#777; font-size:13px;'>
        © 2025 — Desenvolvido por Silva Adenilton (Denis) | Hexagon
    </p>
    """,
    unsafe_allow_html=True
)
