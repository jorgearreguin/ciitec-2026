# Requirements Document

## Introduction

Sistema de monitoreo del conductor (DMS) de laboratorio para conferencia universitaria. El sistema detecta distracción mediante cámara y modelo de IA, luego aplica lógica determinista para decidir cuándo alertar al conductor según la normativa ADDW (Alerta Avanzada de Distracción) del Reglamento General de Seguridad de la Unión Europea.

## Glosario

- **DMS**: Sistema de Monitoreo del Conductor (Driver Monitoring System)
- **ADDW**: Alerta Avanzada de Distracción (Advanced Driver Distraction Warning)
- **Modelo_IA**: Componente que estima estado del conductor mediante visión por computadora
- **Logica_Decision**: Componente determinista que decide si emitir alerta basándose en estimaciones
- **Cuadro**: Instante de análisis del sistema (frame de cámara con datos asociados)
- **Mirada_Fuera**: Estado donde el conductor no mira hacia el camino
- **Ojos_Cerrados**: Estado donde ambos ojos del conductor están cerrados

## Requirements

### Requirement 1: Detección de distracción por velocidad

**User Story:** Como conductor, quiero que el sistema detecte cuando estoy distraído y me alerte antes de que sea peligroso, para mantenerme seguro en la carretera.

#### Acceptance Criteria

1. **REQ-01** (Origen: ADDW) CUANDO la velocidad del vehículo sea mayor o igual a 20 km/h, CUANDO la Mirada_Fuera esté activa continuamente durante 6000 ms o más, EL DMS DEBE emitir una alerta de distracción.

2. **REQ-02** (Origen: ADDW) CUANDO la velocidad del vehículo sea mayor o igual a 50 km/h, CUANDO la Mirada_Fuera esté activa continuamente durante 3500 ms o más, EL DMS DEBE emitir una alerta de distracción.

3. **REQ-03** (Origen: SUPUESTO) CUANDO la velocidad del vehículo sea menor a 20 km/h, EL DMS DEBE inhibir las alertas de distracción.

### Requirement 2: Detección de somnolencia

**User Story:** Como conductor, quiero que el sistema detecte señales de somnolencia para alertarme antes de quedarme dormido al volante.

#### Acceptance Criteria

1. **REQ-04** (Origen: SUPUESTO) CUANDO Ojos_Cerrados esté activo continuamente durante 2000 ms o más, EL DMS DEBE emitir una alerta de somnolencia.

2. **REQ-05** (Origen: SUPUESTO) CUANDO la velocidad del vehículo sea menor a 20 km/h, EL DMS DEBE continuar monitoreando somnolencia y emitir alertas de Ojos_Cerrados.

### Requirement 3: Modalidades de alerta

**User Story:** Como conductor, necesito alertas efectivas que capten mi atención sin resultar abrumadoras.

#### Acceptance Criteria

1. **REQ-06** (Origen: ADDW) CUANDO el DMS emita una alerta, EL DMS DEBE presentar una señal visual combinada con al menos una señal sonora o vibración.

2. **REQ-07** (Origen: SUPUESTO) CUANDO el DMS emita una alerta de distracción, EL DMS DEBE mostrar el mensaje "ATENCIÓN: MIRADA FUERA DEL CAMINO" en la interfaz visual.

3. **REQ-08** (Origen: SUPUESTO) CUANDO el DMS emita una alerta de somnolencia, EL DMS DEBE mostrar el mensaje "ATENCIÓN: SOMNOLENCIA DETECTADA" en la interfaz visual.

### Requirement 4: Monitoreo no disponible

**User Story:** Como conductor, quiero saber cuando el sistema no puede monitorearme para entender sus limitaciones.

#### Acceptance Criteria

1. **REQ-09** (Origen: SUPUESTO) CUANDO el Modelo_IA no detecte un rostro visible en el Cuadro actual, EL DMS DEBE emitir una alerta de monitoreo no disponible.

2. **REQ-10** (Origen: SUPUESTO) CUANDO el DMS emita una alerta de monitoreo no disponible, EL DMS DEBE mostrar el mensaje "SISTEMA NO DISPONIBLE: ROSTRO NO VISIBLE" en la interfaz visual.

### Requirement 5: Persistencia de alertas

**User Story:** Como conductor, necesito que las alertas persistan hasta que corrija mi comportamiento, para asegurarme de tomar acción.

#### Acceptance Criteria

1. **REQ-11** (Origen: SUPUESTO) MIENTRAS una alerta de distracción esté activa, CUANDO la Mirada_Fuera siga activa, EL DMS DEBE mantener la alerta de distracción.

2. **REQ-12** (Origen: SUPUESTO) MIENTRAS una alerta de distracción esté activa, CUANDO la Mirada_Fuera se desactive, EL DMS DEBE cancelar la alerta de distracción dentro de 100 ms.

