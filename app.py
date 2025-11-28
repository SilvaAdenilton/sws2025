import streamlit as st
import pandas as pd

# ===============================
# INTERFACE DO DASHBOARD
# ===============================

st.title("Filtros SWS - Arquivos 2025")
st.subheader("Dashboard Streamlit para análise e filtragem dos arquivos SWS")

st.write("Interface inicial carregada com sucesso – fundo removido temporariamente.")

# ===============================
# UPLOAD DE ARQUIVOS
# ===============================

uploaded_file = st.file_uploader(
    "Envie um arquivo SWS",
    type=["csv", "xlsx"]
)

if uploaded_file:
    st.success("Arquivo enviado com sucesso!")

    # Leitura do arquivo com tratamento de erros
    df = None  
    try:
        if uploaded_file.name.endswith(".csv"):
            try:
                df = pd.read_csv(uploaded_file, sep=";", encoding="latin1")
            except UnicodeDecodeError:
                st.warning("Tentando outro encoding (UTF-8)...")
                df = pd.read_csv(uploaded_file, sep=";", encoding="utf-8")
        else:
            df = pd.read_excel(uploaded_file)

        if df is not None and not df.empty:
            st.write("Pré-visualização dos dados:")
            st.dataframe(df)
        else:
            st.error("O arquivo está vazio ou não pôde ser lido.")

    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")

# ===============================
# RODAPÉ
# ===============================

st.markdown("---")
st.caption("Sistema SWS - Análise 2025 • Desenvolvido com Streamlit")
