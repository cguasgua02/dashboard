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
    "Tasa de conversión Lead → Cita": 56.0,
    "Tasa de asistencia (Show rate)": 77.0,
    "Tasa de cierre (Asistencia → Paciente)": 64.0,
    "Tasa de No-Show": 23.0,
    "Ticket promedio ($)": 300.0,
    "Ingreso estimado ($)": 27000.0,
}

DEFAULT_PIPELINE = {
    "Nuevo": 80,
    "Contactado": 70,
    "Agendado": 60,
    "Asistió": 45,
    "Cerrado": 30,
    "No Show": 15,
}

DEFAULT_CUELLOS = {
    "Lead → Cita": 56.0,
    "Cita → Asistencia": 77.0,
    "Asistencia → Cierre": 64.0,
}

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


def read_csv_or_default(default_values: dict[str, float], local_path: Path | None = None) -> dict[str, float]:
    if local_path is None or not local_path.exists():
        return default_values.copy()

    data = pd.read_csv(local_path)
    if {"metrica", "valor"}.issubset(data.columns):
        mapped = {}
        for _, row in data.iterrows():
            try:
                mapped[str(row["metrica"])] = float(str(row["valor"]).replace("$", "").replace("%", ""))
            except ValueError:
                continue
        return {**default_values, **mapped}

    return default_values.copy()


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


resumen_base = read_csv_or_default(DEFAULT_RESUMEN, DATA_DIR / "resumen.csv")

with st.sidebar:
    st.header("Entrada manual de datos")
    st.caption("Actualiza los números y el dashboard se refresca en tiempo real.")

    st.subheader("Resumen general")
    leads_totales = st.number_input("Leads totales", min_value=0, value=int(resumen_base["Leads totales"]), step=1)
    leads_calificados = st.number_input(
        "Leads calificados", min_value=0, value=int(resumen_base["Leads calificados"]), step=1
    )
    citas_agendadas = st.number_input(
        "Citas agendadas", min_value=0, value=int(resumen_base["Citas agendadas"]), step=1
    )
    citas_asistidas = st.number_input(
        "Citas asistidas", min_value=0, value=int(resumen_base["Citas asistidas"]), step=1
    )
    pacientes_cerrados = st.number_input(
        "Pacientes cerrados", min_value=0, value=int(resumen_base["Pacientes cerrados"]), step=1
    )

    st.subheader("Tasas (%)")
    tasa_lead_cita = st.number_input(
        "Lead → Cita (%)", min_value=0.0, max_value=100.0, value=float(resumen_base["Tasa de conversión Lead → Cita"]), step=0.1
    )
    show_rate = st.number_input(
        "Show rate (%)", min_value=0.0, max_value=100.0, value=float(resumen_base["Tasa de asistencia (Show rate)"]), step=0.1
    )
    tasa_cierre = st.number_input(
        "Asistencia → Cierre (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(resumen_base["Tasa de cierre (Asistencia → Paciente)"]),
        step=0.1,
    )
    tasa_no_show = st.number_input(
        "No-Show (%)", min_value=0.0, max_value=100.0, value=float(resumen_base["Tasa de No-Show"]), step=0.1
    )

    ticket_promedio = st.number_input(
        "Ticket promedio ($)", min_value=0.0, value=float(resumen_base["Ticket promedio ($)"]), step=10.0
    )
    ingreso_estimado = st.number_input(
        "Ingreso estimado ($)", min_value=0.0, value=float(resumen_base["Ingreso estimado ($)"]), step=100.0
    )

    st.subheader("Pipeline")
    pipeline_values = {}
    for stage, default_value in DEFAULT_PIPELINE.items():
        pipeline_values[stage] = st.number_input(stage, min_value=0, value=default_value, step=1)

    st.subheader("Cuellos de botella (%)")
    cuello_values = {}
    for stage, default_value in DEFAULT_CUELLOS.items():
        cuello_values[stage] = st.number_input(stage, min_value=0.0, max_value=100.0, value=default_value, step=0.1)

    st.subheader("Proyección")
    no_show_pacientes = st.number_input("No-shows actuales", min_value=0, value=40, step=1)
    recuperables_pct = st.number_input("% recuperables", min_value=0.0, max_value=100.0, value=50.0, step=1.0)

