# Design Document

## Overview

El Sistema de Monitoreo del Conductor (DMS) es un sistema de laboratorio para demostración universitaria que detecta distracción y somnolencia del conductor mediante visión por computadora y lógica determinista. El diseño sigue la normativa ADDW (Alerta Avanzada de Distracción) del Reglamento General de Seguridad de la Unión Europea.

### Objetivos del Diseño

1. **Separación de responsabilidades**: Modelo de IA separado de la lógica de decisión
2. **Determinismo**: Toda la lógica de decisión es reproducible y verificable
3. **Precisión temporal**: Umbrales exactos en milisegundos enteros para evitar errores de punto flotante
4. **Trazabilidad**: Cada decisión mapea a un requisito específico

### Arquitectura de dos capas

- **Capa de Percepción** (Modelo_IA): Estima estado del conductor mediante MediaPipe u otro modelo
- **Capa de Decisión** (Logica_Decision): Procesa estimaciones y decide cuándo alertar

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Aplicación Principal                   │
│                    (fuera de alcance)                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │     Modelo_IA          │
          │   (MediaPipe, etc.)    │
          │                        │
          │  - Detecta rostro      │
          │  - Estima mirada       │
          │  - Estima ojos         │
          └───────────┬────────────┘
                      │
                      │ Cuadro (tiempo_ms, velocidad, 
                      │         rostro_visible, mirada_fuera,
                      │         ojos_cerrados)
                      ▼
          ┌────────────────────────┐
          │  Logica_Decision       │
          │  (logica_alerta.py)    │
          │                        │
          │  - Acumula tiempo      │
          │  - Evalúa umbrales     │
          │  - Decide alerta       │
          └───────────┬────────────┘
                      │
                      │ Alerta: "ninguna" | "distraccion" |
                      │         "somnolencia" | "monitoreo_no_disponible"
                      ▼
          ┌────────────────────────┐
          │  Sistema de Alertas    │
          │   (fuera de alcance)   │
          │                        │
          │  - Visual + sonido     │
          │  - Mensajes            │
          └────────────────────────┘
```

### Responsabilidades

- **Modelo_IA**: Estimación, no decisión
- **Logica_Decision**: Decisión determinista basada en reglas y tiempo
- **Sistema de Alertas**: Presentación multimodal (visual + auditiva)

## Components and Interfaces

### Componente: Logica_Decision

**Archivo**: `logica_alerta.py`

**Responsabilidad**: Procesar cuadros secuenciales y emitir alertas según la normativa ADDW.

#### Interfaz Pública

```python
class LogicaAlerta:
    """
    Lógica determinista de alertas del DMS.
    No depende de bibliotecas de visión; opera solo con datos numéricos.
    """
    
    def __init__(self) -> None:
        """
        Inicializa el monitor con todos los temporizadores en 0 ms.
        Cubre: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16
        """
        pass
    
    def procesar_cuadro(
        self,
        tiempo_ms: int,
        velocidad_kmh: float,
        rostro_visible: bool,
        mirada_fuera: bool,
        ojos_cerrados: bool
    ) -> str:
        """
        Procesa un cuadro y devuelve la alerta correspondiente.
        
        Args:
            tiempo_ms: Tiempo absoluto del cuadro en milisegundos (entero no negativo)
            velocidad_kmh: Velocidad del vehículo en km/h (número con un decimal)
            rostro_visible: True si el modelo detecta rostro
            mirada_fuera: True si el modelo estima que la mirada está fuera del camino
            ojos_cerrados: True si el modelo estima que ambos ojos están cerrados
            
        Returns:
            Una de: "ninguna", "distraccion", "somnolencia", "monitoreo_no_disponible"
            
        Cubre: REQ-13, REQ-14
        """
        pass
```

#### Estado Interno

El módulo mantiene el siguiente estado privado:

```python
# Tiempos de inicio de cada condición (None cuando inactivos)
_inicio_mirada_fuera_ms: Optional[int]    # REQ-01, REQ-02, REQ-15
_inicio_ojos_cerrados_ms: Optional[int]   # REQ-04, REQ-16
_inicio_sin_rostro_ms: Optional[int]      # REQ-06

