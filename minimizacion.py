from automata import AFD

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