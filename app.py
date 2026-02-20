from __future__ import annotations

import copy

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Diagnóstico de Conversión Clínica", layout="wide")

DEFAULT_CHANNELS = pd.DataFrame(
    {
        "Canal": ["Meta Ads", "Google Ads", "Orgánico", "Bases de Datos"],
        "leads": [100, 80, 90, 50],
        "citas": [60, 50, 45, 25],
        "pacientes": [35, 30, 20, 10],
        "gasto_publicitario": [1200.0, 1000.0, 300.0, 200.0],
    }
)


def build_default_summary(channels_df: pd.DataFrame) -> dict[str, int]:
    return {
        "Leads totales": int(channels_df["leads"].sum()),
        "Leads calificados": 240,
        "Citas agendadas": int(channels_df["citas"].sum()),
        "Citas asistidas": 140,
        "Citas no asistidas": 40,
        "Pacientes cerrados": int(channels_df["pacientes"].sum()),
    }


def format_percentage(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100, 1)


def compute_rates(summary: dict[str, int]) -> dict[str, float]:
    return {
        "Lead → Cita": format_percentage(summary["Citas agendadas"], summary["Leads totales"]),
        "Asistencia → Cierre": format_percentage(summary["Pacientes cerrados"], summary["Citas asistidas"]),
        "Show rate": format_percentage(summary["Citas asistidas"], summary["Citas agendadas"]),
        "No-Show rate": format_percentage(summary["Citas no asistidas"], summary["Citas agendadas"]),
        "Tasa de cierre real": format_percentage(summary["Pacientes cerrados"], summary["Leads totales"]),
    }


def compute_pipeline(summary: dict[str, int]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Etapa": ["Nuevo", "Contactado", "Agendado", "Asistió", "Cerrado", "No Show"],
            "Cantidad": [
                max(summary["Leads totales"] - summary["Leads calificados"], 0),
                summary["Leads calificados"],
                summary["Citas agendadas"],
                summary["Citas asistidas"],
                summary["Pacientes cerrados"],
                summary["Citas no asistidas"],
            ],
        }
    )


