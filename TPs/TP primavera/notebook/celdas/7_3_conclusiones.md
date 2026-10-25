### 7.3 Conclusiones de la Fase 7

| Medida | Valor |
|---|---|
| F1 de cajas en las particiones de prueba (media ± desvío) | **0,673 ± 0,023** |
| F1 de la configuración final dentro de la muestra (2.9) | 0,679 → optimismo estimado de 0,006 |
| Configuración elegida en cada partición | umbral 0,25 en 3 particiones y 0,22 en 2; k = 3 en 4 de 5 |
| F1 con umbrales a ±0,03 del final (0,22 a 0,28) | entre 0,671 y 0,679 |
| E9 · dos umbrales (imagen / ventanas) contra uno, ambos elegidos por validación cruzada | 0,674 contra 0,674: +0,001, mejora en 2 particiones y empeora en 1 |

**Lectura.**
- **El F1 de desarrollo es una estimación razonable.** Elegir el umbral sobre las mismas imágenes infla el F1 en sólo 0,006. El requisito de promoción (≥ 0,50) se cumple con margen también fuera de la muestra.
- **La configuración es estable:** el óptimo casi no se mueve entre particiones y el F1 cambia menos de 0,01 en un rango de ±0,03 alrededor del umbral.
- **El ruido entre imágenes domina.** El desvío entre particiones (0,023) es cuatro veces el optimismo. Por eso las diferencias de menos de ~0,01 entre variantes de 2.9 (sinónimos, ventanas, ensamble) no son concluyentes sólo con desarrollo. La configuración final se apoya además en el leaderboard, que subió de 0,6656 a 0,7022 al adoptarla (v3 → v4).
- **E9 no se adopta.** Un umbral por fuente agrega un parámetro sin una mejora que se sostenga fuera de la muestra: se mantiene el umbral único.