# Alerta actual
_alerta_actual: str  # REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12
```

**Nota crítica sobre temporizadores**: En lugar de acumular `delta_ms`, el sistema guarda `tiempo_ms` del primer cuadro en que se activa cada condición. Alertar cuando `(tiempo_ms - tiempo_inicio) >= umbral`. Razón: sumar deltas cuenta el intervalo anterior a que empiece la condición y alerta antes de tiempo.

#### Algoritmo de Procesamiento de Cuadro

```python
def procesar_cuadro(tiempo_ms, velocidad_kmh, rostro_visible, mirada_fuera, ojos_cerrados):
    # REQ-13: Validación de tipos de entrada
    
    # REQ-12: Prioridad a monitoreo no disponible
    if not rostro_visible:
        if _inicio_sin_rostro_ms is None:
            _inicio_sin_rostro_ms = tiempo_ms
        if (tiempo_ms - _inicio_sin_rostro_ms) >= 2000:
            _alerta_actual = "monitoreo_no_disponible"
            # Suprimir otras alertas
            return _alerta_actual  # REQ-14
    else:
        # Rostro visible: reiniciar temporizador sin rostro
        _inicio_sin_rostro_ms = None
        if _alerta_actual == "monitoreo_no_disponible":
            _alerta_actual = "ninguna"
    
    # REQ-11: Prioridad somnolencia sobre distracción
    # REQ-05: Evaluar somnolencia sin restricción de velocidad
    alerta_somnolencia = False
    if ojos_cerrados:
        if _inicio_ojos_cerrados_ms is None:
            _inicio_ojos_cerrados_ms = tiempo_ms
        if (tiempo_ms - _inicio_ojos_cerrados_ms) >= 2000:
            alerta_somnolencia = True
            _alerta_actual = "somnolencia"
    else:
        # REQ-16, REQ-10: Reiniciar y cancelar
        if _inicio_ojos_cerrados_ms is not None:
            _inicio_ojos_cerrados_ms = None
            if _alerta_actual == "somnolencia":
                _alerta_actual = "ninguna"
    
    # REQ-09: Mantener alerta de somnolencia mientras ojos_cerrados = True
    # Solo evaluar distracción si no hay alerta de somnolencia
    if not alerta_somnolencia:
        # REQ-03: Inhibir distracción < 20 km/h
        if velocidad_kmh < 20.0:
            if _inicio_mirada_fuera_ms is not None:
                _inicio_mirada_fuera_ms = None
            if _alerta_actual == "distraccion":
                _alerta_actual = "ninguna"
        else:
            # REQ-01, REQ-02: Umbrales por velocidad
            if mirada_fuera:
                if _inicio_mirada_fuera_ms is None:
                    _inicio_mirada_fuera_ms = tiempo_ms
                
                duracion_ms = tiempo_ms - _inicio_mirada_fuera_ms
                umbral = 3500 if velocidad_kmh >= 50.0 else 6000
                
                if duracion_ms >= umbral:
                    _alerta_actual = "distraccion"
            else:
                # REQ-15, REQ-08: Reiniciar y cancelar
                if _inicio_mirada_fuera_ms is not None:
                    _inicio_mirada_fuera_ms = None
                    if _alerta_actual == "distraccion":
                        _alerta_actual = "ninguna"
    
    # REQ-07: Mantener alerta de distracción mientras mirada_fuera = True
    return _alerta_actual  # REQ-14: Salida determinista
```

### Umbrales y Constantes

```python
# Umbrales de tiempo (en milisegundos)
UMBRAL_DISTRACCION_ALTA_VELOCIDAD = 3500  # REQ-01: >= 50 km/h
UMBRAL_DISTRACCION_MEDIA_VELOCIDAD = 6000 # REQ-02: 20-50 km/h
UMBRAL_SOMNOLENCIA = 2000                 # REQ-04
UMBRAL_SIN_ROSTRO = 2000                  # REQ-06
TIMEOUT_CANCELACION = 100                 # REQ-08, REQ-10

# Umbrales de velocidad (en km/h)
VELOCIDAD_MINIMA_DISTRACCION = 20.0       # REQ-03
VELOCIDAD_ALTA = 50.0                     # REQ-01
```

## Data Models

### Cuadro de Entrada

```python
@dataclass
class Cuadro:
    """
    Datos de entrada para un instante de análisis.
    Producido por Modelo_IA, consumido por Logica_Decision.
    """
    tiempo_ms: int           # Tiempo absoluto, no negativo
    velocidad_kmh: float     # Velocidad con un decimal de precisión
    rostro_visible: bool     # True si hay rostro detectado
    mirada_fuera: bool       # True si mirada fuera del camino
    ojos_cerrados: bool      # True si ambos ojos cerrados
```

**Invariantes**:
- `tiempo_ms >= 0`
- `velocidad_kmh >= 0.0`
- Cuadros procesados en orden cronológico creciente

### Tipos de Alerta

```python
from enum import Enum

class TipoAlerta(str, Enum):
    """
    Posibles alertas que puede emitir la Logica_Decision.
    """
    NINGUNA = "ninguna"                           # No hay alerta activa
    DISTRACCION = "distraccion"                   # REQ-01, REQ-02
    SOMNOLENCIA = "somnolencia"                   # REQ-04
    MONITOREO_NO_DISPONIBLE = "monitoreo_no_disponible"  # REQ-06
