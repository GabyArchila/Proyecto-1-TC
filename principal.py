import sys
import os
from preprocesamiento import infix_to_postfix, format_regex
from thompson import Thompson
from subconjuntos import Subconjuntos
from minimizacion import MinimizacionAFD


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

        # Construcción paso a paso para depuración
        if len(postfix) > 2:
            afn = debug_construccion_paso_a_paso(postfix)
        else:
            thompson = Thompson()
            afn = thompson.construir_desde_postfix(postfix)

        if not afn:
            print("Error: No se pudo construir el AFN")
            return False

        print(f"\nAFN construido exitosamente:")
        print(f"  - Estados: {len(afn.states)}")
        print(f"  - Estado inicial: {afn.start_state}")
        print(f"  - Estados finales: {len(afn.final_states)}")

        # Mostrar información detallada del AFN
        afn.debug_info()

        # Visualizar AFN (COMENTADO)
        # print("Visualizando AFN...")
        # afn.visualizar(f"AFN para: {regex}")

        # Simular cadena en AFN
        resultado_afn = afn.simular(cadena)
        print(f"Resultado simulación AFN: {'SÍ' if resultado_afn else 'NO'}")

        # Paso 3: Convertir AFN a AFD (subconjuntos)
        print("\n3. CONVERSIÓN AFN A AFD (SUBCONJUNTOS)")
        subconjuntos = Subconjuntos(afn)
        afd = subconjuntos.convertir()

        print(f"AFD construido exitosamente:")
        print(f"  - Estados: {len(afd.states)}")
        print(f"  - Estado inicial: {afd.start_state}")
        print(f"  - Estados finales: {len(afd.final_states)}")
        print(f"  - Alfabeto: {afd.alphabet}")

        # Mostrar información detallada del AFD
        afd.debug_info()

        # Visualizar AFD (COMENTADO)
        # print("Visualizando AFD...")
        # afd.visualizar(f"AFD para: {regex}")

        # Simular cadena en AFD
        resultado_afd = afd.simular(cadena)
        print(f"Resultado simulación AFD: {'SÍ' if resultado_afd else 'NO'}")

        # Paso 4: Minimizar AFD
        print("\n4. MINIMIZACIÓN DE AFD")
        minimizador = MinimizacionAFD(afd)
        afd_min = minimizador.minimizar()

        print(f"AFD minimizado construido exitosamente:")
        print(f"  - Estados: {len(afd_min.states)}")
        print(f"  - Estado inicial: {afd_min.start_state}")
        print(f"  - Estados finales: {len(afd_min.final_states)}")

        # Mostrar información detallada del AFD minimizado
        afd_min.debug_info()

        # Visualizar AFD minimizado (COMENTADO)
        # print("Visualizando AFD minimizado...")
        # afd_min.visualizar(f"AFD Minimizado para: {regex}")

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


