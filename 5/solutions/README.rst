================================================================================
                                   Solutions
================================================================================

This folder aggregates my solutions to the problems of this round. They are
split into three folders: ``simple`` stores the solutions written in Simple
Green, ``phrog`` stores the solutions written in Phrog, and ``bin`` stores the
compiled binary forms ready for execution with the Green interpreter.


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

.. _attached program: ../deobf_stages/test1.prog
.. _round #59 of code guessing: https://cg.esolangs.gay/59/
.. _one of my languages: https://esolangs.org/wiki/PricK


Attached program
================

Let's start with the warmup. The sample program when decoded to Simple Green
looks like this::

  '0 '1 '2 UN '0 '1 '2 MUBU '3 '4 '5 EUIU

Let's walk through this to help you get familiar with the language:

1. The program starts with a single root node with a value zero, which has no
   children or siblings.

2. Three child nodes are created for this root with values of ASCII ``0``, ``1``
   and ``2``. The order of creation makes it so that ``2`` is the direct child
   of the root node, and the others can be reached via sibling pointers. This
   state of the tree is printed with ``U``::

    0
      50
      49
      48

3. The execution moves down from the root (the ``N`` command) to the ``2`` node
   and adds three new nodes to it, again with values ASCII ``0``, ``1`` and
   ``2``. The command ``M`` goes to the parent of the current node, so back to
   the root, and another ``U`` prints the current state of the tree::

    0
      50
        50
        49
        48
      49
      48

4. Command ``B`` removes the first child (the ``2`` node) from the root. This
   time the ``U`` output looks like::

    0
      49
      48

5. Three more nodes are added to the tree, this time with values ASCII ``3``,
   ``4`` and ``5``. The ``E`` command adds the value of all nodes in the tree
   and stores it in the root, resulting in the ``U`` output of::

    253
      53
      52
      51
      49
      48

6. Finally a "push down" operation is performed by ``I``, giving us the final
   ``U`` output::

    253
      52
        53
      51
      49
      48

This short program showcases some basic tree operations with commands ``NMBEI``,
prints intermediate tree states with ``U`` and the ``A`` operation also works
there, since that's what the node creation gets compiled to.


Segfault
========

I implemented two ways of segfaulting the provided intepreter of Green. One of
them exploits the decoder to eat up all available RAM, and the other works
within the language to try executing code from outside the program.

The first solution is found in `preprocessor_segfault.bin`_ and it
consists of a single ``A`` byte. In fact any single byte that has the highest
bit equal to 0 will work like that. The preprocessor will read the 0 bit,
consume another 8 bits (getting 1s after end of file) and create an entry in the
Huffman tree corresponding to the byte represented by these 8 bits::

     Root
      /\
     a  b
    /    \
   ?    byte

Since it aready read the byte in the file it will keep getting 1-bits because
that's what C does for end-of-file, and those 1-bits will keep instructing it to
go along the ``b`` branch and add ``byte`` to the program forever, until it runs
out of memory. (For more info on how the preprocessor works see
`deobf_stages/README.rst`_)

The second solution is found in `segfault.prog`_::

  80 NLHLTF VW

A node holding the byte hex ``80`` is created, but because the program is stored
as signed characters it gets sign extended to the value -128. It is loaded to
both registers, multiplied with itself and negated to obtain the value -16384
which then is used for a relative jump. This causes the interpreter to attempt
to read program from an invalid address which results in a segfault.


.. _preprocessor_segfault.bin:
   ./bin/preprocessor_segfault.bin
.. _segfault.prog: ./simple/segfault.prog
.. _deobg_stages/README.rst: ../deobf_stages/README.rst


Terminating cat
===============

Now let's start with the actual challenges. A terminating cat is a loop that
takes input, checks whether it is equal to -1, and if not then outputs it and
repeats. Input and output are just ``S`` and ``R`` commands, so the difficulty
is making the jump. The skeleton of the solution looks like this::

  S 01 EB

  (if zero jump past end)

  ff EB R

  (jump back to start)