```

## Correctness Properties

*Aunque este diseño usa unittest en lugar de property-based testing con Hypothesis, las propiedades de corrección siguen describiendo el comportamiento esperado del sistema en términos formales. Estas propiedades se implementarán como casos de prueba con secuencias fijas dentro de clases `unittest.TestCase`.*

### Property 1: Umbral de distracción a alta velocidad

Para cualquier secuencia de cuadros donde la velocidad sea >= 50 km/h y mirada_fuera esté continuamente activa, el sistema DEBE emitir alerta de distracción cuando la duración acumulada alcance exactamente 3500 ms.

**Validates: REQ-01**

### Property 2: Umbral de distracción a velocidad media

Para cualquier secuencia de cuadros donde la velocidad sea >= 20 km/h y < 50 km/h y mirada_fuera esté continuamente activa, el sistema DEBE emitir alerta de distracción cuando la duración acumulada alcance exactamente 6000 ms.

**Validates: REQ-02**

### Property 3: Inhibición de distracción a baja velocidad

Para cualquier secuencia de cuadros donde la velocidad sea < 20 km/h, el sistema NO DEBE emitir alertas de distracción independientemente del estado de mirada_fuera.

**Validates: REQ-03**

### Property 4: Umbral de somnolencia

Para cualquier secuencia de cuadros donde ojos_cerrados esté continuamente activo, el sistema DEBE emitir alerta de somnolencia cuando la duración acumulada alcance exactamente 2000 ms.

**Validates: REQ-04**

### Property 5: Monitoreo de somnolencia a baja velocidad

Para cualquier secuencia de cuadros donde la velocidad sea < 20 km/h y ojos_cerrados esté activo, el sistema DEBE continuar evaluando somnolencia y emitir alerta correspondiente.

**Validates: REQ-05**

### Property 6: Monitoreo no disponible

Para cualquier secuencia de cuadros donde rostro_visible sea False continuamente, el sistema DEBE emitir alerta de monitoreo no disponible cuando la duración acumulada alcance exactamente 2000 ms.

**Validates: REQ-06**

### Property 7: Persistencia de alerta de distracción

Para cualquier estado donde existe una alerta de distracción activa y mirada_fuera sigue siendo True, el sistema DEBE mantener la alerta de distracción.

**Validates: REQ-07**

### Property 8: Cancelación de alerta de distracción

Para cualquier estado donde existe una alerta de distracción activa y mirada_fuera cambia a False, el sistema DEBE cancelar la alerta de distracción dentro de 100 ms.

**Validates: REQ-08**

### Property 9: Persistencia de alerta de somnolencia

Para cualquier estado donde existe una alerta de somnolencia activa y ojos_cerrados sigue siendo True, el sistema DEBE mantener la alerta de somnolencia.

**Validates: REQ-09**

### Property 10: Cancelación de alerta de somnolencia

Para cualquier estado donde existe una alerta de somnolencia activa y ojos_cerrados cambia a False, el sistema DEBE cancelar la alerta de somnolencia dentro de 100 ms.

**Validates: REQ-10**

### Property 11: Prioridad somnolencia sobre distracción

Para cualquier estado donde tanto mirada_fuera como ojos_cerrados alcancen sus umbrales simultáneamente, el sistema DEBE emitir únicamente la alerta de somnolencia.

**Validates: REQ-11**

### Property 12: Supresión durante monitoreo no disponible

Para cualquier estado donde exista una alerta de monitoreo no disponible activa, el sistema DEBE suprimir todas las alertas de distracción y somnolencia.

**Validates: REQ-12**

### Property 13: Procesamiento de datos del cuadro

Para cualquier cuadro recibido, el sistema DEBE procesar exactamente estos datos: tiempo_ms (entero), velocidad_kmh (número con un decimal), rostro_visible (booleano), mirada_fuera (booleano), ojos_cerrados (booleano).

**Validates: REQ-13**

### Property 14: Salida determinista

Para cualquier cuadro procesado, el sistema DEBE devolver exactamente una de estas alertas: "ninguna", "distraccion", "somnolencia", o "monitoreo_no_disponible".

**Validates: REQ-14**

### Property 15: Reinicio de temporizador de distracción

Para cualquier estado donde mirada_fuera cambie de True a False antes de alcanzar el umbral de alerta, el sistema DEBE reiniciar el temporizador de distracción a 0 ms.

**Validates: REQ-15**

### Property 16: Reinicio de temporizador de somnolencia

Para cualquier estado donde ojos_cerrados cambie de True a False antes de alcanzar el umbral de alerta, el sistema DEBE reiniciar el temporizador de somnolencia a 0 ms.

**Validates: REQ-16**

### Property 17: Temporizador basado en tiempo de inicio

Para cualquier condición que se active (mirada_fuera, ojos_cerrados, sin rostro), el sistema DEBE registrar el tiempo_ms del primer cuadro en que se activa y calcular la duración como (tiempo_ms_actual - tiempo_inicio), NO acumulando deltas. Esto previene alertas prematuras causadas por contar el intervalo anterior al inicio de la condición.

**Validates: REQ-01, REQ-02, REQ-04, REQ-06, REQ-15, REQ-16**

## Error Handling

### Validación de Entrada

```python
def procesar_cuadro(tiempo_ms, velocidad_kmh, rostro_visible, mirada_fuera, ojos_cerrados):
    # Validaciones
    if tiempo_ms < 0:
        raise ValueError(f"tiempo_ms debe ser no negativo, recibido: {tiempo_ms}")
    
    if velocidad_kmh < 0.0:
        raise ValueError(f"velocidad_kmh debe ser no negativa, recibida: {velocidad_kmh}")
    
    if not isinstance(rostro_visible, bool):
        raise TypeError(f"rostro_visible debe ser bool, recibido: {type(rostro_visible)}")
    
    if not isinstance(mirada_fuera, bool):
        raise TypeError(f"mirada_fuera debe ser bool, recibido: {type(mirada_fuera)}")
    
    if not isinstance(ojos_cerrados, bool):
        raise TypeError(f"ojos_cerrados debe ser bool, recibido: {type(ojos_cerrados)}")
    
    # Continuar con lógica...
