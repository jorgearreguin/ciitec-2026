# -*- coding: utf-8 -*-
"""
Pruebas de Valores Límite para el Sistema DMS
=============================================

Suite de pruebas unitarias que verifican comportamiento en umbrales exactos
para todos los requisitos REQ-01 a REQ-16.

Las pruebas siguen el formato:
- Nombre: test_reqNN_descripcion
- Docstring: "Verifica: REQ-NN"
- Valores límite: justo antes y exactamente en el umbral

Ejecutar con: python -m unittest test_limites -v
"""

import unittest
from logica_alerta import LogicaAlerta


class TestValidacionEntrada(unittest.TestCase):
    """Pruebas de validación de datos de entrada (REQ-13)"""
    
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
        self.assertEqual(alerta, "ninguna")
    
    def test_req13_tiempo_negativo(self):
        """Verifica: REQ-13
        Rechaza tiempo_ms negativo
        """
        logica = LogicaAlerta()
        
        with self.assertRaises(ValueError) as context:
            logica.procesar_cuadro(-100, 50.0, True, False, False)
        
        self.assertIn("tiempo_ms debe ser no negativo", str(context.exception))
    
    def test_req13_velocidad_negativa(self):
        """Verifica: REQ-13
        Rechaza velocidad_kmh negativa
        """
        logica = LogicaAlerta()
        
        with self.assertRaises(ValueError) as context:
            logica.procesar_cuadro(100, -10.0, True, False, False)
        
        self.assertIn("velocidad_kmh debe ser no negativa", str(context.exception))
    
    def test_req13_secuencia_no_monotona(self):
        """Verifica: REQ-13
        Rechaza secuencias de tiempo no monótonas
        """
        logica = LogicaAlerta()
        
        # Primer cuadro
        logica.procesar_cuadro(100, 50.0, True, False, False)
        
        # Segundo cuadro con tiempo anterior: debe fallar
        with self.assertRaises(ValueError) as context:
            logica.procesar_cuadro(50, 50.0, True, False, False)
        
        self.assertIn("no monótono", str(context.exception))


class TestDistraccionAltaVelocidad(unittest.TestCase):
    """Pruebas de umbral de distracción a >= 50 km/h (REQ-01)"""
    
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
    """Pruebas de umbral de distracción a 20-50 km/h (REQ-02)"""
    
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
    """Pruebas de inhibición de distracción < 20 km/h (REQ-03)"""
    
    def test_req03_19_9_kmh_sin_alerta(self):
        """Verifica: REQ-03
        A 19.9 km/h con mirada fuera por 7000 ms: sin alerta
        """
        logica = LogicaAlerta()
        
        logica.procesar_cuadro(0, 19.9, True, False, False)
        logica.procesar_cuadro(100, 19.9, True, True, False)
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
    """Pruebas de detección de somnolencia (REQ-04, REQ-05, REQ-09, REQ-10, REQ-16)"""
    
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


class TestMonitoreoNoDisponible(unittest.TestCase):
    """Pruebas de monitoreo no disponible (REQ-06, REQ-12)"""
    
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


class TestPersistenciaAlertas(unittest.TestCase):
    """Pruebas de persistencia y cancelación de alertas (REQ-07, REQ-08, REQ-11, REQ-15)"""
    
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


class TestSalidaDeterminista(unittest.TestCase):
    """Pruebas de salida determinista (REQ-14)"""
    
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


if __name__ == '__main__':
    unittest.main(verbosity=2)