Because jumping over the end of the program will always terminate safely we can
reuse the same relative jump distance for both jumps. For the forward jump we
will use ``W``, because we don't want to pick between jumping or not jumping,
not between jumping either direction. For the backward jump we will do ``Q``,
since this jump will always happen in one direction and using ``Q`` we can
invert the direction of the jump. We will need to set up the jump distance in
``r1`` first::

  (jump-distance) NLVB 00

  VS 01 EB W

  ff EB R NQ

And we see that our jump distance is 14, because we need to jump from ``Q`` to
*before* the ``VS``, and creating a new node takes up two bytes. The final
program in Simple Green is::

  0e NLVB 00
  VS 01 EB W
  ff EB R NQ


Repeat input
============

This is just like cat, but twice! Unfortunately that means it's nothing like
cat. Sure, we still have to read and print the input, but now we also need to
store it somewhere for later copying.

We're in a tree language, so the intuitive approach would make a chain of
children, or siblings, but both of those have their problems: for siblings it's
hard to add them in the correct order, and having arbitrary data among node's
children makes it hard to do math on that node. Instead we will make a sort of a
linked list with nodes like this::

     node
      /\
     /  \
    /    \
  char  next_node

This way we can keep appending new nodes as we add characters and are free to do
math on the chars. The reading part of the solution is similar to cat::

  14 08 NLHOLVBB
  00 'A NS 01 EB HW
  ff EB R OHQ

This time we load up two jump distances and switch between them with ``H``. From
``Q`` we want to jump back by 20 (``14`` in hex), and from ``W`` we want to jump
forward by 8.

The next part is very similar but instead of building the structure as we read
input we are traversing an already existing structure. We will reuse the longer
jump distance we already have set up so some padding will be required. ::

  VH
  N 01 EB BBBBBBB W
  ff EB R OQ

This could surely get golfed further, but it's good enough for me. (Btw calling
``B`` with no children is safe as long as you didn't mess with your tree's root.
It will just set the root's parent to itself (which it should have already been)
and your child to root's sibling (which should be root/zero))


Hello, world!
=============

This is actually the easiest challenge of them all. You just create a new node
with the desired letter, go to it, output it, and repeat. ::

  'H NR 'e NR 'l NR     R 'o NR ', NR '  NR
  'w NR 'o NR 'r NR 'l NR 'd NR '! NR

I doubt you can golf it significantly, but you're welcome to try.


Sort input bytes
================

This challenge isn't trivial, and writing stuff with multiple jumps in Simple
Green is a pain. Sure would be nice if there was another language we could use
to solve these challenges!

Yes, this is time to switch to Phrog. Its output isn't golfed by any means (in
fact there are some very simple optimisations that could be done), but I'm fine
with just having completed the challenge. If you want to learn how Phrog works
internally check out `compiler/README.rst`_.

So I'm thinking the ugliest stack-based code you've ever seen: keping all input
on the stacks, some guards on the edges, and run a selection sort over it. Yeah,
that sounds just jank enough. ::

  ; Selection sort. No vars or structs needed.

  #256                                  ; A guard value

  begin in dup #1 + while repeat drop   ; Just read *everything*

  #256 >aux                             ; Another guard value for good measure

  begin dup #256 = #0 = while           ; Until all actual values are exhausted
    begin over #256 = #0 = while        ;   Until we have only one value left
      over over > if swap then >aux     ;     Send the bigger one to aux stack
    repeat out                          ;   Output the smallest value
    begin aux> dup #256 = #0 = while    ;   Fetch all values back from aux
    repeat >aux                         ;   Get the guard back there again
  repeat

Ah yeah, that felt awful. What horrible code, I hate it.

.. _compiler/README.rst: ../compiler/README.rst


AVL tree
========

Ok so in a tree-based language with a builtin tree printing feature it would
make sense to write the tree building challenge directly in the language. Well,
TOO BAD, because that's another challenge that requires comparing numbers, and
those are ass to write in Simple Green, so we're going with Phrog again.

If you know the AVL algorithm you probably recall its convoluted 6-case (or was
it 8?) self-balancing bullshit. We ain't touching any of that here. We don't
need to implement a full AVL tree with insertion and deletion operations, we
only need to build one from a given list of data, so the plan is: sort the data,
make the middle value the head of the tree, and build left and right subtrees
from the left and right halves of the rest of the data. The result is guaranteed
to be ballanced and all, but will be way simpler to implement (and will have
much worse time complexity but shhhh).

