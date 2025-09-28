import simpy
from Nodo import *
from Canales.CanalRecorridos import *

# La unidad de tiempo
TICK = 1

class NodoDFS(Nodo):

    def __init__(self, id_nodo, vecinos, canal_entrada, canal_salida):
        ''' Constructor de nodo que implemente el algoritmo DFS. '''
        super().__init__(id_nodo, vecinos, canal_entrada, canal_salida)
        self.padre = None
        self.hijos = []
        self.completed_children = set()

    def dfs(self, env):
        ''' Algoritmo DFS. '''
        if self.id_nodo == 0:
            yield self.canal_entrada.put(("START", None))

        while True:
            mensaje = yield self.canal_entrada.get()
            tipo = mensaje[0]

            # when START() is received do
            if tipo == "START":
                self.padre = self.id_nodo
                self.hijos = []
                self.visitados = set()

                if not self.vecinos:
                    # si no hay vecinos, terminamos
                    continue
                else:
                    # let k in neighbors_i; send GO() to p_k
                    for v in self.vecinos:
                        if v not in self.visitados:
                            k = v
                            break
                    yield self.canal_salida.envia(("GO", self.id_nodo), [k])

            # when GO() is received from p_j do
            elif tipo == "GO":
                j = mensaje[1]
                if self.padre == None:
                    self.padre = j
                    self.hijos = []
                    self.visitados = set([j])

                    if self.visitados == set(self.vecinos):
                        # if(visited_i = neighbors_i) then send BACK(yes) to p_j
                        yield self.canal_salida.envia(("BACK", self.id_nodo, "yes"), [j])
                    else:
                        # else let k in neighbors_i \ visied_i; send GO() to p_k
                        for v in self.vecinos:
                            if v not in self.visitados:
                                k = v
                                break
                        yield self.canal_salida.envia(("GO", self.id_nodo), [k])
                else:
                    # else send BACK(no) to p_j
                    yield self.canal_salida.envia(("BACK", self.id_nodo, "no"), [j])

            # when BACK(resp) is received from p_j do
            elif tipo == "BACK":
                j = mensaje[1]
                resp = mensaje[2]
                if resp == "yes":
                    # if(resp = yes) then children_i = children_i u {j} end if;
                    if j not in self.hijos:
                        self.hijos.append(j)
                self.visitados.add(j)

                if self.visitados == set(self.vecinos):
                    # if(visited_i = neighbors_i)
                    if self.padre == self.id_nodo:
                        # then if(parent_i = i) then the traversal is terminated
                        continue
                    else:
                        # else send BACK(yes) to p_(parent_i)
                        yield self.canal_salida.envia(("BACK", self.id_nodo, "yes"), [self.padre])
                else:
                    # else let k in neighnors_i \ visited_i; send GO() to p_k
                    for v in self.vecinos:
                        if v not in self.visitados:
                            k = v
                            break
                    yield self.canal_salida.envia(("GO", self.id_nodo), [k])