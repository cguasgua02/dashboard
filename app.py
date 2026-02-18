from __future__ import annotations

import copy

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Dashboard de Conversión Clínica", layout="wide")

DEFAULT_CHANNELS = pd.DataFrame(
    {
        "Canal": ["Instagram Ads", "Google Ads", "Facebook Ads", "Web / Orgánico"],
        "leads": [100, 80, 90, 50],
        "citas": [60, 50, 45, 25],
        "pacientes": [35, 30, 20, 10],
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
        .stApp { background-color: #0a1033; color: #f0f4ff; }
        .block-container { padding-top: 1.1rem; max-width: 1280px; }
        [data-testid="stSidebar"] {
            background-color: #101a4d;
            border-right: 1px solid rgba(123, 162, 255, 0.25);
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
        .module-value {
            font-size: 1.9rem;
            font-weight: 700;
            color: #ffffff;
        }
        .module-note { color: #b7c6f6; font-size: .82rem; }
        .section-box {
            background: #121843;
            border: 1px solid rgba(133, 177, 255, 0.2);
            border-radius: 12px;
            padding: 10px 12px;
            margin: 8px 0 12px;
        }
        .section-box h3 { color: #eaf0ff; margin: 0; }
        </style>
        """,
        unsafe_allow_html=True,
    )


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


def init_state() -> None:
    if "stage1_channels" not in st.session_state:
        st.session_state.stage1_channels = DEFAULT_CHANNELS.copy()
        st.session_state.stage1_signature = tuple(DEFAULT_CHANNELS[["leads", "citas", "pacientes"]].to_numpy().flatten())

    if "stage2_summary" not in st.session_state:
        st.session_state.stage2_summary = build_default_summary(st.session_state.stage1_channels)

    if "stage3_projection" not in st.session_state:
        st.session_state.stage3_projection = {"Ticket promedio": 300.0, "% recuperación": 50.0}

    if "applied" not in st.session_state:
        summary = copy.deepcopy(st.session_state.stage2_summary)
        channels = st.session_state.stage1_channels.copy()
        st.session_state.applied = {
            "channels": channels,
            "summary": summary,
            "rates": compute_rates(summary),
            "pipeline": compute_pipeline(summary),
            "ticket": st.session_state.stage3_projection["Ticket promedio"],
            "recovery": st.session_state.stage3_projection["% recuperación"],
        }


def stage1_form() -> None:
    st.sidebar.markdown("### 1) Leads por canal")
    with st.sidebar.form("stage1_form"):
        edited = st.data_editor(
            st.session_state.stage1_channels,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            disabled=["Canal"],
            column_config={
                "leads": st.column_config.NumberColumn("leads", min_value=0, step=1),
                "citas": st.column_config.NumberColumn("citas", min_value=0, step=1),
                "pacientes": st.column_config.NumberColumn("pacientes", min_value=0, step=1),
            },
        )
        save_stage1 = st.form_submit_button("Guardar etapa 1")

    if save_stage1:
        st.session_state.stage1_channels = edited.astype({"leads": int, "citas": int, "pacientes": int})
        new_signature = tuple(edited[["leads", "citas", "pacientes"]].to_numpy().flatten())

        if new_signature != st.session_state.stage1_signature:
            suggested = build_default_summary(st.session_state.stage1_channels)
            st.session_state.stage2_summary = suggested
            st.session_state.stage1_signature = new_signature
            st.sidebar.warning(
                "Cambiaste la etapa 1, por eso se reinició la etapa 2 con valores sugeridos. Revísala antes de aplicar."
            )
        else:
            st.sidebar.success("Etapa 1 guardada.")


def stage2_form() -> None:
    st.sidebar.markdown("### 2) Resumen y pipeline")
    s = st.session_state.stage2_summary

    with st.sidebar.form("stage2_form"):
        leads_totales = st.number_input("Leads totales", min_value=0, value=int(s["Leads totales"]), step=1)
        leads_calificados = st.number_input("Leads calificados/contactados", min_value=0, value=int(s["Leads calificados"]), step=1)
        citas_agendadas = st.number_input("Citas agendadas", min_value=0, value=int(s["Citas agendadas"]), step=1)
        citas_asistidas = st.number_input("Citas asistidas", min_value=0, value=int(s["Citas asistidas"]), step=1)
        citas_no_asistidas = st.number_input(
            "Citas no asistidas", min_value=0, value=int(s["Citas no asistidas"]), step=1
        )
        pacientes_cerrados = st.number_input("Pacientes cerrados", min_value=0, value=int(s["Pacientes cerrados"]), step=1)
        save_stage2 = st.form_submit_button("Guardar etapa 2")

    if save_stage2:
        st.session_state.stage2_summary = {
            "Leads totales": int(leads_totales),
            "Leads calificados": int(leads_calificados),
            "Citas agendadas": int(citas_agendadas),
            "Citas asistidas": int(citas_asistidas),
            "Citas no asistidas": int(citas_no_asistidas),
            "Pacientes cerrados": int(pacientes_cerrados),
        }
        st.sidebar.success("Etapa 2 guardada.")


def stage3_form() -> None:
    st.sidebar.markdown("### 3) Proyección de ingresos")
    p = st.session_state.stage3_projection
    with st.sidebar.form("stage3_form"):
        ticket = st.number_input("Ticket promedio ($)", min_value=0.0, value=float(p["Ticket promedio"]), step=10.0)
        recovery = st.number_input(
            "% recuperación de no-shows", min_value=0.0, max_value=100.0, value=float(p["% recuperación"]), step=1.0
        )
        save_stage3 = st.form_submit_button("Guardar etapa 3")

    if save_stage3:
        st.session_state.stage3_projection = {"Ticket promedio": float(ticket), "% recuperación": float(recovery)}
        st.sidebar.success("Etapa 3 guardada.")


def apply_button() -> None:
    st.sidebar.markdown("---")
    st.sidebar.info("Cuando termines, aplica para validar coherencia entre las 3 etapas.")
    if st.sidebar.button("Actualizar dashboard", type="primary", use_container_width=True):
        summary = st.session_state.stage2_summary
        channels = st.session_state.stage1_channels
        errors = validate_consistency(channels, summary)
        if errors:
            for error in errors:
                st.sidebar.error(error)
            return

        st.session_state.applied = {
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
st.sidebar.caption("Puedes editar cualquier etapa, pero siempre valida con el botón final.")
stage1_form()
stage2_form()
stage3_form()
apply_button()

a = st.session_state.applied
channels_df = a["channels"].copy()
summary = a["summary"]
rates = a["rates"]
pipeline_df = a["pipeline"]

ticket_promedio = float(a["ticket"])
recovery_pct = float(a["recovery"])
recuperables = int(summary["Citas no asistidas"] * (recovery_pct / 100))
extra_ingresos = int(recuperables * ticket_promedio)

channels_df["Conv. cita %"] = channels_df.apply(lambda row: format_percentage(row["citas"], row["leads"]), axis=1)
channels_df["Conv. cierre %"] = channels_df.apply(
    lambda row: format_percentage(row["pacientes"], row["citas"]), axis=1
)

st.title("Dashboard de Conversión Clínica")
st.caption("Flujo en 3 etapas: canales → resumen/pipeline → proyección, con validaciones cruzadas.")

k1, k2, k3, k4 = st.columns(4)
with k1:
    module_card("Leads totales", f"{summary['Leads totales']:,}", "Etapa 2")
with k2:
    module_card("Citas agendadas", f"{summary['Citas agendadas']:,}", "Etapa 2")
with k3:
    module_card("Citas asistidas", f"{summary['Citas asistidas']:,}", "Etapa 2")
with k4:
    module_card("Pacientes cerrados", f"{summary['Pacientes cerrados']:,}", "Etapa 2")

r1, r2, r3, r4 = st.columns(4)
with r1:
    module_card("Lead → Cita", f"{rates['Lead → Cita']:.1f}%", "Calculado automáticamente")
with r2:
    module_card("Show rate", f"{rates['Show rate']:.1f}%", "Calculado automáticamente")
with r3:
    module_card("Asistencia → Cierre", f"{rates['Asistencia → Cierre']:.1f}%", "Calculado automáticamente")
with r4:
    module_card("No-Show", f"{rates['No-Show rate']:.1f}%", "Calculado automáticamente")

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

    st.markdown('<div class="section-box"><h3>Leads por canal + conversiones</h3></div>', unsafe_allow_html=True)
    st.dataframe(channels_df, use_container_width=True, hide_index=True)

with right:
    st.markdown('<div class="section-box"><h3>Cuellos de botella (calculados)</h3></div>', unsafe_allow_html=True)
    bottlenecks = pd.DataFrame(
        {
            "Etapa": ["Lead → Cita", "Cita → Asistencia", "Asistencia → Cierre"],
            "Conversión": [
                f"{rates['Lead → Cita']:.1f}%",
                f"{rates['Show rate']:.1f}%",
                f"{rates['Asistencia → Cierre']:.1f}%",
            ],
        }
    )
    st.table(bottlenecks)

    st.markdown('<div class="section-box"><h3>Proyección de ingresos</h3></div>', unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        module_card("No-shows", str(summary["Citas no asistidas"]), "Desde etapa 2")
    with p2:
        module_card("Recuperables", str(recuperables), f"{recovery_pct:.0f}% recuperación")
    module_card("Ingreso adicional", f"${extra_ingresos:,.0f}", f"Ticket: ${ticket_promedio:,.0f}")

st.markdown("---")
st.info(
    "Recomendación aplicada: 3 formularios secuenciales + botón final de validación. "
    "Así puedes editar cualquier etapa, pero el dashboard solo se actualiza cuando todo es coherente."
)