def validate_consistency(channels_df: pd.DataFrame, summary: dict[str, int]) -> list[str]:
    errors = []
    if int(channels_df["leads"].sum()) != summary["Leads totales"]:
        errors.append("La suma de leads por canal debe ser igual a Leads totales.")
    if int(channels_df["citas"].sum()) != summary["Citas agendadas"]:
        errors.append("La suma de citas por canal debe ser igual a Citas agendadas.")
    if int(channels_df["pacientes"].sum()) != summary["Pacientes cerrados"]:
        errors.append("La suma de pacientes por canal debe ser igual a Pacientes cerrados.")

    expected_no_show = summary["Citas agendadas"] - summary["Citas asistidas"]
    if summary["Citas no asistidas"] != expected_no_show:
        errors.append("Citas no asistidas debe ser igual a Citas agendadas - Citas asistidas.")

    if summary["Leads calificados"] > summary["Leads totales"]:
        errors.append("Leads calificados no puede ser mayor que Leads totales.")
    if summary["Citas asistidas"] > summary["Citas agendadas"]:
        errors.append("Citas asistidas no puede ser mayor que Citas agendadas.")

    return errors


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root, html, body, [data-testid="stAppViewContainer"], .stApp {
            color-scheme: dark !important;
            --background-color: #0a1033 !important;
            --secondary-background-color: #121843 !important;
            --text-color: #f0f4ff !important;
            --primary-color: #3f84ff !important;
        }
        .stApp { background-color: #0a1033 !important; color: #f0f4ff !important; }
        .block-container { padding-top: 1.1rem; max-width: 1280px; }
        [data-testid="stSidebar"] {
            background-color: #101a4d !important;
            border-right: 1px solid rgba(123, 162, 255, 0.25);
        }
        [data-testid="stSidebar"] * { color: #f0f4ff !important; }
        [data-testid="stHeader"] {
            background: #0a1033 !important;
            border-bottom: 1px solid rgba(133, 177, 255, 0.15);
        }
        [data-testid="stToolbar"] {
            background: #0a1033 !important;
        }
        [data-testid="stToolbar"] * {
            color: #f0f4ff !important;
        }

        .stTextInput input,
        .stNumberInput input,
        [data-baseweb="input"] input,
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        textarea {
            background-color: #121843 !important;
            color: #ffffff !important;
            border-color: rgba(133, 177, 255, 0.35) !important;
        }

        .stNumberInput button,
        [data-testid="stNumberInputStepUp"],
        [data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInput"] button {
            background-color: #121843 !important;
            color: #ffffff !important;
            border: 1px solid rgba(133, 177, 255, 0.35) !important;
        }

        [data-testid="stDataFrame"] [data-testid="stToolbar"],
        [data-testid="stDataFrame"] [role="toolbar"],
        [data-testid="stDataEditor"] [role="toolbar"] {
            background-color: #121843 !important;
            color: #ffffff !important;
            border-bottom: 1px solid rgba(133, 177, 255, 0.25) !important;
        }

        [data-testid="stDataEditor"],
        [data-testid="stDataEditor"] * {
            background-color: #121843 !important;
            color: #ffffff !important;
            border-color: rgba(133, 177, 255, 0.25) !important;
        }

        .stDataFrame, .stTable, .stMarkdownTable {
            background-color: #121843 !important;
            color: #ffffff !important;
            border-radius: 10px;
        }
        .stDataFrame [role="gridcell"],
        .stDataFrame [role="columnheader"],
        .stTable td,
        .stTable th,
        .stMarkdownTable td,
        .stMarkdownTable th {
            color: #ffffff !important;
            background-color: #121843 !important;
            border-color: rgba(133, 177, 255, 0.25) !important;
        }
        .module-card {
            background: linear-gradient(145deg, #151d4f 0%, #121843 100%);
            border: 1px solid rgba(133, 177, 255, 0.25);
            border-radius: 12px;
            padding: 12px 14px;
            min-height: 105px;
            box-shadow: 0 8px 20px rgba(7, 11, 35, 0.35);
            margin-bottom: 10px;
        }
        .module-title {
            color: #9fb4ff;
            font-size: .82rem;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        .module-value { font-size: 1.9rem; font-weight: 700; color: #ffffff; }
        .module-value.warning { color: #ffa63d; }
        .module-value.danger { color: #ff4d4d; }
        .module-note { color: #b7c6f6; font-size: .82rem; }
        .section-box {
            background: #121843;
            border: 1px solid rgba(133, 177, 255, 0.2);
            border-radius: 12px;
            padding: 10px 12px;
            margin: 8px 0 12px;
        }
        .section-box h3 { color: #eaf0ff; margin: 0; }
        .roas-feedback {
            background: #0f173f;
            border: 1px solid rgba(133, 177, 255, 0.2);
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 8px;
            margin-bottom: 10px;
            color: #f0f4ff;
            line-height: 1.35;
        }
        .roas-note {
            color: #9aa4c5;
            font-size: 0.78rem;
            margin-top: 8px;
        }
        .table-scroll {
            width: 100%;
            overflow-x: auto;
            overflow-y: hidden;
        }
        .dark-table {
            width: 100%;
            min-width: 720px;
            border-collapse: collapse;
            background-color: #121843;
            color: #ffffff;
            border: 1px solid rgba(133, 177, 255, 0.25);
            border-radius: 10px;
            overflow: hidden;
        }
        .dark-table th, .dark-table td {
            padding: 10px 12px;
            border: 1px solid rgba(133, 177, 255, 0.20);
            background-color: #121843;
            color: #ffffff;
            text-align: left;
        }
        .dark-table th {
            background-color: #17215b;
            color: #eaf0ff;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def module_card(title: str, value: str, note: str = "", value_class: str = "") -> None:
    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-title">{title}</div>
            <div class="module-value {value_class}">{value}</div>
            <div class="module-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "stage1_channels" not in st.session_state:
        st.session_state.stage1_channels = DEFAULT_CHANNELS.copy()
        st.session_state.stage1_signature = tuple(DEFAULT_CHANNELS[["leads", "citas", "pacientes"]].to_numpy().flatten())

    if "company_name" not in st.session_state:
        st.session_state.company_name = ""

    if "stage2_summary" not in st.session_state:
        st.session_state.stage2_summary = build_default_summary(st.session_state.stage1_channels)

    if "stage3_projection" not in st.session_state:
        st.session_state.stage3_projection = {"Ticket promedio": 300.0, "% recuperación": 50.0}

    if "applied" not in st.session_state:
        summary = copy.deepcopy(st.session_state.stage2_summary)
        channels = st.session_state.stage1_channels.copy()
        st.session_state.applied = {
            "company": st.session_state.company_name,
            "channels": channels,
            "summary": summary,
            "rates": compute_rates(summary),
            "pipeline": compute_pipeline(summary),
            "ticket": st.session_state.stage3_projection["Ticket promedio"],
            "recovery": st.session_state.stage3_projection["% recuperación"],
        }


def stage_company() -> None:
    st.sidebar.markdown("### Empresa")
    company = st.sidebar.text_input("Nombre de la empresa", value=st.session_state.company_name, placeholder="Ej: Santa María")
    st.session_state.company_name = company.strip()


def stage1_form() -> None:
    st.sidebar.markdown("### 1) Leads por canal")
    st.sidebar.caption("Incluye gasto publicitario con valores sugeridos por canal.")
    edited = st.sidebar.data_editor(
        st.session_state.stage1_channels,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Canal"],
        column_config={
            "leads": st.column_config.NumberColumn("leads", min_value=0, step=1),
            "citas": st.column_config.NumberColumn("citas", min_value=0, step=1),
            "pacientes": st.column_config.NumberColumn("pacientes", min_value=0, step=1),
            "gasto_publicitario": st.column_config.NumberColumn(
                "gasto_publicitario", min_value=0.0, step=50.0, format="$ %.0f"
            ),
        },
    )

    st.session_state.stage1_channels = edited.astype(
        {"leads": int, "citas": int, "pacientes": int, "gasto_publicitario": float}
    )
    new_signature = tuple(edited[["leads", "citas", "pacientes"]].to_numpy().flatten())

    if new_signature != st.session_state.stage1_signature:
        st.session_state.stage2_summary = build_default_summary(st.session_state.stage1_channels)
        st.session_state.stage1_signature = new_signature
        st.sidebar.warning(
            "Cambiaste la etapa 1, por eso se reinició la etapa 2 con valores sugeridos. Revísala antes de enviar."
        )


def stage2_form() -> None:
    st.sidebar.markdown("### 2) Resumen y pipeline")
    s = st.session_state.stage2_summary

    leads_totales = st.sidebar.number_input("Leads totales", min_value=0, value=int(s["Leads totales"]), step=1)
    leads_calificados = st.sidebar.number_input(
        "Leads calificados/contactados", min_value=0, value=int(s["Leads calificados"]), step=1
    )
    citas_agendadas = st.sidebar.number_input("Citas agendadas", min_value=0, value=int(s["Citas agendadas"]), step=1)
    citas_asistidas = st.sidebar.number_input("Citas asistidas", min_value=0, value=int(s["Citas asistidas"]), step=1)
    citas_no_asistidas = st.sidebar.number_input(
        "Citas no asistidas", min_value=0, value=int(s["Citas no asistidas"]), step=1
    )
    pacientes_cerrados = st.sidebar.number_input(
        "Pacientes cerrados", min_value=0, value=int(s["Pacientes cerrados"]), step=1
    )

    st.session_state.stage2_summary = {
        "Leads totales": int(leads_totales),
        "Leads calificados": int(leads_calificados),
        "Citas agendadas": int(citas_agendadas),
        "Citas asistidas": int(citas_asistidas),
        "Citas no asistidas": int(citas_no_asistidas),
        "Pacientes cerrados": int(pacientes_cerrados),
    }


def stage3_form() -> None:
    st.sidebar.markdown("### 3) Proyección de ingresos")
    p = st.session_state.stage3_projection
    ticket = st.sidebar.number_input("Ticket promedio ($)", min_value=0.0, value=float(p["Ticket promedio"]), step=10.0)
    recovery = st.sidebar.number_input(
        "% recuperación de no-shows", min_value=0.0, max_value=100.0, value=float(p["% recuperación"]), step=1.0
    )

    st.session_state.stage3_projection = {"Ticket promedio": float(ticket), "% recuperación": float(recovery)}


def apply_button() -> None:
    st.sidebar.markdown("---")
    st.sidebar.info("Al enviar, se valida la coherencia de todos los datos ingresados.")
    if st.sidebar.button("Enviar", type="primary", use_container_width=True):
        summary = st.session_state.stage2_summary
        channels = st.session_state.stage1_channels
        errors = validate_consistency(channels, summary)
        if errors:
            for error in errors:
                st.sidebar.error(error)
            return

        st.session_state.applied = {
            "company": st.session_state.company_name,
            "channels": channels.copy(),
            "summary": copy.deepcopy(summary),
            "rates": compute_rates(summary),
            "pipeline": compute_pipeline(summary),
            "ticket": st.session_state.stage3_projection["Ticket promedio"],
            "recovery": st.session_state.stage3_projection["% recuperación"],
        }
        st.sidebar.success("Dashboard actualizado correctamente.")


apply_theme()
init_state()
st.sidebar.header("Formulario secuencial")
st.sidebar.caption("Completa las 3 etapas en la misma página y presiona Enviar para validar y actualizar.")
stage_company()
stage1_form()
stage2_form()
stage3_form()
apply_button()

a = st.session_state.applied
channels_df = a["channels"].copy()
summary = a["summary"]
rates = a["rates"]
pipeline_df = a["pipeline"]

company = a.get("company", "").strip()
title_company = company if company else "Tu Empresa"

ticket_promedio = float(a["ticket"])
recovery_pct = float(a["recovery"])

total_inversion = float(channels_df["gasto_publicitario"].sum())
total_leads = int(summary["Leads totales"])
total_ventas = int(summary["Pacientes cerrados"])

cpl = total_inversion / total_leads if total_leads > 0 else 0.0
cpa = total_inversion / total_ventas if total_ventas > 0 else 0.0

facturacion_actual = total_ventas * ticket_promedio
roas = facturacion_actual / total_inversion if total_inversion > 0 else 0.0

no_shows = int(summary["Citas no asistidas"])
potencial_recuperable = int(no_shows * (recovery_pct / 100) * ticket_promedio)
dinero_perdido = int(no_shows * ticket_promedio)
potencial_recuperable_anual = potencial_recuperable * 12
dinero_perdido_anual = dinero_perdido * 12

channels_df["Conv. cita %"] = channels_df.apply(lambda row: format_percentage(row["citas"], row["leads"]), axis=1)
channels_df["Conv. cierre %"] = channels_df.apply(
    lambda row: format_percentage(row["pacientes"], row["citas"]), axis=1
)

st.title(f"Diagnóstico para Clínica {title_company}")
st.caption("Flujo en 3 etapas: canales → resumen/pipeline → proyección, con validaciones cruzadas.")

k1, k2, k3, k4 = st.columns(4)
with k1:
    module_card("Leads totales", f"{total_leads:,}", "Etapa 2")
with k2:
    module_card("Citas agendadas", f"{summary['Citas agendadas']:,}", "Etapa 2")
with k3:
    module_card("Citas asistidas", f"{summary['Citas asistidas']:,}", "Etapa 2")
with k4:
    module_card("Pacientes cerrados", f"{total_ventas:,}", "Etapa 2")

inv1, inv2, inv3 = st.columns(3)
with inv1:
    module_card("Inversión total", f"${total_inversion:,.0f}", "Suma gasto publicitario")
with inv2:
    module_card("CPL", f"${cpl:,.2f}", "Inversión / Leads totales")
with inv3:
    module_card("CPA", f"${cpa:,.2f}", "Inversión / Ventas")

r1, r2, r3, r4, r5 = st.columns(5)
with r1:
    module_card("Lead → Cita", f"{rates['Lead → Cita']:.1f}%", "Calculado automáticamente")
with r2:
    module_card("Show rate", f"{rates['Show rate']:.1f}%", "Calculado automáticamente")
with r3:
    module_card("No-Show", f"{rates['No-Show rate']:.1f}%", "Calculado automáticamente")
with r4:
    module_card("Asistencia → Cierre", f"{rates['Asistencia → Cierre']:.1f}%", "Calculado automáticamente")
with r5:
    close_class = ""
    if rates["Tasa de cierre real"] < 35:
        close_class = "danger"
    elif rates["Tasa de cierre real"] < 50:
        close_class = "warning"
    module_card("Tasa de cierre real", f"{rates['Tasa de cierre real']:.1f}%", "Ventas / Leads", close_class)

left, right = st.columns([1.4, 1])

with left:
    st.markdown('<div class="section-box"><h3>Pipeline (calculado desde etapa 2)</h3></div>', unsafe_allow_html=True)
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

with right:
    st.markdown('<div class="section-box"><h3>Cuellos de botella (calculados)</h3></div>', unsafe_allow_html=True)
    bottlenecks = pd.DataFrame(
        {
            "Etapa": ["Lead → Cita", "Cita → Asistencia", "Asistencia → Cierre", "Cierre real"],
            "Conversión": [
                f"{rates['Lead → Cita']:.1f}%",
                f"{rates['Show rate']:.1f}%",
                f"{rates['Asistencia → Cierre']:.1f}%",
                f"{rates['Tasa de cierre real']:.1f}%",
            ],
        }
    )
    st.table(bottlenecks)

    st.markdown('<div class="section-box"><h3>Facturación y ROAS</h3></div>', unsafe_allow_html=True)
    module_card("Facturación actual", f"${facturacion_actual:,.0f}", "Ventas x Ticket promedio")
    module_card("ROAS", f"{roas:,.2f}x", "Facturación / Inversión")
    st.markdown(f"**Por cada $1 dolar invertido, generas ${roas:,.2f}.**")

    st.markdown('<div class="section-box"><h3>Proyección de ingresos</h3></div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        module_card("No-shows", f"{no_shows:,}", "Desde etapa 2")
    with p2:
        module_card("Potencial Recuperable", f"${potencial_recuperable:,.0f}", f"{recovery_pct:.0f}% de recuperación")
    module_card("Dinero perdido", f"${dinero_perdido:,.0f}", "No-shows x Ticket promedio")
    module_card("Potencial recuperable anual", f"${potencial_recuperable_anual:,.0f}", "Potencial recuperable x 12")
    module_card("Dinero perdido anual", f"${dinero_perdido_anual:,.0f}", "Dinero perdido x 12")

st.markdown('<div class="section-box"><h3>Leads por canal + conversiones</h3></div>', unsafe_allow_html=True)
table_html = channels_df.to_html(index=False, classes="dark-table", border=0)
st.markdown(f'<div class="table-scroll">{table_html}</div>', unsafe_allow_html=True)


# Bloques finales: Feedback + Oportunidad Estratégica
if roas < 2:
    roas_title = "Diagnóstico Crítico"
    roas_body = (
        "Tu costo de adquisición es alto. Estás recuperando menos de $2 por cada $1 invertido. "
        "Revisa urgentemente tu tasa de cierre y la calidad de tus leads."
    )
    roas_note = "El promedio saludable en clínicas estéticas se encuentra entre 3 y 5."
elif roas <= 5:
    roas_title = "Diagnóstico Estable"
    roas_body = (
        "Tu clínica es rentable, pero existen fugas operativas. Optimizar la confirmación y "
        "recuperación de citas podría aumentar tu facturación sin incrementar la inversión publicitaria."
    )
    roas_note = "Tu rentabilidad está dentro del rango promedio saludable del sector."
else:
    roas_title = "Diagnóstico Excelente"
    roas_body = (
        "Tu modelo comercial es altamente eficiente. Existe margen suficiente para escalar la "
        "inversión publicitaria con bajo riesgo."
    )
    roas_note = "Estás por encima del promedio habitual del sector (3–5)."

if roas > 5 and rates["No-Show rate"] > 20:
    oportunidad_texto = "Tu marketing funciona. Tu sistema de confirmación no."
elif roas < 2:
    oportunidad_texto = "Antes de escalar publicidad, necesitas optimizar cierre y recuperación."
elif dinero_perdido > 0:
    oportunidad_texto = (
        "Tu clínica no tiene un problema de demanda.\n"
        "Tiene un problema de eficiencia operativa.\n"
        "Si corriges las fugas actuales, podrías aumentar tu facturación sin invertir un dólar adicional en publicidad."
    )
else:
    oportunidad_texto = "No se detectan fugas operativas relevantes con los datos actuales."

st.markdown('<div class="section-box"><h3>Feedback ROAS</h3></div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="roas-feedback">
        <strong>{roas_title}:</strong><br>
        {roas_body}
        <div class="roas-note">{roas_note}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-box"><h3>Oportunidad Estratégica Detectada</h3></div>', unsafe_allow_html=True)
oportunidad_html = oportunidad_texto.replace("\n", "<br>")
st.markdown(
    f"""
    <div class="roas-feedback">
        {oportunidad_html}
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")