resumen = {
    "Leads totales": leads_totales,
    "Leads calificados": leads_calificados,
    "Citas agendadas": citas_agendadas,
    "Citas asistidas": citas_asistidas,
    "Pacientes cerrados": pacientes_cerrados,
    "Tasa de conversión Lead → Cita": tasa_lead_cita,
    "Tasa de asistencia (Show rate)": show_rate,
    "Tasa de cierre (Asistencia → Paciente)": tasa_cierre,
    "Tasa de No-Show": tasa_no_show,
    "Ticket promedio ($)": ticket_promedio,
    "Ingreso estimado ($)": ingreso_estimado,
}

pipeline_df = pd.DataFrame({"Etapa": list(pipeline_values.keys()), "Cantidad": list(pipeline_values.values())})
cuellos_df = pd.DataFrame({"Etapa": list(cuello_values.keys()), "Conversión": [f"{v:.1f}%" for v in cuello_values.values()]})

canales_df = pd.DataFrame(
    {
        "Canal": ["Instagram Ads", "Google Ads", "Facebook Ads", "Web / Orgánico"],
        "leads": [100, 80, 90, 50],
        "citas": [60, 50, 45, 25],
        "pacientes": [35, 30, 20, 10],
    }
)
canales_df["Conv. cita %"] = (canales_df["citas"] / canales_df["leads"] * 100).round(1)
canales_df["Conv. cierre %"] = (canales_df["pacientes"] / canales_df["citas"] * 100).round(1)

st.title("Dashboard de Conversión Clínica")
st.caption("Diseño modular con entrada manual en la barra izquierda.")

col_top_1, col_top_2, col_top_3, col_top_4 = st.columns(4)
with col_top_1:
    module_card("Leads totales", f"{resumen['Leads totales']:,}", "Leads recibidos")
with col_top_2:
    module_card("Leads calificados", f"{resumen['Leads calificados']:,}", "Potencial real")
with col_top_3:
    module_card("Citas agendadas", f"{resumen['Citas agendadas']:,}", "Agenda comercial")
with col_top_4:
    module_card("Pacientes cerrados", f"{resumen['Pacientes cerrados']:,}", "Cierres totales")

col_rate_1, col_rate_2, col_rate_3, col_rate_4 = st.columns(4)
with col_rate_1:
    module_card("Lead → Cita", f"{resumen['Tasa de conversión Lead → Cita']:.1f}%", "Conversión a cita")
with col_rate_2:
    module_card("Show rate", f"{resumen['Tasa de asistencia (Show rate)']:.1f}%", "Asistencia a cita")
with col_rate_3:
    module_card("Asistencia → Cierre", f"{resumen['Tasa de cierre (Asistencia → Paciente)']:.1f}%", "Tasa de cierre")
with col_rate_4:
    module_card("No-Show", f"{resumen['Tasa de No-Show']:.1f}%", "Citas perdidas")

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
    st.dataframe(canales_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-box"><h3>Cuellos de botella</h3></div>', unsafe_allow_html=True)
    st.table(cuellos_df)

    recuperables = int(no_show_pacientes * (recuperables_pct / 100))
    extra_ingresos = int(recuperables * ticket_promedio)

    st.markdown('<div class="section-box"><h3>Proyección de ingresos</h3></div>', unsafe_allow_html=True)
    p_col_1, p_col_2 = st.columns(2)
    with p_col_1:
        module_card("No-shows actuales", str(no_show_pacientes), "Pacientes perdidos")
    with p_col_2:
        module_card("Recuperables", str(recuperables), f"{recuperables_pct:.0f}% de recuperación")
    module_card("Ingreso adicional potencial", f"${extra_ingresos:,.0f}", "Ticket promedio aplicado")

st.markdown("---")
st.info("Tip: cada cambio en el panel izquierdo actualiza en tiempo real todo el dashboard.")
