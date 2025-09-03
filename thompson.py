from automata import AFN

class Thompson:
    def __init__(self):
        pass

    def crear_simbolo(self, char):
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, char)
        return afn

    def crear_epsilon(self):
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, 'ε')
        return afn

    def concatenacion(self, afn1, afn2):
        nuevo_afn = AFN()
        estado_map = {}

        # Mapear estados de afn1
        for estado in afn1.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            estado_map[estado] = nuevo_estado

        # Mapear estados de afn2
        for estado in afn2.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=estado.is_final)
            estado_map[estado] = nuevo_estado

        # Copiar transiciones de afn1
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(estado_map[origen], estado_map[destino], simbolo)

        # Copiar transiciones de afn2
        for origen in afn2.transitions:
            for simbolo in afn2.transitions[origen]:
                for destino in afn2.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(estado_map[origen], estado_map[destino], simbolo)

        # Conectar estados finales de afn1 con estado inicial de afn2
        for estado_final in afn1.final_states:
            nuevo_afn.agregar_transicion(estado_map[estado_final], estado_map[afn2.start_state], 'ε')

        nuevo_afn.start_state = estado_map[afn1.start_state]
        nuevo_afn.final_states = {estado_map[e] for e in afn2.final_states}

        return nuevo_afn

    def union(self, afn1, afn2):
        nuevo_afn = AFN()
        nuevo_inicio = nuevo_afn.crear_estado()
        nuevo_fin = nuevo_afn.crear_estado(is_final=True)

        estado_map1 = {}
        for estado in afn1.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            estado_map1[estado] = nuevo_estado

        estado_map2 = {}
        for estado in afn2.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            estado_map2[estado] = nuevo_estado

        # Copiar transiciones de afn1
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(estado_map1[origen], estado_map1[destino], simbolo)

        # Copiar transiciones de afn2
        for origen in afn2.transitions:
            for simbolo in afn2.transitions[origen]:
                for destino in afn2.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(estado_map2[origen], estado_map2[destino], simbolo)

        # Conectar nuevo inicio a los inicios de afn1 y afn2
        nuevo_afn.agregar_transicion(nuevo_inicio, estado_map1[afn1.start_state], 'ε')
        nuevo_afn.agregar_transicion(nuevo_inicio, estado_map2[afn2.start_state], 'ε')

        # Conectar estados finales de afn1 y afn2 al nuevo fin
        for estado in afn1.final_states:
            nuevo_afn.agregar_transicion(estado_map1[estado], nuevo_fin, 'ε')
        for estado in afn2.final_states:
            nuevo_afn.agregar_transicion(estado_map2[estado], nuevo_fin, 'ε')

        nuevo_afn.start_state = nuevo_inicio
        nuevo_afn.final_states = {nuevo_fin}

        return nuevo_afn

    def estrella(self, afn):
        nuevo_afn = AFN()
        nuevo_inicio = nuevo_afn.crear_estado(is_final=True)

        estado_map = {}
        for estado in afn.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            estado_map[estado] = nuevo_estado

        # Copiar transiciones
        for origen in afn.transitions:
            for simbolo in afn.transitions[origen]:
                for destino in afn.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(estado_map[origen], estado_map[destino], simbolo)

        # Conectar nuevo inicio al inicio del afn original
        nuevo_afn.agregar_transicion(nuevo_inicio, estado_map[afn.start_state], 'ε')

        # Conectar estados finales al inicio del afn original y al nuevo inicio
        for estado_final in afn.final_states:
            nuevo_afn.agregar_transicion(estado_map[estado_final], estado_map[afn.start_state], 'ε')
            nuevo_afn.agregar_transicion(estado_map[estado_final], nuevo_inicio, 'ε')

        nuevo_afn.start_state = nuevo_inicio
        nuevo_afn.final_states = {nuevo_inicio}

        return nuevo_afn

    def construir_desde_postfix(self, postfix):
        if not postfix:
            return self.crear_epsilon()

        stack = []

        for char in postfix:
            try:
                if char == '.':
                    # Concatenación - necesita 2 operandos
                    if len(stack) < 2:
                        raise ValueError(f"Concatenación requiere 2 operandos, solo hay {len(stack)}")
                    afn2 = stack.pop()
                    afn1 = stack.pop()
                    stack.append(self.concatenacion(afn1, afn2))
                elif char == '|':
                    # Unión - necesita 2 operandos
                    if len(stack) < 2:
                        raise ValueError(f"Unión requiere 2 operandos, solo hay {len(stack)}")
                    afn2 = stack.pop()
                    afn1 = stack.pop()
                    stack.append(self.union(afn1, afn2))
                elif char == '*':
                    # Cerradura de Kleene - necesita 1 operando
                    if len(stack) < 1:
                        raise ValueError(f"Estrella requiere 1 operando, stack está vacío")
                    afn = stack.pop()
                    stack.append(self.estrella(afn))
                elif char == '+':
                    # Uno o más (equivalente a aa*)
                    if len(stack) < 1:
                        raise ValueError(f"Plus requiere 1 operando, stack está vacío")
                    afn = stack.pop()
                    afn_copy = self.crear_simbolo('temp')  # Crear copia temporal
                    # Simular a+ = aa*
                    kleene = self.estrella(afn)
                    stack.append(self.concatenacion(afn, kleene))
                elif char == '?':
                    # Cero o uno (equivalente a ε|a)
                    if len(stack) < 1:
                        raise ValueError(f"Interrogación requiere 1 operando, stack está vacío")
                    afn = stack.pop()
                    epsilon = self.crear_epsilon()
                    stack.append(self.union(epsilon, afn))
                elif char == 'ε':
                    # Épsilon
                    stack.append(self.crear_epsilon())
                else:
                    # Símbolo del alfabeto
                    stack.append(self.crear_simbolo(char))
            except Exception as e:
                raise ValueError(f"Error procesando carácter '{char}': {e}")

        if len(stack) != 1:
            raise ValueError(f"Expresión postfix inválida: stack final tiene {len(stack)} elementos (debería ser 1)")

        return stack.pop()