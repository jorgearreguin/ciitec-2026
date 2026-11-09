# Matriz de trazabilidad

Especificación: `.kiro\specs\sistema-alerta-distraccion\requirements.md` · Generada: 2026-11-09 12:37 · Pruebas: 26 de 26 pasan

Cadena: regla → requisito (REQ-NN) → código (`# REQ-NN`) → prueba (`test_reqNN_…`) → resultado.

| Requisito | Origen | Qué exige | Código | Pruebas | Resultado | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-01 | ADDW | MIENTRAS la velocidad sea de 50 km/h o más, CUANDO Mirada_Fuera esté activa continuamente durante 3500 ms o más, EL DMS DEBE emitir una alerta de distracción. | logica_alerta.py: 21, 28, 47, 162, 169, 172 | 3 | 3/3 pasan | Completo |
| REQ-02 | ADDW | MIENTRAS la velocidad sea de 20 km/h o más y menor de 50 km/h, CUANDO Mirada_Fuera esté activa continuamente durante 6000 ms o más, EL DMS DEBE emitir una alerta de distracción. | logica_alerta.py: 22, 47, 162, 170, 174 | 3 | 3/3 pasan | Completo |
| REQ-03 | SUPUESTO | MIENTRAS la velocidad sea menor a 20 km/h, EL DMS DEBE inhibir las alertas de distracción. | logica_alerta.py: 27, 153, 154, 158, 160 | 2 | 2/2 pasan | Completo |
| REQ-04 | SUPUESTO | CUANDO Ojos_Cerrados esté activo continuamente durante 2000 ms o más, EL DMS DEBE emitir una alerta de somnolencia. | logica_alerta.py: 23, 48, 136, 140 | 2 | 2/2 pasan | Completo |
| REQ-05 | SUPUESTO | MIENTRAS la velocidad sea menor a 20 km/h, EL DMS DEBE continuar monitoreando somnolencia y emitir alertas de Ojos_Cerrados. | logica_alerta.py: 133 | 1 | 1/1 pasan | Completo |
| REQ-06 | SUPUESTO | CUANDO el Modelo_IA no detecte un rostro visible continuamente durante 2000 ms o más, EL DMS DEBE emitir una alerta de monitoreo no disponible. | logica_alerta.py: 24, 49, 118, 122 | 2 | 2/2 pasan | Completo |
| REQ-07 | SUPUESTO | MIENTRAS una alerta de distracción esté activa, CUANDO Mirada_Fuera siga activa, EL DMS DEBE mantener la alerta de distracción. | logica_alerta.py: 52, 177 | 1 | 1/1 pasan | Completo |
| REQ-08 | SUPUESTO | MIENTRAS una alerta de distracción esté activa, CUANDO Mirada_Fuera se desactive, EL DMS DEBE cancelar la alerta de distracción dentro de 100 ms. | logica_alerta.py: 52, 182, 184 | 1 | 1/1 pasan | Completo |
| REQ-09 | SUPUESTO | MIENTRAS una alerta de somnolencia esté activa, CUANDO Ojos_Cerrados siga activo, EL DMS DEBE mantener la alerta de somnolencia. | logica_alerta.py: 52, 142 | 1 | 1/1 pasan | Completo |
| REQ-10 | SUPUESTO | MIENTRAS una alerta de somnolencia esté activa, CUANDO Ojos_Cerrados se desactive, EL DMS DEBE cancelar la alerta de somnolencia dentro de 100 ms. | logica_alerta.py: 52, 147, 149 | 1 | 1/1 pasan | Completo |
| REQ-11 | SUPUESTO | CUANDO tanto Mirada_Fuera como Ojos_Cerrados alcancen sus umbrales simultáneamente, EL DMS DEBE emitir únicamente la alerta de somnolencia. | logica_alerta.py: 52, 132 | 1 | 1/1 pasan | Completo |
| REQ-12 | SUPUESTO | MIENTRAS una alerta de monitoreo no disponible esté activa, EL DMS DEBE suprimir todas las alertas de distracción y somnolencia. | logica_alerta.py: 52, 116, 123, 124 | 1 | 1/1 pasan | Completo |
| REQ-13 | SUPUESTO | CUANDO la Logica_Decision reciba un Cuadro, EL DMS DEBE procesar los siguientes datos: tiempo en ms (entero), velocidad en km/h (número con un decimal), rostro_visible (booleano), mirada_fuera (booleano), ojos_cerrados (booleano). | logica_alerta.py: 84, 100 | 4 | 4/4 pasan | Completo |
| REQ-14 | SUPUESTO | CUANDO la Logica_Decision procese un Cuadro, EL DMS DEBE devolver exactamente una de estas alertas: "ninguna", "distraccion", "somnolencia", o "monitoreo_no_disponible". | logica_alerta.py: 125, 186, 187 | 1 | 1/1 pasan | Completo |
| REQ-15 | SUPUESTO | CUANDO Mirada_Fuera se desactive antes de alcanzar el umbral de alerta, EL DMS DEBE reiniciar el temporizador de distracción a 0 ms. | logica_alerta.py: 47, 155, 157, 179, 181 | 1 | 1/1 pasan | Completo |
| REQ-16 | SUPUESTO | CUANDO Ojos_Cerrados se desactive antes de alcanzar el umbral de alerta, EL DMS DEBE reiniciar el temporizador de somnolencia a 0 ms. | logica_alerta.py: 48, 144, 146 | 1 | 1/1 pasan | Completo |

## Huecos

- Ninguno: cada requisito tiene origen, código y pruebas que pasan.

## Detalle de pruebas por requisito

**REQ-01**

- `test_req01_en_umbral`: pasa
- `test_req01_justo_antes_umbral`: pasa
- `test_req01_temporizador_inicio_no_acumulador`: pasa

**REQ-02**

- `test_req02_en_umbral_49_9_kmh`: pasa
- `test_req02_justo_antes_umbral_49kmh`: pasa
- `test_req02_limite_inferior_20kmh`: pasa

**REQ-03**

- `test_req03_19_9_kmh_sin_alerta`: pasa
- `test_req03_transicion_velocidad`: pasa

**REQ-04**

- `test_req04_en_umbral`: pasa
- `test_req04_justo_antes_umbral`: pasa

**REQ-05**

- `test_req05_somnolencia_baja_velocidad`: pasa

**REQ-06**

- `test_req06_en_umbral`: pasa
- `test_req06_justo_antes_umbral`: pasa

**REQ-07**

- `test_req07_persistencia_distraccion`: pasa

**REQ-08**

- `test_req08_cancelacion_distraccion`: pasa

**REQ-09**

- `test_req09_persistencia_somnolencia`: pasa

**REQ-10**

- `test_req10_cancelacion_somnolencia`: pasa

**REQ-11**

- `test_req11_prioridad_somnolencia_sobre_distraccion`: pasa

**REQ-12**

- `test_req12_supresion_por_monitoreo_no_disponible`: pasa

**REQ-13**

- `test_req13_secuencia_no_monotona`: pasa
- `test_req13_tiempo_negativo`: pasa
- `test_req13_tipos_correctos`: pasa
- `test_req13_velocidad_negativa`: pasa

**REQ-14**

- `test_req14_salidas_validas`: pasa

**REQ-15**

- `test_req15_reinicio_temporizador_distraccion`: pasa

**REQ-16**

- `test_req16_reinicio_temporizador_somnolencia`: pasa

