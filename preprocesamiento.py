import re
from collections import defaultdict, deque

PRECEDENCE = {
    '|': 2,  # Unión
    '.': 3,  # Concatenación
    '?': 4,  # Cero o uno
    '*': 4,  # Cero o más
    '+': 4,  # Uno o más
    '^': 5  # Potencia
}

def v_operador(c1, c2):
    if c1 == '(' or c2 == ')':
        return False
    if c1 in ['|']:
        return False
    if c2 in ['|', '*', '+', '?']:
        return False
    if c1 in ['*', '+', '?'] and c2 not in ['(']:
        return True
    if c1 not in PRECEDENCE and c2 not in PRECEDENCE:
        return True
    if c1 not in PRECEDENCE and c2 == '(':
        return True
    if c1 == ')' and c2 not in PRECEDENCE:
        return True
    if c1 == ')' and c2 == '(':
        return True
    return False

def format_regex(regex):
    formatted = []
    i = 0
    while i < len(regex):
        c = regex[i]

        # Manejar caracteres escapados
        if c == '\\' and i + 1 < len(regex):
            formatted.append(c + regex[i + 1])
            i += 2
            continue

        # Manejar épsilon
        if c == '#':
            formatted.append('#')
            i += 1
            continue

        formatted.append(c)

        # Verificar si necesita concatenación con el siguiente caracter
        if i + 1 < len(regex):
            next_c = regex[i + 1]
            # No agregar concatenación si el siguiente es un caracter escapado
            if next_c == '\\' and i + 2 < len(regex):
                if v_operador(c, regex[i + 1:i + 3]):
                    formatted.append('.')
            elif v_operador(c, next_c):
                formatted.append('.')

        i += 1

    return ''.join(formatted)

def infix_to_postfix(regex):
    output = []
    operator_stack = []
    formatted_re = format_regex(regex)

    i = 0
    while i < len(formatted_re):
        c = formatted_re[i]

        # Manejar caracteres escapados
        if c == '\\':
            if i + 1 < len(formatted_re):
                output.append(c + formatted_re[i + 1])
                i += 2
            else:
                output.append(c)
                i += 1
            continue

        # Manejar épsilon
        if c == '#':
            output.append(c)
            i += 1
            continue

        if c == '(':
            operator_stack.append(c)
        elif c == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()  # Remover el '('
        elif c in PRECEDENCE:
            while (operator_stack and operator_stack[-1] != '(' and
                   PRECEDENCE.get(operator_stack[-1], 0) >= PRECEDENCE[c]):
                output.append(operator_stack.pop())
            operator_stack.append(c)
        else:
            output.append(c)
        i += 1

    while operator_stack:
        output.append(operator_stack.pop())

    return ''.join(output)