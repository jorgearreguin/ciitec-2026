# Código barato, errores millonarios

Material de la conferencia de José Jorge Arreguin Martinez en CIITEC 2026, TecNM Celaya (11 de noviembre de 2026): *La IA en la ingeniería de software de los vehículos inteligentes*.

Sitio: https://jorgearreguin.github.io/ciitec-2026/

| Archivo | Qué es |
| --- | --- |
| `index.html` | Portada con los enlaces al material |
| `presentacion.pdf` | Las diapositivas |
| `demo.html` | Demo interactiva «Cómo ve una CNN»; funciona sin internet |
| `laboratorio/laboratorio_edge_ai.zip` | Laboratorio: Kiro, trazabilidad, lógica del DMS y cuantización |
| `laboratorio/c/` | La tabla de verdad de la alerta en C y sus pruebas |
| `kiro/` | Tutorial paso a paso con Kiro: capturas, la spec revisada, el código, las pruebas y la matriz de trazabilidad |
| `qr/` | El código QR que lleva a este sitio, en PNG y SVG |

Para compilar y correr las pruebas en C:

```
gcc -std=c99 -Wall -Wextra -o test_dms laboratorio/c/dms_alerta.c laboratorio/c/test_dms_alerta.c
./test_dms
```

© 2026 José Jorge Arreguin Martinez