This time we will actually use variables and structs to organise our data. We're
gonna keep a list of unfinished trees along with their depths to work around the
fact that Phrog doesn't have functions and a call stack. ::

  trees

  : tree data depth

For sorting values we can use a similar selection sort approach as in the
previous problem::

  ; AVL Tree

  {} begin in dup #1 + while push repeat    ; Gather input into a list
  drop

  {} swap begin dup length while            ; Until we run out of values
    {} >aux
    dup pop begin over length while         ;   Scan through all the values
      over pop over over > if swap then     ;     Keep the smallest element
      aux> swap push >aux                   ;     Move the rest to another list
    repeat swap drop push aux>              ;   Add the smallest to a list
  repeat drop

This leaves us with a list of neatly sorted values on the stack. All we need to
do now is use the not-so-recursive algorithm to keep splitting that in half and
printing the middle value until we print everything. ::

  #0 <tree> {} swap push trees!             ; Set up our list of trees

  begin trees length while                  ; Until we process all of them
    trees first data>> length if            ;   If there's any data
      trees first dup depth>>
      dup begin dup while
        #32 out #32 out #1 -                ;     Print indentation
      repeat drop
      #1 + >>depth
      data>> #0 over length                 ;     Claculate half of data size
      begin dup #1 > while
        swap #1 + swap #2 -
      repeat drop
      >aux {} begin                         ;     Move that much to new list
        aux> dup #1 - >aux while
        over pop push
      repeat aux> drop
      {} begin                              ;     Reverse the new list
        over length while
        over pop push
      repeat swap drop
      trees first depth>> <tree>            ;     Make a new tree from new list
      trees swap push drop
      pop .                                 ;     Print the middle item
    else trees pop drop then                ;   If there's no data drop the tree
  repeat

The less stack-minded among you may wonder how is this better than using raw
Simple Green, but I assure you not having to set up jumps and implement
comparison is worth it. Phrog could use some improvements, but for now it's Good
Enough™️.


Digital root
============

This is just a simple loop: as long as a number is greater than 10 split it into
digits and sum them. But we can do better! Because of mathematical properties of
stuff taking a digital root is equivalent to getting the remainder from division
by one less than the base we're using (in our case it's decimal so we're doing
mod 9). Nothing to think about really if you're using Phrog. ::

  ; Digital root. No vars or structs needed.

  ; Sum the input digits
  #0 begin
    in dup #1 + while
    '0 - +
  repeat drop

  dup if
    ; If the sum is non-zero calculate the remainder
    begin
      dup #9 - 0> while
      #9 -
    repeat
  then .

That's it! Notice one special case: if the initial number is zero we output
zero, but otherwise if the remainder of division by 9 is zero we actually need
to output 9.


Truth machine
=============

Let's take a break from hard problems. A truth machine is as simple of a concept
as they get, and since I'm not winning on byte count anyway I can make it behave
nicely as well. My goal for this one is to treat an odd input as 1 and an even
input as 0, so that it works both with literal ``0`` and ``1`` bytes as well as
the ASCII digits. And we will be making this in Phrog because I can't be
bothered to work in Simple Green anymore. ::

  ; Truth machine. No vars or structs needed.

  in dup begin                      ; Take input and keep a copy
    dup #1 > while                  ; Decrement by two until you get 0 or 1
    #2 -
  repeat

  if                                ; If you got 1
    begin #1 while dup out repeat   ; Output the original copy infinitely
  else out then                     ; Otherwise output it once


Non-empty quine
===============

**Four days** after the deadline. I was obsessing over writing this thing for
most of the second week, and I needed four more days of rest, giving up,
pursuing other stuff, getting some minor ideas and failing over and over again
to get this one to work in acceptable time. It still takes over an hour to
execute on my computer and can definitely be optimised by rewriting it in Simple
Green, but to my knowledge I am the author of the first Green quine.

Thanks to `@blaumeise20`_ for the idea for the ``0>`` operator, which is both
faster and smaller than the ``>`` operator.

Ahhhh, quine......

