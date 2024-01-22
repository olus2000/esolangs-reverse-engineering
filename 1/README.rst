================================================================================
                                      UM8
================================================================================

UM8_ is the esolang created for the first Esolangs Reverse Engineering contest.
I did not have a chance to take part in the contest, but I took a stab at it
in 2023 and managed to blindly disassemble and understand the system (with minor
mistakes on disassembly), and write the following programs.

Most work on UM8 at the time was done after the round by Matthilde_ who made
`a short writeup`_ about it.

.. _UM8: https://esolangs.org/wiki/UM8
.. _Matthilde: https://esolangs.org/wiki/User:Matthilde
.. _a short writeup: https://codeberg.org/matthilde/um8-writeup


Structure of this directory
===========================

You can see several files and direcotries here:

1. ``contest.zip`` - original code of the contest.

2. raw_ - original code of the contest, unzipped.

3. tools_ - a Factor vocab for generating code that prints constant bytes, and
   a UM8 interpreter. Used for Hello, World!

4. deobf_stages_ - files I created in the process of disassembling the
   interpreter.

   1. ``interpreter-3.0.exe`` - provided executable binary, unchanged.

   2. sectioned-3.0.dump_ - hexdump of the binary split into sections based
      on the PE file structure.

   3. disassembly-3.0.txt_ - code section of the binary disassembled by hand
      into something assembly-like, with comments, notes, and addresses.

5. `addition-attempt.txt`_ - A working program for adding two digits. I am not
   ready to explain how it works, but there's a lot of comments inside.

.. _raw: ./raw/
.. _tools: ./tools/
.. _deobf_stages: ./deobf_stages/
.. _sectioned-3.0.dump: ./deobf_stages/sectioned-3.0.dump
.. _disassembly-3.0.txt: ./deobf_stages/disassembly-3.0.txt
.. _addition-attempt.txt: ./addition-attempt.txt


Commands
========

This explanation is pretty bad. Look at the UM8_ esolangs wiki page instead for
a better one.

UM8 interpreter takes the program followed by any character that's not a valid
command followed by the input. These commands are recognised by the
interpretter, and are valid in programs with exception of E and F.

There are three byte-sized registers, each starting at 0. ::

  0 - exit
  1 - if b: a = c
  2 - a <=> c
  3 - a = ~(b & c)
  4 - write b
  5 - b = get-char
  6 - a <=> b
  7 - a = [c] - '0'
  8 - [a] = b + '0'
  9 - a = next - '0'
  A - jmp b; [0] = c + '0'
  B - a = not a (only 0 or 1)
  C - a = a >>> 1
  D - a = a << 1
  E - ???
  F - break stuff, then 1

IO: 5, 4

Calculation: 3, B, C, D

Memory: 7, 8, 9, A

Jump: 9, A

Conditional: 1, B

Data movement: 2, 3, 6

E and F aren't legal instructions in programs and may potentially break programs
when executed. With conscious planning and awareness of underlying mechanisms E
may be used to get access to more values, but getting it in the first place is
hard enough to not matter.


Hello, world!
=============

Stolen from esolang wiki, by Matthilde_::

  94DDDD294DDDD6369989829863690236496DDDD296DDDD6369989529
  563690236496DDDD296DDDD636998982986369023216369989429463
  6902364496DDDD296DDDD63699898298636902321636998972976369
  0236492DDDD292DDDD63699898298636902321636998942946369023
  6492DDDD292DDDD6369989029063690236495DDDD295DDDD63699897
  29763690236496DDDD296DDDD6369989829863690232163699897297
  63690236497DDDD297DDDD6369989229263690236496DDDD296DDDD6
  36998982986369023216369989429463690236496DDDD296DDDD6369
  989429463690236492DDDD292DDDD6369989129163690236491DDDD2
  91DDDD6369989029063690236491DDDD291DDDD63699893293636902
  364

Matthilde's approach (outlined in `her writeup`_) is based on splitting bytes
into 4 or 3 bit parts and combining them with a NAND operation (``3``). This has
big drawbacks, because every usage of ``3`` takes up all three registers which
requires storing any intermediate data in memory (see extensive use of ``8`` in
presented code). Fortunately I am too dumb to actually figure out how to do it
so I ended up finding a simpler, shorter solution.

My naive approach::

  91691DD2163D2163DDD64912163D2163DD2163D2163D2163D2163649
  12163D2163D2163DD2163DD64912163D2163D2163DD2163DD6491216
  3D2163D2163DDDD21636491D2163DD2163DD6491DDDDD6491D2163D2
  163D2163DDD216364912163D2163D2163DDDD216364912163DD2163D
  D2163D2163D64912163D2163D2163DD2163DD64912163D2163DD2163
  D2163DD6491DDDD2163D21636491D2163D2163D64

I start from the value 1 (``91``) and then keep shifting it left (``D``) and
doing bitwise not (``2163``) until I achieve the desired byte. The naive
generation I used will fail on 0 bytes but they can be easily specialcased. It
also needs a non-zero value in register b which is why it starts with ``916``.

This simplistic approach can be improved easily by starting not with 1 but with
a bigger value matching the desired bit pattern more closely. For example
getting the letter H previously was done with ``91DD2163D2163DDD`` (start with
1, shift, twice, not, shift, not, shift thrice) it could be achieved from the
value represented with the letter B (18) by just shifting it twice (``9BDD``).
This cut about 2/3 of the code.

My optimized approach::

  9169BDD6496D2163D2163D2163D216364962163DD2163DD64962163D
  D2163DD64962163DDDD216364952163D2163DD6498DD6495D2163DDD
  216364962163DDDD21636497DD2163D2163D64962163DD2163DD6496
  D2163D2163DD6498D2163D21636495D64

.. _her writeup: `a short writeup`_

Halting cat
===========

::

  942986A649629D516A

Breakdown of the solution:
  
* ``942``  - put 4 in c to not break code when jumping

* ``986A`` - jump into the loop overwriting the 4 with 4

* ``64``   - loop start, print what was in a

* ``962``  - loop entry, put address of loop start in c

* ``9D``   - put big address in a

* ``516A`` - getc and jump to either loop start or big address


Truth machine
=============

My solution terminates when given an even byte and loops when given an odd byte::

  56649C891232616369129AD1690A

Breakdown of the solution:

* ``56``      - get input and prepare for loop

* ``64``      - loop start, output

* ``9C8``     - store the character where the ``0`` is

* ``9123``    - ``nand`` the character with 1

* ``26163``   - ``not`` the result, extracting the least significant bit of the
  character

* ``69129AD`` - prepare the loop address in c and big address in a

* ``16``      - if input was even put big address in b, otherwise put loop
  address

* ``690A``    - load what was saved earlier where the ``0`` is and jump
