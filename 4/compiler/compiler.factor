! Copyright (C) 2023 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: accessors arrays ascii assocs bit-arrays combinators
combinators.short-circuit command-line generalizations
hashtables io io.encodings.binary io.encodings.utf8 io.files
kernel make math math.bits math.combinatorics math.parser
namespaces random sequences splitting ; auto-use
QUALIFIED-WITH: sets s
IN: esolang_games.reverse_engineering.4.compiler


: parse-a=b ( string -- a=b )
  "\n" split [ { [ empty? ] [ first CHAR: # = ] } 1|| ] reject
  [ "=" split [ " " split harvest ] map ] map ;


! Generate symbols

: keyword? ( string -- ? ) { "_" "'0" "'1" } s:in? ;


: extract-symbols ( a=b -- set )
  [ first2 s:union ] map s:union-all
  [ { [ "_" = ] [ [ digit? ] all? ] } 1|| ] reject ;


: make-symbol ( length index -- symbol )
  [ f , t , dup [ t , ] times f , - [ t , ] times f , ]
  ?{ } make ;


: make-symbol-group ( length -- symbols )
  dup <iota> [ make-symbol ] with map ;


: make-enough-symbols ( amount -- symbols )
  V{ } clone 1 [ [ 2dup length > ] dip swap ]
  [ [ make-symbol-group append! ] [ 1 + ] bi ] while
  make-symbol-group append! nip ;


! Compile to IR

: compile-num ( n -- )
  [ f , ]
  [ make-bits dup length [ t , ] times f , <reversed> % ]
  if-zero ;


: compile-seq ( seq -- ) dup length compile-num % ;


: compile-token ( symbols token -- symbols )
  { { [ dup "_" = ] [ drop f , f , f , ] }
    { [ dup "'0" = ] [ drop f , ] }
    { [ dup "'1" = ] [ drop t , ] }
    { [ dup [ digit? ] all? ]
      [ string>number f , 1 + [ t , ] times f , ] }
    [ over at % ] } cond ;


: compile-block ( symbols block -- symbols )
  [ [ compile-token ] each ] ?{ } make compile-seq ;


: compile-rule ( symbols rule -- symbols )
  first2 [ compile-block ] dip f , t , compile-block ;


: precompile ( symbols a=b -- bits )
  [ t , f , t , dup length compile-num
    [ compile-rule ] each ] ?{ } make nip ;


! Encode

TUPLE: encoding-state ct prob ctx low high ;

: <encoding-state> ( -- encoding-state )
  256 <iota> [ drop { 0 0 } clone ] map
  0xffffffff 0 0 0xffffffffffffffff
  encoding-state boa ;


: update-bounds ( encoding-state ? -- encoding-state ) dupd
  [ [ low>> ] [ high>> over - -32 shift ] [ prob>> * + ] tri ]
  dip [ >>high ] [ 1 + >>low ] if ;


: update-prediction ( encoding-state ? -- encoding-state ) 1 0 ?
  [let :> y
    dup [ ctx>> ] [ ct>> ] bi nth
    y over [ 1 + ] change-nth
    y swap nth 0xfffffff > [ [ 2/ ] map! ] when
    [ 2 * y + 0xff bitand ] change-ctx ]
  dup [ ctx>> ] [ ct>> ] bi nth first2 [ 1 + ] bi@
  [ 32 shift swap ] keep + /i 0xffffffff bitand >>prob ;


: steppable? ( encoding-state? -- ? )
  [ high>> ] [ low>> ] bi bitxor -56 shift 0 > ;


: extract-byte ( encoding-state -- encoding-state )
  dup high>> -56 shift ,
  [ 8 shift 0xff + 0xffffffffffffffff bitand ] change-high
  [ 8 shift 0xffffffffffffffff bitand ] change-low ;


: encode-bit ( encoding-state ? -- encoding-state )
  [ update-bounds ] [ update-prediction ] bi
  [ dup steppable? ] [ extract-byte ] until ;


: encode-bits ( bits -- bytes )
  [ <encoding-state> swap [ encode-bit ] each extract-byte ]
  B{ } make nip ;


! Bruteforce

SYMBOL: bruteforce-limit


: with-limit ( ..a quot: ( ..a -- ..b ) limit -- ..b )
  bruteforce-limit set call ; inline


USE: grouping ! XXX


: (compile) ( a=b symbols codes -- bytes )
  [ 2array ] 2map >hashtable swap precompile encode-bits ;


: compile ( string -- bytes )
  parse-a=b dup extract-symbols dup length make-enough-symbols
  over length <k-permutations> dup length bruteforce-limit get >
  [ [ random (compile) ] 3 ncurry
    bruteforce-limit get swap replicate ]
  [ [ (compile) ] 2with map ] if shortest ;


! Main

: main ( -- )
  command-line get first3 string>number
  [ swap utf8 [ read-contents ] with-file-reader compile
    swap binary [ write ] with-file-writer ] swap with-limit ;


MAIN: main