How to do a quine again? You need to conceptualize the code as two parts. The
first one creates a string representation of the second part, as repetetively as
possible, this is the one that should be easy to generate. The second one
operates on the string from the first part to recreate the string representation
of the first part (code that would create that string), and outputs all of that.
In Green there is also added difficulty of encoding the output once it's ready.

The first part (creating a data representation of the code for second part) will
be generated by `the special quine compiler`_, and to make it as small and
simple to generate it will be just::

  'Q'u'i'n'e...

This attaches all the characters straight to the root node, so the compiler will
also be responsible for copying it to a valid Phrog variable. I could have done
this all in Simple Green, but I value my sanity.

The structure we get from that is similar to Phrog representation of stacks, but
*not exactly*, so the quine compiler includes a special word for popping from
this type of stack: ``pop'``. The not-exactly-stack with a character
representation of our program will be moved by the compiler to the last
variable, so our variable and struct declaration for this program will be as
follows::

  byte-buf bit-cnt bytes nodes tail-node string

  : list rest head
  : node parent weight bit id

The almost-stack we got has the *last* character of the program on top, which
is the opposite of what we want for encoding. The first thing to do then is to
move all the data to a proper Phrog stack, this time in correct order::

  string copy {} begin over length while
    over pop' push
  repeat swap drop

We can also reuse the almost-stack to prepend the program with its encoded
representation. The final resulting stack containing the representation of *the
whole quine* in correct order can be stored back to the ``string`` variable. ::

  string swap begin over length while
    over pop' push 'A push
  repeat string! drop

In any normal language that would be the end, the only thing left being to
output the string. Unfortunately Green has its encoding so we need to implement
that. We will need some encoding structures: a stack of nodes encoding each byte
value (initially 256 empty pointers), and a root node of our huffman tree::

  ; An empty list for the 256 possible bytes
  #256 {} begin over while
    {} push swap #1 - swap
  repeat bytes! drop

  ; root node is represented as empty, it won't be swapped, it doesn't encode
  ; bits.
  {} {} <list> dup nodes! tail-node!

Now we begin a big loop over the whole ``string``! First we check if the byte
has already been encoded, if so we output the bits leading to it. Indexing into
the ``bytes`` stack is done with an offset of 65 so that capital letters
corresponding to Green commands are closer to its beginning. ::

  begin string length while
    
    ; Fetch the node corresponding to the next byte in the string
    bytes copy string first dup #64 - 0> if #65 - else #191 + then
    begin dup while
      over pop drop #1 -
    repeat drop first

    dup length if
      
      ; If the node exists gather bits to reach it
      first dup {} begin over length while
        over bit>> push swap
        parent>> swap
      repeat swap drop

      ; Output the bits in the top-down order
      begin dup length while
        dup pop byte-buf dup + + byte-buf!
        bit-cnt #1 - dup if bit-cnt!
        else drop #8 bit-cnt! byte-buf out #0 byte-buf! then
      repeat drop
      ; Leave the node on the stack for later use

That was the simpler case. Now we need to manage creation of a new node. ::

    else

      ; A new node needs to be created for the new byte
      tail-node dup >aux head>> #1 #1 string first <node>
      tail-node head>> #0 #0 string first #256 + <node>
      {} swap <list> dup tail-node! over <list>
      >aux push drop aux> aux> swap >>rest head>>

      ; Gather bits needed to reach the former tail node
      {} #0 push over begin dup length while
        dup parent>> >aux
        bit>> push aux>
      repeat drop

      ; Output the bits in the top-down order
      begin dup length while
        dup pop byte-buf dup + + byte-buf!
        bit-cnt #1 - dup if bit-cnt!
        else drop #8 bit-cnt! byte-buf out #0 byte-buf! then
      repeat drop
      ; Leave the former tail node for later use

      ; Convert the byte into bits and output them
      string first dup #1 + 0> if else #256 + then #8 begin dup while
        #1 - swap
        #0 begin over #1 - 0> while
          #1 + swap #2 - swap
        repeat swap
        byte-buf dup + + byte-buf!
        bit-cnt #1 - dup if bit-cnt!
        else drop #8 bit-cnt! byte-buf out #0 byte-buf! then
        swap
      repeat drop drop

    then

