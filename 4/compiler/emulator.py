#!/bin/python3


from dataclasses import dataclass, field
from sys import argv
from enum import Enum, auto
from random import sample


# Decoder

@dataclass
class ReadBitState:
    x : int
    high : int = 0xffffffffffffffff
    low : int = 0
    cxt : int = 0
    _pr : int = 0xffffffff
    ct : list[(int, int)] = field(default_factory=lambda: [(0, 0) for i in
                                                           range(256)])

    def copy(self):
        return ReadBitState(
                x = self.x,
                high = self.high,
                low = self.low,
                cxt = self.cxt,
                _pr = self._pr,
                ct = [i for i in self.ct],
        )


def steppable(state):
    return (state.high ^ state.low) & 0xff00000000000000


def step(state):
    if not steppable(state):
        raise Exception('State is not steppable!')
    middle = state.low + ((state.high - state.low) >> 32) * state._pr
    y = int(state.x <= middle)
    if y:
        state.high = middle
    else:
        state.low = middle + 1
    update(state, y)
    return y


def update(state, y):
    q = list(state.ct[state.cxt])
    q[y] += 1
    if q[y] > 0xfffffff:
        q[0] >>= 1
        q[1] >>= 1
    state.ct[state.cxt] = tuple(q)
    state.cxt = ((state.cxt << 1) | y) & 0xff
    state._pr = (((state.ct[state.cxt][1] + 1) << 32) //
            (sum(state.ct[state.cxt]) + 2)) & 0xffffffff


def feed(state, byte):
    state.low = (state.low << 8) & 0xffffffffffffffff
    state.high = ((state.high << 8) | 0xff) & 0xffffffffffffffff
    state.x = ((state.x << 8) | byte) & 0xffffffffffffffff


def decode(bs, n):

    bs = list(reversed(bs))

    def get():
        if bs: return bs.pop()
        else: return 0

    x = 0
    for i in range(8):
        x = (x << 8) | get()

    state = ReadBitState(x)
    ans = []

    for i in range(n):
        while not steppable(state):
            feed(state, get())
        ans.append(str(step(state)))

    return ''.join(ans)


def decode_generator(bs):

    bs = list(reversed(bs))

    def get():
        if bs: return bs.pop()
        else: return 0

    x = 0
    for i in range(8):
        x = (x << 8) | get()

    state = ReadBitState(x)
    ans = []

    while True:
        while not steppable(state):
            feed(state, get())
        yield step(state)


# Parser

def get_int(bs):
    n = 0
    while next(bs): n += 1
    x = 0
    for i in range(n):
        x = (x << 1) | next(bs)
    return x


def get_str(bs):
    return ''.join(str(next(bs)) for i in range(get_int(bs)))


def get_type(bs):
    return 2 * next(bs) + next(bs)


@dataclass
class Expression:
    ...

@dataclass
class Cat(Expression):
    left : Expression
    right : Expression

@dataclass
class Literal(Expression):
    substitution : str

@dataclass
class Drop(Expression):
    length : int

@dataclass
class Application(Expression):
    function : int
    argument : Expression


# These two are just for intermediate representation for parsing smart syntax.
# All compiling code represents the program as list[list[(str, Expression)]]

@dataclass
class Operator:
    pattern : str
    expression : Expression


@dataclass
class Function:
    name : str
    operators : list[Operator]



def parse_expression(bs):
    match get_type(bs):
        case 0:
            return Cat(parse_expression(bs), parse_expression(bs))
        case 1:
            return Literal(get_str(bs))
        case 2:
            return Drop(get_int(bs))
        case 3:
            return Application(get_int(bs), parse_expression(bs))


def parse_file(bs):
    fs = []
    for i in range(get_int(bs)):
        fs.append([])
        for j in range(get_int(bs)):
            fs[i].append((get_str(bs), parse_expression(bs)))
    return fs


# Execution

def main(fs, inp):
    return apply(fs, 0, '000' + inp)