```

### Manejo de Secuencias No Monótonas

Si se recibe un cuadro con `tiempo_ms` menor que el último procesado:

```python
if tiempo_ms < _ultimo_tiempo_ms:
    raise ValueError(
        f"tiempo_ms no monótono: {tiempo_ms} < {_ultimo_tiempo_ms}. "
        "Los cuadros deben procesarse en orden cronológico."
    )
```

### Condiciones de Carrera

La `Logica_Decision` es single-threaded y mantiene estado. Si se requiere procesamiento multi-hilo:

- Cada hilo debe tener su propia instancia de `LogicaAlerta`
- O usar sincronización explícita (locks) al llamar `procesar_cuadro()`

## Testing Strategy

### Enfoque de Pruebas

Este diseño utiliza **únicamente unittest** del módulo estándar de Python para todas las pruebas. No se usa Hypothesis ni ninguna biblioteca de property-based testing.

### Estructura de Pruebas

```
c:\dms_kiro\kiro_inicio\
├── logica_alerta.py          # Implementación
└── test_limites.py           # Pruebas de valores límite con unittest
```

### Tipos de Pruebas

#### 1. Pruebas de Valores Límite (test_limites.py)

Implementadas con `unittest.TestCase`, estas pruebas verifican comportamiento en umbrales exactos:

```python
import unittest
from logica_alerta import LogicaAlerta

class TestDistraccionAltaVelocidad(unittest.TestCase):
    """Pruebas de umbral de distracción a >= 50 km/h"""
    
    def test_req01_justo_antes_umbral(self):
        """Verifica: REQ-01
        A 50 km/h con mirada fuera por 3499 ms: sin alerta
        """
        logica = LogicaAlerta()
        
        # t=0: inicio, mirada al frente
        alerta = logica.procesar_cuadro(0, 50.0, True, False, False)
        self.assertEqual(alerta, "ninguna")
        
        # t=100: mirada fuera (inicio de condición)
        alerta = logica.procesar_cuadro(100, 50.0, True, True, False)
        self.assertEqual(alerta, "ninguna")
        
        # t=3599: 3499 ms desde inicio (100 ms antes del umbral)
        alerta = logica.procesar_cuadro(3599, 50.0, True, True, False)
        self.assertEqual(alerta, "ninguna")
    
    def test_req01_en_umbral(self):
        """Verifica: REQ-01
        A 50 km/h con mirada fuera por exactamente 3500 ms: alerta
        """
        logica = LogicaAlerta()
        
        # t=0: inicio, mirada al frente
        logica.procesar_cuadro(0, 50.0, True, False, False)
        
        # t=100: mirada fuera (inicio de condición)
        logica.procesar_cuadro(100, 50.0, True, True, False)
        
        # t=3600: exactamente 3500 ms desde inicio
        alerta = logica.procesar_cuadro(3600, 50.0, True, True, False)
        self.assertEqual(alerta, "distraccion")
    
    def test_req01_temporizador_inicio_no_acumulador(self):
        """Verifica: REQ-01
        A 50 km/h: t=0 mirada al frente, t=100 mirada fuera, 
        t=3599 sigue fuera -> sin alerta; t=3600 -> alerta.
        Confirma que el temporizador usa tiempo de inicio, no acumulador delta.
        """
        logica = LogicaAlerta()
        
        # t=0: mirada al frente
        alerta = logica.procesar_cuadro(0, 50.0, True, False, False)
        self.assertEqual(alerta, "ninguna")
        
        # t=100: mirada fuera inicia (tiempo_inicio = 100)
        alerta = logica.procesar_cuadro(100, 50.0, True, True, False)
        self.assertEqual(alerta, "ninguna")
        
        # t=3599: duración = 3599 - 100 = 3499 ms (justo antes)
        alerta = logica.procesar_cuadro(3599, 50.0, True, True, False)
        self.assertEqual(alerta, "ninguna")
        
        # t=3600: duración = 3600 - 100 = 3500 ms (umbral alcanzado)
        alerta = logica.procesar_cuadro(3600, 50.0, True, True, False)
        self.assertEqual(alerta, "distraccion")

