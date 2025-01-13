================================================================================
     Esolangs Reverse Engineering 6: 4D Befunge with Destructive Time Travel
================================================================================


Not much in terms of the writeup this time. It was the simplest challenge in the
series yet, but I still enjoyed it a lot (especially that I didn't have as much
time to spend on it than previous rounds). I didn't make a ton of tooling or a
compiler, but there's still a bit of Factor code I wrote to help me decode and
encode programs.


Language
========

Despite its name the language is 2D and its time travel aspect is not
destructive. It runs on a grid with each cell represented by a 2x2 square of
characters in the source code. Each character is read as a base-94 digit by
taking its ASCII value and subtracting 32 (so space is 0 and ``~`` is 93). The
instruction pointer starts in the top left corner and proceeds to the righ,
though it can change directions over the course of execution.

One important thing to note is that the cells behave erraticly if a negative
number is ever stored in one. It is consistent, but I won't be trying to explain
what's going on there. To solve the challenges you only need to know that
storing a -1 will result in some negative value in the cell.


Instruction format
------------------

To decode the instruction the cell's numeric value is split into one base-94
digit and up to four base-24 digits. The base-94 digit decides what operation
the cell represents, and a balanced base-24 digits indicate coordinate offsets
at which parameters for the operation are located. This is somewhat confusing,
so let me go through decoding a cell::

  Cell in the source code:
    
    +W
    [%

  Decoded into a value:

    + -> ASCII 43 -> digit 11
    W -> ASCII 87 -> digit 55
    [ -> ASCII 91 -> digit 39
    % -> ASCII 37 -> digit 5

  Total cell value: 9627955

  Decoded into the command elements:

    9627955 / 94 = 102425 rem 5  -> command 5
    102425  / 24 = 4267   rem 17 -> offset y1  6
    4267    / 24 = 177    rem 19 -> offset x1  8
    177     / 24 = 7      rem 9  -> offset y2 -2
    7       / 24 = 0      rem 7  -> offset x2 -4

So in this example we ended up with the command 5, first argument at offset
(+8, +6) and second argument at offset (-4, -2). Let's now see what the commands
actually do.


Commands
--------

Available commands range from 1 to 21. All other command numbers are ignored and
treated as no-ops. For each command I will say how many arguments it takes and
in their descriptions I will refer to the argument at (x1, y1) as ``X`` and the
argument at (x2, y2) as ``Y``.

=== ==== ========================================================
Com Args Description
=== ==== ========================================================
 1   2   ``Y += X``
 2   2   ``Y -= X``
 3   2   ``Y *= X``
 4   2   ``Y /= X`` (integer division)
 5   2   ``Y %= X``
 6   2   ``Y`` is set to 1 if ``Y`` is equal to ``X``, else 0
 7   2   ``Y`` is set to 1 if ``Y`` is not equal to ``X``, else 0
 8   2   ``Y`` is set to 1 if ``Y`` is smaller than ``X``, else 0
 9   2   ``Y`` is set to 1 if ``Y`` is greater than ``X``, else 0
10   2   ``Y ||= X``
11   2   ``Y &&= X``
12   1   output ``X`` as a character
13   1   read a character to ``X`` (it may be broken)
14   0   change direction of the instruction pointer to left
15   0   change direction of the instruction pointer to right
16   0   change direction of the instruction pointer to down
17   0   change direction of the instruction pointer to up
18   1   move the instruction pointer back in time ``X`` steps
19   0   halt the program
20   1   print ``X`` as a decimal number
21   1   read a number to ``X``
=== ==== ========================================================

Note that there aren't any conditional jumps or such, so the main ways of
control flow I used were changing the directional commands or switching time
jump to halt. In any case, self-modification is necessary.


Solutions
=========

I won't be talking in-depth about my solutions, but I will describe the
pseudocode format I employed. It consists of three sections: linear algorithm,
variables and constants, and the layout.

The linear algorithm is just a list of instructions to run the algorithm. They
reference variable and constant names from the variables and constants section.
So for example ``Y += 32`` would be a use of command 1, and ``D < 93`` would be
a use of command 8. There are also some labels to indicate jumps.

Variables and constants are a list of, well, variables and constants used in the
program. They are all listed because each of them needs to actually have a cell
dedicated to it in the program so they all need to be included in the layout.

Layout is how the program is laid out on the 2D grid. The lines (``-`` and
``|``) correspond to commands from the linear algorithm, sometimes interjected
by turning commands (``>``, ``<``, ``^`` and ``v``). Dots (``.``) indicate ends
of execution (either halts or time jumps), and spaces indicate empty tiles. Any
other letters correspond to variables and constants, either specifically if they
were given a one-character name, or just by a vague ``x``.

You can see the actual code used to compile some of the more complex solutions
in the Factor file ``6.factor`` that also includes my tooling for the challenge.