Now the paths converge: we need to increment the weight of our node and weights
of all nodes above it. ::

    begin dup length while

      ; Find a the first node with the same weight, or {} if it's itself
      nodes begin
        rest>> over weight>> over head>> weight>> <>
      while repeat

      ; Swap nodes if found something other than itself or its parent
      over id>> over head>> id>> = if drop else
        over parent>> length if
          over parent>> id>> over head>> id>> = if drop #0
          else #1 then else #1
        then if
          ; If their parents are the same set bits correctly
          over parent>> length over head>> parent>> length * if
            over parent>> id>> over head>> parent>> id>> =
          else
            over parent>> length over head>> parent>> length + #0 =
          then
          if dup head>> #0 >>bit drop over #1 >>bit drop then  
          swap nodes begin
            rest>> over id>> over head>> id>> <>
          while repeat swap >aux
          over head>> >>head drop
          dup head>> swap aux@ >>head drop
          dup parent>> aux@ parent>> swap >aux >>parent
          aux> aux> swap >>parent >aux
          dup bit>> aux@ bit>> swap >aux >>bit drop
          aux> aux> swap >>bit
        then
      then

      ; Increment the weight and proceed to parent
      dup weight>> #1 + >>weight parent>>
    
    repeat drop

    string pop drop
  repeat

Finally we close the big encoding loop by dropping the character from the
string. ::

    string pop drop
  repeat

The only thing left to do is to encode the end of text::

  {} push tail-node head>> begin dup length while
    dup parent>> >aux
    bit>> push aux>
  repeat drop

  ; Output the bits in the top-down order
  begin dup length while
    dup pop byte-buf dup + + byte-buf!
    bit-cnt #1 - dup if bit-cnt!
    else drop #8 bit-cnt! byte-buf out #0 byte-buf! then
  repeat

  ; Pad the remaining byte with 1s and output it
  bit-cnt byte-buf begin over while
    dup + #1 + swap #1 - swap
  repeat out

Was that too convoluted and not enough details? Well, TOO BAD! This algorithm
was a pain to write, and I'm too drained to explain it in-depth at the moment.
If you really have no idea what's going on here take a look at the section
explaining Green's encoding in `deobf_stages/README.rst`_. This is the inverse
of that algorithm, which involves doing almost the same stuff, just that instead
of following the tree based on bits to get to a byte value we start from a leaf
with the value we want to encode and go up to the root collecting bits, and the
``o`` values are replaced with the order in the ``nodes`` list.

.. _the special quine compiler: ../compiler/quine/quine.factor
.. _@blaumeise20: https://github.com/blaumeise20


Prefix/Suffix trie
==================

I didn't attempt those. Nobody did AFAIK, and they were considered for removal
by the host of the challenge.


The ultimate challenge
======================

This is what I *actually* wanted to do with this ERE. This is why I created
Phrog. This is the pinacle of my work on this contest. The cg59 entry!

The challenge was to implement a probabilistic PricK interpreter. In short,
PricK is a stack language which has one stack, an infinite addressable memory, a
simple looping/conditional construct and only natural numbers. The
"Probabilistic" part adds an additional command that takes a number and replaces
it with a random number between zero and that number inclusive. The goal of a
Probabilistic PricK interpreter is to find the number most likely to end up on
top of the stack at the end of execution.

My solution uses only two variables, but makes heavy use of structures. To get
the most likely answer we simulate all possible paths, aggregating their outputs
in the ``answers`` variable and then pick the one connected to the highest
probability.

To get all the paths every time a ``?`` command is executed it spawns ``n`` new
timelines to execute. Those are all stored in the ``states`` variable, and the
main loop of this program runs until there are any more ``states`` to handle.

A state holds *everything* needed to correctly execute a program: the program
itself, split into the ``future`` (program yet to be executed) and ``past``
already executed part of the program), the ``stack`` and ``memory``, and an
additional stack of loop ``bounds`` to handle loops. It also has an attached
``odds`` vaule, representing the inverse of the probability of reaching that
state.

