from pprint import pprint as pp


# Everything is safe until 315 989 607

def P(x):
    x ^= x >> 17
    x *= 0xed5ad4bb
    x %= 2**32
    x ^= x >> 11
    x *= 0xac4c1b51
    x %= 2**32
    x ^= x >> 15
    x *= 0x31848bab
    x %= 2**32
    x ^= x >> 14
    return x


def antiP(x):
    x = anti_sxor(x, 14)
    x *= 0x32b21703
    x %= 2**32
    x = anti_sxor(x, 15)
    x *= 0x469e0db1
    x %= 2**32
    x = anti_sxor(x, 11)
    x *= 0x79a85073
    x %= 2**32
    x = anti_sxor(x, 17)
    return x


def nf(x, f, n):
    for i in range(n):
        x = f(x)
    return x


def anti_sxor(x, n):
    ans = x
    while (ans >> n) ^ x != ans:
        ans = (ans >> n) ^ x
    return ans


def pc(x):
    ans = 0
    while x > 0:
        ans ^= x
        x >>= 2
    return ans & 1


t = [(j << 10) * 2**16 for i in range(256) for j in range(65)]
ai = 0


def sse_test(p, c, b):
    w = p & 127
    tai = (p >> 2) + (c << 6) + c
    return (t[tai] * (128 - w) + t[tai + 1] * w) >> 15


def find_smallest(start, size):
    a = set()
    for i in range(start, start + size):
        for j in range(256):
            q = P(i) ^ j
            for k in range(size - i + start):
                a.add((q, i, j, k))
                q = P(q)
    return sorted(list(a))


def find_exact(point, target):
    point -= 2
    rng = 1
    target = antiP(target)
    while True:
        if point < 3: return None
        for i in range(256):
            if point - rng < antiP(target ^ i) <= point:
                return antiP(target ^ i), i, point - antiP(target ^ i)
        point -= 1
        rng += 1
        target = antiP(target)


