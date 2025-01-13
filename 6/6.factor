! Copyright (C) 2025 Aleksander "olus2000" Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: arrays grouping io io.files io.encodings.ascii kernel
literals math sequences splitting ;
IN: esolang_games.reverse_engineering.6


: decode-cell ( string -- n ) 0 [ swap 94 * + 32 - ] reduce ;


: decode ( string -- grid )
  "\n" split 2 group
  [ first2 [ 2 group ] bi@ [ append decode-cell ] 2map ] map ;


: encode-cell ( n -- string )
  "" 4 [ [ 94 /mod 32 + ] dip swap suffix ] times nip reverse ;


: encode ( grid -- string )
  [ [ encode-cell ] map
    [ [ 2 head ] map concat ] [ [ 2 tail ] map concat ] bi
    2array ] map concat "\n" join ;


: make-binop ( opcode dy1 dx1 dy2 dx2 -- n )
  11 + 24 * + 11 + 24 * + 11 + 24 * + 11 + 94 * + ;


: make-unop ( opcode dy1 dx1 -- n )
  11 + 24 * + 11 + 94 * + ;


: compile-to ( string filename -- )
  "vocab:esolang_games/reverse_engineering/6/" prepend
  ascii [ write ] with-file-writer ;


ALIAS: u make-unop
ALIAS: b make-binop
: | ( -- ) ; inline


CONSTANT: cat
{
  ${
    0
    0
    2 0 -2 0 -2 b
    2 0 -2 0 -2 b
    21 0 7 u
    9 0 6 0 -4 b
    1 0 -5 0 4 b
    1 0 6 0 -7 b
    1 0 6 0 -7 b
    0
    18 0 2 u
    0
    10
    20 0 11 u
    12 0 11 u
  }
}


CONSTANT: euclid
{
  ${ 21 0 0 u       | 21 0 0 u        | 14              | 1 0 -3 1 -1 b   | 4 0 -3 1 -2 b   | 5 0 -4 0 -5 b   |
   | 1 0 -6 2 -4 b  | 2 0 -7 0 -7 b   | 1 0 -7 0 -8 b   | 2 0 -8 0 -8 b   | 1 2 -8 0 -9 b   | 16              }
  ${ 1              | 0               | 0               | 16              | 2 0 -3 0 -3 b   | 1 0 -4 0 -5 b   |
   | 2 0 -6 0 -6 b  | 1 0 -7 0 -5 b   | 3 0 -7 0 -6 b   | 1 0 -7 1 -7 b   | 2 1 -8 1 -8 b   | 15              }
  ${ 0              | 1               | 0               | 14              | 1 -1 -2 -1 -3 b | 2 -1 -3 -1 -3 b |
   | 3 0 -5 0 -4 b  | 1 0 -7 0 -5 b   | 2 0 -8 0 -8 b   | 1 0 -8 0 -9 b   | 16              |                 }
  ${ CHAR: -        | 0               | 17              | 0               | 2 -1 -2 0 -2 b  | 6 -3 -4 -1 -3 b |
   | 6 -1 -4 0 -5 b | 2 -1 -5 -1 -5 b | 1 -1 -6 -1 -7 b | 2 -1 -8 -1 -8 b | 15              |                 }
  ${ 19             | CHAR: \n        | 14              | 20 -4 -3 u      | 12 0 -3 u       | 1 -1 -4 1 -1 b  |
   | 1 -1 -5 1 3 b  | 0               | 0               | 16              |                 |                 }
  ${ 12 -1 1 u      | 0               | 16              | 12 -2 -3 u      | 15              | 12 -1 -4 u      |
   | 20  -4 -6 u    | 15              | 0               | 15              |                 |                 }
  ${ 17             | 20 -4 -1 u      | 15              | 0               | 15              | 0               |
   | 0              | 17              | 12 -3 -8 u      | 15              |                 |                 }
}


CONSTANT: quine
{
  ${ 2 2 2 0 2 b     | 3 2 5 2 11 b   | 1 0 0 2 -1 b   | 4 2 9 2 -2 b    | 4 2 8 2 -3 b    |
   | 1 2 -4 2 8 b    | 4 2 0 2 7 b    | 5 2 -1 2 6 b   | 1 2 -5 2 5 b    | 12 2 4 u        |
   | 2 2 3 2 3 b     | 5 2 -5 2 -10 b | 16             | 1 0 12 2 -1 b   }
  ${ 16              | 8 0 12 1 11 b  | 12 1 9 u       | 1 1 10 0 1 b    | 16              |
   | 2 1 8 0 -1 b    | 6 -1 7 1 7 b   | 1 -1 -5 1 6 b  | 1 1 -3 -1 -6 b  | 2 1 -8 1 -8 b   |
   | 12 1 -9 u       | 1 1 -8 1 -10 b | 15             | 93              }
  ${ 1 0 12 0 1 b    | 0              | 2 24 * 94 *    | 32              | 18 0 5 u        |
   | 24 94 *         | 94             | 14 24 * 94 *   | 1 4 -2 2 -1 b   | 20              |
   | 37              | 10             | 1              | 0               }
  ${ 14              | 3 -1 5 -1 0 b  | 1 -1 -1 -3 0 b | 1 -1 -2 -3 10 b | 2 -1 3 -3 -2 b  |
   | 2 -1 -4 -1 -4 b | 3 -2 7 -1 6 b  | 1 -1 6 -1 5 b  | 2 -1 5 -1 5 b   | 1 -3 -7 -1 4 b  |
   | 6 -1 -2 -1 3 b  | 1 -1 2 0 1 b   | 18 -1 -2 u     | 0             }
}


CONSTANT: bct
"
get the program
Do some other stuff idc
Quine is somehow more interesting?
"
