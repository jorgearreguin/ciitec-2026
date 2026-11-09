# Implementation Plan: Sistema de Alerta de Distracción

## Overview

El plan de implementación del DMS se organiza en 4 tareas grandes que cubren la implementación completa del módulo de lógica de alertas y su suite de pruebas. El enfoque prioriza la trazabilidad completa: cada requisito REQ-01 a REQ-16 debe estar implementado en código con comentarios `# REQ-NN`, verificado por pruebas unitarias con nomenclatura `test_reqNN_*`, y validado por el script `trazabilidad.py`.

La estructura sigue el diseño documentado, con separación entre la lógica determinista (`logica_alerta.py`) y las pruebas de valores límite (`test_limites.py`). Todas las pruebas son requeridas para garantizar la cobertura completa de la matriz de trazabilidad.

## Tasks

- [ ] 1. Implementar logica_alerta.py completo
  - Crear archivo `logica_alerta.py` en la raíz del proyecto
  - Definir todas las constantes según el diseño: UMBRAL_DISTRACCION_ALTA_VELOCIDAD (3500 ms), UMBRAL_DISTRACCION_MEDIA_VELOCIDAD (6000 ms), UMBRAL_SOMNOLENCIA (2000 ms), UMBRAL_SIN_ROSTRO (2000 ms), VELOCIDAD_MINIMA_DISTRACCION (20.0 km/h), VELOCIDAD_ALTA (50.0 km/h)
  - Implementar clase `LogicaAlerta` con método `__init__()` que inicializa todos los temporizadores a `None` y la alerta actual a "ninguna"
  - Implementar estado interno: `_inicio_mirada_fuera_ms`, `_inicio_ojos_cerrados_ms`, `_inicio_sin_rostro_ms`, `_alerta_actual`, `_ultimo_tiempo_ms`
  - Implementar método `procesar_cuadro(tiempo_ms, velocidad_kmh, rostro_visible, mirada_fuera, ojos_cerrados)` con toda la lógica del algoritmo documentado en el diseño
  - Implementar validación de entrada completa: tipos correctos (REQ-13), valores no negativos para tiempo_ms y velocidad_kmh, secuencia monótona de tiempo_ms
  - Implementar lógica de monitoreo no disponible: detectar ausencia de rostro durante 2000 ms (REQ-06), suprimir otras alertas cuando está activa (REQ-12)
  - Implementar lógica de somnolencia: detectar ojos cerrados durante 2000 ms (REQ-04), monitorear a cualquier velocidad (REQ-05), mantener mientras ojos_cerrados=True (REQ-09), cancelar cuando ojos_cerrados=False (REQ-10), reiniciar temporizador antes del umbral (REQ-16), prioridad sobre distracción (REQ-11)
  - Implementar lógica de distracción: umbral 3500 ms para velocidad >= 50 km/h (REQ-01), umbral 6000 ms para 20-50 km/h (REQ-02), inhibir < 20 km/h (REQ-03), mantener mientras mirada_fuera=True (REQ-07), cancelar cuando mirada_fuera=False (REQ-08), reiniciar temporizador antes del umbral (REQ-15), menor prioridad que somnolencia (REQ-11)
  - Implementar retorno de salida determinista: devolver exactamente una de "ninguna", "distraccion", "somnolencia", "monitoreo_no_disponible" (REQ-14)
  - CRÍTICO: Agregar comentarios `# REQ-NN` en las líneas correspondientes del código para cada requisito REQ-01 a REQ-16 según el mapa de trazabilidad del diseño
  - CRÍTICO: Usar temporizadores basados en tiempo de inicio (guardar `tiempo_ms` del primer cuadro, calcular duración como `tiempo_ms_actual - tiempo_inicio`), NO acumular deltas
  - _Requisitos: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16_

