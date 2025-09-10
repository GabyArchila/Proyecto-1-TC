from collections import deque
from automata import AFD


class Subconjuntos:
    def __init__(self, afn):
        self.afn = afn
        self.afd = AFD()
        self.estados_afd = {}  # {frozenset(state_ids): afd_state_name}

    def convertir(self):
        # Obtener el alfabeto (excluyendo epsilon)
        alphabet = set()
        for estado in self.afn.states:
            alphabet.update(estado.transitions.keys())

        if '#' in alphabet:
            alphabet.remove('#')

        self.afd.alphabet = alphabet

        # Estado inicial del AFD es la ε-clausura del estado inicial del AFN
        inicio_afn = self.afn.epsilon_closure({self.afn.start_state})
        estado_inicial = self._obtener_estado_afd(inicio_afn)
        self.afd.start_state = estado_inicial

        por_procesar = deque([inicio_afn])
        procesados = set()

        while por_procesar:
            conjunto_actual = por_procesar.popleft()
            estado_actual = self._obtener_estado_afd(conjunto_actual)

            # Marcar como procesado
            conjunto_key = frozenset(e.id for e in conjunto_actual)
            if conjunto_key in procesados:
                continue
            procesados.add(conjunto_key)

            # Marcar como final si contiene algún estado final del AFN
            if any(e.is_final for e in conjunto_actual):
                self.afd.final_states.add(estado_actual)

            # Para cada símbolo en el alfabeto
            for simbolo in alphabet:
                siguiente_conjunto = self.afn.mover(conjunto_actual, simbolo)
                if siguiente_conjunto:
                    siguiente_estado = self._obtener_estado_afd(siguiente_conjunto)
                    self.afd.transitions[(estado_actual, simbolo)] = siguiente_estado

                    # Agregar a la cola si no ha sido procesado
                    siguiente_key = frozenset(e.id for e in siguiente_conjunto)
                    if siguiente_key not in procesados:
                        por_procesar.append(siguiente_conjunto)

        return self.afd

    def _obtener_estado_afd(self, conjunto_estados):
        conjunto_key = frozenset(e.id for e in conjunto_estados)

        if conjunto_key not in self.estados_afd:
            nuevo_estado = f"S{len(self.estados_afd)}"
            self.estados_afd[conjunto_key] = nuevo_estado
            self.afd.states.add(nuevo_estado)

        return self.estados_afd[conjunto_key]