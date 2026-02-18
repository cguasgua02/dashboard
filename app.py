from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard de Conversión Clínica", layout="wide")

DATA_DIR = Path(__file__).parent / "data"

DEFAULT_RESUMEN = {
    "Leads totales": 320,
    "Leads calificados": 240,
    "Citas agendadas": 180,
    "Citas asistidas": 140,
    "Pacientes cerrados": 90,
    "Tasa de conversión Lead → Cita": "56%",
    "Tasa de asistencia (Show rate)": "77%",
    "Tasa de cierre (Asistencia → Paciente)": "64%",
    "Tasa de No-Show": "23%",
    "Ticket promedio ($)": 300,
    "Ingreso estimado ($)": 27000,
}

DEFAULT_PIPELINE = pd.DataFrame(
    {
        "Etapa": ["Nuevo", "Contactado", "Agendado", "Asistió", "Cerrado", "No Show"],
        "Cantidad": [80, 70, 60, 45, 30, 15],
    }
)

DEFAULT_CANALES = pd.DataFrame(
    {
        "Canal": ["Instagram Ads", "Google Ads", "Facebook Ads", "Web / Orgánico"],
        "leads": [100, 80, 90, 50],
        "citas": [60, 50, 45, 25],
        "pacientes": [35, 30, 20, 10],
    }
)

DEFAULT_CUELLOS = pd.DataFrame(
    {
        "Etapa": ["Lead → Cita", "Cita → Asistencia", "Asistencia → Cierre"],
        "Conversión": ["56%", "77%", "64%"],
    }
)


