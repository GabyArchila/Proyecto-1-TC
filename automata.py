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
        closure = set(estados)
        stack = list(estados)

        while stack:
            estado = stack.pop()
            for next_state in self.transitions[estado].get('#', set()):
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

    def debug_info(self):
        print(f"INFO DEL AFN:")
        print(f"   Estado inicial: {self.start_state}")
        print(f"   Estados finales: {[str(e) for e in self.final_states]}")
        print(f"   Total de estados: {len(self.states)}")
        print(f"   Transiciones:")
        for origen in self.transitions:
            for simbolo in self.transitions[origen]:
                destinos = self.transitions[origen][simbolo]
                print(f"      {origen} --{simbolo}--> {[str(d) for d in destinos]}")
        print()

    def visualizar(self, titulo="AFN"):
        G = nx.DiGraph()

        # Agregar nodos
        for estado in self.states:
            G.add_node(str(estado))

        edge_labels = {}
        # Procesar transiciones usando la misma lógica que el AFD
        for origen in self.transitions:
            for simbolo in self.transitions[origen]:
                for destino in self.transitions[origen][simbolo]:
                    key = (str(origen), str(destino))
                    # Reemplazar épsilon para mejor visualización
                    display_symbol = '#' if simbolo == '#' else simbolo
                    if key in edge_labels:
                        edge_labels[key] += f",{display_symbol}"
                    else:
                        edge_labels[key] = display_symbol
                    G.add_edge(str(origen), str(destino))

        plt.figure(figsize=(14, 10))  # Aumentar tamaño

        # Usar un layout más estable y espaciado
        pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

        # Ajustar posiciones manualmente si es necesario para mejorar visualización
        # Esto ayuda especialmente con grafos pequeños como a*
        if len(self.states) <= 4:
            # Para grafos pequeños, usar posiciones más controladas
            states_list = list(self.states)
            if len(states_list) == 3:  # Caso específico de a*
                pos[str(states_list[0])] = (0, 0)  # q0 (centro-izquierda)
                pos[str(states_list[1])] = (-1, -1)  # q1 (abajo-izquierda)
                pos[str(states_list[2])] = (1, 0)  # q2 (derecha)

        # Convertir a string
        initial = [str(self.start_state)] if self.start_state else []
        final = [str(e) for e in self.final_states]
        all_states = [str(e) for e in self.states]
        regular = [e for e in all_states if e not in final and e not in initial]

        # Dibujar nodos con colores más distintivos
        if initial:
            nx.draw_networkx_nodes(G, pos, nodelist=initial, node_color='lightgreen',
                                   node_size=1000, edgecolors='black', linewidths=2)
        if final:
            nx.draw_networkx_nodes(G, pos, nodelist=final, node_color='lightcoral',
                                   node_size=1000, edgecolors='black', linewidths=2)
        if regular:
            nx.draw_networkx_nodes(G, pos, nodelist=regular, node_color='lightblue',
                                   node_size=900, edgecolors='black', linewidths=1)

        # Dibujar aristas con mejor estilo
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=25,
                               edge_color='black', width=1.5, alpha=0.8)

        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Dibujar etiquetas manualmente para evitar problemas de renderizado
        for (node1, node2), label in edge_labels.items():
            x1, y1 = pos[node1]
            x2, y2 = pos[node2]
            # Posición de la etiqueta en el punto medio de la arista
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2

            # Desplazamiento para evitar superposición
            offset_x = 0.15 if x2 > x1 else -0.15
            offset_y = 0.15 if y2 > y1 else -0.15

            plt.annotate(label, xy=(label_x + offset_x, label_y + offset_y),
                         ha='center', va='center',
                         fontsize=12, fontweight='bold', color='darkred',
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow',
                                   edgecolor='darkred', alpha=0.9))

        plt.title(titulo, fontsize=14, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.show()

        # DEBUG para verificar
        print(f"DEBUG - Aristas creadas: {list(G.edges())}")
        print(f"DEBUG - Etiquetas: {edge_labels}")



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

        # Agregar nodos
        for estado in self.states:
            G.add_node(str(estado))

        edge_labels = {}
        for (origen, simbolo), destino in self.transitions.items():
            key = (str(origen), str(destino))  # Convertir a string
            if key in edge_labels:
                edge_labels[key] += f",{simbolo}"
            else:
                edge_labels[key] = simbolo
            G.add_edge(str(origen), str(destino))

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)

        # Convertir a string
        initial = [str(self.start_state)] if self.start_state else []
        final = [str(e) for e in self.final_states]
        all_states = [str(e) for e in self.states]
        regular = [e for e in all_states if e not in final and e not in initial]

        if initial:
            nx.draw_networkx_nodes(G, pos, nodelist=initial, node_color='green', node_size=800)
        if final:
            nx.draw_networkx_nodes(G, pos, nodelist=final, node_color='red', node_size=800)
        if regular:
            nx.draw_networkx_nodes(G, pos, nodelist=regular, node_color='lightblue', node_size=700)

        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20)
        nx.draw_networkx_labels(G, pos, font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

        plt.title(titulo)
        plt.axis('off')
        plt.show()