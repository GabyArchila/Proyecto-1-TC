import re
from thompson import Thompson

PRECEDENCE = {
    '|': 1,  # Unión (más baja precedencia)
    '.': 2,  # Concatenación
    '?': 3,  # Cero o uno
    '*': 3,  # Cero o más
    '+': 3,  # Uno o más
}


def preprocess_regex(regex):
    """Preprocesa la expresión regular para manejar casos especiales"""
    if not regex:
        return regex

    # Normalizar epsilon - manejar tanto ε como "ε"
    result = regex.replace('ε', '#')

    return result


def format_regex(regex):
    if not regex:
        return regex

    regex = preprocess_regex(regex)

    formatted = []
    i = 0
    n = len(regex)

    while i < n:
        c = regex[i]

        # 1) Si es escapado, añade el token escapado y decide concatenación contra el siguiente
        if c == '\\' and i + 1 < n:
            escaped_char = c + regex[i + 1]
            formatted.append(escaped_char)
            i += 2
            if i < n:
                next_c = regex[i]
                # tras un token 'escapado', concatena si sigue un átomo
                if next_c not in ['|', ')', '*', '+', '?']:
                    formatted.append('.')
            continue

        # 2) Añade el caracter actual
        formatted.append(c)

        # 3) Decide si va '.' entre c y el siguiente token
        if i + 1 < n:
            next_c = regex[i + 1]

            # el "siguiente es átomo" si es escapado, '(', o símbolo normal
            next_is_atom = (next_c == '\\') or (next_c not in ['|', ')', '*', '+', '?'])

            # el "actual permite concatenar" si es átomo, ')', o un operador postfix
            curr_is_atom = (c not in ['|', '(']) or (c in ['*', '+', '?']) or (c == ')')

            if curr_is_atom and next_is_atom:
                formatted.append('.')

        i += 1

    return ''.join(formatted)



def infix_to_postfix(regex):
    """Convierte expresión regular infix a postfix usando shunting yard"""
    output = []
    operator_stack = []

    formatted_re = format_regex(regex)
    print(f"Expresión formateada: {formatted_re}")

    i = 0
    n = len(formatted_re)

    while i < n:
        c = formatted_re[i]

        # Manejar caracteres escapados
        if c == '\\' and i + 1 < n:
            escaped_char = c + formatted_re[i + 1]
            output.append(escaped_char)
            i += 2
            continue

        if c == '#':  # Epsilon
            output.append(c)
        elif c == '(':
            operator_stack.append(c)
        elif c == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            if operator_stack and operator_stack[-1] == '(':
                operator_stack.pop()  # Remover el '('
        elif c in PRECEDENCE:
            # Para operadores, respetar precedencia y asociatividad
            while (operator_stack and operator_stack[-1] != '(' and
                   operator_stack[-1] in PRECEDENCE and
                   PRECEDENCE[operator_stack[-1]] >= PRECEDENCE[c]):
                output.append(operator_stack.pop())
            operator_stack.append(c)
        else:
            # Es un símbolo
            output.append(c)

        i += 1

    # Vaciar la pila de operadores
    while operator_stack:
        op = operator_stack.pop()
        if op != '(':
            output.append(op)

    result = ''.join(output)
    print(f"Postfix resultante: {result}")
    return result


# Test principal
def test_expresiones():
    """Prueba las expresiones problemáticas"""
    test_cases = [

        # Casos básicos
        #("(a|b)*abb", "aaaaaaaaaaaaaaaaaaaaaaaaabb", True),
        #("(a|b)*abb", "aaaaaaaaaaaaaaaaaaaaaaaaabab", False),

        # Con epsilon y símbolos especiales
        #("((a|b)_ε(c|ε)+)|(d?ε+(a|εb)_)", "c", False),
        #("((a|b)_ε(c|ε)+)|(d?ε+(a|εb)_)", "a_c", True),

        # Caracteres escapados
        #(r"\?(((\.|ε)?!?)\*)+", "?", True),
        #(r"\?(((\.|ε)?!?)\*)+", "?!.", True),
        #(r"\?(((\.|ε)?!?)\*)+", "?..", False),

        # Expresiones complejas
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(a){y}else{n}", True),
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(atx){y}", True),
        #(r"if\((a|x|t)+\)\{y\}(else\{n\})?", "if(){y}else{n}", False),


        # Pruebas adicionales
        ("(a*|b*)+((ε|a)|b*)*", "aa", True),
        ("(a*|b*)+((ε|a)|b*)*", "ab", True),
        ("(a|b)*abb(a|b)*", "abb", True),
        ("(a|b)*abb(a|b)*", "aba", False),
        ("0?(1?)?0*", "0", True),
        ("0?(1?)?0*", "2", False),

    ]

    print("=== PRUEBAS DE EXPRESIONES CORREGIDAS ===")

    for regex, cadena, esperado in test_cases:
        print(f"\nPrueba: {regex} -> '{cadena}' (esperado: {esperado})")

        try:
            # Convertir a postfix
            postfix = infix_to_postfix(regex)

            # Construir AFN
            thompson = Thompson()
            afn = thompson.construir_desde_postfix(postfix)

            # Simular
            resultado = afn.simular(cadena)

            if resultado == esperado:
                print(f"✅ CORRECTO: {'ACEPTA' if resultado else 'RECHAZA'}")
            else:
                print(
                    f"❌ ERROR: obtenido {'ACEPTA' if resultado else 'RECHAZA'}, esperado {'ACEPTA' if esperado else 'RECHAZA'}")

        except Exception as e:
            print(f"❌ ERROR en procesamiento: {e}")


if __name__ == "__main__":
    test_expresiones()