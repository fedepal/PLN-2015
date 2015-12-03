Ejercicio 1
-----------

**Flat**

| Parsed **1444** sentences

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   99.93%    14.57% 25.43%
**Unlabeled** 100.00%   14.58% 25.45%
============= ========= ====== ======

**RBranch**

| Parsed **1444** sentences

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   8.81%     14.57% 10.98%
**Unlabeled** 8.87%     14.68% 11.06%
============= ========= ====== ======

**LBranch**

| Parsed **1444** sentences

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   8.81%     14.57% 10.98%
**Unlabeled** 14.71%    24.33% 18.33%
============= ========= ====== ======


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

Estos dos son posibles parseos, el de la izquierda es el menos probable.

.. image:: https://github.com/fedepal/PLN-2015/blob/practico3/parsing/treeW.png?raw=true
.. image:: https://github.com/fedepal/PLN-2015/blob/practico3/parsing/treeOK.png?raw=true


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

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   73.14%    72.84% 72.99%
**Unlabeled** 75.25%    74.94% 75.09%
============= ========= ====== ======

| real	1m58.124s
| user	1m57.956s
| sys	0m0.224s


Ejercicio 4
-----------
Con solo agregar horzMarkov como parametro de la clase UPCFG y utlizarlo en la
función chomsky_normal_form, obtenemos los árboles binarizados y con
markovizacion horizontal.

**horzMarkov = 0**

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   70.18%    69.95% 70.06%
**Unlabeled** 72.04%    71.81% 71.93%
============= ========= ====== ======

| real	1m0.016s
| user	0m59.936s
| sys	0m0.104s
|

**horzMarkov = 1**

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   74.67%    74.58% 74.62%
**Unlabeled** 76.54%    76.44% 76.49%
============= ========= ====== ======

| real	1m22.816s
| user	1m22.772s
| sys	0m0.064s
|

**horzMarkov = 2**

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   74.82%    74.30% 74.56%
**Unlabeled** 76.74%    76.21% 76.47%
============= ========= ====== ======

| real	1m42.013s
| user	1m41.860s
| sys	0m0.200s
|

**horzMarkov = 3**

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   73.95%    73.31% 73.63%
**Unlabeled** 76.11%    75.45% 75.78%
============= ========= ====== ======

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

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   68.37%    68.88% 68.63%
**Unlabeled** 71.61%    72.15% 71.88%
============= ========= ====== ======

| real	82m45.370s
| user	82m47.452s
| sys	0m0.916s

**UPCFG sin unarios**

| Parsed 100 sentences

============= ========= ====== ======
|             Precision Recall F1
============= ========= ====== ======
**Labeled**   72.70%    73.53% 73.11%
**Unlabeled** 75.19%    76.04% 75.61%
============= ========= ====== ======

| real	0m21.348s
| user	0m21.272s
| sys	0m0.084s
