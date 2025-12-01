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

    .stCard, .css-1d391kg, .css-12oz5g7 {{
        background: rgba(18,18,18,0.48) !important;
        border-radius: 10px;
        padding: 12px;
        backdrop-filter: blur(4px);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Chamada da imagem de fundo
add_bg_from_local("/mnt/data/imagesbackground.png", overlay_opacity=0.30)

# ============================================================
#  Configuração Streamlit
# ============================================================
st.set_page_config(page_title="Analise_Dados_SWS2", layout="wide", initial_sidebar_state="expanded")

# Cabeçalho atualizado
st.markdown("<h1 style='margin-bottom:6px'>📊 Analise Técnica  Arquivos Enviados — SWS</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='color:lightgray;margin-top:0px'>Dashboard interativa | Desenvolvido por <b>Silva Adenilton (Denis)</b></h4>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
#  Upload do arquivo e leitura
# ============================================================
uploaded_file = st.file_uploader("📂 Envie o arquivo SWS (.xlsx) — contenha SWS1/SWS2 ou planilha com colunas esperadas", type=["xlsx", "xls"])

def read_first_sheet(xl_file):
    try:
        xls = pd.ExcelFile(xl_file)
        sheet = xls.sheet_names[0]
        return pd.read_excel(xl_file, sheet_name=sheet)
    except Exception:
        return pd.read_excel(xl_file)

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_names = list(df.keys())

        if "SWS1" in sheet_names or "SWS2" in sheet_names:
            sheets_dict = df
            df = None
        else:
            first_sheet = sheet_names[0]
            df = df[first_sheet]
            sheets_dict = None

    except Exception:
        try:
            df = read_first_sheet(uploaded_file)
            sheets_dict = None
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()

    st.success("Arquivo carregado com sucesso!")

    # Se houver múltiplas planilhas
    if sheets_dict:
        prioridade = [s for s in ["SWS1","SWS2"] if s in sheets_dict]
        outras = [s for s in sheets_dict if s not in prioridade]
        escolha = st.selectbox("Selecione a aba para análise:", prioridade + outras)
        df = sheets_dict[escolha]

    # Normalização de colunas
    df.columns = [str(c).strip().lower() for c in df.columns]

    # Mapear colunas possíveis
    date_col = next((c for c in ["work_date","date","data","workdate"] if c in df.columns), None)
    code_col = next((c for c in ["code","codigo","cod","codigo_id"] if c in df.columns), None)
    eff_col = next((c for c in ["over_effective_area","overeffectivearea","effective_area","area_efetiva"] if c in df.columns), None)
    not_eff_col = next((c for c in ["over_not_effective_area","overnoteffectivearea","not_effective_area","area_nao_efetiva"] if c in df.columns), None)

    serial_col = "serial_number" if "serial_number" in df.columns else ("serial" if "serial" in df.columns else None)
    prestador_col = "prestador" if "prestador" in df.columns else ("provider" if "provider" in df.columns else None)
    status_col = "status" if "status" in df.columns else None
    error_col = "error_msg" if "error_msg" in df.columns else None

    # Conversões
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if eff_col:
        df[eff_col] = pd.to_numeric(df[eff_col], errors="coerce").fillna(0)
    if not_eff_col:
        df[not_eff_col] = pd.to_numeric(df[not_eff_col], errors="coerce").fillna(0)

    if error_col:
        df[error_col] = df[error_col].astype(str).str.strip()
        df[error_col] = df[error_col].replace({"nan":"","None":""})
        df.loc[df[error_col].str.lower().isin(["nan","none"]), error_col] = ""
    else:
        df["error_msg_clean"] = ""
        error_col = "error_msg_clean"

    # ============================================================
    #  SIDEBAR: filtros
    # ============================================================
    st.sidebar.header("Filtros rápidos")

    def clean_filter(sel):
        return [] if ("Todos" in sel) else sel

    # SERIAL
    if serial_col:
        ops = ["Todos"] + sorted(df[serial_col].dropna().astype(str).unique())
        serial_sel = clean_filter(st.sidebar.multiselect("Serial Number", ops, default=["Todos"]))
    else:
        serial_sel = []

    # PRESTADOR
    if prestador_col:
        ops = ["Todos"] + sorted(df[prestador_col].dropna().astype(str).unique())
        prestador_sel = clean_filter(st.sidebar.multiselect("Prestador", ops, default=["Todos"]))
    else:
        prestador_sel = []

    # STATUS
    if status_col:
        ops = ["Todos"] + sorted(df[status_col].dropna().astype(str).unique())
        status_sel = clean_filter(st.sidebar.multiselect("Status", ops, default=["Todos"]))
    else:
        status_sel = []

    # ERROS
    ops = ["Todos"] + sorted([e for e in df[error_col].unique() if str(e).strip() != ""], key=str)
    error_sel = clean_filter(st.sidebar.multiselect("Erros (error_msg)", ops, default=["Todos"]))

    # CÓDIGO
    if code_col:
        ops = ["Todos"] + sorted(df[code_col].dropna().astype(str).unique())
        code_sel = clean_filter(st.sidebar.multiselect("Código", ops, default=["Todos"]))
    else:
        code_sel = []

    # DATA
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
    #  Aplicar filtros
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
        start_dt = pd.to_datetime(date_range[0])
        end_dt = pd.to_datetime(date_range[1])
        df_filt = df_filt[(df_filt[date_col] >= start_dt) & (df_filt[date_col] <= end_dt)]

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
    most_freq_code = df_filt[code_col].mode().iloc[0] if code_col else "-"

    kpi1, kpi2, kpi3, kpi4 = st.columns([1.5,1.5,1.5,1.5])
    kpi1.metric("Registros (filtrados)", f"{total_records}")
    kpi2.metric("Área Efetiva Total", f"{total_effective:,.2f}")
    kpi3.metric("Área Não Efetiva Total", f"{total_not_effective:,.2f}")
    kpi4.metric("Área Efetiva Média", f"{avg_effective:,.2f}")

    st.markdown("---")

    # ============================================================
    #  GRÁFICO 1 — TOP CÓDIGOS
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
    #  GRÁFICO 2 — EVOLUÇÃO TEMPORAL
    # ============================================================
    st.subheader("📈 Evolução Temporal — Área Efetiva")
    if date_col and eff_col:
        df_time = df_filt.groupby(pd.Grouper(key=date_col, freq="D"))[eff_col].sum().reset_index()
        df_time = df_time.sort_values(by=date_col)
        df_time = df_time.dropna(subset=[date_col])

        fig_time = px.line(df_time, x=date_col, y=eff_col, markers=True,
                           title="Soma diária de Área Efetiva",
                           labels={date_col:"Data", eff_col:"Área Efetiva"})
        fig_time.update_layout(margin=dict(t=40,b=30))
        st.plotly_chart(fig_time, use_container_width=True)
    else:
        st.info("Dados de data ou área efetiva ausentes — não é possível gerar série temporal.")

    # ============================================================
    #  GRÁFICO 3 — ERROS
    # ============================================================
    st.subheader("🧭 Distribuição por Erros (Top categorias)")
    df_err = df_filt[error_col].astype(str).replace({"": "Sem erro informado"})
    df_err_counts = df_err.value_counts().reset_index()
    df_err_counts.columns = ["error", "count"]
    df_err_counts_top = df_err_counts.head(10)

    fig_err = px.pie(df_err_counts_top, names="error", values="count",
                     title="Distribuição dos principais erros")
    fig_err.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_err, use_container_width=True)

    # ============================================================
    #  GRÁFICO 4 — PRESTADORES
    # ============================================================
    st.subheader("🔁 Comparativo: Área Efetiva vs Não Efetiva (por Prestador — Top 10)")
    if prestador_col and eff_col and not_eff_col:
        df_prest = df_filt.groupby(prestador_col).agg({
            eff_col: "sum",
            not_eff_col: "sum"
        }).reset_index()
        df_prest["total"] = df_prest[eff_col] + df_prest[not_eff_col]
        df_prest_top = df_prest.sort_values("total", ascending=False).head(10)

        df_melt = df_prest_top.melt(id_vars=prestador_col, 
                                    value_vars=[eff_col, not_eff_col],
                                    var_name="tipo", value_name="area")

        fig_prest = px.bar(df_melt, x="area", y=prestador_col, color="tipo", orientation="h",
                           title="Área Efetiva vs Não Efetiva — Top 10 Prestadores",
                           labels={"area":"Área", prestador_col:"Prestador", "tipo":"Tipo"})
        fig_prest.update_layout(barmode='stack', margin=dict(t=40,b=30))
        st.plotly_chart(fig_prest, use_container_width=True)

    st.markdown("---")
    st.caption("Sistema SWS - Desenvolvido por Silva Adenilton (Denis) — Dashboard profissional")

else:
    st.info("Envie um arquivo Excel para começar. O app aceita planilhas com colunas como: work_date/date, code/codigo, over_effective_area, over_not_effective_area, prestador, Status, serial_number, error_msg.")