class TestDistraccionVelocidadMedia(unittest.TestCase):
    """Pruebas de umbral de distracción a 20-50 km/h"""
    
    def test_req02_justo_antes_umbral_49kmh(self):
        """Verifica: REQ-02
        A 49.9 km/h con mirada fuera por 5999 ms: sin alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 49.9, True, False, False)
        logica.procesar_cuadro(100, 49.9, True, True, False)
        
        # 5999 ms desde inicio
        alerta = logica.procesar_cuadro(6099, 49.9, True, True, False)
        self.assertEqual(alerta, "ninguna")
    
    def test_req02_en_umbral_49_9_kmh(self):
        """Verifica: REQ-02
        A 49.9 km/h con mirada fuera por exactamente 6000 ms: alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 49.9, True, False, False)
        logica.procesar_cuadro(100, 49.9, True, True, False)
        
        # Exactamente 6000 ms desde inicio
        alerta = logica.procesar_cuadro(6100, 49.9, True, True, False)
        self.assertEqual(alerta, "distraccion")
    
    def test_req02_limite_inferior_20kmh(self):
        """Verifica: REQ-02
        A 20.0 km/h (velocidad mínima), con mirada fuera por 6000 ms: alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 20.0, True, False, False)
        logica.procesar_cuadro(100, 20.0, True, True, False)
        
        # Exactamente 6000 ms desde inicio
        alerta = logica.procesar_cuadro(6100, 20.0, True, True, False)
        self.assertEqual(alerta, "distraccion")

class TestInhibicionBajaVelocidad(unittest.TestCase):
    """Pruebas de inhibición de distracción < 20 km/h"""
    
    def test_req03_19_9_kmh_sin_alerta(self):
        """Verifica: REQ-03
        A 19.9 km/h con mirada fuera por 7000 ms: sin alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 19.9, True, False, False)
        logica.procesar_cuadro(100, 19.9, True, True, False)
        logica.procesar_cuadro(7100, 19.9, True, True, False)
        
        alerta = logica.procesar_cuadro(7100, 19.9, True, True, False)
        self.assertEqual(alerta, "ninguna")
    
    def test_req03_transicion_velocidad(self):
        """Verifica: REQ-03
        Mirada fuera a 25 km/h, luego reduce a 19 km/h: cancela alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 25.0, True, False, False)
        logica.procesar_cuadro(100, 25.0, True, True, False)
        logica.procesar_cuadro(6100, 25.0, True, True, False)
        
        # Alerta activa
        alerta = logica.procesar_cuadro(6100, 25.0, True, True, False)
        self.assertEqual(alerta, "distraccion")
        
        # Reduce velocidad < 20 km/h: debe cancelar
        alerta = logica.procesar_cuadro(6200, 19.0, True, True, False)
        self.assertEqual(alerta, "ninguna")

class TestSomnolencia(unittest.TestCase):
    """Pruebas de detección de somnolencia"""
    
    def test_req04_justo_antes_umbral(self):
        """Verifica: REQ-04
        Ojos cerrados por 1999 ms: sin alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, False, True)
        
        # 1999 ms desde inicio
        alerta = logica.procesar_cuadro(2099, 50.0, True, False, True)
        self.assertEqual(alerta, "ninguna")
    
    def test_req04_en_umbral(self):
        """Verifica: REQ-04
        Ojos cerrados por exactamente 2000 ms: alerta somnolencia
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, False, True)
        
        # Exactamente 2000 ms desde inicio
        alerta = logica.procesar_cuadro(2100, 50.0, True, False, True)
        self.assertEqual(alerta, "somnolencia")
    
    def test_req05_somnolencia_baja_velocidad(self):
        """Verifica: REQ-05
        Ojos cerrados a 10 km/h por 2000 ms: alerta somnolencia
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 10.0, True, False, False)
        logica.procesar_cuadro(100, 10.0, True, False, True)
        
        alerta = logica.procesar_cuadro(2100, 10.0, True, False, True)
        self.assertEqual(alerta, "somnolencia")

