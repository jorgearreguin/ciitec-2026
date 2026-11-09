/* dms_alerta.c: tabla de verdad de la alerta del DMS (reglas 1 a 7) */
/* DS_DISTRAIDO: el modelo ve la mirada en la zona 3 (ADDW).          */
#include <stdint.h>
#include "dms_alerta.h"

#define VEL_MINIMA_KMH    (20U)    /* REQ-03: debajo no se alerta     */
#define VEL_ALTA_KMH      (50U)    /* REQ-01: a partir de aquí, 3.5 s */
#define T_VEL_ALTA_MS     (3500U)  /* REQ-01: 50 km/h o más           */
#define T_VEL_MEDIA_MS    (6000U)  /* REQ-02: de 20 a 49 km/h         */

Alerta_t DMS_Evaluar(Ignicion_t     ignicion,
                     DriverStatus_t estado,
                     uint16_t       velocidad_kmh,
                     uint32_t       t_zona3_ms)
{
    Alerta_t alerta;

    if (ignicion != IGN_ON)                      /* regla 1 · SUPUESTO */
    {
        alerta = ALERTA_NO;
    }
    else if (estado != DS_DISTRAIDO)             /* regla 2 */
    {
        alerta = ALERTA_NO;
    }
    else if (velocidad_kmh < VEL_MINIMA_KMH)     /* regla 3 · REQ-03 */
    {
        alerta = ALERTA_NO;
    }
    else if (velocidad_kmh < VEL_ALTA_KMH)       /* reglas 4 y 5 · REQ-02 */
    {
        alerta = (t_zona3_ms >= T_VEL_MEDIA_MS) ? ALERTA_SI : ALERTA_NO;
    }
    else                                         /* reglas 6 y 7 · REQ-01 */
    {
        alerta = (t_zona3_ms >= T_VEL_ALTA_MS) ? ALERTA_SI : ALERTA_NO;
    }

    return alerta;                               /* un solo punto de salida */
}
