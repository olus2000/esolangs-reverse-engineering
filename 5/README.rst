================================================================================
                                     Green
================================================================================

In May 2024 the fifth edition of Esolangs Reverse Engineering contest took
place. I took part in the contest and have compiled `my solutions`_ to the given
problems, `the languages`_ that I implemented to solve these problems and
`an explanation`_ of the challenge language along with some general guidance to
how I approach understanding such systems.

.. _my solutions: ./solutions/README.rst
.. _an explanation: ./deobf_stages/README.rst
.. _the languages: ./compiler/README.rst


The challenge
=============

As it is customary the form of the contest requires participants to write
programs in a language invented by the host while only having been given
obfuscated source code for the interpreter of that language. Green turned out to
be a tree-based language with single-letter primitive operations, with an added
layer of huffman encoding on top. To solve the problems we had to both figure
out the solutions in terms of the primitive tree operations and figure out the
huffman encoding algorithm such that the interpreter decodes them correctly.


Summary of problems
===================

This event was meant to be easier than last editions, so the staple hardest
problem of ERE, proving Turing Completeness, is not present. Instead you can see
a couple tree-related challenges, inline with the theme of this edition.

1. Implement a terminating ``cat`` program - 1 point

2. Repeat the input twice - 1 point

3. Hello, world! - 1 point

4. Sort input bytes - 5 points

5. Display a ballanced AVL tree of input bytes - 8 points

6. Output the digital root of a number - 8 points

7. Truth machine - 2 points

8. Non-empty quine - 5 points

9. Construct a prefix trie of the input - 10 points

10. Construct a suffix trie of the input - 15 points

In addition to those the organiser provided two warmup tasks, not directly
related to programming in Green:

1. Provide an input that segfaults the interpreter - 1 point

2. Explain what the `attached program`_ does - 1 point

In addition to those I set another challenge for myself. Parallel to this round
of ERE ran `round #59 of code guessing`_, for which the task involved
implementing an interpreter of a modified version of `one of my languages`_.
Having already won two editions of ERE I decided to flex on the community and
make my submission to this code guessin in Green.

.. _attached program: ./deobf_stages/test1.prog
.. _round #59 of code guessing: https://cg.esolangs.gay/59/
.. _one of my languages: https://esolangs.org/wiki/PricK


The languages
=============

To solve this year's problems I implemented two languages that compile to Green:
Simple Green that is barely a language of its own and corresponds directly to
Green's internal command structure, and Phrog which is a concatenative
stack-based system with familiar control flow and struct definitions. Simple
Green allows precise control over the compiled binary, which is great because
size is one of the factors contributing to ranking in the contest. A golfed
solution is no good though if you can't write it in the first place though, so
for harder problems Phrog offers layers of abstraction that relieve you from
thinking in terms of tree manipulation commands.
