from collections import deque
from automata import AFD


class Subconjuntos:
    def __init__(self, afn):
        self.afn = afn
        self.afd = AFD()
        self.estados_afd = {}  # Mapeo de conjuntos de estados AFN a estados AFD

    # Mejorar el método convertir
    def convertir(self):
        # Obtener el alfabeto (excluyendo épsilon)
        alphabet = set()
        for estado in self.afn.transitions:
            for simbolo in self.afn.transitions[estado]:
                if simbolo != '#':
                    alphabet.add(simbolo)

        self.afd.alphabet = alphabet

        # Estado inicial del AFD es la ε-clausura del estado inicial del AFN
        inicio_afn = self.afn.epsilon_closure({self.afn.start_state})
        estado_inicial = self.obtener_estado_afd(inicio_afn)
        self.afd.start_state = estado_inicial

        por_procesar = deque([inicio_afn])
        procesados = set()

        while por_procesar:
            conjunto_actual = por_procesar.popleft()
            estado_actual = self.obtener_estado_afd(conjunto_actual)

            # Crear clave única para el conjunto
            clave_conjunto = frozenset(conjunto_actual)

            if clave_conjunto in procesados:
                continue

            procesados.add(clave_conjunto)

            # Marcar como final si contiene algún estado final del AFN
            if any(estado.is_final for estado in conjunto_actual):
                self.afd.final_states.add(estado_actual)

            # Para cada símbolo en el alfabeto
            for simbolo in sorted(alphabet):
                siguiente_conjunto = self.afn.mover(conjunto_actual, simbolo)

                if siguiente_conjunto:
                    siguiente_estado = self.obtener_estado_afd(siguiente_conjunto)
                    self.afd.transitions[(estado_actual, simbolo)] = siguiente_estado

                    # Agregar a la cola si no ha sido procesado
                    siguiente_clave = frozenset(siguiente_conjunto)
                    if siguiente_clave not in procesados:
                        por_procesar.append(siguiente_conjunto)

        return self.afd

    def obtener_estado_afd(self, conjunto_estados):
        # Convertir el conjunto a una tupla ordenada para usar como clave
        clave = tuple(sorted(estado.id for estado in conjunto_estados))

        if clave not in self.estados_afd:
            nuevo_estado = f"S{len(self.estados_afd)}"
            self.estados_afd[clave] = nuevo_estado
            self.afd.states.add(nuevo_estado)

        return self.estados_afd[clave]