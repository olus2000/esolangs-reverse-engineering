! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: accessors arrays ascii bit-arrays combinators
command-line grouping io io.encodings io.encodings.binary
io.encodings.utf8 io.files kernel make math math.functions
math.order namespaces sequences sequences.parser ;
IN: esolang_games.reverse_engineering.5.compiler.simple


SYMBOLS: leaves root ;


: spawner-leaf ( -- leaf ) 256 leaves get nth ;


TUPLE: tree p a b o v ;


: <root> ( -- tree ) tree new 512 >>o 0 >>v ;


: <byte-leaf> ( byte -- )
  spawner-leaf f f pick o>> 1 - 1 tree boa
  dup spawner-leaf b<< swap leaves get set-nth ;


: <spawner-leaf> ( -- )
  spawner-leaf f f pick o>> 2 - 0 tree boa
  dup spawner-leaf a<< 256 leaves get set-nth ;


! : print-tree ( tree n -- )
!   dup [ "| " write ] times 1 + swap dup
!   [ o>> number>string write ": " write ]
!   [ v>> number>string write "\n" write ] bi dup a>>
!   [ [ a>> swap print-tree ] [ b>> swap print-tree ] 2bi ]
!   [ 2drop ] if ;


: compile-path ( tree -- )
  dup p>> [ dup compile-path b>> eq? , ] [ drop ] if* ;


: compile-literal-byte ( byte -- )
  integer>bit-array [ % ] [ 8 swap length - [ f , ] times ] bi ;


: new-leaf ( byte -- ) <byte-leaf> <spawner-leaf> ;


! Potentially searches through the whole tree, cba to fix this
: (find-biggest) ( v ?tree -- ?tree )
  [ 2dup v>> = [ nip ]
    [ [ a>> ] [ b>> ] 2bi [ (find-biggest) ] 2bi@ 2dup and
      [ [ [ o>> ] bi@ > ] 2keep ? ] [ or ] if ] if ]
  [ drop f ] if* ;


: find-biggest ( v -- tree ) root get (find-biggest) ;


: swap-parent ( tree tree -- )
  dup p>> a>> over eq? [ p>> a<< ] [ p>> b<< ] if ;


: swap-nodes ( tree tree -- )
  2dup [ p>> eq? ] [ eq? ] 2bi or [ 2drop ]
  [ 2dup [ o>> ] bi@ -rot [ >>o ] 2bi@
    2dup 2dup swap [ swap-parent ] 2bi@
    2dup [ p>> ] bi@ -rot [ >>p ] 2bi@ 2drop ] if ;


: bump-v ( tree -- )
  dup root get eq?
  [ dup [ v>> find-biggest ] keep swap-nodes dup p>> bump-v ]
  unless [ 1 + ] change-v drop ;


: compile-byte ( byte -- )
  dup leaves get nth [ nip dup compile-path ]
  [ spawner-leaf tuck compile-path f ,
    dup compile-literal-byte new-leaf ] if* bump-v ;


: compile ( bytes -- bits )
  [ 256 f <array> <root> dup root set suffix leaves set
    [ [ compile-byte ] each spawner-leaf compile-path t , ]
    ?{ } make ] with-scope ;


: bits>bytes ( bits -- bytes )
  8 group
  [ [ reverse bit-array>integer 1 + ]
    [ 2 8 rot length - ^ ] bi * 1 - ] B{ } map-as ;


: hex-digit? ( n -- ? )
  [ CHAR: a CHAR: f between? ] [ digit? ] bi or ;


: hex>number ( char -- n )
  dup digit? [ CHAR: 0 - ] [ CHAR: a - 10 + ] if ;


: parse ( string -- bytes )
  <sequence-parser>
  [ [ dup sequence-parse-end? ]
    [ dup consume
      { { [ dup LETTER? ] [ , ] }
        { [ dup hex-digit? ]
          [ [ dup consume ] dip [ hex>number ] bi@ 16 * +
            CHAR: A , , ] }
        { [ dup CHAR: ' = ] [ drop dup consume CHAR: A , , ] }
        { [ dup CHAR: ( = ]
          [ drop 1 [ dup 0 = ] [ over consume dup CHAR: ( =
            [ drop 1 + ] [ CHAR: ) = [ 1 - ] when ] if ] until
            drop ] }
        [ drop ] } cond ] until drop ] { } make ;


: main ( -- )
  command-line get first utf8 file-contents
  parse compile bits>bytes
  binary [ write ] with-encoded-output ;


MAIN: main
