! Copyright (C) 2024 Aleksander Sabak.
! See https://factorcode.org/license.txt for BSD license.
USING: bit-arrays kernel make math sequences ; auto-use
IN: esolang_games.reverse_engineering.1.tools


: naive ( char -- program )
  [ integer>bit-array but-last reverse "91" % f swap
    [ over = [ not "2163" % ] unless CHAR: D , ] each
    [ "2163" % ] when ] "" make ;


: naive-string ( string -- program )
  [ naive "64" append ] { } map-as concat "916" prepend ;
