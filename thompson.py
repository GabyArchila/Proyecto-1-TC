from automata import AFN


class Thompson:
    def __init__(self):
        pass

    def crear_simbolo(self, char):
        """Crear AFN para un símbolo individual: q0 --char--> q1"""
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, char)
        return afn

    def crear_epsilon(self):
        """Crear AFN que acepta solo épsilon: q0 --ε--> q1"""
        afn = AFN()
        inicio = afn.crear_estado()
        fin = afn.crear_estado(is_final=True)
        afn.start_state = inicio
        afn.agregar_transicion(inicio, fin, '#')
        return afn

    def concatenacion(self, afn1, afn2):
        """
        Concatenación: AFN1 · AFN2
        Conecta los estados finales de AFN1 con el estado inicial de AFN2
        """
        nuevo_afn = AFN()

        # Mapeo de estados viejos a nuevos
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

        # Copiar transiciones de AFN1
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados1[origen],
                        mapa_estados1[destino],
                        simbolo
                    )

        # Copiar transiciones de AFN2
        for origen in afn2.transitions:
            for simbolo in afn2.transitions[origen]:
                for destino in afn2.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados2[origen],
                        mapa_estados2[destino],
                        simbolo
                    )

        # Conectar estados finales de AFN1 con estado inicial de AFN2 usando ε
        for estado_final in afn1.final_states:
            nuevo_afn.agregar_transicion(
                mapa_estados1[estado_final],
                mapa_estados2[afn2.start_state],
                '#'
            )

        # Configurar estado inicial y finales
        nuevo_afn.start_state = mapa_estados1[afn1.start_state]
        nuevo_afn.final_states = {mapa_estados2[e] for e in afn2.final_states}

        return nuevo_afn

    def union(self, afn1, afn2):
        """
        Unión: AFN1 | AFN2
        Crea nuevos estados inicial y final, conecta con ε-transiciones
        """
        nuevo_afn = AFN()

        # Crear nuevos estados inicial y final
        nuevo_inicio = nuevo_afn.crear_estado()
        nuevo_fin = nuevo_afn.crear_estado(is_final=True)

        # Mapeo de estados
        mapa_estados1 = {}
        mapa_estados2 = {}

        # Copiar estados de AFN1 (ninguno será final)
        for estado in afn1.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados1[estado] = nuevo_estado

        # Copiar estados de AFN2 (ninguno será final)
        for estado in afn2.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados2[estado] = nuevo_estado

        # Copiar transiciones de AFN1
        for origen in afn1.transitions:
            for simbolo in afn1.transitions[origen]:
                for destino in afn1.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados1[origen],
                        mapa_estados1[destino],
                        simbolo
                    )

        # Copiar transiciones de AFN2
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

        # Conectar finales de AFN1 y AFN2 con nuevo final
        for estado_final in afn1.final_states:
            nuevo_afn.agregar_transicion(mapa_estados1[estado_final], nuevo_fin, '#')
        for estado_final in afn2.final_states:
            nuevo_afn.agregar_transicion(mapa_estados2[estado_final], nuevo_fin, '#')

        # Configurar estados
        nuevo_afn.start_state = nuevo_inicio
        nuevo_afn.final_states = {nuevo_fin}

        return nuevo_afn

    def estrella(self, afn):
        """
        Cerradura de Kleene: AFN*
        """
        nuevo_afn = AFN()

        # Crear nuevos estados inicial y final
        nuevo_inicio = nuevo_afn.crear_estado()
        nuevo_fin = nuevo_afn.crear_estado(is_final=True)

        # Mapeo de estados
        mapa_estados = {}

        # Copiar estados del AFN original (ninguno será final)
        for estado in afn.states:
            nuevo_estado = nuevo_afn.crear_estado(is_final=False)
            mapa_estados[estado] = nuevo_estado

        # Copiar transiciones del AFN original
        for origen in afn.transitions:
            for simbolo in afn.transitions[origen]:
                for destino in afn.transitions[origen][simbolo]:
                    nuevo_afn.agregar_transicion(
                        mapa_estados[origen],
                        mapa_estados[destino],
                        simbolo
                    )

        # ε-transiciones para la estructura de Kleene
        # 1. nuevo_inicio -> inicio_original
        nuevo_afn.agregar_transicion(nuevo_inicio, mapa_estados[afn.start_state], '#')

        # 2. finales_originales -> nuevo_fin
        for estado_final in afn.final_states:
            nuevo_afn.agregar_transicion(mapa_estados[estado_final], nuevo_fin, '#')

        # 3. finales_originales -> inicio_original (bucle)
        for estado_final in afn.final_states:
            nuevo_afn.agregar_transicion(mapa_estados[estado_final], mapa_estados[afn.start_state], '#')

        # 4. nuevo_inicio -> nuevo_fin (para aceptar ε)
        nuevo_afn.agregar_transicion(nuevo_inicio, nuevo_fin, '#')

        nuevo_afn.start_state = nuevo_inicio
        nuevo_afn.final_states = {nuevo_fin}

        return nuevo_afn

    def plus(self, afn):
        """
        Uno o más: AFN+ = AFN · AFN*
        """
        afn_estrella = self.estrella(afn)
        return self.concatenacion(afn, afn_estrella)

    def opcional(self, afn):
        """
        Cero o uno: AFN? = ε | AFN
        """
        epsilon = self.crear_epsilon()
        return self.union(epsilon, afn)

    def construir_desde_postfix(self, postfix):
        """
        Construye AFN desde expresión postfix usando pila
        """
        if not postfix:
            return self.crear_epsilon()

        stack = []

        for char in postfix:
            if char == '.':
                if len(stack) < 2:
                    raise ValueError("Concatenación requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                resultado = self.concatenacion(afn1, afn2)
                stack.append(resultado)
            elif char == '|':
                if len(stack) < 2:
                    raise ValueError("Unión requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                resultado = self.union(afn1, afn2)
                stack.append(resultado)
            elif char == '*':
                if len(stack) < 1:
                    raise ValueError("Estrella requiere 1 operando")
                afn = stack.pop()
                resultado = self.estrella(afn)
                stack.append(resultado)
            elif char == '+':
                if len(stack) < 1:
                    raise ValueError("Plus requiere 1 operando")
                afn = stack.pop()
                resultado = self.plus(afn)
                stack.append(resultado)
            elif char == '?':
                if len(stack) < 1:
                    raise ValueError("Opcional requiere 1 operando")
                afn = stack.pop()
                resultado = self.opcional(afn)
                stack.append(resultado)
            elif char == '#':
                resultado = self.crear_epsilon()
                stack.append(resultado)
            else:
                resultado = self.crear_simbolo(char)
                stack.append(resultado)

        if len(stack) != 1:
            raise ValueError(f"Expresión postfix inválida: stack final tiene {len(stack)} elementos")

        return stack[0]