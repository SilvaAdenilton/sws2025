import streamlit as st
import pandas as pd

st.set_page_config(page_title="SWS Dashboard", layout="wide")

# =====================================
# INTERFACE
# =====================================
st.title("Dashboard SWS • Filtragem Completa e KPIs")
st.subheader("SWS1 • SWS2 — Filtros Inteligentes, Datas e Indicadores")
st.write("Sistema atualizado com filtros avançados automáticos.")

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

        # =====================================
        # LIMPEZA BÁSICA
        # =====================================
        df.columns = [c.strip() for c in df.columns]

        # Detectar colunas de data
        col_datas = [c for c in df.columns if "data" in c.lower() or "date" in c.lower()]

        # Detectar colunas numéricas
        col_numericas = df.select_dtypes(include=['float64','int64']).columns.tolist()

        # Detectar colunas de texto
        col_texto = df.select_dtypes(include=['object']).columns.tolist()

        # Detectar possíveis áreas efetivas
        col_area = None
        for c in df.columns:
            if "area" in c.lower() or "efetiv" in c.lower():
                col_area = c
                break

        # =====================================
        # KPIs AUTOMÁTICOS
        # =====================================
        st.markdown("### 📊 Indicadores Gerais")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Registros", len(df))

        if col_area:
            with col2:
                st.metric("Área Efetiva Total", round(df[col_area].sum(), 2))

        if "STATUS_SCHEDULED" in df.columns:
            with col3:
                prontos = df[df["STATUS_SCHEDULED"].str.contains("READY", na=False)]
                st.metric("Total Prontos", len(prontos))

        if "STATUS_SCHEDULED" in df.columns:
            with col4:
                erros = df[df["STATUS_SCHEDULED"].str.contains("ERROR", na=False)]
                st.metric("Total com Erro", len(erros))

        st.markdown("---")

        # =====================================
        # FILTROS AVANÇADOS
        # =====================================
        st.markdown("### 🔎 Filtros avançados")

        # --- Colunas de texto ---
        for col in col_texto:
            valores = sorted(df[col].dropna().unique().tolist())
            selecionados = st.multiselect(f"Filtrar por {col}:", valores)
            if selecionados:
                df = df[df[col].isin(selecionados)]

        # --- Colunas numéricas ---
        for col in col_numericas:
            minimo = float(df[col].min())
            maximo = float(df[col].max())
            faixa = st.slider(f"Faixa de {col}:", minimo, maximo, (minimo, maximo))
            df = df[(df[col] >= faixa[0]) & (df[col] <= faixa[1])]

        # --- Colunas de data ---
        for col in col_datas:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                intervalo = st.date_input(f"Data de trabalho ({col}):", [])
                if intervalo and len(intervalo) == 2:
                    df = df[(df[col] >= pd.to_datetime(intervalo[0])) &
                            (df[col] <= pd.to_datetime(intervalo[1]))]
            except:
                pass

        st.markdown("---")

        # =====================================
        # RESULTADO FILTRADO
        # =====================================
        st.markdown("### □ Resultado após filtros")
        st.write(f"Total de linhas filtradas: **{len(df)}**")

        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")

# =====================================
# RODAPÉ
# =====================================
st.markdown("---")
st.caption("Sistema SWS - Análise 2025 • Desenvolvido com Streamlit")
st.caption("Responsável: **Silva Adenilton ( Denis ) – Analista**")
