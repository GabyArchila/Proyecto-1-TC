import sys
import re
from collections import defaultdict, deque
import networkx as nx
import matplotlib.pyplot as plt

# ==================== CONVERSIÓN INFIX A POSTFIX ====================

# Precedencia de operadores
PRECEDENCE = {
    '|': 2,  # Unión
    '.': 3,  # Concatenación
    '?': 4,  # Cero o uno
    '*': 4,  # Cero o más
    '+': 4,  # Uno o más
    '^': 5  # Potencia
}


# Verifica la necesidad de un operador de concatenación
def needs_concat(c1, c2):
    if c1 == '(' or c2 == ')':
        return False
    if c1 in ['|']:
        return False
    if c2 in ['|', '*', '+', '?']:
        return False
    if c1 in ['*', '+', '?'] and c2 not in ['(']:
        return True
    if c1 not in PRECEDENCE and c2 not in PRECEDENCE:
        return True
    if c1 not in PRECEDENCE and c2 == '(':
        return True
    if c1 == ')' and c2 not in PRECEDENCE:
        return True
    if c1 == ')' and c2 == '(':
        return True
    return False


# Inserta operadores de concatenación explícitos
def format_regex(regex):
    formatted = []
    i = 0
    while i < len(regex):
        c = regex[i]

        # Manejar caracteres escapados
        if c == '\\' and i + 1 < len(regex):
            formatted.append(c + regex[i + 1])
            i += 2
            continue

        # Manejar épsilon
        if c == 'ε':
            formatted.append('ε')
            i += 1
            continue

        formatted.append(c)

        # Verificar si necesita concatenación con el siguiente caracter
        if i + 1 < len(regex):
            next_c = regex[i + 1]
            # No agregar concatenación si el siguiente es un caracter escapado
            if next_c == '\\' and i + 2 < len(regex):
                if needs_concat(c, regex[i + 1:i + 3]):
                    formatted.append('.')
            elif needs_concat(c, next_c):
                formatted.append('.')

        i += 1

    return ''.join(formatted)


# Convierte expresión de infix a postfix
def infix_to_postfix(regex):
    output = []
    operator_stack = []
    formatted_re = format_regex(regex)

    i = 0
    while i < len(formatted_re):
        c = formatted_re[i]

        # Manejar caracteres escapados
        if c == '\\':
            if i + 1 < len(formatted_re):
                output.append(c + formatted_re[i + 1])
                i += 2
            else:
                output.append(c)
                i += 1
            continue

        # Manejar épsilon
        if c == 'ε':
            output.append(c)
            i += 1
            continue

        if c == '(':
            operator_stack.append(c)
        elif c == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Remover el '('
        elif c in PRECEDENCE:
            while (operator_stack and operator_stack[-1] != '(' and
                   PRECEDENCE.get(operator_stack[-1], 0) >= PRECEDENCE[c]):
                output.append(operator_stack.pop())
            operator_stack.append(c)
        else:
            output.append(c)
        i += 1

    while operator_stack:
        output.append(operator_stack.pop())

    return ''.join(output)


# ==================== CLASES PARA AUTÓMATAS ====================

class Estado:
    def __init__(self, state_id):
        self.id = state_id
        self.is_final = False

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Estado) and self.id == other.id

    def __repr__(self):
        return f"q{self.id}"


