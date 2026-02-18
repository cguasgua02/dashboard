# Dashboard de Conversión Clínica

Dashboard en Streamlit con diseño modular y flujo de captura en 3 etapas con validación de coherencia.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Flujo recomendado (implementado)

### Etapa 1: Leads por canal
Completa la tabla por canal con:
- `leads`
- `citas`
- `pacientes`

El sistema calcula automáticamente:
- `Conv. cita %`
- `Conv. cierre %`

> Si cambias la etapa 1 la etapa 2 se reinicia con valores sugeridos para evitar inconsistencias.

### Etapa 2: Resumen y pipeline
Captura:
- leads totales
- leads calificados/contactados
- citas agendadas
- citas asistidas
- citas no asistidas
- pacientes cerrados

Con estos datos el sistema calcula automáticamente:
- Lead → Cita
- Show rate
- Asistencia → Cierre
- No-Show rate

Y además construye el Pipeline:
- Nuevo
- Contactado
- Agendado
- Asistió
- Cerrado
- No Show

### Etapa 3: Proyección
Captura:
- ticket promedio
- % recuperación de no-shows

Y calcula ingreso adicional potencial.

## Validaciones cruzadas
Al pulsar **Enviar**, el sistema valida:
- suma de leads por canal = leads totales
- suma de citas por canal = citas agendadas
- suma de pacientes por canal = pacientes cerrados
- citas no asistidas = citas agendadas - citas asistidas

Si hay errores, muestra mensajes y no actualiza el dashboard hasta que todo sea coherente.
