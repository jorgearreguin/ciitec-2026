# -*- coding: utf-8 -*-
"""
Sistema de Monitoreo del Conductor (DMS) - Lógica de Alertas
=============================================================

Módulo de lógica determinista para el sistema DMS de laboratorio.
Implementa la normativa ADDW (Alerta Avanzada de Distracción) del
Reglamento General de Seguridad de la Unión Europea.

Este módulo NO depende de bibliotecas de visión por computadora.
Opera exclusivamente con datos numéricos y booleanos.

Cubre: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07, 
       REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, 
       REQ-15, REQ-16
"""

from typing import Optional

# Umbrales de tiempo (en milisegundos)
UMBRAL_DISTRACCION_ALTA_VELOCIDAD = 3500  # REQ-01: >= 50 km/h
UMBRAL_DISTRACCION_MEDIA_VELOCIDAD = 6000  # REQ-02: 20-50 km/h
UMBRAL_SOMNOLENCIA = 2000  # REQ-04
UMBRAL_SIN_ROSTRO = 2000  # REQ-06

# Umbrales de velocidad (en km/h)
VELOCIDAD_MINIMA_DISTRACCION = 20.0  # REQ-03
VELOCIDAD_ALTA = 50.0  # REQ-01


class LogicaAlerta:
    """
    Lógica determinista de alertas del DMS.
    No depende de bibliotecas de visión; opera solo con datos numéricos.
    
    Cubre: REQ-01, REQ-02, REQ-03, REQ-04, REQ-05, REQ-06, REQ-07,
           REQ-08, REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14,
           REQ-15, REQ-16
    """
    
    def __init__(self) -> None:
        """
        Inicializa el monitor con todos los temporizadores en None (inactivos)
        y la alerta actual en "ninguna".
        """
        # Tiempos de inicio de cada condición (None cuando inactivos)
        self._inicio_mirada_fuera_ms: Optional[int] = None  # REQ-01, REQ-02, REQ-15
        self._inicio_ojos_cerrados_ms: Optional[int] = None  # REQ-04, REQ-16
        self._inicio_sin_rostro_ms: Optional[int] = None  # REQ-06
        
        # Alerta actual
        self._alerta_actual: str = "ninguna"  # REQ-07, REQ-08, REQ-09, REQ-10, REQ-11, REQ-12
        
        # Último tiempo procesado (para validar secuencia monótona)
        self._ultimo_tiempo_ms: Optional[int] = None
    
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
            
        Raises:
            ValueError: Si los valores numéricos son negativos o el tiempo no es monótono
            TypeError: Si los tipos de datos no coinciden con la especificación
            
        Cubre: REQ-13, REQ-14
        """
        # REQ-13: Validación de tipos de entrada
        if not isinstance(tiempo_ms, int):
            raise TypeError(f"tiempo_ms debe ser int, recibido: {type(tiempo_ms).__name__}")
        
        if not isinstance(velocidad_kmh, (int, float)):
            raise TypeError(f"velocidad_kmh debe ser número, recibido: {type(velocidad_kmh).__name__}")
        
        if not isinstance(rostro_visible, bool):
            raise TypeError(f"rostro_visible debe ser bool, recibido: {type(rostro_visible).__name__}")
        
        if not isinstance(mirada_fuera, bool):
            raise TypeError(f"mirada_fuera debe ser bool, recibido: {type(mirada_fuera).__name__}")
        
        if not isinstance(ojos_cerrados, bool):
            raise TypeError(f"ojos_cerrados debe ser bool, recibido: {type(ojos_cerrados).__name__}")
        
        # REQ-13: Validación de valores no negativos
        if tiempo_ms < 0:
            raise ValueError(f"tiempo_ms debe ser no negativo, recibido: {tiempo_ms}")
        
        if velocidad_kmh < 0.0:
            raise ValueError(f"velocidad_kmh debe ser no negativa, recibida: {velocidad_kmh}")
        
        # Validar secuencia monótona
        if self._ultimo_tiempo_ms is not None and tiempo_ms < self._ultimo_tiempo_ms:
            raise ValueError(
                f"tiempo_ms no monótono: {tiempo_ms} < {self._ultimo_tiempo_ms}. "
                "Los cuadros deben procesarse en orden cronológico."
            )
        
        self._ultimo_tiempo_ms = tiempo_ms
        
        # REQ-12: Prioridad a monitoreo no disponible
        if not rostro_visible:
            # REQ-06: Detectar ausencia de rostro durante 2000 ms
            if self._inicio_sin_rostro_ms is None:
                self._inicio_sin_rostro_ms = tiempo_ms
            
            if (tiempo_ms - self._inicio_sin_rostro_ms) >= UMBRAL_SIN_ROSTRO:  # REQ-06
                self._alerta_actual = "monitoreo_no_disponible"  # REQ-12
                # REQ-12: Suprimir otras alertas
                return self._alerta_actual  # REQ-14
        else:
            # Rostro visible: reiniciar temporizador sin rostro
            self._inicio_sin_rostro_ms = None
            if self._alerta_actual == "monitoreo_no_disponible":
                self._alerta_actual = "ninguna"
        
        # REQ-11: Prioridad somnolencia sobre distracción
        # REQ-05: Evaluar somnolencia sin restricción de velocidad
        alerta_somnolencia = False
        if ojos_cerrados:
            # REQ-04: Detectar ojos cerrados durante 2000 ms
            if self._inicio_ojos_cerrados_ms is None:
                self._inicio_ojos_cerrados_ms = tiempo_ms
            
            if (tiempo_ms - self._inicio_ojos_cerrados_ms) >= UMBRAL_SOMNOLENCIA:  # REQ-04
                alerta_somnolencia = True
                self._alerta_actual = "somnolencia"  # REQ-09: Mantener mientras ojos_cerrados = True
        else:
            # REQ-16: Reiniciar temporizador cuando ojos se abren antes del umbral
            if self._inicio_ojos_cerrados_ms is not None:
                self._inicio_ojos_cerrados_ms = None  # REQ-16
                # REQ-10: Cancelar alerta cuando ojos_cerrados = False
                if self._alerta_actual == "somnolencia":
                    self._alerta_actual = "ninguna"  # REQ-10
        
        # Solo evaluar distracción si no hay alerta de somnolencia
        if not alerta_somnolencia:
            # REQ-03: Inhibir distracción < 20 km/h
            if velocidad_kmh < VELOCIDAD_MINIMA_DISTRACCION:  # REQ-03
                # REQ-15: Reiniciar temporizador cuando la velocidad cae < 20 km/h
                if self._inicio_mirada_fuera_ms is not None:
                    self._inicio_mirada_fuera_ms = None  # REQ-15
                # REQ-03: Cancelar alerta si estaba activa
                if self._alerta_actual == "distraccion":
                    self._alerta_actual = "ninguna"  # REQ-03
            else:
                # REQ-01, REQ-02: Umbrales por velocidad
                if mirada_fuera:
                    if self._inicio_mirada_fuera_ms is None:
                        self._inicio_mirada_fuera_ms = tiempo_ms
                    
                    duracion_ms = tiempo_ms - self._inicio_mirada_fuera_ms
                    
                    # REQ-01: >= 50 km/h -> 3500 ms
                    # REQ-02: 20-50 km/h -> 6000 ms
                    if velocidad_kmh >= VELOCIDAD_ALTA:
                        umbral = UMBRAL_DISTRACCION_ALTA_VELOCIDAD  # REQ-01
                    else:
                        umbral = UMBRAL_DISTRACCION_MEDIA_VELOCIDAD  # REQ-02
                    
                    if duracion_ms >= umbral:
                        self._alerta_actual = "distraccion"  # REQ-07: Mantener mientras mirada_fuera = True
                else:
                    # REQ-15: Reiniciar temporizador cuando mirada vuelve al frente antes del umbral
                    if self._inicio_mirada_fuera_ms is not None:
                        self._inicio_mirada_fuera_ms = None  # REQ-15
                        # REQ-08: Cancelar alerta cuando mirada_fuera = False
                        if self._alerta_actual == "distraccion":
                            self._alerta_actual = "ninguna"  # REQ-08
        
        # REQ-14: Salida determinista - devolver exactamente una alerta
        return self._alerta_actual  # REQ-14
