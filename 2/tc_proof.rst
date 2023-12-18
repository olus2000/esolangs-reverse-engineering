=======================================================================================================
                                 Proof that Nuova is Turing Complete
=======================================================================================================

Written for the version with broken ``sse`` and command ``0x50``.

I will start by proving that I can put an arbitrary sequence of values in consecutive cells given
enough space before those cells. Then I will present an interpreter for the Cyclic Tag language,
which is known to be Turing Complete, writen in Nuova commands.


------------------------
 Important observations
------------------------

Nuova operates on a dynamically allocated memory addressable with 32-bit values. It uses functions
``ms`` and ``mg`` to set and get the values in the memory and they contain no nuance in their operation
so I will assume I am working on a fully initialized memory.

Inital values of each cell in the memory are ``P(i)`` where ``i`` is the index of the cell. Function
``P`` and it's inverse ``P'`` are known. ``P(0)`` is zero.

``sse`` only changes a single cell that comes after the program and thus can be disregarded.

The interpreter reads the program in one of two modes: 1-byte and 4-byte. By default it reads the
program 1 byte at a time xoring it with the corresponding cell, but if a byte ending with 0xF is
read next 4 bytes of the program are interpreted as a big-endian 32-bit integer that is xored with
the cell value. This gives us full control over values of some cells at the start of the execution,
but makes sure we don't have full control over values of *all* cells at the start of the execution.

----------------------------
 Arbitrary string of values
----------------------------

After the program is xored into the memory execution follows a simple loop:

1. read cell
2. if it belongs to a set of instructions execute the corresponding instruction
3. otherwise execute ``P`` on values of registers
4. repeat

It's impossible to directly set a consecutive string of values, but we can put every second value
in place by including a sequence of 0xF and the value to be xored to achieve the desired value in
the program. The rest of the cells must be set at execution time by the rest of the program. This
is hard because most useful commands depend on two consecutive cells having non-garbage values: the
command and the immediate argument.


Setting a value of a register
-----------------------------

We can set a value of a register by putting a ``0xF`` value in the program followed by the 4-byte
value to be xored with the cell to produce the correct command. This prevents us from having
complete control over it's immediate argument: the next value will be read in the 1-byte mode,
meaning we only have control over its lowest byte. This will set the register to value ``N``, which
after one garbage command will change to ``P(N)``, after two to ``P(P(N))`` and so on. We can further
control the point at which each particular value is achieved by setting a number of cells to a
command that doesn't affect the register, in my case it would be ``0x70``. As already mentioned we
can do it every second cell, so we can achieve the value ``P^x(N)`` in the register between ``x`` and
``2x`` cells after ``N`` appeared in initial memory.


Searching for ``N``
-------------------

We want to achieve the inverse of what we said: we want to have registers set to a particular value
at a particular memory location, and we want to search for the place at which we should set it, the
value with which the initial memory should be xored, and the number of noops to be included between
the locations. This can be achieved with a simple search algorithm::

    Given the target value T we want to achieve before executing the command at address A:
        Set R to 1;
        Decrement A;
        Repeat until done:
            If A is smaller than 3:
                You have requested too low of an address!
                Try again starting from a higher one.
            For each value X between 0 and 255 inclusive:
                If P'(T ^ X) is higher than A - R and lower or equal to A:
                    P'(T ^ X) is the address of initial N;
                    X is the value it should be xored with;
                    A - P'(T ^ X) is the number of noops needed between the locations;
                    Calculations are done.
            Decrement A;
            Increment R;
            Set T to P'(T)

This algorithm operates on the principle of a growing range of candidates for N given by addresses
between ``A - R`` and ``A``. The algorithm checks for each ``x`` if a value ``P'^x(T)``, or another than
can be xored with a byte to produce it, can be found in the range.

I can't be bothered to prove that it actually always finds the solution a reasonable distance from
initial ``A``, but in practice it happens on average within less than 3000 cells. It could go
something along the lines of: "it checks 256 values for matching any of the values in the range in
each step, so in ``n`` steps it checks ``128 * n * (n + 1)`` values, which reaches 2^32 at around 6000".


