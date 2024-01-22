! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: bit-arrays kernel make math sequences ; auto-use
IN: esolang_games.reverse_engineering.1.tools


CONSTANT: literals
  $[ "0123456789ABCD" [ [ CHAR: 0 - ] map ] keep zip ]


: rest-base ( target -- rest base )
  V{ } clone swap [ literals ?at ]
  [ 2 /mod 0 > pick push ] until ;


: extend-bits ( bits -- )
  f swap reverse
  [ over = [ not "2163" % ] unless CHAR: D , ] each
  [ "2163" % ] when ;


: naive ( char -- program )
  [ integer>bit-array but-last "91" % extend-bits ] "" make ;


: better ( char -- program )
  [ CHAR: 9 , rest-base , extend-bits ] "" make ;


: um8-print-with ( string quot: ( char -- program ) -- program )
  [ dup 0 prefix ] dip
  [ [ [ "64" append ] dip 0 =
      [ "916" prepend ] when ] bi* ] curry
  { } 2map-as concat ; inline


: naive-print ( string -- program ) [ naive ] um8-print-with ;


: better-print ( string -- program ) [ better ] um8-print-with ;
