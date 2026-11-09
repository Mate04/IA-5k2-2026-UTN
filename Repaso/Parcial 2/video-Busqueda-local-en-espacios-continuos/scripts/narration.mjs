// Guion de la narración, una entrada por escena.
// Las marcas {{nombre}} no se leen en voz alta: marcan el instante exacto en que
// arranca cada animación (el generador las convierte en tiempos usando los
// timestamps de ElevenLabs).

export const VOICE_ID = "XrExE9yKIg1WjnnlVkGX"; // Matilda (voz incluida, educativa, español verificado)
export const MODEL_ID = "eleven_v4";

export const scenes = [
  {
    id: "intro",
    text:
      "Sección cuatro punto dos: búsqueda local en espacios continuos. " +
      "{{reina}}Hasta ahora, la búsqueda local se movía entre estados discretos, como mover una reina a otra casilla del tablero. " +
      "{{continuo}}Pero la mayoría de los problemas del mundo real son continuos. Veamos qué cambia, y qué herramientas usamos.",
  },
  {
    id: "infinito",
    text:
      "En un espacio discreto, {{discreto}}cada estado tiene una cantidad finita de vecinos: los podés revisar todos y quedarte con el mejor. " +
      "{{continuo}}En un espacio continuo, desde cualquier punto te podés mover una distancia tan chiquita como quieras, en cualquier dirección. " +
      "{{infinito}}Hay infinitos sucesores: el factor de ramificación es infinito. " +
      "{{rompe}}Por eso la mayoría de los algoritmos que vimos no sirven tal cual. " +
      "{{excepcion}}Las excepciones son el ascenso de colina de primera opción y el recocido simulado, porque no necesitan mirar todos los vecinos: les alcanza con elegir uno al azar.",
  },
  {
    id: "aeropuertos",
    text:
      "El libro usa este ejemplo. {{mapa}}Queremos ubicar tres aeropuertos nuevos en cualquier lugar de Rumania. " +
      "{{asignacion}}Cada ciudad usa el aeropuerto que le queda más cerca, y queremos minimizar la suma de las distancias al cuadrado de cada ciudad a su aeropuerto. " +
      "{{estado}}¿Cuál es el estado? Las coordenadas de los tres aeropuertos: equis uno, ye uno, equis dos, ye dos, equis tres, ye tres. " +
      "{{seis}}Seis números: es un espacio de seis dimensiones, o de seis variables, que escribimos como un vector equis. " +
      "{{mover}}Moverse en este espacio es, literalmente, mover aeropuertos en el mapa.",
  },
  {
    id: "objetivo",
    text:
      "Ahora, la función objetivo. {{ci}}Llamamos C sub i al conjunto de ciudades cuyo aeropuerto más cercano es el i. " +
      "{{formula}}Entonces, f de equis suma, para cada aeropuerto, las distancias al cuadrado a cada una de sus ciudades. Es la ecuación cuatro punto uno. " +
      "{{local}}Ojo con un detalle: esta fórmula vale en el estado actual y en su vecindario cercano. " +
      "{{cambia}}Pero si movemos mucho un aeropuerto, algunas ciudades pasan a tener otro aeropuerto más cercano, y hay que recalcular los conjuntos C. " +
      "{{global}}La fórmula es correcta localmente, pero no globalmente.",
  },
  {
    id: "discretizar",
    text:
      "Primera idea: discretizar. {{grilla}}En vez de permitir cualquier punto, limitamos los aeropuertos a una cuadrícula con espaciado delta. " +
      "{{doce}}Así, cada estado tiene solo doce sucesores: elegimos una de las seis variables y le sumamos o restamos delta. Seis por dos, doce. " +
      "Y ya podemos aplicar cualquier algoritmo de búsqueda local. " +
      "{{azar}}Otra opción: muestrear sucesores al azar, moviéndonos una distancia delta en una dirección aleatoria. " +
      "{{empirico}}Los métodos que miden el progreso comparando f entre dos puntos cercanos se llaman de gradiente empírico: es el ascenso de colina más empinada, en el espacio discretizado. " +
      "{{achicar}}Achicar delta con el tiempo da soluciones más precisas, pero no garantiza llegar al óptimo global.",
  },
  {
    id: "gradiente",
    text:
      "Segunda idea: si tenemos la fórmula de f, podemos usar cálculo en vez de probar puntos. " +
      "{{gradiente}}La herramienta clave es el gradiente, nabla f: un vector que apunta hacia donde la función sube más rápido, y cuyo largo dice qué tan empinada es la subida. " +
      "{{flechas}}Imaginá una montaña con niebla: el gradiente es la flecha que, desde donde estás parado, apunta a la subida más fuerte. " +
      "{{componentes}}En nuestro problema tiene seis componentes: la derivada parcial de f respecto de cada coordenada. " +
      "{{cero}}A veces se puede resolver nabla f igual a cero directamente. Con un solo aeropuerto, la solución es el promedio de las coordenadas de todas las ciudades. " +
      "{{tres}}Pero con tres no hay fórmula cerrada, porque los conjuntos C dependen del estado. Lo que sí podemos es calcular el gradiente localmente, " +
      "{{eq42}}como en la ecuación cuatro punto dos.",
  },
  {
    id: "paso",
    text:
      "Con el gradiente, la regla para moverse es simple: {{regla}}equis pasa a ser equis más alfa por nabla f. Un pasito en la dirección que más sube. " +
      "{{signo}}El libro habla de maximizar; en los aeropuertos queremos minimizar, así que restamos y bajamos: descenso por gradiente. " +
      "{{alfa}}Alfa se llama tamaño de paso, y elegirlo bien es el problema. " +
      "{{chico}}Si es muy chico, necesitamos muchísimos pasos. " +
      "{{grande}}Si es muy grande, nos pasamos del máximo y quedamos rebotando. " +
      "{{lineal}}La búsqueda lineal, que el libro traduce como búsqueda online, ataca este dilema: sigue la dirección del gradiente duplicando alfa una y otra vez, " +
      "{{empeora}}hasta que f empieza a empeorar. Ese punto es el nuevo estado actual, y desde ahí se elige una nueva dirección.",
  },
  {
    id: "demo",
    text:
      "Así se ve en el mapa. {{pasos}}En cada paso calculamos el gradiente de cada aeropuerto con sus ciudades, y lo movemos un poquito cuesta abajo. " +
      "{{baja}}La función objetivo baja, y baja, hasta que los aeropuertos se acomodan.",
  },
  {
    id: "newton",
    text:
      "Para muchos problemas, el método más efectivo es el de Newton-Raphson. " +
      "{{raices}}Sirve para encontrar raíces: resolver ecuaciones de la forma g de equis igual a cero. " +
      "{{tangente}}En el punto actual trazamos la recta tangente, y vemos dónde corta al eje: esa es la nueva estimación. " +
      "{{formula}}En fórmula: equis menos g de equis sobre g prima de equis. " +
      "{{converge}}Repitiendo, llega a la raíz muy rápido. " +
      "{{conexion}}¿Y para optimizar? En un máximo o un mínimo, el gradiente vale cero. Entonces aplicamos Newton a la ecuación nabla f igual a cero. " +
      "{{hessiana}}Con vectores, dividir por la derivada se vuelve multiplicar por la inversa de la Hessiana, la matriz de segundas derivadas. " +
      "{{tazon}}Intuitivamente, Newton ajusta un tazón cuadrático a f en el punto actual, y salta directo a su fondo.",
  },
  {
    id: "newtonAeropuertos",
    text:
      "En los aeropuertos, la Hessiana es muy simple. " +
      "{{diagonal}}Fuera de la diagonal todo es cero, y en la diagonal, para el aeropuerto i, aparece dos veces la cantidad de ciudades de C sub i. " +
      "{{centroide}}Haciendo la cuenta, un solo paso de Newton lleva cada aeropuerto directo al centroide de sus ciudades. " +
      "{{repetir}}Después recalculamos los conjuntos C, y repetimos. " +
      "{{costo}}El problema: con n variables, la Hessiana tiene n al cuadrado entradas, y encima hay que invertirla. Con muchas dimensiones es carísimo, por eso se usan versiones aproximadas de Newton.",
  },
  {
    id: "problemas",
    text:
      "Los problemas de siempre no desaparecen. {{problemas}}En espacios continuos también hay máximos locales, crestas y mesetas. " +
      "{{soluciones}}Los reinicios aleatorios y el recocido simulado siguen ayudando. " +
      "{{perderse}}Pero un espacio continuo de muchas dimensiones es enorme, y es muy fácil perderse.",
  },
  {
    id: "restricciones",
    text:
      "Último tema: optimización con restricciones. {{restr}}Las soluciones tienen que cumplir condiciones estrictas. Por ejemplo, los aeropuertos deben quedar dentro de Rumania, y en tierra firme, no en el medio de un lago. " +
      "{{lp}}El caso más conocido es la programación lineal: las restricciones son desigualdades lineales, y la función objetivo también es lineal. " +
      "{{vertice}}En dos dimensiones, la región permitida es un polígono, y el óptimo aparece en un vértice. " +
      "{{convexo}}Esa región es un conjunto convexo: el segmento entre dos puntos cualesquiera queda adentro. " +
      "{{poli}}La programación lineal se resuelve en tiempo polinomial en el número de variables. " +
      "{{convexa}}Y es un caso especial de la optimización convexa: región convexa, objetivo convexo. Bajo ciertas condiciones también es polinomial, aun con miles de variables, y aparece mucho en aprendizaje automático y control.",
  },
  {
    id: "resumen",
    text:
      "Resumiendo. {{r1}}En espacios continuos hay infinitos sucesores. " +
      "{{r2}}Podemos discretizar con un paso delta y usar gradiente empírico. " +
      "{{r3}}Si tenemos la fórmula, usamos el gradiente, cuidando el tamaño de paso alfa. " +
      "{{r4}}Newton-Raphson usa además la Hessiana para saltar al óptimo de una aproximación cuadrática. " +
      "{{r5}}Los máximos locales siguen existiendo. " +
      "{{r6}}Y con restricciones, la programación lineal y la optimización convexa son los casos que sabemos resolver bien.",
  },
];