class AFN:
    def __init__(self):
        self.states = set()
        self.transitions = defaultdict(lambda: defaultdict(set))
        self.start_state = None
        self.final_states = set()
        self.state_counter = 0

    def crear_estado(self, is_final=False):
        e = Estado(self.state_counter)
        e.is_final = is_final
        self.states.add(e)
        self.state_counter += 1
        if is_final:
            self.final_states.add(e)
        return e

    def agregar_transicion(self, from_state, to_state, symbol):
        self.transitions[from_state][symbol].add(to_state)

    def epsilon_closure(self, estados):
        closure = set(estados)
        stack = list(estados)

        while stack:
            estado = stack.pop()
            for next_state in self.transitions[estado].get('ε', set()):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def mover(self, estados, simbolo):
        next_states = set()
        for estado in estados:
            if simbolo in self.transitions[estado]:
                next_states.update(self.transitions[estado][simbolo])
        return self.epsilon_closure(next_states)

    def simular(self, cadena):
        current_states = self.epsilon_closure({self.start_state})

        for simbolo in cadena:
            next_states = set()
            for estado in current_states:
                if simbolo in self.transitions[estado]:
                    next_states.update(self.transitions[estado][simbolo])

            if not next_states:
                return False

            current_states = self.epsilon_closure(next_states)

        return any(estado.is_final for estado in current_states)

    def visualizar(self, titulo="AFN"):
        G = nx.DiGraph()
        for estado in self.states:
            G.add_node(estado.id)

        edge_labels = {}
        for origen in self.transitions:
            for simbolo in self.transitions[origen]:
                for destino in self.transitions[origen][simbolo]:
                    key = (origen.id, destino.id)
                    if key in edge_labels:
                        edge_labels[key] += f",{simbolo}"
                    else:
                        edge_labels[key] = simbolo
                    G.add_edge(origen.id, destino.id)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)

        initial = [self.start_state.id] if self.start_state else []
        final = [e.id for e in self.final_states]
        regular = [e.id for e in self.states if e.id not in final and e.id not in initial]

        if initial:
            nx.draw_networkx_nodes(G, pos, nodelist=initial, node_color='green', node_size=800)
        if final:
            nx.draw_networkx_nodes(G, pos, nodelist=final, node_color='red', node_size=800)
        if regular:
            nx.draw_networkx_nodes(G, pos, nodelist=regular, node_color='lightblue', node_size=700)

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(G, pos, {e.id: f"q{e.id}" for e in self.states}, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        plt.title(titulo)
        plt.axis('off')
        plt.show()


class AFD:
    def __init__(self):
        self.states = set()
        self.transitions = {}  # Diccionario: (state, symbol) -> state
        self.start_state = None
        self.final_states = set()
        self.alphabet = set()

    def simular(self, cadena):
        current = self.start_state
        for simbolo in cadena:
            if (current, simbolo) in self.transitions:
                current = self.transitions[(current, simbolo)]
            else:
                return False
        return current in self.final_states

    def visualizar(self, titulo="AFD"):
        G = nx.DiGraph()
        for estado in self.states:
            G.add_node(estado)

        edge_labels = {}
        for (origen, simbolo), destino in self.transitions.items():
            key = (origen, destino)
            if key in edge_labels:
                edge_labels[key] += f",{simbolo}"
            else:
                edge_labels[key] = simbolo
            G.add_edge(origen, destino)

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)

        initial = [self.start_state] if self.start_state else []
        final = list(self.final_states)
        regular = [e for e in self.states if e not in final and e not in initial]

        if initial:
            nx.draw_networkx_nodes(G, pos, nodelist=initial, node_color='green', node_size=800)
        if final:
            nx.draw_networkx_nodes(G, pos, nodelist=final, node_color='red', node_size=800)
        if regular:
            nx.draw_networkx_nodes(G, pos, nodelist=regular, node_color='lightblue', node_size=700)

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(G, pos, {e: f"{e}" for e in self.states}, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        plt.title(titulo)
        plt.axis('off')
        plt.show()


# ==================== ALGORITMO DE THOMPSON ====================

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


# ==================== ALGORITMO DE SUBCONJUNTOS ====================

class Subconjuntos:
    def __init__(self, afn):
        self.afn = afn
        self.afd = AFD()
        self.estados_afd = {}  # Mapeo de conjuntos de estados AFN a estados AFD

    def convertir(self):
        # Obtener el alfabeto (excluyendo épsilon)
        alphabet = set()
        for estado in self.afn.transitions:
            for simbolo in self.afn.transitions[estado]:
                if simbolo != 'ε':
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

            # Si ya procesamos este conjunto, saltar
            if tuple(sorted(e.id for e in conjunto_actual)) in procesados:
                continue

            procesados.add(tuple(sorted(e.id for e in conjunto_actual)))

            # Marcar como final si contiene algún estado final del AFN
            if any(estado.is_final for estado in conjunto_actual):
                self.afd.final_states.add(estado_actual)

            # Para cada símbolo en el alfabeto
            for simbolo in alphabet:
                siguiente_conjunto = self.afn.mover(conjunto_actual, simbolo)

                if siguiente_conjunto:
                    siguiente_estado = self.obtener_estado_afd(siguiente_conjunto)
                    self.afd.transitions[(estado_actual, simbolo)] = siguiente_estado

                    # Agregar a la cola si no ha sido procesado
                    siguiente_clave = tuple(sorted(e.id for e in siguiente_conjunto))
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


# ==================== MINIMIZACIÓN DE AFD ====================

class MinimizacionAFD:
    def __init__(self, afd):
        self.afd = afd
        self.particiones = []
        self.grupos = {}

    def minimizar(self):
        # Paso 1: Crear partición inicial (estados finales vs no finales)
        grupo_finales = self.afd.final_states
        grupo_no_finales = self.afd.states - grupo_finales

        # Solo agregar grupos no vacíos
        self.particiones = []
        if grupo_finales:
            self.particiones.append(grupo_finales)
        if grupo_no_finales:
            self.particiones.append(grupo_no_finales)

        # Paso 2: Refinar particiones hasta que no haya cambios
        cambiado = True
        while cambiado:
            cambiado = False
            nuevas_particiones = []

            for grupo in self.particiones:
                if len(grupo) <= 1:
                    nuevas_particiones.append(grupo)
                    continue

                subgrupos = self.dividir_grupo(grupo)
                if len(subgrupos) > 1:
                    cambiado = True
                nuevas_particiones.extend(subgrupos)

            self.particiones = nuevas_particiones

        # Paso 3: Construir AFD minimizado
        return self.construir_afd_minimizado()

    def dividir_grupo(self, grupo):
        subgrupos = {}

        for estado in grupo:
            firma = []
            for simbolo in sorted(self.afd.alphabet):
                transicion = self.afd.transitions.get((estado, simbolo), None)

                # Encontrar a qué partición pertenece el estado destino
                grupo_destino = -1
                if transicion is not None:
                    for i, particion in enumerate(self.particiones):
                        if transicion in particion:
                            grupo_destino = i
                            break

                firma.append((simbolo, grupo_destino))

            firma_tupla = tuple(firma)
            if firma_tupla not in subgrupos:
                subgrupos[firma_tupla] = set()
            subgrupos[firma_tupla].add(estado)

        return list(subgrupos.values())

    def construir_afd_minimizado(self):
        afd_min = AFD()
        afd_min.alphabet = self.afd.alphabet

        # Mapear cada estado a su grupo
        for i, grupo in enumerate(self.particiones):
            for estado in grupo:
                self.grupos[estado] = f"M{i}"

        # Agregar estados al AFD minimizado
        for i in range(len(self.particiones)):
            estado_grupo = f"M{i}"
            afd_min.states.add(estado_grupo)

            # Verificar si es estado final
            if any(estado in self.afd.final_states for estado in self.particiones[i]):
                afd_min.final_states.add(estado_grupo)

            # Verificar si es estado inicial
            if self.afd.start_state in self.particiones[i]:
                afd_min.start_state = estado_grupo

        # Construir transiciones
        for (origen, simbolo), destino in self.afd.transitions.items():
            grupo_origen = self.grupos[origen]
            grupo_destino = self.grupos[destino]
            afd_min.transitions[(grupo_origen, simbolo)] = grupo_destino

        return afd_min


# ==================== FUNCIÓN PRINCIPAL ====================

def procesar_expresion(regex, cadena):
    print(f"\n{'=' * 60}")
    print(f"Procesando expresión: {regex}")
    print(f"Cadena a evaluar: '{cadena}'")
    print(f"{'=' * 60}")

    try:
        # Validación inicial
        if not regex.strip():
            print("❌ Error: Expresión regular vacía")
            return False, False, False

        # Paso 1: Convertir a postfix
        print("\n1. CONVERSIÓN INFIX A POSTFIX")
        print(f"Expresión original: {regex}")
        formatted = format_regex(regex)
        print(f"Expresión formateada: {formatted}")
        postfix = infix_to_postfix(regex)
        print(f"Expresión postfix: {postfix}")

        if not postfix:
            print("❌ Error: No se pudo convertir a postfix")
            return False, False, False

        # Paso 2: Construir AFN con Thompson
        print("\n2. CONSTRUCCIÓN DE AFN (THOMPSON)")
        thompson = Thompson()
        afn = thompson.construir_desde_postfix(postfix)
        print("✅ AFN construido exitosamente")

        # Visualizar AFN
        print("📊 Visualizando AFN...")
        afn.visualizar(f"AFN para: {regex}")

        # Simular cadena en AFN
        resultado_afn = afn.simular(cadena)
        print(f"🔍 Resultado simulación AFN: {'SÍ' if resultado_afn else 'NO'}")

        # Paso 3: Convertir AFN a AFD (subconjuntos)
        print("\n3. CONVERSIÓN AFN A AFD (SUBCONJUNTOS)")
        subconjuntos = Subconjuntos(afn)
        afd = subconjuntos.convertir()
        print("✅ AFD construido exitosamente")

        # Visualizar AFD
        print("📊 Visualizando AFD...")
        afd.visualizar(f"AFD para: {regex}")

        # Simular cadena en AFD
        resultado_afd = afd.simular(cadena)
        print(f"🔍 Resultado simulación AFD: {'SÍ' if resultado_afd else 'NO'}")

        # Paso 4: Minimizar AFD
        print("\n4. MINIMIZACIÓN DE AFD")
        minimizador = MinimizacionAFD(afd)
        afd_min = minimizador.minimizar()
        print("✅ AFD minimizado construido exitosamente")

        # Visualizar AFD minimizado
        print("📊 Visualizando AFD minimizado...")
        afd_min.visualizar(f"AFD Minimizado para: {regex}")

        # Simular cadena en AFD minimizado
        resultado_afd_min = afd_min.simular(cadena)
        print(f"🔍 Resultado simulación AFD minimizado: {'SÍ' if resultado_afd_min else 'NO'}")

        # Resumen final
        print(f"\n{'=' * 60}")
        print("📋 RESUMEN FINAL")
        print(f"{'=' * 60}")
        print(f"Expresión regular: {regex}")
        print(f"Cadena evaluada: '{cadena}'")
        print(f"AFN: {'ACEPTA' if resultado_afn else 'RECHAZA'}")
        print(f"AFD: {'ACEPTA' if resultado_afd else 'RECHAZA'}")
        print(f"AFD Minimizado: {'ACEPTA' if resultado_afd_min else 'RECHAZA'}")

        # Verificar consistencia
        if resultado_afn == resultado_afd == resultado_afd_min:
            print("✅ Todos los autómatas son consistentes")
        else:
            print("⚠️  ADVERTENCIA: Los autómatas no son consistentes")

        return resultado_afn, resultado_afd, resultado_afd_min

    except Exception as e:
        print(f"❌ Error procesando expresión: {e}")
        import traceback
        print("📍 Detalles del error:")
        traceback.print_exc()
        return False, False, False


def crear_archivo_ejemplo():
    """Crea un archivo de ejemplo para pruebas"""
    contenido_ejemplo = """# Archivo de pruebas para el Analizador Léxico
# Formato: expresion_regular,cadena_a_evaluar
# Líneas que empiecen con # son comentarios

# ========== EJEMPLOS BÁSICOS ==========
# Símbolos individuales
a,a
a,b
b,b

# ========== OPERADOR UNIÓN (|) ==========
(a|b),a
(a|b),b
(a|b),c

# ========== CONCATENACIÓN ==========
ab,ab
ab,a
ab,ba
abc,abc

# ========== ESTRELLA DE KLEENE (*) ==========
a*,
a*,a
a*,aa
a*,aaa
a*,b

# ========== COMBINACIONES COMPLEJAS ==========
# Ejemplo del PDF: (b|b)*abb(a|b)*
(a|b)*abb,abb
(a|b)*abb,aabb
(a|b)*abb,babbaaaa
(b|b)*abb(a|b)*,babbaaaa

# Más ejemplos complejos
(a*b*)*,ab
(a*b*)*,aabb
(a*b*)*,ba

# Expresiones con paréntesis anidados
((a|b)*a)*,a
((a|b)*a)*,ba
((a|b)*a)*,aba

# ========== CASOS ESPECIALES ==========
# Épsilon (cadena vacía)
ε,

# Expresiones que no aceptan nada específico
a,
b*a,a
b*a,ba
b*a,bba"""

    try:
        with open('pruebas.txt', 'w', encoding='utf-8') as f:
            f.write(contenido_ejemplo)
        print("✅ Archivo 'pruebas.txt' creado exitosamente")
        print("Ejecute: python analizador_lexico.py pruebas.txt")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo ejemplo: {e}")
        return False


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--crear-ejemplo':
            crear_archivo_ejemplo()
            return

        # Leer desde archivo
        archivo = sys.argv[1]
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                print(f"📖 Leyendo archivo: {archivo}")
                print("=" * 60)

                linea_num = 0
                procesadas = 0

                for linea in f:
                    linea_num += 1
                    linea = linea.strip()

                    # Saltar líneas vacías y comentarios
                    if not linea or linea.startswith('#'):
                        continue

                    # Formato: "regex,cadena"
                    if ',' in linea:
                        partes = linea.split(',', 1)
                        if len(partes) == 2:
                            regex = partes[0].strip()
                            cadena = partes[1].strip()
                            print(f"\n📍 Línea {linea_num}: {regex} -> {cadena}")
                            procesar_expresion(regex, cadena)
                            procesadas += 1
                        else:
                            print(f"⚠️  Línea {linea_num}: Formato incorrecto: {linea}")

                    else:
                        print(f"⚠️  Línea {linea_num}: Falta cadena para evaluar: {linea}")

                print(f"\n✅ Procesamiento completado: {procesadas} expresiones procesadas")

        except FileNotFoundError:
            print(f"❌ Error: Archivo no encontrado: {archivo}")
            print("Uso: python analizador_lexico.py <archivo.txt>")
            print("O ejecute: python analizador_lexico.py --crear-ejemplo")
        except UnicodeDecodeError:
            print(f"❌ Error: No se pudo leer el archivo {archivo}. Verifica la codificación.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

    else:
        # Modo interactivo o ejemplo por defecto
        print("🚀 ANALIZADOR LÉXICO - PROYECTO 1")
        print("=" * 50)
        print("Modo interactivo activado")
        print("Comandos disponibles:")
        print("- Ingrese una expresión regular")
        print("- 'ejemplo' para ejecutar casos de prueba")
        print("- 'quit' para salir")
        print("=" * 50)

        while True:
            try:
                regex = input("\n📝 Expresión regular (o 'ejemplo'/'quit'): ").strip()

                if regex.lower() in ['quit', 'exit', 'salir', 'q']:
                    print("👋 ¡Hasta luego!")
                    break

                if regex.lower() == 'ejemplo':
                    # Ejecutar casos de ejemplo
                    ejemplos = [
                        ("(a|b)*abb", "abb"),
                        ("(a|b)*abb", "babbaaaa"),
                        ("a*", "aaa"),
                        ("(a|b)", "a"),
                        ("(a|b)", "c"),
                        ("ab", "ab"),
                        ("a*b*", "aabb")
                    ]

                    print("\n🎯 Ejecutando casos de ejemplo...")
                    for i, (r, c) in enumerate(ejemplos, 1):
                        print(f"\n--- Ejemplo {i}/{len(ejemplos)} ---")
                        procesar_expresion(r, c)

                    continue

                if not regex:
                    print("⚠️  Expresión vacía, intente de nuevo.")
                    continue

                cadena = input("📝 Cadena a evaluar: ").strip()
                procesar_expresion(regex, cadena)

            except (KeyboardInterrupt, EOFError):
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()