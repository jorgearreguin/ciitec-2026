/* test_dms_alerta.c: un caso por renglón de la tabla, en los límites */
/* (la regla 1 usa ACC, el vecino de ON). Corre en la PC, no en la ECU. */
#include <stdint.h>
#include <stdio.h>
#include "dms_alerta.h"

typedef struct
{
    uint8_t        regla;
    Ignicion_t     ignicion;
    DriverStatus_t estado;
    uint16_t       velocidad_kmh;
    uint32_t       t_zona3_ms;
    Alerta_t       esperado;
} Caso_t;

static const Caso_t casos[] =
{
    /* regla  ignición  estado        km/h  ms      esperado  */
    {  1U,    IGN_ACC,  DS_DISTRAIDO,  80U, 9000U,  ALERTA_NO },
    {  2U,    IGN_ON,   DS_ATENTO,     80U, 9000U,  ALERTA_NO },
    {  3U,    IGN_ON,   DS_DISTRAIDO,  19U, 9000U,  ALERTA_NO },
    {  4U,    IGN_ON,   DS_DISTRAIDO,  49U, 5999U,  ALERTA_NO },
    {  5U,    IGN_ON,   DS_DISTRAIDO,  20U, 6000U,  ALERTA_SI },
    {  6U,    IGN_ON,   DS_DISTRAIDO,  50U, 3499U,  ALERTA_NO },
    {  7U,    IGN_ON,   DS_DISTRAIDO,  50U, 3500U,  ALERTA_SI }
};

int main(void)
{
    uint32_t fallas = 0U;
    uint32_t i;
    const uint32_t total = (uint32_t)(sizeof(casos) / sizeof(casos[0]));

    for (i = 0U; i < total; i++)
    {
        const Caso_t *c = &casos[i];

        if (DMS_Evaluar(c->ignicion, c->estado, c->velocidad_kmh,
                        c->t_zona3_ms) != c->esperado)
        {
            (void)printf("Falla la regla %u\n", (unsigned int)c->regla);
            fallas++;
        }
    }

    (void)printf("%u de %u reglas pasan\n",
                 (unsigned int)(total - fallas), (unsigned int)total);
    return (fallas == 0U) ? 0 : 1;
}
