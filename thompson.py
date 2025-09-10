from automata import AFN

class Thompson:
    def __init__(self):
        pass

    def crear_simbolo(self, char):
        """Crear AFN para un símbolo individual"""
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio

        # Manejar caracteres escapados correctamente
        if isinstance(char, str) and char.startswith('\\') and len(char) == 2:
            actual_char = char[1]  # Quitar el backslash
            afn.agregar_transicion(inicio, fin, actual_char)
        else:
            afn.agregar_transicion(inicio, fin, char)

        return afn

    def crear_epsilon(self):
        """Crear AFN que acepta solo epsilon"""
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, '#')
        return afn

    def concatenacion(self, afn1, afn2):
        """Concatenación: AFN1 · AFN2"""
        nuevo_afn = AFN()
        nuevo_afn.state_counter = max(afn1.state_counter, afn2.state_counter)

        # Mapeo de estados
        mapa_estados1 = {}
        mapa_estados2 = {}

        # Copiar estados de AFN1 (ninguno será final)
        for estado in afn1.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados1[estado] = nuevo_estado

        # Copiar estados de AFN2 (mantener finalidad)
        for estado in afn2.states:
            is_final = estado in afn2.final_states
            nuevo_estado = nuevo_afn.crear_estado(is_final=is_final)
            mapa_estados2[estado] = nuevo_estado

        # Copiar transiciones
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados1[origen],
                        mapa_estados1[destino],
                        simbolo
                    )

        for origen in afn2.transitions:
            for simbolo in afn2.transitions[origen]:
                for destino in afn2.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados2[origen],
                        mapa_estados2[destino],
                        simbolo
                    )

        # Conectar estados finales de AFN1 con estado inicial de AFN2
        for estado_final in afn1.final_states:
            nuevo_afn.agregar_transicion(
                mapa_estados1[estado_final],
                mapa_estados2[afn2.start_state],
                '#'
            )

        nuevo_afn.start_state = mapa_estados1[afn1.start_state]
        nuevo_afn.final_states = {mapa_estados2[e] for e in afn2.final_states}

        return nuevo_afn

    def union(self, afn1, afn2):
        """Unión: AFN1 | AFN2"""
        nuevo_afn = AFN()
        nuevo_afn.state_counter = max(afn1.state_counter, afn2.state_counter)

        # Crear nuevos estados inicial y final
        nuevo_inicio = nuevo_afn.crear_estado()
        nuevo_fin = nuevo_afn.crear_estado(is_final=True)

        # Mapeo de estados
        mapa_estados1 = {}
        mapa_estados2 = {}

        # Copiar estados (ninguno será final)
        for estado in afn1.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados1[estado] = nuevo_estado

        for estado in afn2.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados2[estado] = nuevo_estado

        # Copiar transiciones
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados1[origen],
                        mapa_estados1[destino],
                        simbolo
                    )

        for origen in afn2.transitions:
            for simbolo in afn2.transitions[origen]:
                for destino in afn2.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados2[origen],
                        mapa_estados2[destino],
                        simbolo
                    )

        # Conectar nuevo inicio con inicios de AFN1 y AFN2
        nuevo_afn.agregar_transicion(nuevo_inicio, mapa_estados1[afn1.start_state], '#')
        nuevo_afn.agregar_transicion(nuevo_inicio, mapa_estados2[afn2.start_state], '#')

        # Conectar finales con nuevo final
        for estado_final in afn1.final_states:
            nuevo_afn.agregar_transicion(mapa_estados1[estado_final], nuevo_fin, '#')
        for estado_final in afn2.final_states:
            nuevo_afn.agregar_transicion(mapa_estados2[estado_final], nuevo_fin, '#')

        nuevo_afn.start_state = nuevo_inicio
        return nuevo_afn

    def estrella(self, afn):
        """Cerradura de Kleene: AFN*"""
        nuevo_afn = AFN()
        nuevo_afn.state_counter = afn.state_counter

        # Crear nuevos estados inicial y final
        nuevo_inicio = nuevo_afn.crear_estado()
        nuevo_fin = nuevo_afn.crear_estado(is_final=True)

        # Mapeo de estados
        mapa_estados = {}
        for estado in afn.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados[estado] = nuevo_estado

        # Copiar transiciones
        for origen in afn.transitions:
            for simbolo in afn.transitions[origen]:
                for destino in afn.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados[origen],
                        mapa_estados[destino],
                        simbolo
                    )

        # Transiciones epsilon para Kleene
        nuevo_afn.agregar_transicion(nuevo_inicio, mapa_estados[afn.start_state], '#')

        for estado_final in afn.final_states:
            nuevo_afn.agregar_transicion(mapa_estados[estado_final], nuevo_fin, '#')
            nuevo_afn.agregar_transicion(mapa_estados[estado_final], mapa_estados[afn.start_state], '#')

        # Epsilon directo para aceptar cadena vacía
        nuevo_afn.agregar_transicion(nuevo_inicio, nuevo_fin, '#')

        nuevo_afn.start_state = nuevo_inicio
        return nuevo_afn

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

        # Tokenizar la expresión postfix para manejar caracteres escapados
        tokens = []
        i = 0
        while i < len(postfix):
            if postfix[i] == '\\' and i + 1 < len(postfix):
                tokens.append(postfix[i:i + 2])
                i += 2
            else:
                tokens.append(postfix[i])
                i += 1

        print(f"Tokens en postfix: {tokens}")

        for token in tokens:
            print(f"Procesando token: '{token}'")

            if token.startswith('\\'):
                # Caracter escapado
                resultado = self.crear_simbolo(token)
                stack.append(resultado)
                print(f"  Creado AFN para símbolo escapado '{token}'")

            elif token == '.':
                if len(stack) < 2:
                    raise ValueError("Concatenación requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                resultado = self.concatenacion(afn1, afn2)
                stack.append(resultado)
                print(f"  Concatenación realizada")

            elif token == '|':
                if len(stack) < 2:
                    raise ValueError("Unión requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                resultado = self.union(afn1, afn2)
                stack.append(resultado)
                print(f"  Unión realizada")

            elif token == '*':
                if len(stack) < 1:
                    raise ValueError("Estrella requiere 1 operando")
                afn = stack.pop()
                resultado = self.estrella(afn)
                stack.append(resultado)
                print(f"  Estrella aplicada")

            elif token == '+':
                if len(stack) < 1:
                    raise ValueError("Plus requiere 1 operando")
                afn = stack.pop()
                resultado = self.plus(afn)
                stack.append(resultado)
                print(f"  Plus aplicado")

            elif token == '?':
                if len(stack) < 1:
                    raise ValueError("Opcional requiere 1 operando")
                afn = stack.pop()
                resultado = self.opcional(afn)
                stack.append(resultado)
                print(f"  Opcional aplicado")

            elif token == '#':  # Epsilon
                resultado = self.crear_epsilon()
                stack.append(resultado)
                print(f"  Creado AFN para epsilon")

            else:
                # Símbolo regular
                resultado = self.crear_simbolo(token)
                stack.append(resultado)
                print(f"  Creado AFN para símbolo '{token}'")

            print(f"  Stack size: {len(stack)}")

        if len(stack) != 1:
            raise ValueError(f"Expresión postfix inválida: stack final tiene {len(stack)} elementos")

        return stack[0]