st.markdown(
    """
    <style>
    .stApp {
        background-color: #0a1033;
        color: #f0f4ff;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.5rem;
        max-width: 1280px;
    }
    [data-testid="stSidebar"] {
        background-color: #101a4d;
        border-right: 1px solid rgba(123, 162, 255, 0.25);
    }
    .module-card {
        background: linear-gradient(145deg, #151d4f 0%, #121843 100%);
        border: 1px solid rgba(133, 177, 255, 0.25);
        border-radius: 14px;
        padding: 14px 16px;
        min-height: 110px;
        box-shadow: 0 8px 20px rgba(7, 11, 35, 0.35);
        margin-bottom: 10px;
    }
    .module-title {
        color: #9fb4ff;
        font-size: 0.82rem;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: .03rem;
    }
    .module-value {
        font-size: 1.95rem;
        line-height: 1.1;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .module-note {
        color: #b7c6f6;
        font-size: 0.84rem;
    }
    .section-box {
        background: #121843;
        border: 1px solid rgba(133, 177, 255, 0.2);
        border-radius: 14px;
        padding: 12px 14px 8px;
        margin-top: 8px;
        margin-bottom: 14px;
    }
    .section-box h3 {
        color: #eaf0ff;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_csv_or_default(uploaded_file, default_df, local_path: Path | None = None):
    if uploaded_file is None:
        if local_path is not None and local_path.exists():
            return pd.read_csv(local_path)
        return default_df.copy()
    return pd.read_csv(uploaded_file)


def to_float(value, percent: bool = False) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("$", "").replace(",", "").replace("%", "").strip()
    number = float(text)
    return number / 100 if percent else number


def module_card(title: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-title">{title}</div>
            <div class="module-value">{value}</div>
            <div class="module-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.header("Fuente de datos (CSV)")
    st.markdown("Exporta desde Excel y carga aquí tus archivos.")

    resumen_file = st.file_uploader("Resumen (metrica, valor)", type=["csv"], key="resumen")
    pipeline_file = st.file_uploader("Pipeline (Etapa, Cantidad)", type=["csv"], key="pipeline")
    canales_file = st.file_uploader("Canales (Canal, leads, citas, pacientes)", type=["csv"], key="canales")
    cuellos_file = st.file_uploader("Cuellos (Etapa, Conversión)", type=["csv"], key="cuellos")

if resumen_file is not None:
    resumen_df = pd.read_csv(resumen_file)
    resumen = dict(zip(resumen_df["metrica"], resumen_df["valor"]))
elif (DATA_DIR / "resumen.csv").exists():
    resumen_df = pd.read_csv(DATA_DIR / "resumen.csv")
    resumen = dict(zip(resumen_df["metrica"], resumen_df["valor"]))
else:
    resumen = DEFAULT_RESUMEN

pipeline_df = read_csv_or_default(pipeline_file, DEFAULT_PIPELINE, DATA_DIR / "pipeline.csv")
canales_df = read_csv_or_default(canales_file, DEFAULT_CANALES, DATA_DIR / "canales.csv")
cuellos_df = read_csv_or_default(cuellos_file, DEFAULT_CUELLOS, DATA_DIR / "cuellos.csv")

st.title("Dashboard de Conversión Clínica")
st.caption("Vista modular estilo operaciones clínicas. Ajusta los datos con CSV desde la barra lateral.")

col_top_1, col_top_2, col_top_3, col_top_4 = st.columns(4)
with col_top_1:
    module_card("Leads totales", f"{int(to_float(resumen.get('Leads totales', 0)))}", "Leads recibidos")
with col_top_2:
    module_card("Leads calificados", f"{int(to_float(resumen.get('Leads calificados', 0)))}", "Potencial real")
with col_top_3:
    module_card("Citas agendadas", f"{int(to_float(resumen.get('Citas agendadas', 0)))}", "Agenda comercial")
with col_top_4:
    module_card("Pacientes cerrados", f"{int(to_float(resumen.get('Pacientes cerrados', 0)))}", "Cierres totales")

col_rate_1, col_rate_2, col_rate_3, col_rate_4 = st.columns(4)
with col_rate_1:
    module_card("Lead → Cita", str(resumen.get("Tasa de conversión Lead → Cita", "56%")), "Conversión a cita")
with col_rate_2:
    module_card("Show rate", str(resumen.get("Tasa de asistencia (Show rate)", "77%")), "Asistencia a cita")
with col_rate_3:
    module_card("Asistencia → Cierre", str(resumen.get("Tasa de cierre (Asistencia → Paciente)", "64%")), "Tasa de cierre")
with col_rate_4:
    module_card("No-Show", str(resumen.get("Tasa de No-Show", "23%")), "Citas perdidas")

left, right = st.columns([1.45, 1])

with left:
    st.markdown('<div class="section-box"><h3>Pipeline visual</h3></div>', unsafe_allow_html=True)
    fig_pipeline = px.funnel(
        pipeline_df,
        x="Cantidad",
        y="Etapa",
        color="Etapa",
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig_pipeline.update_layout(
        paper_bgcolor="#121843",
        plot_bgcolor="#121843",
        font_color="#eaf0ff",
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text="",
    )
    st.plotly_chart(fig_pipeline, use_container_width=True)

    st.markdown('<div class="section-box"><h3>Análisis por canal</h3></div>', unsafe_allow_html=True)
    fig_canales = px.bar(
        canales_df,
        x="Canal",
        y=["leads", "citas", "pacientes"],
        barmode="group",
        color_discrete_sequence=["#7db4ff", "#3f84ff", "#69e0d3"],
    )
    fig_canales.update_layout(
        paper_bgcolor="#121843",
        plot_bgcolor="#121843",
        font_color="#eaf0ff",
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text="",
    )
    st.plotly_chart(fig_canales, use_container_width=True)

with right:
    st.markdown('<div class="section-box"><h3>Rendimiento por canal</h3></div>', unsafe_allow_html=True)
    canales_df["Conv. cita %"] = (canales_df["citas"] / canales_df["leads"] * 100).round(1)
    canales_df["Conv. cierre %"] = (canales_df["pacientes"] / canales_df["citas"] * 100).round(1)
    st.dataframe(canales_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-box"><h3>Cuellos de botella</h3></div>', unsafe_allow_html=True)
    st.table(cuellos_df)

    ticket = to_float(resumen.get("Ticket promedio ($)", 0))
    no_show_pacientes = int(to_float(resumen.get("Citas agendadas", 0)) - to_float(resumen.get("Citas asistidas", 0)))
    recuperables = int(no_show_pacientes * 0.5)
    extra_ingresos = int(recuperables * ticket)

    st.markdown('<div class="section-box"><h3>Proyección de ingresos</h3></div>', unsafe_allow_html=True)
    p_col_1, p_col_2 = st.columns(2)
    with p_col_1:
        module_card("No-shows actuales", str(no_show_pacientes), "Pacientes perdidos")
    with p_col_2:
        module_card("Recuperables (50%)", str(recuperables), "Potencial de rescate")
    module_card("Ingreso adicional potencial", f"${extra_ingresos:,.0f}", "Ticket promedio aplicado")

st.markdown("---")
st.markdown("#### Plantillas CSV")
st.code(
    """# resumen.csv
metrica,valor
Leads totales,320
Leads calificados,240
Citas agendadas,180
Citas asistidas,140
Pacientes cerrados,90

# pipeline.csv
Etapa,Cantidad
Nuevo,80
Contactado,70
Agendado,60
Asistió,45
Cerrado,30
No Show,15""",
    language="text",
)
