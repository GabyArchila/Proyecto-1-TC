import sys
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
            print("❌ Error: Expresión regular vacía")
            return

        # Paso 1: Convertir a postfix
        print("\n1. CONVERSIÓN INFIX A POSTFIX")
        print(f"Expresión original: {regex}")
        formatted = format_regex(regex)
        print(f"Expresión formateada: {formatted}")
        postfix = infix_to_postfix(regex)
        print(f"Expresión postfix: {postfix}")

        if not postfix:
            print("❌ Error: No se pudo convertir a postfix")
            return

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

    except Exception as e:
        print(f"❌ Error procesando expresión: {e}")
        import traceback
        print("📍 Detalles del error:")
        traceback.print_exc()


def main():
    if len(sys.argv) == 3:
        # Modo línea de comandos: python main.py "expresion" "cadena"
        regex = sys.argv[1]
        cadena = sys.argv[2]
        procesar_expresion(regex, cadena)
    else:
        # Modo interactivo simple
        print("🚀 ANALIZADOR LÉXICO - PROYECTO 1")
        print("=" * 50)

        regex = input("📝 Expresión regular: ").strip()
        cadena = input("📝 Cadena a evaluar: ").strip()

        procesar_expresion(regex, cadena)


if __name__ == "__main__":
    main()