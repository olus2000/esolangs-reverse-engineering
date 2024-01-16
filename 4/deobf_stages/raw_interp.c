#include"a.h"
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <math.h>
#include <stdlib.h>

typedef struct E {
  int t;
  union {
    struct {
      struct E* l, *r;
    } c;
    C* v;
    int r;
    struct {
      int f;
      struct E* a;
    } ap;
  };
} E;

typedef struct {
  C* s;
  E* d;
} O;

E* me(int t) _(
    E* e = malloc(sizeof(E));
    e -> t = t;
    e
)

E* mc(E* l, E* r) _(
    E* e = me(0);
    e -> c.l = l;
    e -> c.r = r;
    e
)

E* mf(C* v) _(
    E* e = me(1);
    e -> v = v;
    e
)

E* mr(int r) _(
    E* e = me(2);
    e -> r = r;
    e
)

E* ma(int f, E* a) _(
    E* e = me(3);
    e -> ap.f = f;
    e -> ap.a = a;
    e
)

FILE* in;

U l, h = 0xffffffffffffffffLL, x;
D cxt, _pr = 0xFFFFFFFF;
int ct[512][2];

V up(int y) {
  IF(++ct[cxt][y] > 0xFFFFFFF,
    ct[cxt][0] >>= 1,
    ct[cxt][1] >>= 1
  )
  cxt = (cxt << 1) | y;
  cxt &= 0xff;
  _pr = (((U)(ct[cxt][1] + 1) << 32) / (ct[cxt][0] + ct[cxt][1] + 2));
}

int rb() {
  U m = l + ((h - l) >> 32) * _pr;
  int y = x <= m;
  if (y) h = m;
  else l = m + 1;
  up(y);
  W (((l ^ h) & 0xff00000000000000LL) == 0) {
    l = l << 8;
    h = h << 8 | 0xff;
    int c = getc(in);
    if (c == EOF) c = 0;
    x = x << 8 | c;
  }
  R y;
}

D eg() {
  D l2 = 0;
  W (rb()) l2++;
  D v = 0;
  W (l2--) v = (v << 1) | rb();
  R v;
}

O** fs;
D* fns, nfs;

E* pe() {
  C t = rb() * 2 + rb();
  switch (t) {
    case 0:
      R mc(pe(), pe());
    case 1:
      D len=eg();
      C* v = calloc(len + 1, 1);
      Fi(len, v[i] = rb() ? 49 : 48);
      R mf(v);
    case 2:
      R mr(eg());
    case 3:
      D x = eg();
      R ma(x, pe());
  }
}

V pf() {
  fs = calloc(nfs = eg(), sizeof(O*));
  fns = calloc(nfs, sizeof(O));
  Fi(nfs,
    fs[i] = calloc(fns[i] = eg(), sizeof(O));
    Fj(fns[i],
      O* op = &fs[i][j];
      D len;
      op -> s = calloc((len = eg()) + 1, 1);
      Fx(len,
        op -> s[x] = rb() ? 49 : 48
      )
      op -> d = pe()
    )
  )
}

int pre(C* w, C* z) {
  W (*w) IF(*w != *z, R 0) ELSE(w++, z++)
  R 1;
}

C* eval(int f, C*in);

C* de(E* e,C* in) {
  switch(e -> t) {
    case 2:
      R strdup(!e -> r ? in : e -> r >= strlen(in) ? "" : in + e -> r);
    case 1:
      R strdup(e -> v);
    case 0:
      C* l = de(e -> c.r, in);
      C* r = de(e -> c.l, in);
      C* o = malloc(strlen(l) + strlen(r) + 1);
      strcpy(o, l);
      strcat(o, r);
      free(l);
      free(r);
      R o;
    case 3:
      R eval(e -> ap.f, de(e -> ap.a, in));
  }
}

C* eval(int f, C* in) {
  O* ops = fs[f];
re:
  Fj(strlen(in),
    Fi(fns[f],
      if(pre(ops[i].s, in + j)) {
        C* o = de(ops[i].d, in + j + strlen(ops[i].s));
        C* ni = malloc(strlen(o) + strlen(in) - strlen(ops[i].s) + 1 + j);
        strncpy(ni, in, j);
        ni[j] = 0;
        strcat(ni, o);
        strcat(ni, in + j + strlen(ops[i].s));
        free(in);
        free(o);
        in=ni;
        goto re;
      }
    )
  )
  R in;
}


int main(int ac, C* av[]) {
  in = fopen(av[1], "rb");
  Fi(8,
    int c = getc(in);
    if (c == EOF) c = 0;
    x = x << 8 | c
  )
  pf();
  C* ni = malloc(strlen(av[2]) + 5);
  strcpy(ni, "000");
  strcat(ni, av[2]);
  C* r = eval(0, ni);
  printf("%s\n", r);
}

