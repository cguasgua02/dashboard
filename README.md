# Dashboard de Conversión Clínica

Dashboard en Streamlit con diseño modular, tema oscuro y flujo de captura en 3 etapas con validación de coherencia.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Flujo recomendado (implementado)

### Campo previo (empresa)
Antes de la etapa 1, captura el **nombre de la empresa**.
El título se actualiza dinámicamente como:
- `Diagnóstico para Clínica NOMBRE_EMPRESA`

### Etapa 1: Leads por canal
Completa la tabla por canal con:
- `leads`
- `citas`
- `pacientes`
- `gasto_publicitario`

Canales por defecto:
- Meta Ads
- Google Ads
- Orgánico
- Bases de Datos

El sistema calcula automáticamente:
- `Conv. cita %`
- `Conv. cierre %`

> Si cambias la etapa 1, la etapa 2 se reinicia con valores sugeridos para evitar inconsistencias.

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
- Tasa de cierre real

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

Y calcula:
- Potencial Recuperable
- Dinero perdido
- Potencial recuperable anual
- Dinero perdido anual

## KPIs adicionales
El dashboard muestra también:
- Interfaz con tema oscuro fijo (no depende del modo claro/oscuro del sistema o navegador).
- Inversión total (suma gasto publicitario)
- CPL = inversión total / leads totales
- CPA = inversión total / ventas
- Facturación actual = ventas x ticket
- ROAS = facturación / inversión

Incluye mensaje interpretativo de ROAS:
- `Por cada $1 dolar invertido, generas $X`

Además, el dashboard incorpora un bloque de feedback según ROAS:
- **ROAS < 2**: Diagnóstico Crítico + recomendación urgente y nota de benchmark (3 a 5).
- **ROAS entre 2 y 5**: Diagnóstico Estable + oportunidad de optimización operativa.
- **ROAS > 5**: Diagnóstico Excelente + recomendación de escala.

## Validaciones cruzadas
Al pulsar **Enviar**, el sistema valida:
- suma de leads por canal = leads totales
- suma de citas por canal = citas agendadas
- suma de pacientes por canal = pacientes cerrados
- citas no asistidas = citas agendadas - citas asistidas

Si hay errores, muestra mensajes y no actualiza el dashboard hasta que todo sea coherente.


## Bloques finales de diagnóstico
Al final del dashboard se muestran dos bloques estratégicos:

1. **Feedback ROAS** con mensaje condicional:
   - ROAS < 2: Diagnóstico Crítico
   - ROAS entre 2 y 5: Diagnóstico Estable
   - ROAS > 5: Diagnóstico Excelente

2. **Oportunidad Estratégica Detectada** con reglas:
   - Si ROAS > 5 y No-Show > 20%: "Tu marketing funciona. Tu sistema de confirmación no."
   - Si ROAS < 2: "Antes de escalar publicidad, necesitas optimizar cierre y recuperación."
   - Si Dinero Perdido Mensual > 0: mensaje de tensión operativa por fugas de eficiencia.
