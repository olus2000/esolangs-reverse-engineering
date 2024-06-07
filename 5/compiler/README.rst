================================================================================
                      Compilers for Simple Green and Phrog
================================================================================

For the 5th round of the Esolangs Reverse Engineering contest I used two
programming languages that compile to the challenge target, Green. The first of
them, Simple Green, corresponds almost one-to-one to the internal representation
the actual Green code gets decoded to in the interpreter. The other is a higher
level concatenative language supporting global variables, structs and of course
two stacks.


Usage
-----

Both compilers are Factor scripts that can either be used with the ``factor``
executable or compiled to standalone executables. You may need to adjust the
``USING:`` and ``IN:`` clauses in the files to correctly reflect your file
structure in the places where the files ``USE:`` each other.

To use the Simple Green compiler run::

  factor simple/simple.factor source-file > dest_file

To use the Phrog compiler run::

  factor compiler.factor source-file > dest_file


Simple Green
============

As mentioned this language is based on the internal representation the Green
interpreter uses for its code. It supports the Green commands, number and
character literals, and comments. To understand its behavior you should probably
have a solid understanding of `Green itself`_.

.. _Green itself: ../deobf_stages/README.rst


Grammar
-------

The grammar is very simple::

  program   := { command | number | character | comment | other }
  command   := [A-W]
  number    := digit digit
  digit     := [0-9] | [a-f]
  character := "'" .
  comment   := '(' { [^(] | comment } ')'
  other     := [^A-W0-9a-f'()]

All whitespace between elements falls into the ``other`` category and is
ignored.


Commands
--------

Commands make up most of any Simple Green program. They are denoted by the
capital letters ``A`` through ``W`` and correspond to the Green internal
commands:

======= ========================================================================
Command                                  Action
======= ========================================================================
 ``A``  Add a child to the current node (you should use literals instead)
 ``B``  Remove the first child from the current node
 ``C``  Copy a child or a sibling of the current node to the second register
 ``D``  Paste the value in the second register relative to the current node
 ``E``  Set the value of curent node to the sum of all values in its subtree
 ``F``  Negate values of all nodes in the current node's subtree
 ``G``  Set the current node's value to the number of its children
 ``H``  Swap nodes between the two registers
 ``I``  Perform the "rotate down" operation on the current node
 ``J``  Perform the "rotate up" operation on the current node
 ``K``  Set first register to a deep copy of the current node's subtree
 ``L``  Set first register to the current node
 ``M``  Move up the parent pointer of current node (inconsistent, don't use)
 ``N``  Move to the child of current node
 ``O``  Move to the sibling of current node
 ``P``  Move to the node in the first register
 ``Q``  Jump forward or backward in the program based on the current value
 ``R``  Output the lowest 8 bits of the value of the current node as a byte
 ``S``  Load a byte to the value of the current node
 ``T``  Set the value of the current node to the product of values in registers
 ``U``  Prettyprint the subtree of the current node
 ``V``  Go to the root node of the tree
 ``W``  Conditionally jump in the program based on the current value
======= ========================================================================

For a more detailed description of these commands look at the Green explanation
in `deobf_stages/README.rst`_.

.. _deobf_stages/README.rst: ../deobf_stages/README.rst


Literals
--------

There are two types of literals supported by Simple Green: numbers and
characters. Their semantics is to add a child node to the curret node, just like
the ``A`` command. A number literal is two lowercase hexadecimal digits, and a
character literal is the character ``'`` followed by any character. They are
compiled into an ``A`` command followed by a byte of a given value.


Comments
--------

Everything that doesn't parse as anything else is a comment, but you should
explicitly put comments in parenthesis to make sure their parts don't get parsed
as code by accident. Comments can be nested.


Phrog
=====

This is a higher level language made to easier implement some of the more
complicated challenges, especially the solution to cg59_. It's a stack language
with support for an auxiliary stack, global variables, structs, and (coming
soon) functions.


Grammar
-------

Phrog lexes its programs into space-separated tokens, which are then subject to
the following grammar::

  phrogram    := vars structs body
  vars        := { word }
  structs     := { ":" word word { word } }
  body        := { comment | loop | conditional | literal | word }
  comment     := ";" <any sequence of characters up to a newline>
  loop        := "begin" body "while" body "repeat"
  conditional := "if" body [ "else" body ] "then"
  literal     := number | character
  number      := "#" { [0-9] } (as a single token)
  character   := "'" . (as a single token)
  word        := <any token that isn't a keyword or a literal>

No function definitions yet, but hopefully I will add them before releasing
this.


Stacks and variables
--------------------

Phrog is a stack-based language, meaning that most of the operations are
executed on implicit arguments passed through the data stack. Every phrogram
starts with an empty data stack and an empty auxiliary stack, but if you need
more space to store data you can declare global variables at the start of your
file. They start uninitialised so you have to write to them before reading them.

Every variable will define two words: a getter, named the same as the variable,
will push the value of a variable to the stack; and a setter, named like the
getter with a ``!`` at the end, will set the variable to a value popped from the
stack. For example declaring a variable named ``string`` will define a getter
word ``string`` and a setter word ``string!`` for use in the program's body.

**Warning:** Getters can shadow builtin primitive words if you declare a
variable named the same as one. Make sure to not declare variables named the
same as words you intend to use in your program!


Types and structs
-----------------

Phrog supports three data types: numbers, stacks and structs. Numbers are
straightforward: they're 32 bit signed integers (or whatever C ``int`` compiles
as). Stacks are simple as well: you can create an empty stack with ``{}``, and
then use ``push``, ``first`` and ``pop`` words to modify it and access the
top element. Both stacks and structs are mutable values passed by reference, so
unless you explicitly ``clone`` one all writing operations will affect all
references.

Structs are programmer-defined data structures similar to Factor's tuples. A
struct declaration starts with ``:`` and a name of the struct, followed by names
of struct fields. Each struct declaration defines a constructor for that struct
that is a word that takes as many arguments as the struct has fields, and
creates a new instance of that struct with these values assigned to the fields.
It will also define a getter and a setter word for each field.

For example this struct declaration::

  : fraction numer denom

Will define a constructor ``<fraction>`` that takes the denominator on top of
stack and numerator as second on the stack and creates a fraction. It will also
define ``>>numer`` and ``>>denom`` words that take a value on top of stack and
a fraction as second on the stack and leave a fraction with the field updated.
Finally it will define ``numer>>`` and ``denom>>`` words that pop a fraction and
push the value of the respective field.

**Warning:** Field names will shadow each other. If you need structs to share
the same field names put the fields at the same position *counting from the
end*. They will also shadow variable names so avoid using the constructor,
getter and setter naming conventions in your variables.


Main body
---------

Body of the program starts with any keyword not legal in struct declarations (I
encourage starting with a comment). It is built of control flow constructs,
comments and literal values, but most of all of words. Words correspond to
builtin primitives, variable access and struct access/creation. They are
executed one after the other as they come, acting on the stack and variables.
Any sequence of non-whitespace characters that isn't a keyword or a literal
value is considered a word. Undefined words in the program result in a compiler
error.

Program body is the place where comments are allowed. They start with the ``;``
keyword (requiring whitespace after it) and continue until a newline. Anything
within a comment is ignored.


Number and character literals
-----------------------------

At the start of execution your stacks and variables are empty. To create some
values to operate on you use literal values. They come in two types: number
literals are the ``#`` character followed by decimal digits and represent
nonnegative decimal numbers, and character literals are the ``'`` character
followed by any other character (including whitespace or unicode), and they
correspond to that character's unicode value. Whenever a program execution
encounters a literal value it is pushed to the data stack.

Phrog compiler expects files encoded with utf8.


Conditionals and loops
----------------------

In terms of control flow Phrog offers Forth-style ``if`` and ``while``
statements. ::

  conditional := "if" true-branch [ "else" false-branch ] "then" 
  loop        := "begin" predicate "while" body "repeat"

Unlike applicative languages (a.k.a. most languages) Phrog ``if``\s don't need a
dedicated predicate expression, they just pop a value off the stack and branch
depending on that. If the value is zero the ``false-branch`` is executed (or
nothing if there's no ``else``), and otherwise the ``true-branch`` is executed.
Either way the execution goes back to normal after ``then``.

While loops do have a ``predicate`` section, but there's no restrictions on what
you can put there. It's just a block of code like any other that gets executed
at the start of the loop. Then a value is popped from the stack and if it's zero
the loop terminates and execution continues after ``repeat``. Otherwise the
``body`` is executed and the loop repeats, running the ``predicate`` and popping
a value until it pops a zero.

It's a good practice to balance stack effects of loops and conditionals. This
means making sure that the number of elements of the stack changes by the same
amount in both branches, and that it doesn't change across one full execution of
a loop (``predicate``, ``body``, and popping the value to check looping
condition). This makes thinking about what your code does much easier since you
don't have to consider both variants of what the stack state could be after a
conditional.


Builtin words
-------------

Phrog provides a small set of builtin words, each of them was implemented when I
needed them for one of the challenges so this is definitely not a full set
required for a usable language. I use forth-like stack effect notation here: *(
a b -- c d )* means that the word pops ``a`` and ``b`` from the stack and pushes
``c`` and ``d`` as a result.

``dup`` :: *( x -- x x )*
  Duplicate the top element of the stack. It only copies a reference so any
  mutating changes happening to one will also affect the other.

``swap`` :: *( x y -- y x )*
  Swap top two values on the stack.

``drop`` :: *( x -- )*
  Discard a value from the top of the stack.

``over`` :: *( x y -- x y x )*
  Duplicate the second value on the stack to the top of the stack. It also only
  copies a reference, just like ``dup``.

``>aux`` :: *( x -- aux: x )*
  Pop a value from the data stack and push it to the auxiliary stack.

``aux>`` :: *( aux: x -- x )*
  Pop a value from the auxiliary stack and push it to the data stack.

``aux@`` :: *( aux: x -- x aux: x )*
  Push a duplicate of a value from the top of the auxiliary stack to the data
  stack.

``0>`` :: *( n -- ? )*
  Pops a number *n* from the stack and pushes 1 if *n* was greater than zero,
  otherwise pushes 0. Faster than ``>``, especially for big numbers.

``>`` :: *( n m -- ? )*
  Pops two numbers *n* and *m* from the stack and pushes 1 if *m* is smaller,
  otherwise pushes 0. It's faster to use ``- 0>``, especially for big numbers.

``=`` :: *( n m -- ? )*
  Pops two numbers *n* and *m* from the stack and pushes 1 if they're equal,
  otherwise pushes 0.

``-`` :: *( n m -- n-m )*
  Pops two numbers *n* and *m* from the stack and pushes their difference.

``<>`` :: *( n m -- n-m )*
  Alias for ``-``. The result is a truthy (non-zero) value if *n* and *m* are
  different, and falsy (zero) if they are equal.

``+`` :: *( n m -- n+m )*
  Pops two numbers *n* and *m* from the stack and pushes their sum.

``*`` :: *( n m -- n*m )*
  Pops two numbers *n* and *m* from the stack and pushes their product.

``{}`` :: *( -- {} )*
  Pushes a new empty stack to the stack (oooh, meta!).

``first`` :: *( {x} -- x )*
  Pops a stack from the data stack and pushes the value on top of that stack to
  the data stack.

``push`` :: *( {} x -- {x} )*
  Pops a stack and a value from the data stack, pushes the value to that stack,
  and puts that stack back on the data stack. Mutating operation.

``pop`` :: *( {x} -- x )*
  Pops a stack from the data stack, pops a value from that stack and pushes that
  value to the data stack. Mutating operation.

``length`` :: *( {} -- n )*
  Pops a stack from the data stack and pushes the number of elements in it to
  the data stack.

``clone`` :: *( x -- x' )*
  Pops a value from the stack and pushes a deep copy of that object to the
  stack.

``copy`` :: *( {} -- {}' )*
  Pops a stack from the data stack and pushes a shallow copy of it to the data
  stack. Useful for iterating through a stack of values without destroying the
  original.

``in`` :: *( -- n )*
  Takes a byte from input and pushes it to the stack.

``out`` :: *( n -- )*
  Pops a number from the stack and output it modulo 256 as a byte.

``.`` :: *( n -- )*
  Pops a number from the stack and outputs it in decimal.

``..`` :: *( x -- )*
  Pops a value from the stack and prints out its tree structure representation.

``debug`` :: *( -- )*
  Prints the entire underlying tree structure.

``exit`` :: *( -- )*
  Terminate the program (actualy jumps 2048383 commands forward)


Phrog implementation
====================

You may be wandering why and how I made Phrog, and it would be valuable to
explain that.


Various whys
------------

Why make a language at all should be clear: it's inconvenient to write Simple
Green for the more complex challenges, and getting some level of abstraction is
appreciated.

The language is concatenative for a few reasons. One is that I love
concatenative languages and I feel comfortable writing in them. Another is that
they're very easy to parse and compile. They don't have much syntax, and that
also makes them easy to extend - you usually only need to add a couple primitive
words. And concatenative languages make it very easy to factor out parts of code
into smaller functions, which isn't relevant here since I didn't implement
functions in Phrog yet.

I chose Factor as the implementation language because it's the most usable
concatenative language at the moment, and as mentioned I love concatenative
languages. Factor has the perfect mix of functional and imperative for me, and
(like many other concatenative languages) it's mostly implemented in itself, so
to it's easy to understand and edit the language without the need to know other
languages. It supports both running a script with an interpreter and compiling
to a binary executable. This language is a labour of love of a small community
of deveopers.


General structure
-----------------

The major issue with Green is that parent pointers of nodes are mangled by quite
a few otherwise useful commands. This means that we can only reliably go down
the tree or across the sibling links or get back to the root, which is why I
wanted to have all important data as close to the root as possible. Both of
Phrog's stacks are direct children of the root, and so are variables. This
structure is created by a preamble compiled before any code. For code with three
variables the structure made by the preamble would look like this::

  0 (root)
  |
  1-------2-------A-----A-----A
  (data   (aux    (var) (var) (var
   stack)  stack)

Every command starts by going back to the root so we don't have to worry where
the current node is left after a command finishes. Root always has a value of 0
that it starts with, which is useful for setting the ``r1`` value for ``C`` and
``D`` commands and doing unconditional jumps. Similarly the data stack root node
and the aux stack root node have values 1 and 2 respectively because of how
useful these values are for ``C`` and ``D`` purposes. Variable roots have values
65 (ascii ``A``) to make them compress better. Many nodes will have that value,
and I will be denoting it as ``A`` on the graphs.


System stacks
-------------

Data and auxiliary stacks are supposed to hold data as their children. The
problem with that is twofold:

1. The data may be composite, comprised of several nodes being each other's
   siblings

2. Copying the data would result in overwriting its sibling pointer, mangling
   the stack

To remedy that the stacks have a level of indirection: their children are ``A``
nodes that themselves have data as children. This way those throwaway nodes can
be replicated instead of being copied, and the only data subject to copying
would be their children, which doesn't mangle any pointers (apart from parent
pointers, but those are mangled already anyway). ::

  1-----2--- - - -
  |
  A-----A-----A-----A--- - - -
  |     |     |     |
  data  data  data  data

  And similar for the aux stack with root at 2


Numbers
-------

Numbers are simple. They are stored as nodes with no siblings or children, that
store the number as the node's value. Technically numbers are still copied by
reference with words like ``dup`` or ``over``, but words that operate on numbers
make sure to clone them or otherwise avoid affecting their values and
child/sibling pointers. ::


  X <- this is the "data" node for a number


Stacks as values
----------------

Apart from the two data stacks included in the system Phrog supports stacks as a
type of values, collection where only the most recently inserted values can be
accessed. Their structure is similar to that of system stacks, but with one more
level of indirection. This is because I wanted these stacks to be mutable
collections such that modification via one reference would be reflected in other
references to the same underlying object. If that reference was just a pointer
to the first ``A`` node then popping and pushing would actually change the
pointer itself, not the data it points to. This is why I added an additional
``A`` node to the structure. It also helps with calculating size of a stack. ::

  A <- this is the "data" node for a stack
  |
  A-----A-----A-----A--- - - -
  |     |     |     |
  data  data  data  data


Structs
-------

Structs have a set number of fields that doesn't change over the struct's life.
Because of that we don't need the additional level of indirection stack values
required. They must never be empty, which the compiler enforces. There are some
issues created by skipping this indirection though: when a node is in a register
but not referenced from the tree its siblings will get collected if the garbage
collecter runs. This led to multiple weird and literally random bugs, but with
carefully thinking about the order of operations my compiler is hopefully safe
from that kind of bug. ::

  this is the "data" node for a 4-element struct
  |
  V
  A-----A-----A-----A
  |     |     |     |
  data  data  data  data


The program
-----------

Compilation of a concatenative program is the easiest thing ever. There's a
piece of code associated with each command, so you just concatenate those pieces
of code to get the final program. Of course there's some logic involved in
conditionals, loops and literals, but it's mostly straightforward. For example
an ``if`` compiles to "pop a value from data stack and conditionally jump".


The quine compiler
==================

The quine challenge called for a special variation of the compiler. Apart from
just compiling the code it would also compile some code to pass the code itself
as data to the program! It also defines an additional ``pop'`` command
specifically for popping from that code structure which resembles a Phrog stack
but not quite.

The prepended piece of code creates that stack-like data structure right at the
root of the tree::

  0
  |
  e-----n-----i-----u-----Q--- - - -

Note that unlike in Phrog stacks the values are directly in the line of
children, without the additional level of indirection. The prelude of
quine-compiled programs clones this structure to the last variable and sets the
other variables normally, so the starting structure looks like this::

  0
  |
  1---2---A---A---A---A
                      |
                      e---n---i---u---Q--- - - -

It's the program's job then to process this data structure into its own code,
encode it and output it.
