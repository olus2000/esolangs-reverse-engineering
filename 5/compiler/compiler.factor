! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USE: esolang_games.reverse_engineering.5.compiler.simple
USING: accessors assocs command-line io io.encodings
io.encodings.binary io.encodings.utf8 io.files literals kernel
make math math.parser multiline namespaces peg.ebnf sequences
strings ;
IN: esolang_games.reverse_engineering.5.compiler


USE: prettyprint


TUPLE: loop predicate body ;

TUPLE: conditional then else ;

TUPLE: struct name fields ;

TUPLE: phrogram vars structs body ;


EBNF: phrog-parser [=[
sp = ([ \n\t\r]*)~

keyword = ( "begin" | "while" | "repeat"
          | "if" | "else" | "then"
          | ";" | ":" ) sp

word      = !(keyword) [^ \n\t\r]+ sp => [[ >string ]]
number    = "#"~ [0-9]* sp => [[ string>number ]]
character = "'"~ . sp


comment     = ";"~ ([ \t\r] [^\n]*)? sp => [[ drop f ]]
loop        = "begin"~ sp body "while"~ sp body "repeat"~ sp
            => [[ first2 loop boa ]]
conditional = "if"~ sp body ( "else"~ sp body )? "then"~ sp
            => [[ first2 conditional boa ]]
literal     = number | character


vars    = word*
structs = ( ":"~ sp word word+ => [[ first2 struct boa ]] )*
body    = ( comment | loop | conditional | literal | word )*
        => [[ sift ]]


phrogram = ((sp)?)~ vars structs body
         => [[ first3 phrogram boa ]]
]=]


! First child is stack, second is aux, rest is variables.
! Value of stack is 1, value of aux is 2
! A temp child is sometimes created.
! Numbers may have siblings
! A list is a single node with many children


SYMBOL: dictionary

CONSTANT: base-dictionary
  H{ { "dup"    "VLNNCVNLAANAADB" }
     { "swap"   "VLNNOCVNLAANAADBOOCVNNLD" }
     { "drop"   "VNB" }
     { "over"   "VLNNOCVNLAANAADB" }
     { ">aux"   "VLNNCVNLOAANAADBVNB" }
     { "aux>"   "VLNONCVNLAANAADBVNOB" }
     { "aux@"   "VLNONCVNLAANAADB" }
     { "0>" 
       "VNNNLVCNLNBAADBVA\x0aNLVBNNNWVNBAANA\0VWVNNBA\1VVV" }
     { ">"  
       $[ "VNNNKHVNLNBAADBONKHVNLNOBAADBNA\xffVNNNA\xffVA\x15NL"
          "VBNNONWEVA\x18NLVBNNNWEVA\xdfNLVBWVNBNBA\0" append
          "VA\x07NLVBWVNBNBA\1" append ] }
     { "="
       $[ "VNNNKHVNLBNDNOFVNNINEBVA\x09NLONNWVBNNBA\0VW"
          "VBNNBA\1VV" append ] }
     { "-"      "VNNNKHVNBLNDNOFVNNINEB" }
     { "<>"     "VNNNKHVNBLNDNOFVNNINEB" }
     { "+"      "VNNNKHVNBLNDINEB" }
     { "*"      "VLNNCONKVNBNBAANT" }
     { "{}"     "VNAANAA" }
     { "first"  "VLNNNNCVNLBAANAADB" }
     { "push"   "VLNNCVNLNONAANAADBVNB" }
     { "pop"    "VLNNNNCVNLAANAADBOCNBVND" }
     { "length" "VNNAANLOGVNLVCNND" }
     { "clone"  "VNLHNKHAADBVNJNOCVND" }
     { "copy"   "VLNNNCVNLNAANAADBOCVNND" }
     { "in"     "VNAANAANS" }
     { "out"    "VNNNRVNB" }
     { "."      "VNNNUVNB" }
     { ".."     "VNNUVNB" }
     { "debug"  "VU" }
     { "exit"   "VA\x7fNLHLTTTVW" } }

CONSTANT: prelude "A\x02A\x01"


: compile-vars ( vars -- )
  [ "AA" % CHAR: O <string> over CHAR: ! suffix over
    "VLNNCVNLOO" "AADBVNB" surround swap dictionary get set-at
    "VLNOO" "CVNLAANAADB" surround swap dictionary get set-at
  ] each-index ;

: process-structs ( structs -- )
  [ [ fields>> ] [ name>> ] bi "<" ">" surround over length
    CHAR: O <string> dup "VNLAANCAAD" "CVNDVCNOLVNNAAN" surround
    "DVNNBB" surround swap dictionary get set-at reverse
    [ CHAR: O <string>
      [ ">>" [ append ] [ prepend ] 2bi ] dip tuck "VLNNCVNLNON"
      "AADBVNB" surround swap dictionary get set-at
      "VLNNN" "CVNLNAADB" surround swap dictionary get set-at
    ] each-index
  ] each ;

GENERIC: (compile) ( element -- )

M: sequence (compile) [ (compile) ] each ;


ERROR: word-not-found error ;

M: string (compile)
  dictionary get ?at [ % ] [ word-not-found ] if ;


ERROR: jump-too-long length ;

! Restricted to 128 * 127 length jumps. Optimisation is hard.
: while-jump ( forward-length -- )
  22 + 127 /mod swap dup 127 > [ 127 * + jump-too-long ] when
  "VA" % , "NLVBHA\x7fNLTA" % , "EVBNNNWVNB" % ;


: repeat-jump ( back-length -- )
  43 + 128 /mod 1 + swap
  dup 127 > [ 128 * + jump-too-long ] when
  "VA" % , "NLVBHA\x80NLTA" % 256 swap - , "EVBWVNB" % ;


M: loop (compile)
  [ predicate>> ] [ body>> ] bi [ [ (compile) ] B{ } make ] bi@
  over % tuck [ length ] bi@ [ + ] keep
  while-jump swap % repeat-jump ;


: if-jump ( forward-length -- )
  7 + 127 /mod swap dup 127 > [ 127 * + jump-too-long ] when
  "VA" % , "NLVBHA\x7fNLTA" % , "EVBNNNWVNB" % ;


: else-jump ( forward-length -- )
  3 + 127 /mod swap dup 127 > [ 127 * + jump-too-long ] when
  "VA" % , "NLVBHA\x7fNLTA" % , "EVBWVNB" % ;


: then-jump ( -- ) "VNAAVNB" % ;


M: conditional (compile)
  dup then>>
  [ [ else>> ] [ then>> ] bi [ [ (compile) ] B{ } make ] bi@
    dup length 15 + if-jump % dup length else-jump % ]
  [ then>> [ (compile) ] B{ } make
    dup length if-jump % then-jump ] if ;


M: number (compile)
  [ dup 0 > ] [ 127 /mod ] produce nip
  dup empty? [ 0 ] [ unclip-last ] if "VNAANA" % ,
  [ "A\x7fNLVNNBNHL" % reverse [ CHAR: A , , "TEB" % ] each ]
  unless-empty ;


: compile-phrog ( phrogram -- bytes )
  [ [ base-dictionary clone dictionary set
      [ vars>> compile-vars prelude % ]
      [ structs>> process-structs ]
      [ body>> (compile) ] tri ] with-scope ]
  B{ } make ;


: main ( -- )
  command-line get first utf8 file-contents
  phrog-parser compile-phrog compile bits>bytes
  binary [ write ] with-encoded-output ;


MAIN: main
