from collections import deque
from automata import AFD


class Subconjuntos:
    def __init__(self, afn):
        self.afn = afn
        self.afd = AFD()
        self.estados_afd = {}  # Mapeo de conjuntos de estados AFN a estados AFD

    def convertir(self):
        # Obtener el alfabeto (excluyendo epsilon)
        alphabet = set()
        for estado in self.afn.transitions:
            for simbolo in self.afn.transitions[estado]:
                if simbolo != '#':  # Excluir epsilon
                    alphabet.add(simbolo)

        self.afd.alphabet = alphabet
        print(f"Alfabeto extraído: {alphabet}")

        # Estado inicial del AFD es la ε-clausura del estado inicial del AFN
        if not self.afn.start_state:
            print("Error: AFN no tiene estado inicial")
            return self.afd

        inicio_afn = self.afn.epsilon_closure({self.afn.start_state})
        print(f"ε-clausura del estado inicial: {[str(s) for s in inicio_afn]}")

        estado_inicial = self.obtener_estado_afd(inicio_afn)
        self.afd.start_state = estado_inicial

        por_procesar = deque([inicio_afn])
        procesados = set()

        print(f"Iniciando conversión AFN->AFD...")

        while por_procesar:
            conjunto_actual = por_procesar.popleft()
            estado_actual = self.obtener_estado_afd(conjunto_actual)

            # Crear clave única para el conjunto
            clave_conjunto = frozenset(estado.id for estado in conjunto_actual)

            if clave_conjunto in procesados:
                continue

            procesados.add(clave_conjunto)
            print(f"\nProcesando estado {estado_actual}: {[str(s) for s in conjunto_actual]}")

            # Marcar como final si contiene algún estado final del AFN
            if any(estado.is_final for estado in conjunto_actual):
                self.afd.final_states.add(estado_actual)
                print(f"  Estado {estado_actual} marcado como final")

            # Para cada símbolo en el alfabeto
            for simbolo in sorted(alphabet):
                print(f"  Procesando símbolo '{simbolo}':")
                siguiente_conjunto = self.afn.mover(conjunto_actual, simbolo)

                if siguiente_conjunto:
                    siguiente_estado = self.obtener_estado_afd(siguiente_conjunto)
                    self.afd.transitions[(estado_actual, simbolo)] = siguiente_estado
                    print(f"    Transición: {estado_actual} --{simbolo}--> {siguiente_estado}")
                    print(f"    Estados destino: {[str(s) for s in siguiente_conjunto]}")

                    # Agregar a la cola si no ha sido procesado
                    siguiente_clave = frozenset(estado.id for estado in siguiente_conjunto)
                    if siguiente_clave not in procesados:
                        por_procesar.append(siguiente_conjunto)
                        print(f"    Agregado a cola para procesar")
                else:
                    print(f"    No hay transiciones para '{simbolo}'")

        print(f"\nConversión completada:")
        print(f"  Estados AFD: {len(self.afd.states)}")
        print(f"  Estado inicial: {self.afd.start_state}")
        print(f"  Estados finales: {list(self.afd.final_states)}")
        print(f"  Transiciones: {len(self.afd.transitions)}")

        return self.afd

    def obtener_estado_afd(self, conjunto_estados):
        # Convertir el conjunto a una tupla ordenada para usar como clave
        clave = tuple(sorted(estado.id for estado in conjunto_estados))

        if clave not in self.estados_afd:
            nuevo_estado = f"S{len(self.estados_afd)}"
            self.estados_afd[clave] = nuevo_estado
            self.afd.states.add(nuevo_estado)
            print(f"    Nuevo estado AFD: {nuevo_estado} = {{{','.join(f'q{id}' for id in clave)}}}")

        return self.estados_afd[clave]