class TestMonitoreoNoDisponible(unittest.TestCase):
    """Pruebas de monitoreo no disponible"""
    
    def test_req06_justo_antes_umbral(self):
        """Verifica: REQ-06
        Sin rostro por 1999 ms: sin alerta monitoreo
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, False, False, False)
        
        # 1999 ms sin rostro
        alerta = logica.procesar_cuadro(2099, 50.0, False, False, False)
        self.assertEqual(alerta, "ninguna")
    
    def test_req06_en_umbral(self):
        """Verifica: REQ-06
        Sin rostro por exactamente 2000 ms: alerta monitoreo no disponible
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, False, False, False)
        
        # Exactamente 2000 ms sin rostro
        alerta = logica.procesar_cuadro(2100, 50.0, False, False, False)
        self.assertEqual(alerta, "monitoreo_no_disponible")

class TestPersistenciaAlertas(unittest.TestCase):
    """Pruebas de persistencia y cancelación de alertas"""
    
    def test_req07_persistencia_distraccion(self):
        """Verifica: REQ-07
        Alerta de distracción persiste mientras mirada_fuera = True
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, True, False)
        logica.procesar_cuadro(3600, 50.0, True, True, False)
        
        # Alerta activa
        alerta = logica.procesar_cuadro(3600, 50.0, True, True, False)
        self.assertEqual(alerta, "distraccion")
        
        # Continúa con mirada fuera: debe persistir
        alerta = logica.procesar_cuadro(4000, 50.0, True, True, False)
        self.assertEqual(alerta, "distraccion")
    
    def test_req08_cancelacion_distraccion(self):
        """Verifica: REQ-08
        Alerta de distracción se cancela cuando mirada_fuera = False
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, True, False)
        logica.procesar_cuadro(3600, 50.0, True, True, False)
        
        # Alerta activa
        self.assertEqual(logica.procesar_cuadro(3600, 50.0, True, True, False), "distraccion")
        
        # Mirada vuelve al frente: debe cancelar
        alerta = logica.procesar_cuadro(3700, 50.0, True, False, False)
        self.assertEqual(alerta, "ninguna")
    
    def test_req09_persistencia_somnolencia(self):
        """Verifica: REQ-09
        Alerta de somnolencia persiste mientras ojos_cerrados = True
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, False, True)
        logica.procesar_cuadro(2100, 50.0, True, False, True)
        
        # Alerta activa
        self.assertEqual(logica.procesar_cuadro(2100, 50.0, True, False, True), "somnolencia")
        
        # Continúa con ojos cerrados: debe persistir
        alerta = logica.procesar_cuadro(3000, 50.0, True, False, True)
        self.assertEqual(alerta, "somnolencia")
    
    def test_req10_cancelacion_somnolencia(self):
        """Verifica: REQ-10
        Alerta de somnolencia se cancela cuando ojos_cerrados = False
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, False, True)
        logica.procesar_cuadro(2100, 50.0, True, False, True)
        
        # Alerta activa
        self.assertEqual(logica.procesar_cuadro(2100, 50.0, True, False, True), "somnolencia")
        
        # Ojos abiertos: debe cancelar
        alerta = logica.procesar_cuadro(2200, 50.0, True, False, False)
        self.assertEqual(alerta, "ninguna")