Setting a value of a cell
-------------------------

To set a value of a cell we need to call ``0x30`` with the address of the cell in register ``a`` and
value to be set in register ``b``. The command itself can be put anywhere after a garbage cell so
let's put it on the furthest cell that is not already taken by parts of our program or the target
string. Then we apply the search algorithm to get the correct value of ``a`` in place for this
command, calculate what value ``b`` needs to have at the point of setting ``a`` and apply the algorithm
again to see where to set ``b`` to get its desired value at the site of setting ``a``. This lets us set
an arbitrary cell to an arbitrary value in two executions of the algorithm, consuming some finite
amount of space. If at any point we run out of space it means that the target string was placed too
early. The process can be repeated for all cells in the target string that couldn't be set directly.


Caveats
-------

The algorithm assumes that xoring ``0xF`` with the initial cell value will produce a garbage value
and not a command. This assumption can be explicitely checked and the algorithm can be easily
adjusted to skip places that would require such action. There are only 16 initial values that have
this problem (``0x00`` through ``0xF0``), because the others can be worked around by xoring with
correct upper four bits to produce garbage. This doesn't affect the algorithm in a meaningful way.

The algorithm assumes the target value of a cell is not zero, as there are only 256 initial values
in memory that could produce zero and one of them (zero itself) is not usable in that way. The
algorithm I present will not use the number zero or the command ``0x00`` so we can ignore this
problem for the sake of TC proof.

------------------------
 Cyclic Tag interpreter
------------------------

With the ability to set consecutive cells to given values all we need is the values that will
produce a program capable of interpreting a Turing Complete language. For this I will be using
Cyclic Tag.


Cyclic Tag
----------

The Cyclic Tag I will be using will work with programs consisting of symbols ``1``, ``2`` and ``3``, and
start with the data tape with the ``1`` symbol. If execution encounters the symbol ``1`` and the first
symbol of the tape is ``1`` it will append ``1`` to the tape's end. Similarily if executions encounters
``2`` and the first symbol of the tape is ``1`` it will append ``2``. If it encounters ``3`` it will remove
and print the first symbol of the tape. The program is looped until the data tape contains any
symbols.


Pseudocode of the interpreter
-----------------------------