def apply(fs, f, inp):
    i = 0
    while i < len(inp):
        for k, v in fs[f]:
            if inp[i:i+len(k)] == k:
                inp = inp[:i] + eval(fs, v, inp[i+len(k):]) + inp[i+len(k):]
                i = -1
                break
        i += 1
    return inp


def eval(fs, expr, inp):
    match expr:
        case Cat(left=left, right=right):
            return eval(fs, left, inp) + eval(fs, right, inp)
        case Literal(substitution=substitution):
            return substitution
        case Drop(length):
            return inp[length:]
        case Application(function=function, argument=argument):
            return apply(fs, function, eval(fs, argument, inp))
        case e:
            raise Exception('Bad expression ' + str(e))


# Compilation

@dataclass
class WriteBitState:
    high : int = 0xffffffffffffffff
    low : int = 0
    cxt : int = 0
    _pr : int = 0xffffffff
    x : list[int] = field(default_factory=list)
    ct : list[(int, int)] = field(default_factory=lambda: [(0, 0) for i in
                                                           range(256)])


    def steppable(state):
        return (state.high ^ state.low) & 0xff00000000000000


    def step(state, expected):
        middle = state.low + ((state.high - state.low) >> 32) * state._pr
        if expected:
            state.high = middle
        else:
            state.low = middle + 1
        state.update(expected)
        while not state.steppable():
            state.feed()


    def update(state, y):
        q = list(state.ct[state.cxt])
        q[y] += 1
        if q[y] > 0xfffffff:
            q[0] >>= 1
            q[1] >>= 1
        state.ct[state.cxt] = tuple(q)
        state.cxt = ((state.cxt << 1) | y) & 0xff
        state._pr = (((state.ct[state.cxt][1] + 1) << 32) //
                (sum(state.ct[state.cxt]) + 2)) & 0xffffffff


    def feed(state):
        if state.low >> (7 * 8) != state.high >> (7 * 8):
            raise Exception('Feeding steppable state!')
        state.x.append(state.low >> (7 * 8))
        state.low = (state.low << 8) & 0xffffffffffffffff
        state.high = ((state.high << 8) | 0xff) & 0xffffffffffffffff


def encode(bs):

    state = WriteBitState()
    for i in bs:
        state.step(i)

    last_byte = state.high >> (7 * 8)

    return state.x + [last_byte]


# A=B parsing

def compile_int(n):
    x = []
    while n:
        x.append(n % 2)
        n //= 2
    x.append(0)
    x.extend([1] * (len(x) - 1))
    return list(reversed(x))

def compile_str(s):
    x = compile_int(len(s))
    x.extend(int(i) for i in s)
    return x

def compile_dumb(source):
    source = [s for s in source.split('\n') if s and s[0] != '#']
    source = [''.join(c for c in s if c in '01=') for s in source]
    source = [s.split('=') for s in source]
    target = [1, 0, 1]
    target.extend(compile_int(len(source)))
    for k, v in source:
        target.extend(compile_str(k))
        target.extend([0, 1])
        target.extend(compile_str(v))
    return encode(target)


# Full parsing

# Syntax:
# program       := { function }
# function      := identifier { rule }
# rule          := string expression
# expression    := ( cat | string | drop | call | '(' expression ')' ) [ ',' expression ]
# call          := identifier expression
# string        := '"' binary '"'
# drop          := decimal
# identifier    := { not digit, not whitespace and not in '();,"' }
# binary        := { 1 | 0 }
# decimal       := { 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 }

# Witespace is optional in most places, disallowed in strings, identifiers and
# numbers.


# Lexer

@dataclass
class Token:
    line : int
    column : int


class KeywordEnum(Enum):
    OPEN_PAREN = auto()
    CLOSE_PAREN = auto()
#    SEMICOLON = auto()
    COLON = auto()
    EOF = auto()


