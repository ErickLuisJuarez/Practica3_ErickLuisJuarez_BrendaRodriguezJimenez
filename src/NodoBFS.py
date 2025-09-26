import simpy
from Nodo import *
from Canales.CanalRecorridos import *

# La unidad de tiempo
TICK = 1


class NodoBFS(Nodo):
    ''' Implementa la interfaz de Nodo para el algoritmo de Broadcast.'''

    def __init__(self, id_nodo, vecinos, canal_entrada, canal_salida):
        ''' Constructor de nodo que implemente el algoritmo BFS. '''
        super().__init__(id_nodo, vecinos, canal_entrada, canal_salida)
        self.padre = id_nodo
        self.hijos = []
        self.distancia = 0
        self.mensajes_esperados = 0


    def bfs(self, env):
        ''' Algoritmo BFS. '''
        if self.id_nodo == 0: #Si el nodo es el nodo raiz
            yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
            self.canal_salida.envia(("GO", -1, self.id_nodo), [self.id_nodo]) #Se envia GO a si mismo
        
        # Bucle para procesar los mensajes
        while True:
            mensaje = yield self.canal_entrada.get() #Se espera un mensaje
            tipo = mensaje[0] #tipo de mensaje enviado (GO o BACK)
            d = mensaje[1] #Distancia del mensaje enviado
            j = mensaje[2] #Remitente del mensaje

            # Caso 1:Se recibe un mensaje GO
            if tipo == "GO":
                if self.padre == self.id_nodo: #Si es la primera vez que se visita el ndoo
                    self.padre = j  # Se asigna como padre al remitente
                    self.hijos = [] #Se reinicia la lista de hijos
                    self.distancia = d + 1 #Se actualiza la distancia
                
                    vecinos_a_avisar = [v for v in self.vecinos if v != j]  #Se crea una lista de vecinos a los que voy a reenviar el GO
                    self.mensajes_esperados = len(vecinos_a_avisar) #Se cuenta cuántas respuestas BACK debe esperar de esos vecinos
                    
                    if self.mensajes_esperados == 0: # Si no hay vecinos a los que avisar
                        yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                        self.canal_salida.envia(("BACK", True, self.distancia, self.id_nodo), [self.padre]) # Envío un mensaje BACK afirmativo al padre indicando que termino
                    else: #En otro caso
                        for k in vecinos_a_avisar: #Se recorre todos los vecinos del nodo padre
                            yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                            self.canal_salida.envia(("GO", self.distancia, self.id_nodo), [k])
                
                elif self.distancia > d + 1: # Si encuentro un camino más corto hacia este nodo  
                    self.padre = j #Se actualiza el nodo padre en el nodo remitente
                    self.hijos = [] #Se reinicia la lista de hijos
                    self.distancia = d + 1 #Se actualiza la nueva distancia
                    vecinos_a_avisar = [v for v in self.vecinos if v != j] #Se eliguen a todos los vecinos excepto al padre
                    self.mensajes_esperados = len(vecinos_a_avisar) #Se cuenta cuantos mensajes BACK se debe esperar
                    
                    if self.mensajes_esperados == 0: #Soi es una hoja
                        yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                        self.canal_salida.envia(("BACK", True, self.distancia, self.id_nodo), [self.padre]) #Se envia un BACK Afirmativo a padre
                    else:
                        for k in vecinos_a_avisar: #Recorre tdos los vecinos de padre
                            yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                            self.canal_salida.envia(("GO", self.distancia, self.id_nodo), [k]) #Se envia GO  on la distancia actualizada
                else:
                    yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                    self.canal_salida.envia(("BACK", False, d + 1, self.id_nodo), [j]) #Se envia BACK falso al remitente
            
            # Caso 2: Se recibr un mensaje BACK
            elif tipo == "BACK":
                resp = mensaje[1] #Se envia TRUE si confirma si es hijo, FALSE en otro caso  
                d_hijo = mensaje[2] #Distancia del hijo      
                remitente_back = mensaje[3] #Nodo que envio el BACK
                
              
                if d_hijo == self.distancia + 1:  #Si el hijo está en el nivel correcto
                    if resp:  #Si confirma que es hijo
                        self.hijos.append(remitente_back) #Se agrega a la lista de hijos
                
                    self.mensajes_esperados -= 1 #Se reducen en uno las respuesta pendientes
                    
                    if self.mensajes_esperados == 0: #Si ya se recibieron todas las respuestas de los vecinos
                        if self.padre != self.id_nodo: #Si no es la raiz
                            yield env.timeout(TICK) #Simula retraso con la unidad de tiempo TICK
                            self.canal_salida.envia(("BACK", True, self.distancia, self.id_nodo), [self.padre]) #Se envia un BACK Afirmativo al padre con la distancia actualizada