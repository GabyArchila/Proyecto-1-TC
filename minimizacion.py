from automata import AFD


class MinimizacionAFD:
    def __init__(self, afd):
        self.afd = afd
        self.particiones = []
        self.grupos = {}

    def minimizar(self):
        # Validar que el AFD tenga estados
        if not self.afd.states:
            return self.afd

        # Paso 1: Crear partición inicial (estados finales vs no finales)
        grupo_finales = self.afd.final_states
        grupo_no_finales = self.afd.states - grupo_finales

        # Solo agregar grupos no vacíos
        self.particiones = []
        if grupo_finales:
            self.particiones.append(grupo_finales)
        if grupo_no_finales:
            self.particiones.append(grupo_no_finales)

        print(f"Partición inicial:")
        for i, grupo in enumerate(self.particiones):
            print(f"  Grupo {i}: {sorted(grupo)}")

        # Paso 2: Refinar particiones hasta que no haya cambios
        iteracion = 0
        cambiado = True
        while cambiado:
            iteracion += 1
            print(f"\nIteración {iteracion}:")
            cambiado = False
            nuevas_particiones = []

            for i, grupo in enumerate(self.particiones):
                print(f"  Procesando grupo {i}: {sorted(grupo)}")

                if len(grupo) <= 1:
                    nuevas_particiones.append(grupo)
                    print(f"    Grupo con ≤1 elemento, no se divide")
                    continue

                subgrupos = self.dividir_grupo(grupo)
                if len(subgrupos) > 1:
                    cambiado = True
                    print(f"    Se dividió en {len(subgrupos)} subgrupos:")
                    for j, subgrupo in enumerate(subgrupos):
                        print(f"      Subgrupo {j}: {sorted(subgrupo)}")
                else:
                    print(f"    No se puede dividir más")

                nuevas_particiones.extend(subgrupos)

            self.particiones = nuevas_particiones
            print(f"  Resultado iteración {iteracion}: {len(self.particiones)} grupos")

        print(f"\nParticiones finales:")
        for i, grupo in enumerate(self.particiones):
            print(f"  Grupo {i}: {sorted(grupo)}")

        # Paso 3: Construir AFD minimizado
        return self.construir_afd_minimizado()

    def dividir_grupo(self, grupo):
        if not self.afd.alphabet:
            return [grupo]

        subgrupos = {}

        for estado in grupo:
            # Crear firma basada en las transiciones
            firma = []
            for simbolo in sorted(self.afd.alphabet):
                transicion = self.afd.transitions.get((estado, simbolo), None)

                # Encontrar a qué partición pertenece el estado destino
                grupo_destino = -1  # -1 indica que no hay transición
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

        # Debug: mostrar firmas
        print(f"      Firmas encontradas:")
        for i, (firma, estados) in enumerate(subgrupos.items()):
            print(f"        Firma {i}: {firma} -> {sorted(estados)}")

        return list(subgrupos.values())

    def construir_afd_minimizado(self):
        afd_min = AFD()
        afd_min.alphabet = self.afd.alphabet.copy()

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

        # Construir transiciones (evitar duplicados)
        transiciones_agregadas = set()
        for (origen, simbolo), destino in self.afd.transitions.items():
            grupo_origen = self.grupos[origen]
            grupo_destino = self.grupos[destino]

            transicion_key = (grupo_origen, simbolo)
            if transicion_key not in transiciones_agregadas:
                afd_min.transitions[(grupo_origen, simbolo)] = grupo_destino
                transiciones_agregadas.add(transicion_key)

        print(f"\nAFD minimizado construido:")
        print(f"  Estados: {sorted(afd_min.states)}")
        print(f"  Estado inicial: {afd_min.start_state}")
        print(f"  Estados finales: {sorted(afd_min.final_states)}")
        print(f"  Transiciones:")
        for (origen, simbolo), destino in sorted(afd_min.transitions.items()):
            print(f"    {origen} --{simbolo}--> {destino}")

        return afd_min