# Dashboard de Conversión Clínica

Dashboard online en Streamlit con diseño modular para seguimiento comercial clínico.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ¿Cómo funciona?

- En la **barra lateral izquierda** tienes un formulario para capturar:
  - Leads, citas y pacientes cerrados.
  - Tasas de conversión y no-show.
  - Conteo por etapa del pipeline.
  - Conversiones por cuello de botella.
  - Parámetros de proyección de ingresos.
- El dashboard se actualiza **en tiempo real** conforme editas cada valor.

## Datos iniciales

- El sistema parte con valores por defecto.
- Si existe `data/resumen.csv`, se usa para precargar métricas base.
- No se requieren cargas manuales de CSV por parte del usuario final.