3. **REQ-13** (Origen: SUPUESTO) MIENTRAS una alerta de somnolencia esté activa, CUANDO Ojos_Cerrados siga activo, EL DMS DEBE mantener la alerta de somnolencia.

4. **REQ-14** (Origen: SUPUESTO) MIENTRAS una alerta de somnolencia esté activa, CUANDO Ojos_Cerrados se desactive, EL DMS DEBE cancelar la alerta de somnolencia dentro de 100 ms.

### Requirement 6: Prioridad de alertas

**User Story:** Como conductor, necesito que el sistema priorice la información más crítica cuando ocurren múltiples condiciones simultáneamente.

#### Acceptance Criteria

1. **REQ-15** (Origen: SUPUESTO) CUANDO tanto Mirada_Fuera como Ojos_Cerrados alcancen sus umbrales simultáneamente, EL DMS DEBE emitir únicamente la alerta de somnolencia.

2. **REQ-16** (Origen: SUPUESTO) CUANDO una alerta de monitoreo no disponible esté activa, EL DMS DEBE suprimir todas las alertas de distracción y somnolencia.

### Requirement 7: Procesamiento de entrada

**User Story:** Como desarrollador del sistema, necesito que la Logica_Decision procese datos estandarizados del Modelo_IA para tomar decisiones correctas.

#### Acceptance Criteria

1. **REQ-17** (Origen: SUPUESTO) CUANDO la Logica_Decision reciba un Cuadro, EL DMS DEBE procesar los siguientes datos: tiempo en ms (entero), velocidad en km/h (número con un decimal), rostro_visible (booleano), mirada_fuera (booleano), ojos_cerrados (booleano).

2. **REQ-18** (Origen: SUPUESTO) CUANDO la Logica_Decision procese un Cuadro, EL DMS DEBE devolver exactamente una de estas alertas: "ninguna", "distraccion", "somnolencia", o "monitoreo_no_disponible".

### Requirement 8: Privacidad y almacenamiento

**User Story:** Como usuario del sistema, quiero que mis datos de monitoreo permanezcan privados y no se almacenen de forma que puedan identificarme.

#### Acceptance Criteria

1. **REQ-19** (Origen: ADDW) EL DMS DEBE procesar todos los datos del conductor localmente sin transmitirlos fuera del vehículo.

2. **REQ-20** (Origen: ADDW) EL DMS DEBE operar sin realizar identificación biométrica del conductor.

### Requirement 9: Reinicio de temporizadores

**User Story:** Como conductor, quiero que el sistema reinicie sus contadores cuando corrijo mi comportamiento, para evitar alertas injustificadas.

#### Acceptance Criteria

1. **REQ-21** (Origen: SUPUESTO) CUANDO Mirada_Fuera se desactive antes de alcanzar el umbral de alerta, EL DMS DEBE reiniciar el temporizador de distracción a 0 ms.

2. **REQ-22** (Origen: SUPUESTO) CUANDO Ojos_Cerrados se desactive antes de alcanzar el umbral de alerta, EL DMS DEBE reiniciar el temporizador de somnolencia a 0 ms.

## Preguntas para el cliente

Los siguientes aspectos están marcados como SUPUESTO en los requisitos y requieren confirmación:

1. **REQ-03**: ¿Es correcto inhibir alertas de distracción por debajo de 20 km/h? ¿Hay algún umbral mínimo diferente?

2. **REQ-04**: ¿Cuál es el umbral correcto para detectar somnolencia (ojos cerrados)? Hemos supuesto 2000 ms.

3. **REQ-05**: ¿El monitoreo de somnolencia debe estar activo incluso a velocidades menores a 20 km/h?

4. **REQ-07, REQ-08, REQ-10**: ¿Cuáles son los mensajes exactos que deben mostrarse en cada tipo de alerta?

5. **REQ-09**: ¿Cuándo el rostro no es visible, se debe emitir una alerta de "monitoreo no disponible" o simplemente no emitir ninguna alerta?

6. **REQ-11 a REQ-14**: ¿Cuál es el tiempo máximo aceptable para cancelar una alerta una vez que la condición desaparece? Hemos supuesto 100 ms.

7. **REQ-15**: ¿Qué alerta tiene prioridad cuando ocurren múltiples condiciones simultáneamente (somnolencia vs. distracción)?

8. **REQ-16**: ¿Las alertas de distracción y somnolencia deben suprimirse cuando no hay rostro visible?

9. **REQ-17**: ¿Cuál es el formato exacto de los datos de entrada que proporciona el Modelo_IA? ¿La velocidad requiere un decimal de precisión?

10. **REQ-21, REQ-22**: ¿El reinicio de temporizadores debe ser instantáneo o hay algún periodo de gracia?
