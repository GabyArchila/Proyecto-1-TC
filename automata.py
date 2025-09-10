import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


class Estado:
    def __init__(self, state_id, label=None):
        self.id = state_id
        self.is_final = False
        self.transitions = {}  # {symbol: set(target_states)}
        self.epsilon_transitions = set()
        self.label = f"q{state_id}" if label is None else label

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Estado) and self.id == other.id

    def __repr__(self):
        return self.label

    def add_transition(self, symbol, target):
        if symbol == '#':  # Epsilon
            self.epsilon_transitions.add(target)
        else:
            if symbol not in self.transitions:
                self.transitions[symbol] = set()
            self.transitions[symbol].add(target)


class AFN:
    def __init__(self):
        self.states = set()
        self.start_state = None
        self.final_states = set()
        self.state_counter = 0

    def crear_estado(self, is_final=False, label=None):
        e = Estado(self.state_counter, label)
        e.is_final = is_final
        self.states.add(e)
        self.state_counter += 1
        if is_final:
            self.final_states.add(e)
        return e

    def agregar_transicion(self, from_state, to_state, symbol):
        from_state.add_transition(symbol, to_state)

    def epsilon_closure(self, estados):
        """Calcula la epsilon clausura de un conjunto de estados"""
        if not estados:
            return set()

        closure = set(estados)
        stack = list(estados)

        while stack:
            estado = stack.pop()
            for next_state in estado.epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure

    def mover(self, estados, simbolo):
        """Realiza la operación MOVE para un símbolo específico"""
        if not estados:
            return set()

        # Primero hacer epsilon closure de los estados actuales
        current_with_epsilon = self.epsilon_closure(estados)

        # Encontrar estados alcanzables con el símbolo
        next_states = set()
        for estado in current_with_epsilon:
            if simbolo in estado.transitions:
                next_states.update(estado.transitions[simbolo])

        # Hacer epsilon closure del resultado
        result = self.epsilon_closure(next_states) if next_states else set()
        return result

    def simular(self, cadena):
        """Simula la cadena en el AFN"""
        if not self.start_state:
            return False

        # Estado inicial con epsilon closure
        current_states = self.epsilon_closure({self.start_state})
        print(f"Simulación AFN: estado inicial {[str(s) for s in current_states]}")

        i = 0
        while i < len(cadena):
            char = cadena[i]
            # Manejar caracteres escapados
            if char == '\\' and i + 1 < len(cadena):
                i += 1
                char = cadena[i]  # Tomar el siguiente carácter como literal

            print(f"  Procesando símbolo '{char}' (posición {i}):")
            print(f"    Estados actuales: {[str(s) for s in current_states]}")

            next_states = set()
            for state in current_states:
                if char in state.transitions:
                    next_states.update(state.transitions[char])

            current_states = self.epsilon_closure(next_states)
            print(f"    Estados después de mover: {[str(s) for s in current_states]}")

            if not current_states:
                print(f"    No hay transiciones válidas para '{char}' - RECHAZA")
                return False
            i += 1

        # Verificar si algún estado final está en el conjunto actual
        acepta = any(state.is_final for state in current_states)
        print(f"  Estados finales alcanzados: {[str(s) for s in current_states if s.is_final]}")
        print(f"  Resultado: {'ACEPTA' if acepta else 'RECHAZA'}")

        return acepta

    def debug_info(self):
        print("\n=== INFO AFN ===")
        print(f"Estados: {len(self.states)}")
        print(f"Estado inicial: {self.start_state}")
        print(f"Estados finales: {[str(s) for s in self.final_states]}")
        print("Transiciones:")
        for estado in self.states:
            for simbolo, destinos in estado.transitions.items():
                for d in destinos:
                    print(f"  {estado} --{simbolo}--> {d}")
            for d in estado.epsilon_transitions:
                print(f"  {estado} --ε--> {d}")

    def visualizar(self, titulo="AFN"):
        G = nx.MultiDiGraph()

        # Nodos
        for estado in self.states:
            G.add_node(str(estado))

        # Aristas y etiquetas
        edge_labels = {}
        for estado in self.states:
            for simbolo, destinos in estado.transitions.items():
                for destino in destinos:
                    edge = (str(estado), str(destino))
                    if edge in edge_labels:
                        edge_labels[edge] += f",{simbolo}"
                    else:
                        edge_labels[edge] = simbolo
                    G.add_edge(str(estado), str(destino))

            for destino in estado.epsilon_transitions:
                edge = (str(estado), str(destino))
                if edge in edge_labels:
                    edge_labels[edge] += ",ε"
                else:
                    edge_labels[edge] = "ε"
                G.add_edge(str(estado), str(destino))

        # Visualización
        self._draw_automaton(G, edge_labels, titulo)

    def _draw_automaton(self, G, edge_labels, titulo):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=100, seed=42)

        # Colores de nodos
        node_colors = []
        for node in G.nodes():
            estado_obj = next((s for s in self.states if str(s) == node), None)
            if estado_obj:
                if estado_obj == self.start_state and estado_obj.is_final:
                    node_colors.append('gold')
                elif estado_obj == self.start_state:
                    node_colors.append('lightgreen')
                elif estado_obj.is_final:
                    node_colors.append('lightcoral')
                else:
                    node_colors.append('lightblue')
            else:
                node_colors.append('lightblue')

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800,
                               edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20,
                               edge_color='black', width=1.5, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

        # Etiquetas de aristas
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            plt.text((x1 + x2) / 2, (y1 + y2) / 2, label, fontsize=8,
                     ha='center', va='center',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

        plt.title(titulo, fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()


class AFD:
    def __init__(self):
        self.states = set()
        self.transitions = {}  # {(state, symbol): target_state}
        self.start_state = None
        self.final_states = set()
        self.alphabet = set()

    def simular(self, cadena):
        """Simula la cadena en el AFD"""
        if not self.start_state:
            return False

        current = self.start_state
        print(f"Simulación AFD: estado inicial {current}")

        i = 0
        while i < len(cadena):
            char = cadena[i]
            # Manejar caracteres escapados
            if char == '\\' and i + 1 < len(cadena):
                i += 1
                char = cadena[i]

            print(f"  Procesando símbolo '{char}' (posición {i}):")
            print(f"    Estado actual: {current}")

            if (current, char) in self.transitions:
                current = self.transitions[(current, char)]
                print(f"    Transición a: {current}")
            else:
                print(f"    No hay transición para '{char}' - RECHAZA")
                return False
            i += 1

        acepta = current in self.final_states
        print(f"  Estado final: {current}")
        print(f"  Es estado de aceptación: {acepta}")
        print(f"  Resultado: {'ACEPTA' if acepta else 'RECHAZA'}")

        return acepta

    def debug_info(self):
        print("\n=== INFO AFD ===")
        print(f"Estados: {sorted(self.states)}")
        print(f"Estado inicial: {self.start_state}")
        print(f"Estados finales: {sorted(self.final_states)}")
        print(f"Alfabeto: {sorted(self.alphabet)}")
        print("Transiciones:")
        for (origen, simbolo), destino in sorted(self.transitions.items()):
            print(f"  {origen} --{simbolo}--> {destino}")

    def visualizar(self, titulo="AFD"):
        G = nx.DiGraph()
        for estado in self.states:
            G.add_node(str(estado))

        edge_labels = {}
        for (origen, simbolo), destino in self.transitions.items():
            edge = (str(origen), str(destino))
            if edge in edge_labels:
                edge_labels[edge] += f",{simbolo}"
            else:
                edge_labels[edge] = simbolo
            G.add_edge(str(origen), str(destino))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=100, seed=42)

        # Colores de nodos
        node_colors = []
        for node in G.nodes():
            if node == str(self.start_state) and node in [str(f) for f in self.final_states]:
                node_colors.append('gold')
            elif node == str(self.start_state):
                node_colors.append('lightgreen')
            elif node in [str(f) for f in self.final_states]:
                node_colors.append('lightcoral')
            else:
                node_colors.append('lightblue')

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=800,
                               edgecolors='black', linewidths=2)
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20,
                               edge_color='black', width=1.5, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')

        # Etiquetas de aristas
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            plt.text((x1 + x2) / 2, (y1 + y2) / 2, label, fontsize=8,
                     ha='center', va='center',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

        plt.title(titulo, fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()