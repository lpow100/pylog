#######################################
# CONSTANTS
#######################################

DIGITS = '0123456789'

#######################################
# ERRORS
#######################################

class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

#######################################
# POSITION
#######################################

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#######################################
# TOKENS
#######################################

TT_INT		= 'INT'
TT_FLOAT    = 'FLOAT'
TT_PLUS     = 'PLUS'
TT_MINUS    = 'MINUS'
TT_MUL      = 'MUL'
TT_DIV      = 'DIV'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

#######################################
# LEXER
#######################################

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
    
##################################
#node
##################################
        
class NumberNode:
	def __init__(self, tok):
		self.tok = tok

	def __repr__(self):
		return f'{self.tok}'

class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'
        
class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'

#######################################
# PARSE
#######################################

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.advance()

    def advance(self):
        if self.idx < len(self.tokens):
            self.current_token = self.tokens[self.idx]
            self.idx += 1
        else:
            self.current_token = None

    def parse(self):
        result = self.expr()

        if self.current_token is not None:
            return None, Error("Unexpected token after expression", self.current_token.pos_start, self.current_token.pos_end)

        return result, None

    def factor(self):
        token = self.current_token

        if token.type == TT_INT or token.type == TT_FLOAT:
            self.advance()
            return NumberNode(token), None
        elif token.type == TT_LPAREN:
            self.advance()
            result, error = self.expr()
            if error is not None:
                return None, error
            if self.current_token is None or self.current_token.type != TT_RPAREN:
                return None, Error("Expected ')'", token.pos_start, self.current_token.pos_end)
            self.advance()
            return result, None
        else:
            return None, IllegalCharError(token.pos_start, token.pos_end, "Unexpected token")

    def term(self):
        return self.bin_op(self.factor, [TT_MUL, TT_DIV])

    def expr(self):
        return self.bin_op(self.term, [TT_PLUS, TT_MINUS])

    def bin_op(self, func, ops):
        left, error = func()

        while self.current_token is not None and self.current_token.type in ops:
            op_token = self.current_token
            self.advance()
            right, error = func()
            if error is not None:
                return None, error
            left = BinOpNode(left, op_token, right)

        return left, None

#######################################
# RUN
#######################################

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    if error:
        return None, error

    parser = Parser(tokens)
    parsed_tree, error = parser.parse()

    return parsed_tree, error
