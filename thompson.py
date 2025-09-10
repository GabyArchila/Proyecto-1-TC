from automata import AFN


class Thompson:
    def __init__(self):
        pass

    def crear_simbolo(self, char):
        """Crear AFN para un símbolo individual"""
        afn = AFN()
        inicio = afn.crear_estado(label=f"start_{char}")
        fin = afn.crear_estado(is_final=True, label=f"end_{char}")
        afn.start_state = inicio

        # Manejar caracteres escapados
        if char.startswith('\\') and len(char) == 2:
            actual_char = char[1]  # Quitar el backslash
            afn.agregar_transicion(inicio, fin, actual_char)
        else:
            afn.agregar_transicion(inicio, fin, char)

        return afn

    def crear_epsilon(self):
        """Crear AFN que acepta solo epsilon"""
        afn = AFN()
        inicio = afn.crear_estado(label="start_epsilon")
        fin = afn.crear_estado(is_final=True, label="end_epsilon")
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, '#')
        return afn

    def _copiar_afn(self, afn_original, prefix=""):
        """Copia un AFN completo con nuevos estados"""
        afn_nuevo = AFN()
        afn_nuevo.state_counter = afn_original.state_counter

        # Mapeo de estados viejos a nuevos
        estado_map = {}

        # Crear nuevos estados
        for estado in afn_original.states:
            nuevo_estado = afn_nuevo.crear_estado(
                is_final=estado.is_final,
                label=f"{prefix}{estado.label}"
            )
            estado_map[estado] = nuevo_estado

        # Copiar transiciones
        for estado in afn_original.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_nuevo.agregar_transicion(
                        estado_map[estado],
                        estado_map[destino],
                        simbolo
                    )
            for destino in estado.epsilon_transitions:
                afn_nuevo.agregar_transicion(
                    estado_map[estado],
                    estado_map[destino],
                    '#'
                )

        afn_nuevo.start_state = estado_map[afn_original.start_state]
        return afn_nuevo, estado_map

    def concatenacion(self, afn1, afn2):
        """Concatenación: AFN1 · AFN2"""
        # Copiar ambos AFNs
        afn1_copia, map1 = self._copiar_afn(afn1, "cat1_")
        afn2_copia, map2 = self._copiar_afn(afn2, "cat2_")

        # Conectar estados finales de afn1 con estado inicial de afn2
        for estado_final in afn1_copia.final_states:
            afn1_copia.agregar_transicion(estado_final, afn2_copia.start_state, '#')

        # El AFN resultante
        afn_resultante = AFN()
        afn_resultante.state_counter = max(afn1_copia.state_counter, afn2_copia.state_counter)

        # Combinar estados
        afn_resultante.states.update(afn1_copia.states)
        afn_resultante.states.update(afn2_copia.states)

        # Combinar transiciones
        for estado in afn1_copia.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_resultante.agregar_transicion(estado, destino, simbolo)
            for destino in estado.epsilon_transitions:
                afn_resultante.agregar_transicion(estado, destino, '#')

        for estado in afn2_copia.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_resultante.agregar_transicion(estado, destino, simbolo)
            for destino in estado.epsilon_transitions:
                afn_resultante.agregar_transicion(estado, destino, '#')

        afn_resultante.start_state = afn1_copia.start_state
        afn_resultante.final_states = afn2_copia.final_states.copy()

        return afn_resultante

    def union(self, afn1, afn2):
        """Unión: AFN1 | AFN2"""
        # Copiar ambos AFNs
        afn1_copia, map1 = self._copiar_afn(afn1, "union1_")
        afn2_copia, map2 = self._copiar_afn(afn2, "union2_")

        # Crear nuevos estados inicial y final
        afn_resultante = AFN()
        nuevo_inicio = afn_resultante.crear_estado(label="union_start")
        nuevo_fin = afn_resultante.crear_estado(is_final=True, label="union_end")

        # Combinar todos los estados
        afn_resultante.states.update(afn1_copia.states)
        afn_resultante.states.update(afn2_copia.states)

        # Combinar transiciones
        for estado in afn1_copia.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_resultante.agregar_transicion(estado, destino, simbolo)
            for destino in estado.epsilon_transitions:
                afn_resultante.agregar_transicion(estado, destino, '#')

        for estado in afn2_copia.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_resultante.agregar_transicion(estado, destino, simbolo)
            for destino in estado.epsilon_transitions:
                afn_resultante.agregar_transicion(estado, destino, '#')

        # Conectar nuevo inicio con inicios de ambos AFNs
        afn_resultante.agregar_transicion(nuevo_inicio, afn1_copia.start_state, '#')
        afn_resultante.agregar_transicion(nuevo_inicio, afn2_copia.start_state, '#')

        # Conectar finales de ambos AFNs con nuevo final
        for estado_final in afn1_copia.final_states:
            afn_resultante.agregar_transicion(estado_final, nuevo_fin, '#')
        for estado_final in afn2_copia.final_states:
            afn_resultante.agregar_transicion(estado_final, nuevo_fin, '#')

        afn_resultante.start_state = nuevo_inicio

        return afn_resultante

    def estrella(self, afn):
        """Cerradura de Kleene: AFN*"""
        afn_copia, estado_map = self._copiar_afn(afn, "star_")

        # Crear nuevos estados inicial y final
        afn_resultante = AFN()
        nuevo_inicio = afn_resultante.crear_estado(label="star_start")
        nuevo_fin = afn_resultante.crear_estado(is_final=True, label="star_end")

        # Combinar estados
        afn_resultante.states.update(afn_copia.states)

        # Combinar transiciones
        for estado in afn_copia.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    afn_resultante.agregar_transicion(estado, destino, simbolo)
            for destino in estado.epsilon_transitions:
                afn_resultante.agregar_transicion(estado, destino, '#')

        # Transiciones para Kleene
        afn_resultante.agregar_transicion(nuevo_inicio, afn_copia.start_state, '#')
        afn_resultante.agregar_transicion(nuevo_inicio, nuevo_fin, '#')

        for estado_final in afn_copia.final_states:
            afn_resultante.agregar_transicion(estado_final, nuevo_fin, '#')
            afn_resultante.agregar_transicion(estado_final, afn_copia.start_state, '#')

        afn_resultante.start_state = nuevo_inicio

        return afn_resultante

    def plus(self, afn):
        """Uno o más: AFN+ = AFN · AFN*"""
        afn_estrella = self.estrella(afn)
        return self.concatenacion(afn, afn_estrella)

    def opcional(self, afn):
        """Cero o uno: AFN? = ε | AFN"""
        epsilon = self.crear_epsilon()
        return self.union(epsilon, afn)

    def construir_desde_postfix(self, postfix):
        """Construye AFN desde expresión postfix usando pila"""
        if not postfix:
            return self.crear_epsilon()

        stack = []
        tokens = []
        i = 0

        # Tokenizar la expresión postfix
        while i < len(postfix):
            if postfix[i] == '\\' and i + 1 < len(postfix):
                tokens.append(postfix[i:i + 2])
                i += 2
            else:
                tokens.append(postfix[i])
                i += 1

        for token in tokens:
            if token.startswith('\\'):
                # Caracter escapado
                stack.append(self.crear_simbolo(token))
            elif token == '.':
                if len(stack) < 2:
                    raise ValueError("Concatenación requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                stack.append(self.concatenacion(afn1, afn2))
            elif token == '|':
                if len(stack) < 2:
                    raise ValueError("Unión requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                stack.append(self.union(afn1, afn2))
            elif token == '*':
                if len(stack) < 1:
                    raise ValueError("Estrella requiere 1 operando")
                stack.append(self.estrella(stack.pop()))
            elif token == '+':
                if len(stack) < 1:
                    raise ValueError("Plus requiere 1 operando")
                stack.append(self.plus(stack.pop()))
            elif token == '?':
                if len(stack) < 1:
                    raise ValueError("Opcional requiere 1 operando")
                stack.append(self.opcional(stack.pop()))
            elif token == '#':  # Epsilon
                stack.append(self.crear_epsilon())
            else:
                # Símbolo regular
                stack.append(self.crear_simbolo(token))

        if len(stack) != 1:
            raise ValueError(f"Expresión postfix inválida: stack final tiene {len(stack)} elementos")

        return stack[0]