### 6.3 Redacción con control: respuestas y descripción

**Respuestas.** El LLM recibe la pregunta, el resultado del motor y el valor normalizado, y lo redacta en una oración. Un control con código acepta el texto sólo si conserva el valor: el número en un conteo, "sí" o "no" al principio en existencia, relación y comparación, y la zona, el tamaño o el color en las demás. Si el control falla se usa la frase del motor.

**Descripción.** El código arma un resumen del SceneJSON predicho (cuántos objetos hay de cada clase, en qué zona y de qué tamaño) y el LLM lo redacta en 2 o 3 oraciones, nombrando cada clase en español y con su nombre del vocabulario entre paréntesis. El control de alucinaciones acepta el texto sólo si:
- nombra al menos una clase del vocabulario y **todas** están en la escena;
- cada número que aparece está en el resumen, y cada "N objetos (clase)" coincide con el conteo de esa clase en la escena.

Si el control falla hay un reintento. Si vuelve a fallar se usa la descripción por plantilla de la Fase 5. `evidence` son los objetos de las clases que la descripción nombra.

**Ejemplos resueltos (v5).** En la v4 el control rechazó el 70 % de las redacciones: el modelo contestaba "No" a secas o armaba listas con el nombre en español entre paréntesis. Desde la v5, los dos prompts traen ejemplos de la salida esperada, y el control exige una oración de al menos 12 caracteres.
