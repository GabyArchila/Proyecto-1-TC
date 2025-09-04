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
            # Solo procesar transiciones epsilon
            if '#' in self.transitions[estado]:
                for next_state in self.transitions[estado]['#']:
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
            next_states = self.mover(current_states, simbolo)
            if not next_states:
                return False
            current_states = next_states

        return any(estado.is_final for estado in current_states)

    def debug_info(self):
        print(f"INFO DEL AFN:")
        print(f"   Estado inicial: {self.start_state}")
        print(f"   Estados finales: {[str(e) for e in self.final_states]}")
        print(f"   Total de estados: {len(self.states)}")

        # Verificar consistencia
        estados_en_transiciones = set()
        for origen in self.transitions:
            estados_en_transiciones.add(origen)
            for simbolo in self.transitions[origen]:
                for destino in self.transitions[origen][simbolo]:
                    estados_en_transiciones.add(destino)

        estados_desconectados = self.states - estados_en_transiciones
        if estados_desconectados:
            print(f"   ⚠️  Estados desconectados: {[str(e) for e in estados_desconectados]}")

        print(f"   Transiciones ({len(self.transitions)} estados con transiciones):")
        if not self.transitions:
            print("      ⚠️  No hay transiciones definidas")
        else:
            for origen in sorted(self.transitions.keys(), key=lambda x: x.id):
                for simbolo in sorted(self.transitions[origen].keys()):
                    destinos = self.transitions[origen][simbolo]
                    for destino in sorted(destinos, key=lambda x: x.id):
                        display_symbol = 'ε' if simbolo == '#' else simbolo
                        print(f"      {origen} --{display_symbol}--> {destino}")
        print()

    def visualizar(self, titulo="AFN"):
        G = nx.DiGraph()

        # Agregar nodos
        for estado in self.states:
            G.add_node(str(estado))

        # Agregar aristas y crear etiquetas
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

        # Configurar la figura
        plt.figure(figsize=(12, 8))

        # Crear layout mejorado
        if len(self.states) <= 5:
            pos = nx.spring_layout(G, k=2, iterations=100, seed=42)
        else:
            pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)

        # Clasificar nodos por tipo
        initial_nodes = [str(self.start_state)] if self.start_state else []
        final_nodes = [str(estado) for estado in self.final_states]
        regular_nodes = [str(estado) for estado in self.states
                         if estado not in self.final_states and estado != self.start_state]

        # Nodos que son iniciales Y finales
        initial_final_nodes = [str(estado) for estado in self.final_states
                               if estado == self.start_state]

        # Ajustar listas para evitar duplicados
        if initial_final_nodes:
            initial_nodes = [n for n in initial_nodes if n not in initial_final_nodes]
            final_nodes = [n for n in final_nodes if n not in initial_final_nodes]

        # Dibujar nodos con diferentes estilos
        if initial_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_nodes,
                                   node_color='lightgreen', node_size=1000,
                                   edgecolors='black', linewidths=2)

        if final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=final_nodes,
                                   node_color='lightcoral', node_size=1000,
                                   edgecolors='black', linewidths=2)

        if initial_final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_final_nodes,
                                   node_color='gold', node_size=1200,
                                   edgecolors='black', linewidths=3)

        if regular_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes,
                                   node_color='lightblue', node_size=900,
                                   edgecolors='black', linewidths=1)

        # Dibujar aristas
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20,
                               edge_color='black', width=1.5, alpha=0.8)

        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Dibujar etiquetas de aristas mejoradas
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]

            # Calcular posición de la etiqueta
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2

            # Offset para evitar superposición con la arista
            dx = x2 - x1
            dy = y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5

            if length > 0:
                # Perpendicular a la arista
                offset_x = -dy / length * 0.1
                offset_y = dx / length * 0.1
            else:
                offset_x, offset_y = 0.1, 0.1

            plt.text(label_x + offset_x, label_y + offset_y, label,
                     fontsize=10, fontweight='bold', color='darkred',
                     ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                               edgecolor='darkred', alpha=0.8))

        plt.title(titulo, fontsize=14, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
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

    def debug_info(self):
        print(f"INFO DEL AFD:")
        print(f"   Estado inicial: {self.start_state}")
        print(f"   Estados finales: {list(self.final_states)}")
        print(f"   Total de estados: {len(self.states)}")
        print(f"   Alfabeto: {list(self.alphabet)}")
        print(f"   Transiciones:")
        for (origen, simbolo), destino in self.transitions.items():
            print(f"      {origen} --{simbolo}--> {destino}")
        print()

    def visualizar(self, titulo="AFD"):
        G = nx.DiGraph()

        # Agregar nodos
        for estado in self.states:
            G.add_node(str(estado))

        # Procesar transiciones y crear etiquetas
        edge_labels = {}
        for (origen, simbolo), destino in self.transitions.items():
            edge = (str(origen), str(destino))

            if edge in edge_labels:
                edge_labels[edge] += f",{simbolo}"
            else:
                edge_labels[edge] = simbolo

            G.add_edge(str(origen), str(destino))

        # Configurar la figura
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=2, iterations=100, seed=42)

        # Clasificar nodos
        initial_nodes = [str(self.start_state)] if self.start_state else []
        final_nodes = [str(estado) for estado in self.final_states]
        regular_nodes = [str(estado) for estado in self.states
                         if estado not in self.final_states and str(estado) not in initial_nodes]

        # Nodos que son iniciales Y finales
        initial_final_nodes = []
        if self.start_state and str(self.start_state) in final_nodes:
            initial_final_nodes = [str(self.start_state)]
            initial_nodes = []
            final_nodes = [n for n in final_nodes if n != str(self.start_state)]

        # Dibujar nodos
        if initial_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_nodes,
                                   node_color='lightgreen', node_size=1000,
                                   edgecolors='black', linewidths=2)

        if final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=final_nodes,
                                   node_color='lightcoral', node_size=1000,
                                   edgecolors='black', linewidths=2)

        if initial_final_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=initial_final_nodes,
                                   node_color='gold', node_size=1200,
                                   edgecolors='black', linewidths=3)

        if regular_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=regular_nodes,
                                   node_color='lightblue', node_size=900,
                                   edgecolors='black', linewidths=1)

        # Dibujar aristas
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20,
                               edge_color='black', width=1.5, alpha=0.8)

        # Dibujar etiquetas de nodos
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

        # Dibujar etiquetas de aristas
        for edge, label in edge_labels.items():
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]

            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2

            # Offset perpendicular
            dx = x2 - x1
            dy = y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5

            if length > 0:
                offset_x = -dy / length * 0.1
                offset_y = dx / length * 0.1
            else:
                offset_x, offset_y = 0.1, 0.1

            plt.text(label_x + offset_x, label_y + offset_y, label,
                     fontsize=10, fontweight='bold', color='darkred',
                     ha='center', va='center',
                     bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                               edgecolor='darkred', alpha=0.8))

        plt.title(titulo, fontsize=14, fontweight='bold', pad=20)
        plt.axis('off')
        plt.tight_layout()
        plt.show()