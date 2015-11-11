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
|   Precision: 72.97%
|   Recall: 72.92%
|   F1: 72.95%
| Unlabeled
|   Precision: 75.19%
|   Recall: 75.14%
|   F1: 75.17%

| real	1m58.124s
| user	1m57.956s
| sys	0m0.224s


Ejercicio 4
-----------

**horzMarkov = 0**

| Parsed 1444 sentences
| Labeled
|   Precision: 70.20%
|   Recall: 69.94%
|   F1: 70.07%
| Unlabeled
|   Precision: 72.08%
|   Recall: 71.82%
|   F1: 71.95%

| real	0m59.200s
| user	0m59.180s
| sys	0m0.040s


**horzMarkov = 1**

| Parsed 1444 sentences
| Labeled
|   Precision: 74.62%
|   Recall: 74.58%
|   F1: 74.60%
| Unlabeled
|   Precision: 76.55%
|   Recall: 76.50%
|   F1: 76.53%

| real	1m12.190s
| user	1m11.920s
| sys	0m0.300s

**horzMarkov = 2**

| Parsed 1444 sentences
| Labeled
|   Precision: 74.76%
|   Recall: 74.33%
|   F1: 74.55%
| Unlabeled
|   Precision: 76.78%
|   Recall: 76.34%
|   F1: 76.56%

| real	1m42.013s
| user	1m41.860s
| sys	0m0.200s


**horzMarkov = 3**

| Parsed 1444 sentences
| Labeled
|   Precision: 73.89%
|   Recall: 73.43%
|   F1: 73.66%
| Unlabeled
|   Precision: 76.20%
|   Recall: 75.73%
|   F1: 75.96%

| real	1m56.776s
| user	1m55.028s
| sys	0m1.800s

Ejercicio 5
-----------

| Parsed 1 sentences
| Labeled
|   Precision: 70.00%
|   Recall: 77.78%
|   F1: 73.68%
| Unlabeled
|   Precision: 70.00%
|   Recall: 77.78%
|   F1: 73.68%