Memory and answers are handled as ``dict``\ionaries. For memory the key is the
index and value is the value of the memory cell at that index. For answers the
key is the output value at the end of execution and the value is is the
probability of achieving that result. Probability values in the answer dictionary are stored as ``fraction``\s with a numerator and a denominator, so we should take care to simplify fractions as much as possible so they don't overflow the 32 bit int.

With the data model out of the way let's jump into the code. We start with
variable and struct declarations::

  states answers

  : state future past stack bounds memory odds

  : dict key value next

  : fraction numer denom

They need some initialisation. The state stack needs an initial state loaded
with the program from input, and the answers dict needs a dummy entry of 0 with
0 probability of occurring::

  {} begin in dup #1 + while push repeat drop

  {} begin over length while over pop push repeat

  swap {} {} #0 #0 {} <dict> #1 <state> {} swap push states!

  #0 #0 #1 <fraction> {} <dict> answers!

The main execution loop will repeat as long as there is an unfinished state on
the stack. It pops one command from ``future`` and handles it. We will start
with the hardest commands, the looping constructs ``]`` and ``|``. When
encountered the role of ``]`` is to jump back to the corresponding ``[``, so it
pops from ``past`` back into the ``future`` in a loop keeping a counter for
nesting depth. ::

  begin states length while
    states first future>> pop dup '] = if
      ; handle ]
      #1 >aux begin
        states first future>> swap push drop
        states first past>> pop
        dup '[ = if aux> #1 - >aux
        else dup '] = if aux> #1 + >aux then then
      aux@ while repeat aux> drop
      states first past>> swap push drop

The rest of the commands will always just go to the ``past`` so we may just as
well do that once for all of them. After that we handle the condition command
``|``, which decrements a ``bound`` and pops a value from the stack. Then if
either of those end up being 0 it pops the value from ``bounds`` and jumps past
the corresponding ``]``. ::

    else states first past>> over push drop dup '| = if
      ; handle |
      states first bounds>> dup pop dup >aux #1 - push drop aux>
      states first stack>> dup length if pop else drop #0 then
      if if #0 else #1 then else drop #1 then
      if
        states first bounds>> pop drop
        #1 begin
          states first dup future>> pop swap past>> over push drop
          dup '[ = if drop #1 + else '] = if #1 - then then
        dup while repeat drop
      then

Next we handle the simple commands: ``+``, ``#``, ``@`` and ``!``. They get
increment a value on the stack, push a zero to the stack, get a value from
memory and put a value into memory respectively. ::

    else dup '+ = if
      ; handle +
      states first stack>> dup dup length if pop else drop #0 then
      #1 + push drop
    else dup '# = if
      ; handle #
      states first stack>> #0 push drop
    else dup '@ = if
      ; handle @
      states first dup stack>> dup length if pop else drop #0 then
      swap memory>> #1 >aux begin
        over over key>> = if
          aux> drop #0 >aux swap drop value>>
        else dup next>> length #0 = if
          aux> drop #0 >aux drop drop #0
        then then
      aux@ while next>> repeat aux> drop
      states first stack>> swap push drop
    else dup '! = if
      ; handle !
      states first dup stack>>
      dup length if dup pop else #0 then
      swap dup length if pop else drop #0 then >aux
      swap memory>> #1 >aux begin
        over over key>> = if
          aux> drop aux> #0 >aux >>value drop drop
        else dup next>> length #0 = if
          swap aux> drop aux> #0 >aux {} <dict> >>next drop
        then then
      aux@ while next>> repeat aux> drop

Then there's the new ``?`` command that needs to spawn alternate timelines. They
are ``clone``\s of the original state with smaller values on top of the stack
down to 0. All of the clones get their ``odds`` decreased proportionally to
their number. ::

    else dup '? = if
      ; handle ?
      states first stack>> dup length if
        states first dup odds>> over stack>> first #1 + * >>odds drop
        first begin dup while #1 -
          states first clone states over push drop
          stack>> dup pop drop over push drop
        repeat
      then drop