The interpreter will compile the commands of the CT program into the area before its own code (if
it's not enough the interpreter can be put further in memory) and use space after its code for the
data tape.

::

    Initialize variables PP and X to 1;
    Initialize variables TS and TE to after the program;
    For each symbol in the input:
        If it's not 1, 2 or 3:
            Compile jump to 1 at PP;
            Jump to 1.
        If it's 3:
            Compile this code at PP:
                Set function 3 return value to PP + offset;
                Jump to function 3;
            Set increment PP by offset (offset must be enough for the cells to not overlap).
        Similar for 2 and 1 with functions 2 and 1.

    Function 1:
        If X is 2: jump to return.
        Compile this code at TE:
            Put 1 into register a;
            Jump to return point in function 3.
        Set TE to after the compiled code;
        Return: jump to return address.

    Function 2:
        Same but puts 2 into register a.

    Function 3:
        If TS == TE: halt.
        Jump to TS.
        Return point:
        Set X to value of register a;
        Print register a;
        Set TS to point at the next cell;
        Jump to return address.


Code of the interpreter in the python intermediate language
-----------------------------------------------------------

For the sake of compilation I have devised a set of names and functions that abstract over the
literal numbers representing the code. This is the code that will compile to the above algorithm::

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


Target program string
---------------------

What I want the above program to compile to, assuming it's at address N. Question marks represent a
cell that can have any value.

==== ========= ========= ========= ========= ========= ========= ========= ========= ========= =========
     0:        1:        2:        3:        4:        5:        6:        7:        8:        9:
==== ========= ========= ========= ========= ========= ========= ========= ========= ========= =========
  0: <0xe0>    <0x2f>    <0x31>    <0x60>    <0xc0>    <0x60>    <0xf>     [17]      <0x30>    <0xf>     
 10: [23]      <0x30>    <0x2f>    <0x3>     <0x5f>    [115]     <0x1f>    (?)       <0x2f>    <0x2>     
 20: <0x5f>    [52]      <0x1f>    (?)       <0x2f>    <0x1>     <0x5f>    [40]      <0x1f>    [170]     
 30: <0xf>     [86]      <0x30>    <0x1f>    [129]     <0xf>     [111]     <0x30>    <0x3f>    [62]      
 40: <0x1f>    [212]     <0xf>     [86]      <0x30>    <0x1f>    [171]     <0xf>     [111]     <0x30>    
 50: <0x3f>    [62]      <0x1f>    [251]     <0xf>     [86]      <0x30>    <0x1f>    [213]     <0xf>     
 60: [111]     <0x30>    <0x1f>    <0x7>     <0x2f>    <0x1>     <0xb0>    <0x60>    <0xf>     [65]      
 70: <0x30>    <0xf>     [96]      <0x30>    <0xf>     [116]     <0x30>    <0x90>    <0x1f>    <0xf>     
 80: <0x30>    <0x60>    <0x2f>    <0x1>     <0xb0>    <0x1f>    (?)       <0x30>    <0x60>    <0xb0>    
 90: <0x1f>    <0x1f>    <0x30>    <0x60>    <0xb0>    <0x1f>    <0x1>     <0x30>    <0x60>    <0xb0>    
100: <0x1f>    <0x30>    <0x30>    <0x60>    <0xb0>    <0x1f>    <0x3f>    <0x30>    <0x60>    <0xb0>    
110: <0x1f>    (?)       <0x30>    <0x3f>    [0]       <0xf>     <0x1>     <0x1f>    <0x3f>    <0x30>    
120: <0x2f>    <0x1>     <0x60>    <0xb0>    <0x1f>    <0x1>     <0x30>    <0x3f>    <0x1>     <0x2f>    
130: <0x2>     <0x1f>    <0x1>     <0x5f>    [169]     <0x2f>    <0x1>     <0x1f>    <0xf>     <0xf>     
140: [253]     <0x30>    <0x60>    <0xb0>    <0x1f>    <0x1>     <0x30>    <0x60>    <0xb0>    <0x1f>    
150: <0x3f>    <0x30>    <0x60>    <0xb0>    <0x1f>    [221]     <0x30>    <0x60>    <0xb0>    <0x60>    
160: <0xf>     [140]     <0x30>    <0xf>     [182]     <0x30>    <0xf>     [216]     <0x30>    <0x3f>    
170: (?)       <0x2f>    <0x2>     <0x1f>    <0x1>     <0x5f>    [211]     <0x2f>    <0x1>     <0x1f>    
180: <0xf>     <0xf>     [253]     <0x30>    <0x60>    <0xb0>    <0x1f>    <0x2>     <0x30>    <0x60>    
190: <0xb0>    <0x1f>    <0x3f>    <0x30>    <0x60>    <0xb0>    <0x1f>    [221]     <0x30>    <0x60>    
200: <0xb0>    <0x60>    <0xf>     [140]     <0x30>    <0xf>     [182]     <0x30>    <0xf>     [216]     
210: <0x30>    <0x3f>    (?)       <0x1f>    [253]     <0x2f>    [253]     <0x5f>    [252]     <0x3f>    
220: [253]     <0x60>    <0xf>     [132]     <0x30>    <0xf>     [174]     <0x30>    <0x2f>    <0x30>    
230: <0xb0>    <0xd0>    <0xf>     <0xa>     <0xd0>    <0x2f>    <0x4>     <0x1f>    [253]     <0xb0>    
240: <0x60>    <0xf>     [214]     <0x30>    <0xf>     [220]     <0x30>    <0xf>     [238]     <0x30>    
250: <0x3f>    (?)       <0xf0>
==== ========= ========= ========= ========= ========= ========= ========= ========= ========= =========