def find_commands(point, targets):
    ans = []
    og_targets = targets[:]
    og_point = point
    while targets:
        point -= 2
        rng = 1
        targets = [(antiP(a), antiP(v) for a, v in target]
        cutoff = 2
        best = None
        while point > cutoff:
            for q, (targetA, targetV) in enumerate(targets):
                for i in range(256):
                    if max(point - rng, cutoff) < antiP(targetA ^ i) <= point:
                        best = (True,
                                (targetA, targetV),
                                q,
                                 i,
                                 point - antiP(targetA ^ i)))
                        cutoff = antiP(targetA ^ i)
                    if max(point - rng, cutoff) < antiP(targetV ^ i) <= point:
                        best = (False,
                                q,
                                (antiP(targetV ^ i),
                                 i,
                                 point - antiP(targetV ^ i)))
                        cutoff = antiP(targetV ^ i)
            point -= 1
            rng += 1
            targets = [(antiP(a), antiP(v) for a, v in target]


def find_command(point, a, b):
    answerA = None
    tmpA = find_exact(point, a)
    if tmpA is not None:
        pointA, xorA, skipA = tmpA
        tmpB = find_exact(pointA - 1, nf(b, antiP, point - pointA - skipA - 1))
        if tmpB is not None:
            answerA = tmpA + tmpB + (point,)
    answerB = None
    tmpB = find_exact(point, b)
    if tmpB is not None:
        pointB, xorB, skipB = tmpB
        tmpA = find_exact(pointB - 1, nf(a, antiP, point - pointB - skipB - 1))
        if tmpA is not None:
            answerB = tmpA + tmpB + (point,)
    if answerA is None: return answerB
    if answerB is None or answerA[3] > answerB[0]: return answerA
    return answerB


def compile_print(s, file = None):
    compiled = bytearray([0x60])
    i = 1
    for c in s:
        while True:
            if (ord(c) ^ P(i + 2)) & 15 == 15:
                compiled.append(0x0F)
                com = P(i + 1) ^ 0x0F
                for j in range(24, -8, -8):
                    compiled.append((com >> j) % 256)
                compiled.append((P(i + 2) ^ ord(c)) & 255)
                com = P(i + 3) ^ 0xD0
                for j in range(24, -8, -8):
                    compiled.append((com >> j) % 256)
                i += 4
                break
            else:
                compiled.append(0)
                i += 1
    compiled.append(0x0F)
    com = P(i + 1) ^ 0xF0
    for i in range(24, -8, -8):
        compiled.append((com >> i) % 256)
    if file is not None:
        with open(file, 'wb') as f:
            f.write(compiled)
    return compiled


def encode_int(i):
    return bytearray(map(lambda x: x % 256, [i >> 24, i >> 16, i >> 8, i]))


class Exact:
    def __init__(self, val):
        if val == 0: raise KeyError(0)
        self.val = val

    def __str__(self):
        return f'<{hex(self.val)}>'

class Any:
    def __str__(self):
        return f'(?)'

class Address:
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return f'[{self.val}]'


def compile(t, file=None, start_p=None):
    if start_p is None:
        start_p = len(t) * 10000
    print(start_p)
    funi = []
    p = start_p
    post = bytearray()
    state = "clear"
    for i, c in enumerate(t):
        print(i, p)
        match c:
            case Any():
                match state:
                    case "clear":
                        post.append(0)
                    case "unclear":
                        state = "clear"
            case Exact(val=val):
                match state:
                    case "clear":
                        post.append(0xf)
                        post += encode_int(val ^ P(i + start_p + 2))
                        state = "unclear"
                    case "unclear":
                        tup = find_command(p, i + start_p + 2, val)
                        if tup is None:
                            return compile(t, file, start_p * 2)
                        funi.append(tup)
                        p = min(tup[0], tup[3]) - 3
                        state = "clear"
            case Address(val=val):
                match state:
                    case "clear":
                        post.append(0xf)
                        post += encode_int((val + start_p + 2) ^ P(i + start_p + 2))
                        state = "unclear"
                    case "unclear":
                        print(hex(val + start_p + 2))
                        tup = find_command(p, i + start_p + 2, (val + start_p + 2))
                        if tup is None:
                            return compile(t, file, start_p * 2)
                        funi.append(tup)
                        p = min(tup[0], tup[3]) - 3
                        state = "clear"
            case a:
                ValueError(a)
    print(p)
    assert p >= 0
    compiled = bytearray([0x60])
    idx = 1
    for (pA, xA, sA, pB, xB, sB, p) in reversed(funi):
        if pA < pB:
            compiled += bytearray([0] * (pA - idx - 2) + [0x0F])
            compiled += encode_int(0x0F ^ P(pA - 1))
            compiled.append(xA)
            assert idx < pA + 1
            idx = pA + 1
            if xA & 15 == 15:
                if sA:
                    compiled += encode_int(0x70 ^ P(idx))
                    sA -= 1
                else:
                    compiled += bytearay([0] * 4)
                idx += 1
            for i in range(sA):
                compiled.append(0x0F)
                compiled += encode_int(0x70 ^ P(idx + 1))
                idx += 2
        compiled += bytearray([0] * (pB - idx - 2) + [0x0F])
        compiled += encode_int(0x1F ^ P(pB - 1))
        compiled.append(xB)
        assert idx < pB + 1
        idx = pB + 1
        if xB & 15 == 15:
            if sB:
                compiled += encode_int(0x70 ^ P(idx))
                sB -= 1
            else:
                compiled += bytearay([0] * 4)
            idx += 1
        for i in range(sB):
            compiled.append(0x0F)
            compiled += encode_int(0x70 ^ P(idx + 1))
            idx += 2
        if pA > pB:
            compiled += bytearray([0] * (pA - idx - 2) + [0x0F])
            compiled += encode_int(0x0F ^ P(pA - 1))
            compiled.append(xA)
            idx = pA + 1
            if xA & 15 == 15:
                if sA:
                    compiled += encode_int(0x70 ^ P(idx))
                    sA -= 1
                else:
                    compiled += bytearay([0] * 4)
                idx += 1
            for i in range(sA):
                compiled.append(0x0F)
                compiled += encode_int(0x70 ^ P(idx + 1))
                idx += 2
        compiled += bytearray([0] * (p - idx - 1) + [0x0F])
        compiled += encode_int(0x30 ^ P(p))
        idx = p + 1
    if not funi:
        compiled += bytearray([0] * (start_p))
        idx += start_p
    print(idx)
    assert idx == start_p + 1
    print(start_p)
    if file is not None:
        with open(file, 'wb') as f:
            f.write(compiled)
            f.write(post)
    return compiled + post


# Programs

def loadA(val):
    if isinstance(val, int):
        val = Exact(val)
    return [Exact(0x0F), val]

def loadB(val):
    if isinstance(val, int):
        val = Exact(val)
    return [Exact(0x1F), val]

def loadC(val):
    if isinstance(val, int):
        val = Exact(val)
    return [Exact(0x2F), val]

def jump(adr):
    if isinstance(adr, int):
        adr = Address(adr)
    return [Exact(0x3F), adr]

def condA(adr):
    if isinstance(adr, int):
        adr = Address(adr)
    return [Exact(0x4F), adr]

def condC(adr):
    if isinstance(adr, int):
        adr = Address(adr)
    return [Exact(0x5F), adr]

# sse = useless

# storeA unfortunately requires an Exact(0)
# storeB actually all of those are useless.
# storeC

saveB = [Exact(0x30)]

saveC = [Exact(0x40)]

def storeB(adr):
    if isinstance(adr, int):
        adr = Address(adr)
    return [Exact(0x0F), adr, Exact(0x30)]

def storeC(adr):
    if isinstance(adr, int):
        adr = Address(adr)
    return [Exact(0x0F), adr, Exact(0x40)]

moveAB = [Exact(0x60)]

moveAC = [Exact(0x70)]

moveBA = [Exact(0x80)]

moveCA = [Exact(0x90)]

jumpA = [Exact(0xA0)]

add = [Exact(0xB0)]

sub = [Exact(0xC0)]

put = [Exact(0xD0)]

get = [Exact(0xE0)]

halt = [Exact(0xF0)]

hello_world = [j for c in 'Hello, World!\n' for i in (loadA(ord(c)), put) for j in i] + halt
hi_world = [j for c in 'Hi' for i in (loadA(ord(c)), put) for j in i] + halt

simple_cat = [i for i in get + put + jump(0)]

complex_cat = [i for i in loadC(0xff) + get + moveAB + storeB(10) + condC(14) + loadA(Any())
                        + put + jump(0) + halt]

fizzbuzz = [i for j in (

            loadB(1), loadC(1), sub,
            moveAB, storeB(36), storeB(70),

            loadB(Address(250)), storeB(-1),
            loadB(0x3F), storeB(-2),

            # get
            # if NAN: mainloop
            # multiply thing
            # add to thing
            # jump to start

            # input: [22]
            get, moveAB, loadC(ord('0')), sub,
            moveAB, storeB(51),
            loadC(10), condC(62),

            loadA(Any()), # <- zero, W [36]
            moveAB, moveAC, add, moveAB, moveAC, add,
            moveAB, add, moveAB, add, moveAB, add,
            moveAB, loadC(Any()), add, # <- Q [51]
            moveAB, storeB(36), storeB(70),
            jump(22),

            # reset flag
            # starting with one
            # if more than thing: end

            # mainloop: [62]
            loadB(1), storeB(163),
            loadA(1), # <- E [68]
            loadB(Any()), # <- zero, W [70]
            condA(74), halt,

            # subtract 3
            # if more than -3: skip
            # if more than zero: repeat
            # else print Fizz and set flag

            # fizz: [74]
            moveAB, loadC(3), sub, 
            moveAB, storeB(89),
            loadC(0xFFFFFFFE), condC(108),

            loadC(1), loadB(Any()), # <- F [89]
            moveBA, condC(74),

            # do_fizz
            loadA(ord('F')), put,
            loadA(ord('i')), put,
            loadA(ord('z')), put, put,
            loadB(2), storeB(163),

            # subtract 5
            # if more than zero: repeat
            # if zero: print Buzz, set flag

            # buzz_intro: [108]
            loadB(1), # <- E [109]
            # buzz: [111]
            loadC(5), sub,
            moveAB, storeB(124),
            loadC(0xFFFFFFFC), condC(142),

            loadC(1), loadB(Any()), # <- F [124]
            condC(111),

            # do_buzz
            loadA(ord('B')), put,
            loadA(ord('u')), put,
            loadA(ord('z')), put, put,
            loadB(2), storeB(163),

            # increment: [142]
            loadC(1), loadB(1), storeB(191), # <- E [145]
            add, moveAB, storeB(68), storeB(109), storeB(145),

            # if flag: skip to put newline
            loadC(2), loadB(Any()), # <- flag [163]
            condC(250),

            # 0. Reset pointer
            loadB(Address(-2)), storeB(216),

            # 1. Calculate and store digits
            # initialise other to -1 (number_loop: [171])
            loadB(0xFFFFFFFF), storeB(179),

            # add 1 to other (digt_loop: [176])
            loadC(1), loadB(Any()), # <- R [179]
            add, moveAB, storeB(179), storeB(239),

            # subtract 10
            loadC(10), loadB(Any()), # <- T [191]
            sub, moveAC, storeC(191), storeC(207),

            # if less or equal to -10: repeat
            loadB(0xFFFFFFF5), condC(176),

            # store 10 + 'number'
            loadC(ord('0') + 10), loadB(Any()), add, # <- T [207]
            moveAB, storeB(224),

            # set up stuff
            loadC(1), loadB(Any()), sub, # <- M [216]
            loadB(0xD0), saveB,
            moveAB, sub,
            loadB(Any()), saveB, # <- P [224]
            moveAB, sub,
            loadB(0x0f), saveB,
            moveAB, storeB(216), storeB(248),

            # replace thing with other
            loadB(Any()), storeB(191), # <- R [239]

            # if more than zero: repeat
            loadC(1), condC(171),

            # 2. Jump to them
            loadA(Any()), jumpA, # <- M [248]

            # put newline: [250]
            # repeat mainloop
            loadA(ord('\n')), put, jump(62),
            ) for i in j]

cyclic_tag = [i for j in (

    # start: [0]
    get, loadC(ord('1')), moveAB, sub, ##### <- added moveAB, need to adjust addresses
    moveAB, storeB(17), storeB(23),
    loadC(3), condC(115),
    loadB(Any()), loadC(2), condC(52), # <- Q [17]
    loadB(Any()), loadC(1), condC(40), # <- Q [23]

    # setup compile_f1
    loadB(Address(170)), storeB(86),
    loadB(Address(129)), storeB(111),
    jump(62),

    # setup compile_f2: [40]
    loadB(Address(212)), storeB(86),
    loadB(Address(171)), storeB(111),
    jump(62),
    
    # setup compile_f3: [52]
    loadB(Address(251)), storeB(86),
    loadB(Address(213)), storeB(111),

    # compile program cell: [62], offset = 7
    loadB(7), loadC(1), add, # <- PP [65]
    moveAB, storeB(65), storeB(96), storeB(116),
    moveCA, loadB(0x0F), saveB,
    moveAB, loadC(1), add, loadB(Any()), saveB, # <- RA [86]
    moveAB, add, loadB(0x1F), saveB,
    moveAB, add, loadB(1), saveB, # <- PP [96]
    moveAB, add, loadB(0x30), saveB,
    moveAB, add, loadB(0x3F), saveB,
    moveAB, add, loadB(Any()), saveB, # <- FA [111]
    jump(0),

    # exec_start: [115]
    loadA(1), loadB(0x3F), saveB, # <- PP [116]
    loadC(1), moveAB, add, loadB(1), saveB,
    jump(Exact(1)),

    # f1: [129]
    loadC(2), loadB(1), condC(169), # <- X [132]
    loadC(1), loadB(0x0F), storeB(253), # <- TE [140]
    moveAB, add, loadB(0x01), saveB,
    moveAB, add, loadB(0x3F), saveB,
    moveAB, add, loadB(Address(221)), saveB,
    moveAB, add, moveAB, storeB(140), storeB(182), storeB(216),
    # return_f1: [169]
    jump(Any()), # <- RF1 [170]

    # f2: [171]
    loadC(2), loadB(1), condC(211), # <- X [174]
    loadC(1), loadB(0x0F), storeB(253), # <- TE [182]
    moveAB, add, loadB(0x02), saveB,
    moveAB, add, loadB(0x3F), saveB,
    moveAB, add, loadB(Address(221)), saveB,
    moveAB, add, moveAB, storeB(140), storeB(182), storeB(216),
    # return_f2: [211]
    jump(Any()), # <- RF2 [212]

    # f3: [213]
    loadB(Address(253)), loadC(Address(253)), condC(252), # <- TS [214], TE [216]
    jump(253), # <- TS [220]

    # rp3: [221]
    moveAB, storeB(132), storeB(174),
    loadC(ord('0')), add, put,
    loadA(ord('\n')), put,
    loadC(4), loadB(Address(253)), add, # <- TS [238]
    moveAB, storeB(214), storeB(220), storeB(238),
    # return_f3
    jump(Any()), # <- RF3 [251]

    # end: [252]
    halt,

    # after_end: [253]

) for i in j]