Finally we can handle the start of loop command ``[`` which just consumes one
number and pushes it as a new ``bound``, and we can also add a bit of code to
remove non-command characters from the program to make it slightly faster. ::

    else dup '[ = if
      ; handle [
      states first dup bounds>>
      swap stack>> dup length if pop else drop #0 then push drop
    else
      ; remove the thing from the past
      states first past>> pop drop
    then then then then then then then drop then

At the end of the execution loop we have to handle finished states. If a state
stopped running we need to remove it from the ``states`` stack and note its
result value in the ``answers`` dictionary. This is the first occurrence of the
marvel that is fraction math. ::

    states first future>> length #0 = if
      states first stack>> dup length if first else drop #0 then
      ; upload the answer to answers
      answers #1 >aux begin
        over over key>> = if
          aux> drop #0 >aux

We have the current value in the dictionary, call it ``a/b``, and we need to add
to it one over the odds of getting into that final state, call it ``1/c``. The
result is of course ``(ac+b)/bc``, but we can do better. Before calculating the
products ``ac`` and ``bc`` we can find the greatest common divisor ``gcd(b,
c)`` and scale ``c`` down by them. We can also scale ``b`` down by that factor
for the ``+b`` part. This way we run less risk of the denominator overflowing.
::

          ; Add 1/odds to value
          value>> states pop odds>>
          ; GCD of denom and odds
          over denom>> over begin over while
            begin over over swap #1 - > while over - repeat swap
          repeat swap drop dup >aux
          ; Divide odds by GCD
          #0 >aux swap begin dup while
            over - aux> #1 + >aux
          repeat drop drop
          dup numer>> aux@ * >>numer
          dup denom>> aux> over >aux * >>denom
          ; Divide denom by GCD
          aux> aux> swap #0 >aux begin dup while
            over - aux> #1 + >aux
          repeat drop drop
          dup numer>> aux> + >>numer

After this reduction we have to also account for the fact that ``ac+b`` may
share a common factor with ``bc``. For that we compute another ``gcd`` and scale
both the numerator and denominator by that. ::

          ; GCD of denom and numer
          dup numer>> over denom>> begin over while
            begin over over swap #1 - > while over - repeat swap
          repeat swap drop dup >aux
          ; Divide denom by GCD
          over denom>>
          #0 >aux begin dup while
            over - aux> #1 + >aux
          repeat drop drop aux> >>denom
          ; Divide numer by GCD
          aux> over numer>>
          #0 >aux begin dup while
            over - aux> #1 + >aux
          repeat drop drop aux> >>numer drop drop

And of course if the value isn't in the dictionary yet we need to add it::

        else dup next>> length #0 = if
          aux> drop #0 >aux
          swap #1 states pop odds>> <fraction> {} <dict> >>next drop
        then then
      aux@ while next>> repeat aux> drop
    then
  repeat

And that's it for the main execution loop. At this point we're left with no
``states`` and a dictionary of ``answers`` with their probabilities. Now we
gotta find the one with the highest probability, and that means more fraction
math! We want to compare two fractions, call them ``a/b`` and ``c/d``. First for
the sake of this comparison we can reduce their numerators by ``gcd(a, c)`` and
denominators by ``gcd(b, d)`` without changing the outcome of comparison
(because they're all nonnegative). ::

    ; Reduce numerators by GCD
    over numer>> over numer>> over over begin over while
      begin over over swap #1 - > while over - repeat swap
    repeat swap drop dup >aux
    swap #0 >aux begin dup while
      over - aux> #1 + >aux
    repeat drop drop aux>
    swap aux> swap #0 >aux begin dup while
      over - aux> #1 + >aux
    repeat drop drop >aux

    ; Reduce denominators by GCD
    denom>> swap denom>> over over begin over while
      begin over over swap #1 - > while over - repeat swap
    repeat swap drop dup >aux
    swap #0 >aux begin dup while
      over - aux> #1 + >aux
    repeat drop drop aux>
    swap aux> swap #0 >aux begin dup while
      over - aux> #1 + >aux
    repeat drop drop

Then we can notice that ``a/b > c/d`` is equivalent to ``ad > bc``, so we
calculate that inequality instead::

    aux> swap aux> * swap aux> * swap >

    if drop else swap drop then aux>
  repeat drop

And finally we end up with the dictionary entry where key is our most likely
result, so we just print this one out. ::

  key>> .
