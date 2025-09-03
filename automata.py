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