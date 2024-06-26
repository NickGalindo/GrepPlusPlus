import tokenize
import io
from io import BytesIO

# Define mappings for token types
KEYWORDS = {
    'def': 'DEF',
    'print': 'PRINT',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
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
    tokenize.RPAR: 'RIGHT_PARENTHSIS',
    tokenize.LSQB: 'LEFT_SQ_BRACKET',
    tokenize.RSQB: 'RIGHT_SQ_BRACKET',
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

# Add BOOLEAN literals
BOOLEAN = {
    'True': 'BOOLEAN_TRUE',
    'False': 'BOOLEAN_FALSE'
}


def tokenizeCode(line):
    # Tokenize the Python file
    tokens = tokenize.generate_tokens(io.StringIO(line).readline)

    list_tkns = []
    # Process and print each token
    for tok in tokens:
        token_type = tok.exact_type
        token_string = tok.string.strip()

        # Skip NL, INDENT, and DEDENT tokens
        if token_type in {tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING}:
            continue

        if token_type == tokenize.NAME:
            # Check if the name is a keyword, boolean literal, or identifier
            if token_string in KEYWORDS:
                token_type_str = KEYWORDS[token_string]
            elif token_string in BOOLEAN:
                token_type_str = BOOLEAN[token_string]
            else:
                token_type_str = 'IDENTIFIER'
            #print(token_type_str, repr(token_string))
            list_tkns.append([token_type_str, repr(token_string)])
        elif token_type in LITERALS:
            #print(LITERALS[token_type], repr(token_string))
            list_tkns.append([LITERALS[token_type], repr(token_string)])
        elif token_type in PUNCTUATIONS:
            #print(PUNCTUATIONS[token_type], repr(token_string))
            list_tkns.append([PUNCTUATIONS[token_type], repr(token_string)])
        elif token_type == tokenize.NEWLINE or token_type == tokenize.ENDMARKER:
            continue  # Ignore newline and end-of-file tokens
        else:
            #print(tokenize.tok_name[token_type], repr(token_string))
            list_tkns.append([tokenize.tok_name[token_type], repr(token_string)])
            
    return list_tkns


if __name__ == "__main__":
    line = input()
    tokens = tokenizeCode(line)
    print(tokens)
    