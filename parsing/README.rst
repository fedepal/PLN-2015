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

Ejercicio 4
-----------

**horzMarkov = 0**

| Parsed 1444 sentences
| Labeled
|   Precision: 70.18%
|   Recall: 69.95%
|   F1: 70.06%
| Unlabeled
|   Precision: 72.04%
|   Recall: 71.81%
|   F1: 71.93%

| real	1m1.155s
| user	1m0.256s
| sys	0m0.120s

**horzMarkov = 1**

| Parsed 1444 sentences
| Labeled
|   Precision: 74.71%
|   Recall: 74.62%
|   F1: 74.66%
| Unlabeled
|   Precision: 76.58%
|   Recall: 76.48%
|   F1: 76.53%

| real	1m8.292s
| user	1m8.236s
| sys	0m0.076s

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

| real	1m35.672s
| user	1m35.608s
| sys	0m0.088s

**horzMarkov = 3**

| Parsed 1444 sentences
| Labeled
|   Precision: 73.97%
|   Recall: 73.33%
|   F1: 73.65%
| Unlabeled
|   Precision: 76.13%
|   Recall: 75.47%
|   F1: 75.80%

| real	1m47.418s
| user	1m47.336s
| sys	0m0.128s

Ejercicio 5
-----------

| Parsed 1444 sentences
| Labeled
|   Precision: 97.38%
|   Recall: 14.62%
|   F1: 25.42%
| Unlabeled
|   Precision: 97.58%
|   Recall: 14.65%
|   F1: 25.48%

| real	0m24.281s
| user	0m24.140s
| sys	0m0.144s