keyword_map = {
        '(': KeywordEnum.OPEN_PAREN,
        ')': KeywordEnum.CLOSE_PAREN,
#        ';': KeywordEnum.SEMICOLON,
        ',': KeywordEnum.COLON,
}


@dataclass
class KeywordToken(Token):
    keyword : KeywordEnum


@dataclass
class StringToken(Token):
    value : str


@dataclass
class IdentifierToken(Token):
    value : str


@dataclass
class NumberToken(Token):
    value : int


@dataclass(init=False)
class Lexer:
    stream : object
    lookahead : str
    line : int
    column : int
    token_line : int
    token_column : int

    def __init__(self, stream):
        self.stream = stream
        self.lookahead = stream.read(1)
        self.line = 1
        self.column = 1
        self.token_line = 1
        self.token_column = 1

    def consume(self):
        if self.lookahead == '\n':
            self.line += 1
            self.column = 0
        self.lookahead = self.stream.read(1)
        if self.lookahead: self.column += 1
        return self.lookahead

    def finished(self):
        return not self.lookahead


    def skip_whitespace(self):
        while self.lookahead.isspace(): self.consume()


    def start_token(self):
        self.token_line = self.line
        self.token_column = self.column


    def parse_token(self):
        self.skip_whitespace()
        while self.skip_comment():
            self.skip_whitespace()
        self.start_token()
        if self.finished():
            return KeywordToken(self.token_line, self.token_column, KeywordEnum.EOF)
        return (self.try_parse_string()
                or self.try_parse_number()
                or self.try_parse_keyword()
                or self.parse_identifier())

    def try_parse_string(self):
        if self.lookahead != '"':
            return None
        body = []
        while self.consume() in '01':
            body.append(self.lookahead)
        if self.lookahead != '"':
            raise Exception(f'Invalid character {self.lookahead} in a string\n'\
                            + f'At line {self.line}, column {self.column}.')
        self.consume()
        return StringToken(self.token_line, self.token_column, ''.join(body))


    def try_parse_number(self):
        if not self.lookahead.isdecimal():
            return None
        x = int(self.lookahead)
        while self.consume().isdecimal():
            x *= 10
            x += int(self.lookahead)
        return NumberToken(self.token_line, self.token_column, x)


    def try_parse_keyword(self):
        if self.lookahead not in keyword_map:
            return None
        token = KeywordToken(self.token_line, self.token_column, keyword_map[self.lookahead])
        self.consume()
        return token


    def skip_comment(self):
        if self.lookahead != '#':
            return False
        while self.consume() not in '\n': ...
        return True


    def parse_identifier(self):
        body = [self.lookahead]
        while (self.consume() and
               self.lookahead not in keyword_map and
               not self.lookahead.isdecimal() and
               not self.lookahead.isspace() and
               self.lookahead not in '"#'):
            body.append(self.lookahead)
        return IdentifierToken(self.token_line, self.token_column, ''.join(body))


    def __iter__(self):
        while True:
            token = self.parse_token()
#            print(token)
            yield token


# Parser

