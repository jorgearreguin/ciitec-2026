/* dms_alerta.h: tipos y prototipo de DMS_Evaluar */
#ifndef DMS_ALERTA_H
#define DMS_ALERTA_H
#include <stdint.h>

typedef enum { IGN_OFF = 0, IGN_ACC, IGN_ON } Ignicion_t;
typedef enum { DS_ATENTO = 0, DS_DISTRAIDO } DriverStatus_t; /* salida del modelo */
typedef enum { ALERTA_NO = 0, ALERTA_SI } Alerta_t;

/* t_zona3_ms: tiempo continuo con la mirada en la zona 3 */
Alerta_t DMS_Evaluar(Ignicion_t ignicion, DriverStatus_t estado,
                     uint16_t velocidad_kmh, uint32_t t_zona3_ms);
#endif