- [ ] 2. Implementar test_limites.py con todas las pruebas
  - Crear archivo `test_limites.py` en la raíz del proyecto
  - Importar `unittest` y `LogicaAlerta` de `logica_alerta`
  - Implementar clase `TestValidacionEntrada` con pruebas de REQ-13: `test_req13_tipos_correctos` (acepta int, float, bool), `test_req13_tiempo_negativo` (rechaza tiempo_ms < 0), `test_req13_velocidad_negativa` (rechaza velocidad_kmh < 0), `test_req13_secuencia_no_monotona` (rechaza tiempos desordenados)
  - Implementar clase `TestDistraccionAltaVelocidad` con pruebas de REQ-01: `test_req01_justo_antes_umbral` (50 km/h, mirada fuera 3499 ms → sin alerta), `test_req01_en_umbral` (50 km/h, mirada fuera 3500 ms → alerta distracción), `test_req01_temporizador_inicio_no_acumulador` (verificar que usa tiempo_inicio, no delta acumulado)
  - Implementar clase `TestDistraccionVelocidadMedia` con pruebas de REQ-02: `test_req02_justo_antes_umbral_49kmh` (49.9 km/h, mirada fuera 5999 ms → sin alerta), `test_req02_en_umbral_49_9_kmh` (49.9 km/h, mirada fuera 6000 ms → alerta distracción), `test_req02_limite_inferior_20kmh` (20.0 km/h, mirada fuera 6000 ms → alerta distracción)
  - Implementar clase `TestInhibicionBajaVelocidad` con pruebas de REQ-03: `test_req03_19_9_kmh_sin_alerta` (19.9 km/h, mirada fuera 7000 ms → sin alerta), `test_req03_transicion_velocidad` (alerta activa a 25 km/h, luego reduce a 19 km/h → cancela alerta)
  - Implementar clase `TestSomnolencia` con pruebas de REQ-04, REQ-05, REQ-09, REQ-10, REQ-16: `test_req04_justo_antes_umbral` (ojos cerrados 1999 ms → sin alerta), `test_req04_en_umbral` (ojos cerrados 2000 ms → alerta somnolencia), `test_req05_somnolencia_baja_velocidad` (10 km/h, ojos cerrados 2000 ms → alerta somnolencia), `test_req09_persistencia_somnolencia` (alerta activa, ojos_cerrados=True → persiste), `test_req10_cancelacion_somnolencia` (alerta activa, ojos_cerrados=False → cancela), `test_req16_reinicio_temporizador_somnolencia` (ojos cerrados 1500 ms, abre, cierra nuevamente → reinicia contador)
  - Implementar clase `TestMonitoreoNoDisponible` con pruebas de REQ-06, REQ-12: `test_req06_justo_antes_umbral` (sin rostro 1999 ms → sin alerta), `test_req06_en_umbral` (sin rostro 2000 ms → alerta monitoreo_no_disponible), `test_req12_supresion_por_monitoreo_no_disponible` (alerta distracción activa, sin rostro 2000 ms → suprime con monitoreo_no_disponible)
  - Implementar clase `TestPersistenciaAlertas` con pruebas de REQ-07, REQ-08, REQ-11, REQ-15: `test_req07_persistencia_distraccion` (alerta activa, mirada_fuera=True → persiste), `test_req08_cancelacion_distraccion` (alerta activa, mirada_fuera=False → cancela), `test_req11_prioridad_somnolencia_sobre_distraccion` (ambas condiciones alcanzan umbral → emite somnolencia), `test_req15_reinicio_temporizador_distraccion` (mirada fuera 2000 ms, vuelve al frente, mirada fuera nuevamente → reinicia contador)
  - Implementar clase `TestSalidaDeterminista` con prueba de REQ-14: `test_req14_salidas_validas` (verificar que todas las salidas pertenecen al conjunto {"ninguna", "distraccion", "somnolencia", "monitoreo_no_disponible"})
  - CRÍTICO: Todos los nombres de método de prueba deben empezar con `test_reqNN_` donde NN es el número de requisito (ejemplos: test_req13_tiempo_negativo, test_req01_justo_antes_umbral, test_req02_limite_inferior_20kmh)
  - CRÍTICO: Todas las pruebas verifican valores límite exactos documentados en el diseño
  - CRÍTICO: Cada método de prueba incluye docstring con "Verifica: REQ-NN" para trazabilidad automática
  - _Requisitos: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16_

- [ ] 3. Ejecutar pruebas y corregir fallos
  - Ejecutar `python -m unittest test_limites -v` desde la raíz del proyecto
  - Analizar los fallos reportados por unittest (AssertionError, ValueError, TypeError, etc.)
  - Corregir errores en `logica_alerta.py` si la lógica de decisión es incorrecta
  - Corregir errores en `test_limites.py` si las aserciones o secuencias de cuadros son incorrectas
  - Repetir ejecución de pruebas hasta que todas pasen (100% success rate)
  - Verificar que no hay advertencias de deprecación ni otros problemas
  - _Requisitos: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16_

- [ ] 4. Validar trazabilidad completa
  - Ejecutar `python trazabilidad.py --estricto` desde la raíz del proyecto
  - Revisar la salida: debe reportar "Trazabilidad completa: sin huecos" o listar huecos específicos
  - Si hay huecos en código: agregar comentarios `# REQ-NN` faltantes en `logica_alerta.py` en las líneas correspondientes
  - Si hay huecos en pruebas: agregar métodos de prueba faltantes con nomenclatura `test_reqNN_*` en `test_limites.py`
  - Repetir ejecución de `python trazabilidad.py --estricto` hasta que termine sin huecos
  - Revisar archivo `matriz_trazabilidad.md` generado: verificar que cada requisito tiene entrada en código y prueba
  - Revisar archivo `matriz_trazabilidad.csv` generado: verificar que no hay celdas vacías en las columnas de código y prueba
  - _Requisitos: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16_

## Notes

- **Sin tareas opcionales**: Todas las pruebas son requeridas para completar la matriz de trazabilidad sin huecos
- **Nomenclatura obligatoria**: Todos los métodos de prueba usan `test_reqNN_*` para extracción automática por `trazabilidad.py`
- **Trazabilidad triple**: Cada requisito REQ-NN debe aparecer en (1) comentario de código `# REQ-NN`, (2) nombre de método `test_reqNN_*`, (3) docstring "Verifica: REQ-NN"
- **Estructura plana**: Ambos archivos (`logica_alerta.py` y `test_limites.py`) van en la raíz del proyecto, no en carpetas `src/` o `tests/`
- **Sin dependencias externas**: Solo módulo estándar `unittest`, sin Hypothesis ni pytest
- **Temporizadores críticos**: Usar tiempo de inicio (`tiempo_ms` del primer cuadro), NO acumuladores delta
- **Valores límite exactos**: Las pruebas verifican el valor justo antes del umbral (sin alerta) y el valor exacto del umbral (con alerta)
- **Umbrales del diseño**: 3500 ms (distracción >= 50 km/h), 6000 ms (distracción 20-50 km/h), 2000 ms (somnolencia), 2000 ms (sin rostro)
- **Material didáctico**: Este DMS es para demostración universitaria, no está validado para uso en vehículos reales

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2"] },
    { "id": 2, "tasks": ["3"] },
    { "id": 3, "tasks": ["4"] }
  ]
}
```
