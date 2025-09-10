import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict


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
        """Calcula la epsilon clausura de un conjunto de estados"""
        if not estados:
            return set()

        closure = set(estados)
        stack = list(estados)

        while stack:
            estado = stack.pop()
            if '#' in self.transitions[estado]:
                for next_state in self.transitions[estado]['#']:
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
            if simbolo in self.transitions[estado]:
                next_states.update(self.transitions[estado][simbolo])

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

        for i, simbolo in enumerate(cadena):
            print(f"  Procesando símbolo '{simbolo}' (posición {i}):")
            print(f"    Estados actuales: {[str(s) for s in current_states]}")

            next_states = self.mover(current_states, simbolo)
            print(f"    Estados después de mover: {[str(s) for s in next_states]}")

            if not next_states:
                print(f"    No hay transiciones válidas para '{simbolo}' - RECHAZA")
                return False

            current_states = next_states

        # Verificar si algún estado final está en el conjunto actual
        estados_finales_alcanzados = current_states & self.final_states
        acepta = len(estados_finales_alcanzados) > 0

        print(f"  Estados finales: {[str(s) for s in current_states]}")
        print(f"  Estados finales del AFN: {[str(s) for s in self.final_states]}")
        print(f"  Estados finales alcanzados: {[str(s) for s in estados_finales_alcanzados]}")
        print(f"  Resultado: {'ACEPTA' if acepta else 'RECHAZA'}")

        return acepta

    def debug_info(self):
        print("\n=== INFO AFN ===")
        print(f"Estados: {len(self.states)}")
        print(f"Estado inicial: {self.start_state}")
        print(f"Estados finales: {[str(s) for s in self.final_states]}")
        print("Transiciones:")
        for origen in self.transitions:
            for simbolo, destinos in self.transitions[origen].items():
                disp = 'ε' if simbolo == '#' else simbolo
                for d in destinos:
                    print(f"  {origen} --{disp}--> {d}")

    def visualizar(self, titulo="AFN"):
        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()

        # Nodos
        for estado in self.states:
            G.add_node(str(estado))

        # Aristas y etiquetas
        edge_labels = {}
        for origen in self.transitions:
            for simbolo in self.transitions[origen]:
                for destino in self.transitions[origen][simbolo]:
                    edge = (str(origen), str(destino))
                    display_symbol = 'ε' if simbolo == '#' else simbolo
                    if edge in edge_labels:
                        edge_labels[edge] += f",{display_symbol}"
                    else:
                        edge_labels[edge] = display_symbol
                    G.add_edge(str(origen), str(destino))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2 if len(self.states) <= 5 else 1.5,
                               iterations=100 if len(self.states) <= 5 else 50, seed=42)

        initial_nodes = [str(self.start_state)] if self.start_state else []
        final_nodes = [str(e) for e in self.final_states]
        initial_final_nodes = [n for n in final_nodes if n in initial_nodes]
        if initial_final_nodes:
            initial_nodes = [n for n in initial_nodes if n not in initial_final_nodes]
            final_nodes = [n for n in final_nodes if n not in initial_final_nodes]
        regular_nodes = [str(e) for e in self.states if
                         str(e) not in final_nodes and str(e) not in initial_nodes and str(
                             e) not in initial_final_nodes]

        if initial_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_nodes, node_color='lightgreen', node_size=1000,
                                   edgecolors='black', linewidths=2)
        if final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=final_nodes, node_color='lightcoral', node_size=1000,
                                   edgecolors='black', linewidths=2)
        if initial_final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_final_nodes, node_color='gold', node_size=1200,
                                   edgecolors='black', linewidths=3)
        if regular_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes, node_color='lightblue', node_size=900,
                                   edgecolors='black', linewidths=1)

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='black', width=1.5, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Etiquetas de aristas con ligero offset perpendicular
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            dx, dy = (x2 - x1), (y2 - y1)
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                offx, offy = -dy / length * 0.1, dx / length * 0.1
            else:
                offx, offy = 0.1, 0.1
            plt.text(label_x + offx, label_y + offy, label, fontsize=10, fontweight='bold', color='darkred',
                     ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='darkred', alpha=0.8))

        plt.title(titulo, fontsize=14, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.show()


class AFD:
    def __init__(self):
        self.states = set()
        self.transitions = {}
        self.start_state = None
        self.final_states = set()
        self.alphabet = set()

    def simular(self, cadena):
        """Simula la cadena en el AFD"""
        if not self.start_state:
            return False

        current = self.start_state
        print(f"Simulación AFD: estado inicial {current}")

        for i, simbolo in enumerate(cadena):
            print(f"  Procesando símbolo '{simbolo}' (posición {i}):")
            print(f"    Estado actual: {current}")

            if (current, simbolo) in self.transitions:
                current = self.transitions[(current, simbolo)]
                print(f"    Transición a: {current}")
            else:
                print(f"    No hay transición para '{simbolo}' - RECHAZA")
                return False

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
        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()
        for estado in self.states:
            G.add_node(str(estado))

        edge_labels = {}
        for (origen, simbolo), destino in self.transitions.items():
            edge = (str(origen), str(destino))
            edge_labels[edge] = (edge_labels.get(edge, "") + ("," if edge in edge_labels else "") + simbolo)
            G.add_edge(str(origen), str(destino))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=100, seed=42)

        initial_nodes = [str(self.start_state)] if self.start_state else []
        final_nodes = [str(e) for e in self.final_states]
        initial_final_nodes = [n for n in final_nodes if n in initial_nodes]
        if initial_final_nodes:
            initial_nodes = [n for n in initial_nodes if n not in initial_final_nodes]
            final_nodes = [n for n in final_nodes if n not in initial_final_nodes]
        regular_nodes = [str(e) for e in self.states if
                         str(e) not in final_nodes and str(e) not in initial_nodes and str(
                             e) not in initial_final_nodes]

        if initial_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_nodes, node_color='lightgreen', node_size=1000,
                                   edgecolors='black', linewidths=2)
        if final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=final_nodes, node_color='lightcoral', node_size=1000,
                                   edgecolors='black', linewidths=2)
        if initial_final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_final_nodes, node_color='gold', node_size=1200,
                                   edgecolors='black', linewidths=3)
        if regular_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes, node_color='lightblue', node_size=900,
                                   edgecolors='black', linewidths=1)

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='black', width=1.5, alpha=0.8)
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            dx, dy = (x2 - x1), (y2 - y1)
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                offx, offy = -dy / length * 0.1, dx / length * 0.1
            else:
                offx, offy = 0.1, 0.1
            plt.text(label_x + offx, label_y + offy, label, fontsize=10, fontweight='bold', color='darkred',
                     ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='darkred', alpha=0.8))

        plt.title(titulo, fontsize=14, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.show()
