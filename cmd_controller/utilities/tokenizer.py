import tokenize
import io
from typing import List

# Define mappings for token types
KEYWORDS = {
    'def': 'DEF',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELSE_IF',
    'for': 'FOR',
    'while': 'WHILE',
    'try': 'TRY',
    'except': 'EXCEPT',
    'finally': 'FINALLY',
    'return': 'RETURN',
    'import': 'IMPORT',
    'from': 'FROM',
    'as': 'AS',
    'pass': 'PASS',
    'continue': 'CONTINUE',
    'break': 'BREAK',
    'assert': 'ASSERT',
    'raise': 'RAISE',
    'global': 'GLOBAL',
    'nonlocal': 'NONLOCAL',
    'lambda': 'LAMBDA',
    'with': 'WITH',
    'yield': 'YIELD',
    'in': 'IN',
    'is': 'IS',
    'not': 'NOT',
    'and': 'AND',
    'or': 'OR'
}

LITERALS = {
    tokenize.NUMBER: 'NUMBER',
    tokenize.STRING: 'STRING'
}

PUNCTUATIONS = {
    tokenize.LPAR: 'LEFT_PARENTHESIS',
    tokenize.RPAR: 'RIGHT_PARENTHESIS',
    tokenize.LSQB: 'LEFT_SQUARE_BRACKET',
    tokenize.RSQB: 'RIGHT_SQUARE_BRACKET',
    tokenize.COLON: 'COLON',
    tokenize.COMMA: 'COMMA',
    tokenize.SEMI: 'SEMICOLON',
    tokenize.DOT: 'DOT',
    tokenize.PLUS: 'ADD',
    tokenize.MINUS: 'SUBTRACT',
    tokenize.STAR: 'MULTIPLY',
    tokenize.SLASH: 'DIVIDE',
    tokenize.PERCENT: 'MODULO',
    tokenize.EQEQUAL: 'EQUALS_EQUALS',  # == operator
    tokenize.EQUAL: 'ASSIGN',  # = assignment operator
    tokenize.VBAR: 'BITWISE_OR',
    tokenize.AMPER: 'BITWISE_AND',
    tokenize.CIRCUMFLEX: 'BITWISE_XOR',
    tokenize.TILDE: 'BITWISE_NOT',
    tokenize.DOUBLESLASH: 'FLOOR_DIVIDE',
    tokenize.AT: 'AT',
}

BOOLEAN = {
    'True': 'BOOLEAN_TRUE',
    'False': 'BOOLEAN_FALSE'
}


def tokenize_line(line: str):
    tokens: List = []
    for token in tokenize.generate_tokens(io.StringIO(line).readline):
        token_type = token.exact_type
        token_string = token.string.strip()

        if token_type in {tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}:
            continue

        if token_type == tokenize.NAME:
            if token_string in KEYWORDS:
                token_type_str = KEYWORDS[token_string]
            elif token_string in BOOLEAN:
                token_type_str = BOOLEAN[token_string]
            else:
                token_type_str = 'IDENTIFIER'
            tokens.append({
                "token_type": token_type_str,
                "token_str": token_string,
                "start_pos": f"{token.start[0]},{token.start[1]}",
                "end_pos": f"{token.end[0]},{token.end[1]}"
            })
        elif token_type in LITERALS:
            tokens.append({
                "token_type": LITERALS[token_type],
                "token_str": token_string,
                "start_pos": f"{token.start[0]},{token.start[1]}",
                "end_pos": f"{token.end[0]},{token.end[1]}"
            })
        elif token_type in PUNCTUATIONS:
            tokens.append({
                "token_type": PUNCTUATIONS[token_type],
                "token_str": token_string,
                "start_pos": f"{token.start[0]},{token.start[1]}",
                "end_pos": f"{token.end[0]},{token.end[1]}"
            })
    
    return tokens


def tokenize_lines(doc: str, split_doc: List[str]):
    tokens: List = []
    for token in tokenize.generate_tokens(io.StringIO(doc).readline):
        if tokenize.tok_name[token.exact_type] == "NL" or tokenize.tok_name[token.exact_type] == "INDENT" or tokenize.tok_name[token.exact_type] == "DEDENT" or tokenize.tok_name[token.exact_type] == "ENCODING" or tokenize.tok_name[token.exact_type] == "NEWLINE" or tokenize.tok_name[token.exact_type] == "ENDMARKER":
            continue

        token_type = token.exact_type
        token_string = token.string.strip()
        token_type_str =  tokenize.tok_name[token.exact_type]

        if token_type == tokenize.NAME:
            if token_string in KEYWORDS:
                token_type_str = KEYWORDS[token_string]
            elif token_string in BOOLEAN:
                token_type_str = BOOLEAN[token_string]
        elif token_type in LITERALS:
            token_type_str =  LITERALS[token_type]
        elif token_type in PUNCTUATIONS:
            token_type_str =  PUNCTUATIONS[token_type]

        tokens.append({
            "token_type": token_type_str,
            "token_str": token_string,
            "start_pos": f"{token.start[0]},{token.start[1]}",
            "end_pos": f"{token.end[0]},{token.end[1]}"
        })

    return tokens