class TestPrioridadAlertas(unittest.TestCase):
    """Pruebas de prioridad entre tipos de alertas"""
    
    def test_req11_prioridad_somnolencia_sobre_distraccion(self):
        """Verifica: REQ-11
        Cuando ambas condiciones alcanzan umbral simultáneamente, emitir somnolencia
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        
        # Ambas condiciones inician simultáneamente
        logica.procesar_cuadro(100, 50.0, True, True, True)
        
        # A los 2100 ms: somnolencia alcanza umbral (2000 ms)
        # distracción aún no (necesita 3500 ms)
        alerta = logica.procesar_cuadro(2100, 50.0, True, True, True)
        self.assertEqual(alerta, "somnolencia")
        
        # A los 3600 ms: ambas alcanzaron umbral
        # Debe seguir mostrando somnolencia
        alerta = logica.procesar_cuadro(3600, 50.0, True, True, True)
        self.assertEqual(alerta, "somnolencia")
    
    def test_req12_supresion_por_monitoreo_no_disponible(self):
        """Verifica: REQ-12
        Alerta de monitoreo no disponible suprime distracción y somnolencia
        """
        logica = LogicaAlerta()
        
        # Establecer alerta de distracción
        logica.procesar_cuadro(0, 50.0, True, False, False)
        logica.procesar_cuadro(100, 50.0, True, True, False)
        logica.procesar_cuadro(3600, 50.0, True, True, False)
        self.assertEqual(logica.procesar_cuadro(3600, 50.0, True, True, False), "distraccion")
        
        # Rostro desaparece
        logica.procesar_cuadro(3700, 50.0, False, True, False)
        
        # Después de 2000 ms sin rostro: monitoreo no disponible suprime distracción
        alerta = logica.procesar_cuadro(5700, 50.0, False, True, False)
        self.assertEqual(alerta, "monitoreo_no_disponible")

class TestReinicioTemporizadores(unittest.TestCase):
    """Pruebas de reinicio de temporizadores"""
    
    def test_req15_reinicio_temporizador_distraccion(self):
        """Verifica: REQ-15
        Temporizador de distracción se reinicia cuando mirada vuelve al frente
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        
        # Mirada fuera por 2000 ms (no alcanza umbral de 3500 ms)
        logica.procesar_cuadro(100, 50.0, True, True, False)
        logica.procesar_cuadro(2100, 50.0, True, True, False)
        
        # Vuelve al frente: reinicia temporizador
        logica.procesar_cuadro(2200, 50.0, True, False, False)
        
        # Mirada fuera nuevamente
        logica.procesar_cuadro(2300, 50.0, True, True, False)
        
        # Debe necesitar otros 3500 ms desde t=2300
        alerta = logica.procesar_cuadro(5799, 50.0, True, True, False)
        self.assertEqual(alerta, "ninguna")
        
        alerta = logica.procesar_cuadro(5800, 50.0, True, True, False)
        self.assertEqual(alerta, "distraccion")
    
    def test_req16_reinicio_temporizador_somnolencia(self):
        """Verifica: REQ-16
        Temporizador de somnolencia se reinicia cuando ojos se abren
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 50.0, True, False, False)
        
        # Ojos cerrados por 1500 ms (no alcanza umbral de 2000 ms)
        logica.procesar_cuadro(100, 50.0, True, False, True)
        logica.procesar_cuadro(1600, 50.0, True, False, True)
        
        # Ojos abiertos: reinicia temporizador
        logica.procesar_cuadro(1700, 50.0, True, False, False)
        
        # Ojos cerrados nuevamente
        logica.procesar_cuadro(1800, 50.0, True, False, True)
        
        # Debe necesitar otros 2000 ms desde t=1800
        alerta = logica.procesar_cuadro(3799, 50.0, True, False, True)
        self.assertEqual(alerta, "ninguna")
        
        alerta = logica.procesar_cuadro(3800, 50.0, True, False, True)
        self.assertEqual(alerta, "somnolencia")

class TestValidacionEntrada(unittest.TestCase):
    """Pruebas de validación de datos de entrada"""
    
    def test_req13_tipos_correctos(self):
        """Verifica: REQ-13
        Procesa correctamente los tipos de datos especificados
        """
        logica = LogicaAlerta()
        
        # Debe aceptar estos tipos sin error
        alerta = logica.procesar_cuadro(
            tiempo_ms=100,           # int
            velocidad_kmh=50.5,      # float con un decimal
            rostro_visible=True,     # bool
            mirada_fuera=False,      # bool
            ojos_cerrados=False      # bool
        )
        
        self.assertIsInstance(alerta, str)
    
    def test_req14_salidas_validas(self):
        """Verifica: REQ-14
        La salida es siempre una de las cuatro alertas válidas
        """
        alertas_validas = {"ninguna", "distraccion", "somnolencia", "monitoreo_no_disponible"}
        
        # Probar diversos estados con instancias separadas
        # para evitar conflictos de tiempo no monótono
        
        # Caso 1: Normal
        logica1 = LogicaAlerta()
        alerta = logica1.procesar_cuadro(0, 50.0, True, False, False)
        self.assertIn(alerta, alertas_validas)
        
        # Caso 2: Distracción
        logica2 = LogicaAlerta()
        logica2.procesar_cuadro(0, 50.0, True, False, False)
        logica2.procesar_cuadro(100, 50.0, True, True, False)
        alerta = logica2.procesar_cuadro(3600, 50.0, True, True, False)
        self.assertIn(alerta, alertas_validas)
        
        # Caso 3: Somnolencia
        logica3 = LogicaAlerta()
        logica3.procesar_cuadro(0, 50.0, True, False, False)
        logica3.procesar_cuadro(100, 50.0, True, False, True)
        alerta = logica3.procesar_cuadro(2100, 50.0, True, False, True)
        self.assertIn(alerta, alertas_validas)
        
        # Caso 4: Sin rostro
        logica4 = LogicaAlerta()
        logica4.procesar_cuadro(0, 50.0, True, False, False)
        logica4.procesar_cuadro(100, 50.0, False, False, False)
        alerta = logica4.procesar_cuadro(2100, 50.0, False, False, False)
        self.assertIn(alerta, alertas_validas)
```

### Cobertura de Requisitos

Todas las pruebas referencian explícitamente los requisitos que verifican mediante el formato `Verifica: REQ-XX` en el docstring. Esto permite que `trazabilidad.py` extraiga automáticamente la matriz de cobertura.

### Ejecución de Pruebas

```bash
# Ejecutar todas las pruebas con verbosidad
python -m unittest test_limites -v

# Ejecutar una clase específica
python -m unittest test_limites.TestDistraccionAltaVelocidad -v

# Ejecutar una prueba específica
python -m unittest test_limites.TestDistraccionAltaVelocidad.test_req01_en_umbral -v
```

### Criterios de Aceptación

- ✅ Todas las pruebas deben pasar
- ✅ Cada requisito REQ-01 a REQ-16 tiene al menos una prueba que lo verifica
- ✅ `python trazabilidad.py` no reporta huecos en la matriz

## Appendix: Trazabilidad Completa

### Requisitos → Componentes

| Requisito | Componente | Ubicación |
|-----------|-----------|-----------|
| REQ-01 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-02 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-03 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-04 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-05 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-06 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-07 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-08 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-09 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-10 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-11 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-12 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-13 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-14 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-15 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |
| REQ-16 | LogicaAlerta.procesar_cuadro() | logica_alerta.py |

### Requisitos → Pruebas

| Requisito | Prueba | Ubicación |
|-----------|--------|-----------|
| REQ-01 | test_req01_justo_antes_umbral | test_limites.py |
| REQ-01 | test_req01_en_umbral | test_limites.py |
| REQ-01 | test_req01_temporizador_inicio_no_acumulador | test_limites.py |
| REQ-02 | test_req02_justo_antes_umbral_49kmh | test_limites.py |
| REQ-02 | test_req02_en_umbral_49_9_kmh | test_limites.py |
| REQ-02 | test_req02_limite_inferior_20kmh | test_limites.py |
| REQ-03 | test_req03_19_9_kmh_sin_alerta | test_limites.py |
| REQ-03 | test_req03_transicion_velocidad | test_limites.py |
| REQ-04 | test_req04_justo_antes_umbral | test_limites.py |
| REQ-04 | test_req04_en_umbral | test_limites.py |
| REQ-05 | test_req05_somnolencia_baja_velocidad | test_limites.py |
| REQ-06 | test_req06_justo_antes_umbral | test_limites.py |
| REQ-06 | test_req06_en_umbral | test_limites.py |
| REQ-07 | test_req07_persistencia_distraccion | test_limites.py |
| REQ-08 | test_req08_cancelacion_distraccion | test_limites.py |
| REQ-09 | test_req09_persistencia_somnolencia | test_limites.py |
| REQ-10 | test_req10_cancelacion_somnolencia | test_limites.py |
| REQ-11 | test_req11_prioridad_somnolencia_sobre_distraccion | test_limites.py |
| REQ-12 | test_req12_supresion_por_monitoreo_no_disponible | test_limites.py |
| REQ-13 | test_req13_tipos_correctos | test_limites.py |
| REQ-14 | test_req14_salidas_validas | test_limites.py |
| REQ-15 | test_req15_reinicio_temporizador_distraccion | test_limites.py |
| REQ-16 | test_req16_reinicio_temporizador_somnolencia | test_limites.py |

### Requisitos Fuera de Alcance

Los siguientes requisitos están fuera del alcance del módulo `logica_alerta.py`:

- **SIS-01 a SIS-06**: Implementados en el sistema de alertas visual/auditivo (fuera de este módulo)

## Appendix: Decisiones de Diseño

### ¿Por qué tiempos en milisegundos enteros?

Los umbrales normativos (3500 ms, 6000 ms, 2000 ms) son enteros. Usar `int` para tiempos evita errores de redondeo de punto flotante en comparaciones de límites exactos.

### ¿Por qué velocidad con un decimal?

La especificación del cliente indica velocidad con un decimal de precisión (ej. 49.9 km/h, 50.0 km/h). Esto permite distinguir casos límite justo por debajo y por encima de umbrales.

### ¿Por qué estado mutable en lugar de funcional?

El DMS procesa un flujo continuo de cuadros. Mantener estado interno (temporizadores, alerta actual) simplifica la interfaz: el llamador solo proporciona datos del cuadro actual, sin necesidad de mantener estado externo.

### ¿Por qué temporizadores basados en tiempo de inicio?

Acumular deltas (`delta_ms += tiempo_actual - tiempo_anterior`) cuenta incorrectamente el intervalo anterior al inicio de la condición, causando alertas prematuras. Guardar `tiempo_inicio` y calcular `(tiempo_actual - tiempo_inicio)` mide correctamente la duración desde que la condición se activó.

### ¿Por qué solo unittest sin Hypothesis?

El proyecto requiere estructura plana sin dependencias externas. Unittest está en la biblioteca estándar de Python, mientras que Hypothesis requeriría instalación adicional. Las pruebas de valores límite con secuencias fijas son suficientes para verificar comportamiento determinista en umbrales exactos.
