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
|  Precision: 73.11%
|  Recall: 72.81%
|  F1: 72.96%
| Unlabeled
|  Precision: 75.22%
|  Recall: 74.91%
|  F1: 75.06%

| real	1m56.380s
| user	1m56.312s
| sys	0m0.128s