def debug_construccion_paso_a_paso(postfix):
    """
    Función de depuración para ver la construcción paso a paso del AFN
    """
    print("\nDEBUG CONSTRUCCIÓN PASO A PASO:")
    print(f"Postfix: {postfix}")
    print(f"Longitud: {len(postfix)}")

    thompson = Thompson()
    stack = []

    i = 0
    n = len(postfix)

    while i < n:
        char = postfix[i]
        print(f"\n  Paso {i + 1}: Carácter '{char}'")
        print(f"     Stack antes: {len(stack)} elementos")
        if stack:
            print(f"     Elementos en stack: {[len(afn.states) for afn in stack]} estados")

        try:
            # Manejar caracteres escapados
            if char == '\\' and i + 1 < n:
                escaped_char = char + postfix[i + 1]
                result = thompson.crear_simbolo(escaped_char)
                stack.append(result)
                print(f"     Símbolo escapado '{escaped_char}': -> AFN({len(result.states)} estados)")
                i += 2
                continue

            if char == '.':
                if len(stack) < 2:
                    raise ValueError(f"Concatenación requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                result = thompson.concatenacion(afn1, afn2)
                stack.append(result)
                print(
                    f"     Concatenación: AFN1({len(afn1.states)} estados) + AFN2({len(afn2.states)} estados) -> AFN({len(result.states)} estados)")

            elif char == '|':
                if len(stack) < 2:
                    raise ValueError(f"Unión requiere 2 operandos")
                afn2 = stack.pop()
                afn1 = stack.pop()
                result = thompson.union(afn1, afn2)
                stack.append(result)
                print(
                    f"     Unión: AFN1({len(afn1.states)} estados) | AFN2({len(afn2.states)} estados) -> AFN({len(result.states)} estados)")

            elif char == '*':
                if len(stack) < 1:
                    raise ValueError(f"Estrella requiere 1 operando")
                afn = stack.pop()
                result = thompson.estrella(afn)
                stack.append(result)
                print(f"     Kleene: AFN({len(afn.states)} estados)* -> AFN({len(result.states)} estados)")

            elif char == '+':
                if len(stack) < 1:
                    raise ValueError(f"Plus requiere 1 operando")
                afn = stack.pop()
                result = thompson.plus(afn)
                stack.append(result)
                print(f"     Plus: AFN({len(afn.states)} estados)+ -> AFN({len(result.states)} estados)")

            elif char == '?':
                if len(stack) < 1:
                    raise ValueError(f"Interrogación requiere 1 operando")
                afn = stack.pop()
                result = thompson.opcional(afn)
                stack.append(result)
                print(f"     Opcional: AFN({len(afn.states)} estados)? -> AFN({len(result.states)} estados)")

            elif char == '#':
                result = thompson.crear_epsilon()
                stack.append(result)
                print(f"     Épsilon: -> AFN({len(result.states)} estados)")

            else:
                # Si es un símbolo normal (no operador)
                result = thompson.crear_simbolo(char)
                stack.append(result)
                print(f"     Símbolo '{char}': -> AFN({len(result.states)} estados)")

            print(f"     Stack después: {len(stack)} elementos")
            if stack:
                print(f"     Elementos en stack: {[len(afn.states) for afn in stack]} estados")

        except Exception as e:
            print(f"     Error en paso {i + 1}: {e}")
            print(f"     Stack actual: {len(stack)} elementos")
            raise

        i += 1

    print(f"\nStack final: {len(stack)} elementos")
    for i, afn in enumerate(stack):
        print(f"  Elemento {i}: {len(afn.states)} estados")

    if len(stack) != 1:
        raise ValueError(f"Stack final tiene {len(stack)} elementos, debería tener 1")

    return stack[0]


def test_expresiones():
    """Prueba las expresiones problemáticas mencionadas"""
    test_cases = [
        # Expresiones originales
        #("(a|b)*abb", "aaaaaaaaaaaaaaaaaaaaaaaaabb"),
        #("(a|b)*abb", "aaaaaaaaaaaaaaaaaaaaaaaaabab"),
        #(r"\?(((.|ε)?!?)\*)+", "?"),
        #(r"\?(((.|ε)?!?)\*)+", "?!."),
        #(r"\?(((.|ε)?!?)\*)+", "?.."),
        #(r"\?(((.|ε)?!?)\*)+", "!"),
        #(r"\?(((.|ε)?!?)\*)+", "!.!.!"),
        #(r"\?(((.|ε)?!?)\*)+", "!?."),
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(a){y}else{n}"),
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(atx){y}"),
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(){y}else{n}"),

        # Pruebas con caracteres escapados (SOLO ESTAS)
        (r"a\*b", "a*b"),
        (r"a\+b", "a+b"),
        (r"a\?b", "a?b"),
        # (r"a\|b", "a|b"),  # COMENTADA - problema con postfix
        # (r"a\.b", "a.b"),  # COMENTADA - problema con postfix
    ]

    print("EJECUTANDO PRUEBAS DE EXPRESIONES PROBLEMÁTICAS")
    print("=" * 60)

    for i, (regex, cadena) in enumerate(test_cases, 1):
        print(f"\nPrueba {i}: {regex} -> '{cadena}'")
        procesar_expresion(regex, cadena)


def main():
    print("Analizador Léxico - Construcción de Autómatas")
    print("=" * 60)

    if len(sys.argv) == 3:
        # Modo línea de comandos: python principal.py "expresion" "cadena"
        regex = sys.argv[1]
        cadena = sys.argv[2]
        procesar_expresion(regex, cadena)

    elif len(sys.argv) == 2:
        if sys.argv[1] == "--test":
            # Modo de prueba especial
            test_expresiones()
        else:
            # Modo archivo: python principal.py archivo.txt
            archivo = sys.argv[1]
            procesar_archivo(archivo)

    else:
        # Modo interactivo simple
        print("Modos de uso:")
        print("  python principal.py 'expresion' 'cadena'")
        print("  python principal.py archivo.txt")
        print("  python principal.py --test")
        print("  python principal.py (modo interactivo)")
        print()

        opcion = input("¿Desea procesar un archivo? (s/n): ").strip().lower()

        if opcion == 's' or opcion == 'si':
            archivo = input("Nombre del archivo: ").strip()
            procesar_archivo(archivo)
        else:
            test_opcion = input("¿Desea ejecutar pruebas? (s/n): ").strip().lower()
            if test_opcion == 's' or test_opcion == 'si':
                test_expresiones()
            else:
                regex = input("Expresión regular: ").strip()
                cadena = input("Cadena a evaluar: ").strip()
                procesar_expresion(regex, cadena)


if __name__ == "__main__":
    main()