@dataclass(init=False)
class Parser:
    generator : object
    lookahead : object

    def __init__(self, generator):
        self.generator = iter(generator)
        self.lookahead = next(self.generator)

    def consume(self):
        self.lookahead = next(self.generator)
        return self.lookahead

    def parse_program(self):
        fs = []
        while True:
            match self.lookahead:
                case KeywordToken(keyword=KeywordEnum.EOF):
                    break
                case _:
                    fs.append(self.parse_function())
        fs = [fs[0]] + sample(fs[1:], k=len(fs)-1)
        return self.expand_names(fs)


    def expand_names(self, fs):
        name_dict = {s.name: i for i, s in enumerate(fs)}
        return [[(op.pattern, self.expand_names_expression(op.expression,
                                                           name_dict))
                 for op in f.operators] for f in fs]


    def expand_names_expression(self, expr, name_dict):
        match expr:
            case Drop(): return expr
            case Literal(): return expr
            case Application(function=fun, argument=arg):
                if fun not in name_dict:
                    raise Exception(f'Unknown function: {fun}')
                return Application(
                        name_dict[fun],
                        self.expand_names_expression(arg, name_dict))
            case Cat(left=left, right=right):
                return Cat(
                    self.expand_names_expression(left, name_dict),
                    self.expand_names_expression(right, name_dict))

        

    def parse_function(self):
        match self.lookahead:
            case IdentifierToken(value=name): self.consume()
            case e:
                raise Exception('Error while parsing function\n' + \
                                'Expected: Identifier\n' + \
                                f'Got: {e}')
        ops = []
        while op := self.try_parse_operator():
            ops.append(op)
        return Function(name, ops)

    def try_parse_operator(self):
        match self.lookahead:
            case StringToken(value=pattern): self.consume()
            case e: return None
        return Operator(pattern, self.parse_cat_or_expression())

    def parse_cat_or_expression(self):
        left = self.parse_expression()
        match self.lookahead:
            case KeywordToken(keyword=KeywordEnum.COLON):
                self.consume()
            case e:
                return left
        right = self.parse_cat_or_expression()
        return Cat(left, right)


    def parse_expression(self):
        match self.lookahead:
            case StringToken(value=value):
                self.consume()
                return Literal(value)
            case NumberToken(value=value):
                self.consume()
                return Drop(value)
            case IdentifierToken(value=value):
                self.consume()
                return Application(value, self.parse_cat_or_expression())
            case KeywordToken(keyword=KeywordEnum.OPEN_PAREN):
                self.consume()
                expr = self.parse_cat_or_expression()
                match self.lookahead:
                    case KeywordToken(keyword=KeywordEnum.CLOSE_PAREN):
                        self.consume()
                    case e:
                        raise Exception('Error while parsing expression\n' + \
                                        'Expected: Close parenthesis\n' + \
                                        f'Got: {e}')
                return expr
            case e:
                raise Exception('Error while parsing expression\n' + \
                                f'Unexpected {e}')



# Smart compilation

def compile_smart(fs):
    code = compile_int(len(fs))
#    print(code)
    for f in fs:
        code.extend(compile_int(len(f)))
        for sub, expr in f:
            code.extend(compile_str(sub))
            code.extend(compile_expr(expr))
    return encode(code)


def compile_expr(expr):
    code = []
    match expr:
        case Cat(left=left, right=right):
            code.extend([0, 0])
            code.extend(compile_expr(left))
            code.extend(compile_expr(right))
        case Literal(substitution=substitution):
            code.extend([0, 1])
            code.extend(compile_str(substitution))
        case Drop(length=length):
            code.extend([1, 0])
            code.extend(compile_int(length))
        case Application(function=function, argument=argument):
            code.extend([1, 1])
            code.extend(compile_int(function))
            code.extend(compile_expr(argument))
        case e:
            raise Exception(str(e))
    return code


# Main


def print_help():
    print(f'Usage: {argv[0]} <option> [parameters]')
    print()
    print('Options:')
    print()
    print('    -h')
    print('        Print this help and exit')
    print()
    print('    -a <source> <destination>')
    print('        Compile source code in simple A=B syntax')
    print()
    print('    -c <source> <destination>')
    print('        Compile source code in full featured syntax')


if __name__ == '__main__':
    if len(argv) < 2 or 'h' in argv[1].lower():
        print_help()
    elif 'a' in argv[1].lower():
        if len(argv) < 4:
            print_help()
        else:
            with open(argv[2], 'r') as f:
                source = f.read()
            code = compile_dumb(source)
            with open(argv[3], 'wb') as f:
                f.write(bytes(code))
    elif 'c' in argv[1].lower():
        if len(argv) < 4:
            print_help()
        else:
            with open(argv[2], 'r') as f:
                fs = Parser(Lexer(f)).parse_program()
            code = compile_smart(fs)
            with open(argv[3], 'wb') as f:
                f.write(bytes(code))
