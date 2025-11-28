import streamlit as st
import pandas as pd

st.set_page_config(page_title="SWS Dashboard", layout="wide")

# =====================================
# INTERFACE
# =====================================
st.title("Dashboard SWS • Filtragem Profissional")
st.subheader("SWS1 • SWS2 — Controle e Análise")
st.write("Filtros atualizados conforme necessidade operacional.")

# =====================================
# UPLOAD DO ARQUIVO
# =====================================
uploaded_file = st.file_uploader(
    "Envie o arquivo contendo as abas SWS1 e SWS2",
    type=["xlsx"]
)

if uploaded_file:

    try:
        xls = pd.ExcelFile(uploaded_file)

        # Pega apenas abas SWS
        abas_validas = [a for a in xls.sheet_names if "SWS" in a.upper()]

        aba = st.selectbox("Escolha a base de análise:", abas_validas)
        df = pd.read_excel(uploaded_file, sheet_name=aba)

        st.success(f"Aba carregada: {aba}")
        st.markdown("---")

        # Limpeza básica
        df.columns = [c.strip() for c in df.columns]

        # =====================================
        # DEFINIR COLUNAS QUE DEVEM TER FILTRO
        # =====================================

        filtros_desejados = {
            "serial_number": None,
            "prestador": None,
            "STATUS_SCHEDULED": None,  # ou a coluna exata que houver
            "error_msg": None
        }

        # Verificar quais dessas colunas existem no arquivo
        colunas_disponiveis = {col.lower(): col for col in df.columns}

        filtros_presentes = {}
        for f in filtros_desejados:
            if f.lower() in colunas_disponiveis:
                filtros_presentes[f] = colunas_disponiveis[f.lower()]

        # =====================================
        # FILTROS EXATOS DO JEITO QUE VOCÊ PEDIU
        # =====================================
        st.markdown("### 🔎 Filtros disponíveis")

        for chave, coluna_real in filtros_presentes.items():
            valores_unicos = sorted(df[coluna_real].dropna().unique().tolist())
            selecionados = st.multiselect(f"Filtrar por {coluna_real}:", valores_unicos)
            if selecionados:
                df = df[df[coluna_real].isin(selecionados)]

        st.markdown("---")

        # =====================================
        # RESULTADO FILTRADO
        # =====================================
        st.markdown("### Resultado filtrado")
        st.write(f"Total de registros filtrados: **{len(df)}**")

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

# =====================================
# RODAPÉ
# =====================================
st.markdown("---")
st.caption("Sistema SWS - Análise 2025 • Desenvolvido com Streamlit")
st.caption("Responsável Técnico: **Silva Adenilton ( Denis ) – Analista**")
