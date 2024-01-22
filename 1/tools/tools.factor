! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: accessors assocs bit-arrays combinators kernel literals
make math sequences sequences.parser ;
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


! Interpreter

ERROR: bad-command command state ;


TUPLE: um8-state a b c program input ;

: <um8-state> ( input program -- um8-state )
  swap reverse [ <sequence-parser> ] bi@
  [ 0 0 0 ] 2dip um8-state boa ;


: consume-command ( um8-state -- command )
  program>> consume [ CHAR: 0 ] unless* ;


: clamp ( n -- u8 ) 256 rem ;


: signed ( n -- i8 ) 128 + clamp 128 - ;


: step ( um8-state -- um8-state )
  dup consume-command
  { { CHAR: 0 [ [ [ 1 - ] change-n ] change-program ] }
    { CHAR: 1 [ dup b>> 0 = [ dup c>> >>a ] unless ] }
    { CHAR: 2 [ dup [ a>> ] [ c>> ] bi [ >>c ] [ >>a ] bi* ] }
    { CHAR: 3
      [ dup [ b>> ] [ c>> ] bi bitand bitnot clamp >>a ] }
    { CHAR: 4 [ dup b>> , ] }
    { CHAR: 5 [ dup input>> consume [ 0 ] unless* >>b ] }
    { CHAR: 6 [ dup [ a>> ] [ b>> ] bi [ >>b ] [ >>a ] bi* ] }
    { CHAR: 7
      [ dup [ program>> dup n>> ] [ c>> signed + ] bi
        offset [ 0 ] unless* CHAR: 0 - clamp >>a ] }
    { CHAR: 8
      [ dup [ b>> CHAR: 0 + clamp ] [ a>> signed ]
        [ program>> [ n>> + dup . ] [ sequence>> ] bi ] tri
        set-nth ] }
    { CHAR: 9 [ dup program>> consume CHAR: 0 - clamp >>a ] }
    { CHAR: A
      [ dup [ b>> signed ] [ program>> ] bi n<<
        dup program>> current
        [ dup [ c>> CHAR: 0 + clamp ]
          [ program>> [ n>> ] [ sequence>> ] bi ] bi
          set-nth ] when
        dup program>> advance drop ] }
    { CHAR: B [ [ 0 = 1 0 ? ] change-a ] }
    { CHAR: C [ [ signed 2/ ] change-a ] }
    { CHAR: D [ [ 2 * clamp ] change-a ] }
    { CHAR: E [ CHAR: E swap bad-command ] }
    { CHAR: F [ CHAR: F swap bad-command ] }
    [ drop ] } case ;


: run ( um8-state steps -- um8-state ) [ step ] times ; inline
