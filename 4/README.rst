================================================================================
                       Esolangs Reverse Engineering 4
================================================================================

My solutions to the 4th esolangs reverse engineering contest.


Problem
=======

This time we were given a C source file along with a header file, and two binary
examples. There were points to be gained from understanding what the examples do
as well as writing programs to fulfill the following tasks:

1. Skip the first bit and last bit of the input - two programs worth 1 point
   each.

2. Repeat the input - worth 1 point.

3. Display "Hello" in binary in ASCII - worth 1 point.

4. Sort the input bits - worth 5 points.

5. Increment and decrement a binary number - two programs worth 10 and 15 points
   respectively.

6. Determine whether the input contains the same amount of zeros and ones -
   worth 10 points.

7. Truth machine - worth 2 points.

8. Simulation of another programming language - an exponential amount of points
   based on the computational class of the language.

Original files can be found unchanged in `the archive`_. To compile the
inerpretter run ``gcc interp.c -o interp``, and then to run a program ``./interp
program.bin <input>``.


.. _the archive: ./interp.tar


Structure of this folder
========================

There are three folders:

1. compiler_ - Tools I made and used when solving the challenge can be found
   here.

   1. `emulator.py`_ - Most of my work went into this file from the very first
      attempt at reimplementing the decoding. It can be run and contains two
      compilers: one for a simple substitution syntax and another for a more
      involved syntax utilizing all language features.

   2. `compiler.factor`_ - My final (mostly failed) attempt at optimization. It
      adds identifiers to the basic substitution syntax and checks possible
      encodings for the most effective one.

   3. `bct_generator.py`_ - File I used to generate long, halting test cases for
      the bitwise cyclic tag interpreter.

2. `deobf_stages`_ - Partially deobfuscated versions of the interpreter.

   1. `raw_interp.c`_ - The original file but with added line breaks and
      indentation. Won't work without the header file.

   2. `deobf_interp.c`_ - Like the last stage but with all the ``#define``
      obfuscation resolved. Header file no longer needed.

   3. `understood_interp.c`_ - Fully deobfuscated file with comments and proper
      verbose names.

3. `solutions`_ - A jumble of source codes and binary files solving the tasks.

   1. ``*.bin`` - Compiled files ready to be run by the interpretter.

   2. ``*.ab`` - Simple substitution syntax source files.

   3. ``*.abc`` - Full syntax source files.

   4. ``*.fab`` - Modified substitution syntax for use with the Factor compiler.


Explanation
===========

Uhhh maybe at some point? It's basically just an elaborate substitution engine
with a funny predictive decoding mechanism. Just keep looking at the `understood
source`_, surely you will understand it, it's easy 🤡
