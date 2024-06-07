! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: esolang_games.reverse_engineering.5.compiler.simple
esolang_games.reverse_engineering.5.compiler
accessors assocs command-line io io.encodings
io.encodings.binary io.encodings.utf8 io.files kernel make
namespaces sequences sequences.extras ;
IN: esolang_games.reverse_engineering.5.compiler.quine

CONSTANT: prelude "CAANAANAADBNCVD"

CONSTANT: postlude "BA\2A\1"

CONSTANT: quine-dictionary
  H{ { "pop'" "VNNNNKHVNLAANAADBOCNBVND" } }


: compile-skeleton ( phrogram -- bytes )
  [ [ base-dictionary clone quine-dictionary assoc-union
      dictionary set
      [ prelude % vars>> compile-vars postlude % ]
      [ structs>> process-structs ]
      [ body>> (compile) ] tri ] with-scope ]
  B{ } make ;

: quinify ( bytes -- bytes )
  [ [ "A" swap suffix ] B{ } map-concat-as ] keep
  append ;

: main ( -- )
  command-line get first utf8 file-contents phrog-parser
  compile-skeleton quinify compile bits>bytes
  binary [ write ] with-encoded-output ;

MAIN: main
