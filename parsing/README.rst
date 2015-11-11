Ejercicio 1
-----------

**Flat**

| Parsed **1444** sentences

| Labeled
|  Precision: 99.93%
|  Recall: 14.57%
|  F1: 25.43%
| Unlabeled
|  Precision: 100.00%
|  Recall: 14.58%
|  F1: 25.45%

**RBranch**

| Parsed **1444** sentences

| Labeled
|  Precision: 8.81%
|  Recall: 14.57%
|  F1: 10.98%
| Unlabeled
|  Precision: 8.87%
|  Recall: 14.68%
|  F1: 11.06%

**LBranch**

| Parsed **1444** sentences

| Labeled
|  Precision: 8.81%
|  Recall: 14.57%
|  F1: 10.98%
| Unlabeled
|  Precision: 14.71%
|  Recall: 24.33%
|  F1: 18.33%

Ejercicio 2
-----------
En el init, separo las producciones con terminales y no terminales.
Creo una lista con las producciones con terminales y un diccionario en donde
la key es una tupla con la parte derecha de la producciones y el valor es una
lista de tuplas con el lado izquiero y la logprob de esa producción.

Para el parse, el algorítmo es similar al pseudo-código, solo que para
hacerlo más eficiente no recorro todos los no terminales sino que solo busco
en el diccionario de no terminales aquellos que tengan en la parte derecha al
no terminal del subarbol izquiero y derecho respectivamente.

Para el caso de la amibigüedad, se parsea la frase "the man saw the dog with
the telescope", se crea una gramática probabilistica a partir de una lista de
producciones con probabilidad. Y se parsea a partir de esta gramática. Luego
se comparan que el árbol sea el correcto, la probabilidad sea la correcta
y se compara que pi y bp sean correctos.

Ejercicio 3
-----------
Para la UPCFG en el init recorro la lista de árboles, los deslexicalizo y
convierto a Forma Normal de Chomsky, y elimino las ramas unarias. Luego
extraigo las producciones y las guardo en una lista que permiten inducir la
PCFG.

Para el parse, usamos parse de CKYParser que recibe una lista de tags y devuelve
None si no se puede parsear, en este caso el arból que se devuelve es un árbol
Flat. Si parsea correctamente se lexicaliza el árbol y como viene en forma
normal de Chomsky se la deshace para devolver un árbol desbinarizado.

**UPCFG**

| Parsed **1444** sentences

| Labeled
|   Precision: 73.14%
|   Recall: 72.84%
|   F1: 72.99%
| Unlabeled
|   Precision: 75.25%
|   Recall: 74.94%
|   F1: 75.09%


| real	1m58.124s
| user	1m57.956s
| sys	0m0.224s


Ejercicio 4
-----------
Con solo agregar horzMarkov como parametro de la clase UPCFG y utlizarlo en la
función chomsky_normal_form, obtenemos los árboles binarizados y con
markovizacion horizontal.

**horzMarkov = 0**

| Parsed 1444 sentences
|Labeled
|   Precision: 70.18%
|   Recall: 69.95%
|   F1: 70.06%
|Unlabeled
|   Precision: 72.04%
|   Recall: 71.81%
|   F1: 71.93%


| real	0m59.200s
| user	0m59.180s
| sys	0m0.040s


**horzMarkov = 1**

| Parsed 1444 sentences
| Labeled
|   Precision: 70.00%
|   Recall: 77.78%
|   F1: 73.68%
| Unlabeled
|   Precision: 70.00%
|   Recall: 77.78%
|   F1: 73.68%

| real	1m12.190s
| user	1m11.920s
| sys	0m0.300s

**horzMarkov = 2**

| Parsed 1444 sentences
| Labeled
|   Precision: 74.82%
|   Recall: 74.30%
|   F1: 74.56%
| Unlabeled
|   Precision: 76.74%
|   Recall: 76.21%
|   F1: 76.47%

| real	1m42.013s
| user	1m41.860s
| sys	0m0.200s


**horzMarkov = 3**

| Parsed 1444 sentences
| Labeled
|   Precision: 73.95%
|   Recall: 73.31%
|   F1: 73.63%
| Unlabeled
|   Precision: 76.11%
|   Recall: 75.45%
|   F1: 75.78%


| real	1m56.776s
| user	1m55.028s
| sys	0m1.800s

Ejercicio 5
-----------
Agregue el flag unary, a UPCFG para cuando sea True no llamar a collapse_unary,
y se lo paso también a CKYParser ya que el manejo de unarios baja la performance
del parser.
Se agregó un test, en test_cky_parser, que testee el correcto parseo de una
gramática con producciones unarias.

Es muy lento el algorítmo en comparación a un cky sin manejo de unarios, por el
bucle while, porque por cada No Terminal(nt) que esta en pi(i,j), se busca en un
diccionario si nt es parte derecha, luego se itera sobre la lista de producciones
unarias talque nt es parte derecha y se busca una probabilidad máxima. Y si se
encuentra está probabilidad máxima se realiza nuevamente todo el bucle while.
Haciendo profiling, con un árbol se ve que 203762 veces se agrega o se reemplaza
un elemento en pi, y buscando unarios a lo anterior se le suman 8177677 veces
que se modifica pi.

**UPCFG con unarios**

| Parsed 100 sentences
| Labeled
|   Precision: 68.37%
|   Recall: 68.88%
|   F1: 68.63%
| Unlabeled
|   Precision: 71.61%
|   Recall: 72.15%
|   F1: 71.88%

| real	82m45.370s
| user	82m47.452s
| sys	0m0.916s

**UPCFG sin unarios**
| Parsed 100 sentences
| Labeled
|   Precision: 72.70%
|   Recall: 73.53%
|   F1: 73.11%
| Unlabeled
|   Precision: 75.19%
|   Recall: 76.04%
|   F1: 75.61%

| real	0m21.348s
| user	0m21.272s
| sys	0m0.084s
