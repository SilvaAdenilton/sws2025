# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import BytesIO

# ============================================================
#  FUNÇÃO: Inserir imagem de fundo otimizada (nitidez)
# ============================================================
def add_bg_from_local(image_file: str, overlay_opacity: float = 0.30):
    """Adiciona imagem de fundo (base64) com overlay e nitidez."""
    try:
        with open(image_file, "rb") as img:
            encoded_string = base64.b64encode(img.read()).decode()
    except Exception:
        # Se a imagem não existir, não interrompe o app
        return

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        image-rendering: -webkit-optimize-contrast;
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

    /* Painéis com aparência moderna */
    .stCard, .css-1d391kg, .css-12oz5g7 {{
        background: rgba(18,18,18,0.48) !important;
        border-radius: 10px;
        padding: 12px;
        backdrop-filter: blur(4px);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# Chame a função com o caminho onde sua imagem foi salva
add_bg_from_local("/mnt/data/imagesbackground.png", overlay_opacity=0.30)

# ============================================================
#  Configuração Streamlit
# ============================================================
st.set_page_config(page_title="Analise_Dados_SWS2", layout="wide", initial_sidebar_state="expanded")

# Cabeçalho
st.markdown("<h1 style='margin-bottom:6px'>📊 Analise Técnica — SWS2</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color:lightgray;margin-top:0px'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
#  Upload do arquivo e leitura
# ============================================================
uploaded_file = st.file_uploader("📂 Envie o arquivo SWS (.xlsx) — contenha SWS1/SWS2 ou planilha com colunas esperadas", type=["xlsx", "xls"])

def read_first_sheet(xl_file):
    # tenta ler primeiro sheet por padrão (compatível com formatos diferentes)
    try:
        xls = pd.ExcelFile(xl_file)
        sheet = xls.sheet_names[0]
        return pd.read_excel(xl_file, sheet_name=sheet)
    except Exception:
        # fallback: tentar ler diretamente
        return pd.read_excel(xl_file)

if uploaded_file:
    # tenta carregar com várias possibilidades
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)  # retorna dict de sheets
        # se contiver SWS1 ou SWS2 escolhemos pelo seletor abaixo; caso contrário pegamos a primeira
        sheet_names = list(df.keys())
        if "SWS1" in sheet_names or "SWS2" in sheet_names:
            # we'll let the user choose below
            sheets_dict = df
            df = None
        else:
            # pega a primeira planilha
            first_sheet = sheet_names[0]
            df = df[first_sheet]
            sheets_dict = None
    except Exception:
        # tentativa simples
        try:
            df = read_first_sheet(uploaded_file)
            sheets_dict = None
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()

    st.success("Arquivo carregado com sucesso!")

    # Sevier de escolher entre SWS1 / SWS2 quando presentes
    if sheets_dict:
        escolha = st.selectbox("Selecione a aba para análise:", ["SWS1", "SWS2"] + [s for s in sheets_dict.keys() if s not in ("SWS1","SWS2")])
        if escolha in sheets_dict:
            df = sheets_dict[escolha]
        else:
            # fallback: pega primeira se escolha inválida
            df = sheets_dict[list(sheets_dict.keys())[0]]

    # Normaliza nomes de colunas (lower, strip)
    df.columns = [str(c).strip() for c in df.columns]

    # Colunas esperadas (ajuste flexível)
    # possíveis nomes para data
    date_cols_candidates = ["work_date", "date", "data", "workdate"]
    date_col = next((c for c in date_cols_candidates if c in df.columns), None)

    # possíveis nomes para código
    code_cols_candidates = ["code", "codigo", "cod", "codigo_id"]
    code_col = next((c for c in code_cols_candidates if c in df.columns), None)

    # possíveis nomes para area efetiva e não efetiva
    eff_cols = ["over_effective_area", "overEffectiveArea", "effective_area", "area_efetiva"]
    eff_col = next((c for c in eff_cols if c in df.columns), None)

    not_eff_cols = ["over_not_effective_area", "overNotEffectiveArea", "not_effective_area", "area_nao_efetiva"]
    not_eff_col = next((c for c in not_eff_cols if c in df.columns), None)

    # outros campos úteis
    serial_col = "serial_number" if "serial_number" in df.columns else ("serial" if "serial" in df.columns else None)
    prestador_col = "prestador" if "prestador" in df.columns else ("provider" if "provider" in df.columns else None)
    status_col = "Status" if "Status" in df.columns else ("status" if "status" in df.columns else None)
    error_col = "error_msg" if "error_msg" in df.columns else ("error" if "error" in df.columns else None)

    # Conversões seguras
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if eff_col:
        df[eff_col] = pd.to_numeric(df[eff_col], errors="coerce").fillna(0)
    if not_eff_col:
        df[not_eff_col] = pd.to_numeric(df[not_eff_col], errors="coerce").fillna(0)

    # Normaliza e limpa error_msg (se existir)
    if error_col:
        df[error_col] = df[error_col].astype(str).str.strip()
        # remover entradas vazias ou literais "nan"/"None"
        df[error_col] = df[error_col].replace({"nan": "", "None": ""})
        df.loc[df[error_col].str.lower().isin(["nan", "none"]), error_col] = ""
    else:
        # cria coluna vazia para manter compatibilidade
        df["error_msg_clean"] = ""
        error_col = "error_msg_clean"

    # ============ SIDEBAR: filtros ============
    st.sidebar.header("Filtros rápidos")

    # filtro por serial
    if serial_col:
        serial_options = ["Todos"] + sorted(df[serial_col].dropna().astype(str).unique().tolist())
        serial_sel = st.sidebar.multiselect("Serial Number", serial_options, default=["Todos"])
    else:
        serial_sel = ["Todos"]

    # filtro por prestador
    if prestador_col:
        prestador_options = ["Todos"] + sorted(df[prestador_col].dropna().astype(str).unique().tolist())
        prestador_sel = st.sidebar.multiselect("Prestador", prestador_options, default=["Todos"])
    else:
        prestador_sel = ["Todos"]

    # filtro por status
    if status_col:
        status_options = ["Todos"] + sorted(df[status_col].dropna().astype(str).unique().tolist())
        status_sel = st.sidebar.multiselect("Status", status_options, default=["Todos"])
    else:
        status_sel = ["Todos"]

    # filtro por error_msg (limpo)
    error_options = ["Todos"] + sorted([e for e in df[error_col].unique() if str(e).strip() != ""], key=lambda x: str(x))
    error_sel = st.sidebar.multiselect("Erros (error_msg)", error_options, default=["Todos"])

    # filtro por código (se existir)
    if code_col:
        code_options = ["Todos"] + sorted(df[code_col].dropna().astype(str).unique().tolist())
        code_sel = st.sidebar.multiselect("Código", code_options, default=["Todos"])
    else:
        code_sel = ["Todos"]

    # filtro por data (se existir)
    if date_col:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        date_range = st.sidebar.date_input("Intervalo de datas", value=(min_date.date() if pd.notnull(min_date) else None, max_date.date() if pd.notnull(max_date) else None))
    else:
        date_range = (None, None)

    # filtro por área efetiva (se existir)
    if eff_col:
        min_eff = float(df[eff_col].min())
        max_eff = float(df[eff_col].max())
        eff_range = st.sidebar.slider("Área Efetiva (intervalo)", min_value=min_eff, max_value=max_eff, value=(min_eff, max_eff))
    else:
        eff_range = (None, None)

    st.sidebar.markdown("---")
    st.sidebar.markdown("🛈 Dica: selecione 'Todos' para desativar o filtro correspondente.")

    # ============ APLICAR FILTROS ============
    df_filt = df.copy()

    # Serial
    if serial_col and serial_sel and "Todos" not in serial_sel:
        df_filt = df_filt[df_filt[serial_col].astype(str).isin(serial_sel)]

    # Prestador
    if prestador_col and prestador_sel and "Todos" not in prestador_sel:
        df_filt = df_filt[df_filt[prestador_col].astype(str).isin(prestador_sel)]

    # Status
    if status_col and status_sel and "Todos" not in status_sel:
        df_filt = df_filt[df_filt[status_col].astype(str).isin(status_sel)]

    # Error
    if error_col and error_sel and "Todos" not in error_sel:
        df_filt = df_filt[df_filt[error_col].astype(str).isin(error_sel)]

    # Código
    if code_col and code_sel and "Todos" not in code_sel:
        df_filt = df_filt[df_filt[code_col].astype(str).isin(code_sel)]

    # Date range
    if date_col and date_range and None not in date_range:
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        df_filt = df_filt[(df_filt[date_col] >= start_dt) & (df_filt[date_col] <= end_dt)]

    # Eff range
    if eff_col and eff_range and None not in eff_range:
        df_filt = df_filt[df_filt[eff_col].between(eff_range[0], eff_range[1])]

    # Se não houver dados após filtros
    if df_filt.empty:
        st.warning("Nenhum dado encontrado com os filtros aplicados.")
        st.stop()

    # ============================================================
    #  INDICADORES (KPIs)
    # ============================================================
    total_records = len(df_filt)
    total_effective = df_filt[eff_col].sum() if eff_col else 0
    total_not_effective = df_filt[not_eff_col].sum() if not_eff_col else 0
    avg_effective = df_filt[eff_col].mean() if eff_col else 0
    most_freq_code = df_filt[code_col].mode().iloc[0] if code_col and not df_filt[code_col].dropna().empty else "-"

    kpi1, kpi2, kpi3, kpi4 = st.columns([1.5,1.5,1.5,1.5])
    kpi1.metric(label="Registros (filtrados)", value=f"{total_records}")
    kpi2.metric(label="Área Efetiva Total", value=f"{total_effective:,.2f}")
    kpi3.metric(label="Área Não Efetiva Total", value=f"{total_not_effective:,.2f}")
    kpi4.metric(label="Área Efetiva Média", value=f"{avg_effective:,.2f}")

    st.markdown("---")

    # ============================================================
    #  GRÁFICO 1: Top 10 CÓDIGOS (barras verticais)
    # ============================================================
    st.subheader("🏷️ Top 10 Códigos por Volume")
    if code_col:
        df_codes = df_filt[code_col].astype(str).value_counts().reset_index()
        df_codes.columns = ["code", "count"]
        df_codes_top = df_codes.head(10)
        fig_codes = px.bar(df_codes_top, x="code", y="count", title="Top 10 Códigos (mais frequentes)",
                           labels={"code":"Código", "count":"Quantidade"})
        fig_codes.update_layout(xaxis_tickangle=-45, margin=dict(t=40,b=120))
        st.plotly_chart(fig_codes, use_container_width=True)
    else:
        st.info("Coluna de código não encontrada — nenhum gráfico de códigos será exibido.")

    # ============================================================
    #  GRÁFICO 2: Evolução Temporal (linha) — soma de área efetiva por data
    # ============================================================
    st.subheader("📈 Evolução Temporal — Área Efetiva")
    if date_col and eff_col:
        df_time = df_filt.groupby(pd.Grouper(key=date_col, freq="D"))[eff_col].sum().reset_index()
        df_time = df_time.sort_values(by=date_col)
        fig_time = px.line(df_time, x=date_col, y=eff_col, markers=True,
                           title="Soma diária de Área Efetiva",
                           labels={date_col:"Data", eff_col:"Área Efetiva"})
        fig_time.update_layout(margin=dict(t=40,b=30))
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("Dados de data ou área efetiva ausentes — não é possível gerar série temporal.")

    # ============================================================
    #  GRÁFICO 3: Distribuição por Erros (pizza) — Top categorias
    # ============================================================
    st.subheader("🧭 Distribuição por Erros (Top categorias)")
    if error_col:
        df_err = df_filt[error_col].astype(str).replace({"": "Sem erro informado"})
        df_err_counts = df_err.value_counts().reset_index()
        df_err_counts.columns = ["error", "count"]
        df_err_counts_top = df_err_counts.head(10)
        fig_err = px.pie(df_err_counts_top, names="error", values="count", title="Distribuição dos principais erros")
        fig_err.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_err, use_container_width=True)
    else:
        st.info("Coluna de erros ausente — sem gráfico de erros.")

    # ============================================================
    #  GRÁFICO 4: Comparativo Efetiva x Não Efetiva por Prestador (Top 10) — horizontal
    # ============================================================
    st.subheader("🔁 Comparativo: Área Efetiva vs Não Efetiva (por Prestador — Top 10)")
    if prestador_col and eff_col and not_eff_col:
        df_prest = df_filt.groupby(prestador_col).agg({
            eff_col: "sum",
            not_eff_col: "sum"
        }).reset_index()
        df_prest["total"] = df_prest[eff_col] + df_prest[not_eff_col]
        df_prest_top = df_prest.sort_values("total", ascending=False).head(10)

        # empilhar barras horizontais (efetiva e não efetiva)
        df_melt = df_prest_top.melt(id_vars=prestador_col, value_vars=[eff_col, not_eff_col], var_name="tipo", value_name="area")
        # renomear colunas para labels mais amigáveis
        df_melt[prestador_col] = df_melt[prestador_col].astype(str)
        fig_prest = px.bar(df_melt, x="area", y=prestador_col, color="tipo", orientation="h",
                           title="Área Efetiva vs Não Efetiva — Top 10 Prestadores",
                           labels={"area":"Área", prestador_col:"Prestador", "tipo":"Tipo"})
        fig_prest.update_layout(barmode='stack', margin=dict(t=40,b=30))
        st.plotly_chart(fig_prest, use_container_width=True)
    else:
        st.info("Colunas de prestador ou áreas ausentes — comparativo não disponível.")

    st.markdown("---")
    st.caption("Sistema SWS - Desenvolvido por Silva Adenilton (Denis) — Dashboard profissional")

else:
    st.info("Envie um arquivo Excel para começar. O app aceita planilhas com colunas como: work_date/date, code/codigo, over_effective_area, over_not_effective_area, prestador, Status, serial_number, error_msg.")
