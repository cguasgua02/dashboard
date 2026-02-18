# Dashboard de Conversión Clínica

Dashboard online en Streamlit para clínicas que gestionan sus datos en Excel/CSV.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura de datos

Puedes usar los CSV de ejemplo en `data/` o cargar los tuyos desde la barra lateral del dashboard.

- `resumen.csv`: columnas `metrica, valor`
- `pipeline.csv`: columnas `Etapa, Cantidad`
- `canales.csv`: columnas `Canal, leads, citas, pacientes`
- `cuellos.csv`: columnas `Etapa, Conversión`

## Flujo

1. Resumen general de KPIs.
2. Pipeline visual por etapas.
3. Análisis por canal (barras + tabla de conversiones).
4. Cuellos de botella.
5. Proyección de ingresos por recuperación de no-shows.
