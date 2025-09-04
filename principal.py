import sys
import os
from preprocesamiento import infix_to_postfix, format_regex
from thompson import Thompson
from subconjuntos import Subconjuntos
from minimizacion import MinimizacionAFD


def debug_construccion_paso_a_paso(postfix):
    """
    Función de depuración para ver la construcción paso a paso del AFN
    """
    print("\nDEBUG CONSTRUCCIÓN PASO A PASO:")
    thompson = Thompson()
    stack = []

    for i, char in enumerate(postfix):
        print(f"\n  Paso {i}: Carácter '{char}'")
        print(f"     Stack antes: {[str(afn.start_state) if hasattr(afn, 'start_state') else afn for afn in stack]}")

        try:
            if char == '.':
                if len(stack) < 2:
                    raise ValueError(f"Concatenación requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                result = thompson.concatenacion(afn1, afn2)
                stack.append(result)
                print(f"     Concatenación: {afn1.start_state} + {afn2.start_state} -> {result.start_state}")

            elif char == '|':
                if len(stack) < 2:
                    raise ValueError(f"Unión requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                result = thompson.union(afn1, afn2)
                stack.append(result)
                print(f"     Unión: {afn1.start_state} | {afn2.start_state} -> {result.start_state}")

            elif char == '*':
                if len(stack) < 1:
                    raise ValueError(f"Estrella requiere 1 operando")
                afn = stack.pop()
                result = thompson.estrella(afn)
                stack.append(result)
                print(f"     Kleene: {afn.start_state}* -> {result.start_state}")

            elif char == '+':
                if len(stack) < 1:
                    raise ValueError(f"Plus requiere 1 operando")
                afn = stack.pop()
                kleene = thompson.estrella(afn)
                result = thompson.concatenacion(afn, kleene)
                stack.append(result)
                print(f"     Plus: {afn.start_state}+ -> {result.start_state}")

            elif char == '?':
                if len(stack) < 1:
                    raise ValueError(f"Interrogación requiere 1 operando")
                afn = stack.pop()
                epsilon = thompson.crear_epsilon()
                result = thompson.union(epsilon, afn)
                stack.append(result)
                print(f"     Opcional: {afn.start_state}? -> {result.start_state}")

            elif char == '#':
                result = thompson.crear_epsilon()
                stack.append(result)
                print(f"     Épsilon: -> {result.start_state}")

            else:
                result = thompson.crear_simbolo(char)
                stack.append(result)
                print(f"     Símbolo '{char}': -> {result.start_state}")

            print(f"     Stack después: {[str(afn.start_state) for afn in stack]}")

        except Exception as e:
            print(f"     Error en paso {i}: {e}")
            raise

    return stack[0] if stack else None


def procesar_expresion(regex, cadena):
    print(f"\n{'=' * 60}")
    print(f"Procesando expresión: {regex}")
    print(f"Cadena a evaluar: '{cadena}'")
    print(f"{'=' * 60}")

    try:
        # Validación inicial
        if not regex.strip():
            print("Error: Expresión regular vacía")
            return False

        # Paso 1: Convertir a postfix
        print("\n1. CONVERSIÓN INFIX A POSTFIX")
        print(f"Expresión original: {regex}")
        formatted = format_regex(regex)
        print(f"Expresión formateada: {formatted}")
        postfix = infix_to_postfix(regex)
        print(f"Expresión postfix: {postfix}")

        if not postfix:
            print("Error: No se pudo convertir a postfix")
            return False

        # Paso 2: Construir AFN con Thompson
        print("\n2. CONSTRUCCIÓN DE AFN (THOMPSON)")

        # Depuración paso a paso para expresiones complejas
        if len(postfix) > 3:  # Solo para expresiones complejas
            afn = debug_construccion_paso_a_paso(postfix)
        else:
            thompson = Thompson()
            afn = thompson.construir_desde_postfix(postfix)

        if not afn:
            print("Error: No se pudo construir el AFN")
            return False

        print("AFN construido exitosamente")

        # DEBUG: Mostrar información DETALLADA del AFN (AGREGA ESTO)
        print("\nDEBUG DETALLADO - TRANSICIONES DEL AFN:")
        print("=" * 50)
        for origen in afn.transitions:
            for simbolo in afn.transitions[origen]:
                destinos = afn.transitions[origen][simbolo]
                print(f"   {origen} --{simbolo}--> {[str(d) for d in destinos]}")
        print("=" * 50)

        # DEBUG: Verificar transiciones de símbolos (no solo épsilon)
        simbolos_presentes = set()
        for origen in afn.transitions:
            for simbolo in afn.transitions[origen]:
                if simbolo != '#':
                    simbolos_presentes.add(simbolo)

        print(f"Símbolos no-épsilon encontrados: {simbolos_presentes}")
        print()

        # DEBUG: Mostrar información del AFN
        afn.debug_info()

        # Visualizar AFN
        print("Visualizando AFN...")
        afn.visualizar(f"AFN para: {regex}")

        # Simular cadena en AFN
        resultado_afn = afn.simular(cadena)
        print(f"Resultado simulación AFN: {'SÍ' if resultado_afn else 'NO'}")

        # Paso 3: Convertir AFN a AFD (subconjuntos)
        print("\n3. CONVERSIÓN AFN A AFD (SUBCONJUNTOS)")
        subconjuntos = Subconjuntos(afn)
        afd = subconjuntos.convertir()
        print("FD construido exitosamente")

        # Visualizar AFD
        print("Visualizando AFD...")
        afd.visualizar(f"AFD para: {regex}")

        # Simular cadena en AFD
        resultado_afd = afd.simular(cadena)
        print(f"Resultado simulación AFD: {'SÍ' if resultado_afd else 'NO'}")

        # Paso 4: Minimizar AFD
        print("\n4. MINIMIZACIÓN DE AFD")
        minimizador = MinimizacionAFD(afd)
        afd_min = minimizador.minimizar()
        print("AFD minimizado construido exitosamente")

        # Visualizar AFD minimizado
        print("Visualizando AFD minimizado...")
        afd_min.visualizar(f"AFD Minimizado para: {regex}")

        # Simular cadena en AFD minimizado
        resultado_afd_min = afd_min.simular(cadena)
        print(f"Resultado simulación AFD minimizado: {'SÍ' if resultado_afd_min else 'NO'}")

        # Resumen final
        print(f"\n{'=' * 60}")
        print("RESUMEN FINAL")
        print(f"{'=' * 60}")
        print(f"Expresión regular: {regex}")
        print(f"Cadena evaluada: '{cadena}'")
        print(f"AFN: {'ACEPTA' if resultado_afn else 'RECHAZA'}")
        print(f"AFD: {'ACEPTA' if resultado_afd else 'RECHAZA'}")
        print(f"AFD Minimizado: {'ACEPTA' if resultado_afd_min else 'RECHAZA'}")

        # Verificar consistencia
        if resultado_afn == resultado_afd == resultado_afd_min:
            print("Todos los autómatas son consistentes")
            return True
        else:
            print("ADVERTENCIA: Los autómatas no son consistentes")
            return False

    except Exception as e:
        print(f"Error procesando expresión: {e}")
        import traceback
        print("Detalles del error:")
        traceback.print_exc()
        return False


def procesar_archivo(nombre_archivo):
    """
    Procesa un archivo con múltiples expresiones regulares y cadenas
    Formato esperado: expresión_regular,cadena_a_evaluar
    """
    if not os.path.exists(nombre_archivo):
        print(f"Error: El archivo '{nombre_archivo}' no existe")
        return

    print(f"\nPROCESANDO ARCHIVO: {nombre_archivo}")
    print("=" * 60)

    resultados = []
    linea_num = 0

    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea_num += 1
            linea = linea.strip()

            # Saltar líneas vacías o comentarios
            if not linea or linea.startswith('#'):
                continue

            # Separar expresión regular y cadena (formato: regex,cadena)
            if ',' in linea:
                partes = linea.split(',', 1)
                regex = partes[0].strip()
                cadena = partes[1].strip()

                print(f"\nLínea {linea_num}: {regex} -> '{cadena}'")
                print("-" * 40)

                exito = procesar_expresion(regex, cadena)
                resultados.append((linea_num, regex, cadena, exito))

            else:
                print(f"Error en línea {linea_num}: Formato incorrecto (esperado: regex,cadena)")
                resultados.append((linea_num, linea, "", False))

    # Resumen del procesamiento del archivo
    print(f"\n{'=' * 60}")
    print("RESUMEN DEL ARCHIVO")
    print(f"{'=' * 60}")

    exitosos = sum(1 for r in resultados if r[3])
    total = len(resultados)

    print(f"Expresiones procesadas: {total}")
    print(f"Procesamientos exitosos: {exitosos}")
    print(f"Procesamientos fallidos: {total - exitosos}")

    if total - exitosos > 0:
        print("\nLíneas con errores:")
        for linea_num, regex, cadena, exito in resultados:
            if not exito:
                print(f"  Línea {linea_num}: {regex} -> '{cadena}'")


def main():
    if len(sys.argv) == 3:
        # Modo línea de comandos: python principal.py "expresion" "cadena"
        regex = sys.argv[1]
        cadena = sys.argv[2]
        procesar_expresion(regex, cadena)

    elif len(sys.argv) == 2:
        # Modo archivo: python principal.py archivo.txt
        archivo = sys.argv[1]
        procesar_archivo(archivo)

    else:
        # Modo interactivo simple
        print("Analizador Léxico")
        print("=" * 50)
        print("Modos de uso:")
        print("  python principal.py 'expresion' 'cadena'")
        print("  python principal.py archivo.txt")
        print("  python principal.py (modo interactivo)")
        print()

        opcion = input("¿Desea procesar un archivo? (s/n): ").strip().lower()

        if opcion == 's' or opcion == 'si':
            archivo = input("Nombre del archivo: ").strip()
            procesar_archivo(archivo)
        else:
            regex = input("Expresión regular: ").strip()
            cadena = input("Cadena a evaluar: ").strip()
            procesar_expresion(regex, cadena)


if __name__ == "__main__":
    main()