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
    char* v;
    int r;
    struct {
      int f;
      struct E* a;
    } ap;
  };
} E;

typedef struct {
  char* s;
  E* d;
} O;

E* me(int t) {
  E* e = malloc(sizeof(E));
  e -> t = t;
  return e;
}

E* mc(E* l, E* r) {
  E* e = me(0);
  e -> c.l = l;
  e -> c.r = r;
  return e;
}

E* mf(char* v) {
  E* e = me(1);
  e -> v = v;
  return e;
}

E* mr(int r) {
  E* e = me(2);
  e -> r = r;
  return e;
}

E* ma(int f, E* a) {
  E* e = me(3);
  e -> ap.f = f;
  e -> ap.a = a;
  return e;
}

FILE* in;

unsigned long long l, h = 0xffffffffffffffffLL, x;
unsigned int cxt, _pr = 0xFFFFFFFF;
int ct[512][2];

void up(int y) {
  if (++ct[cxt][y] > 0xFFFFFFF) {
    ct[cxt][0] >>= 1;
    ct[cxt][1] >>= 1;
  }
  cxt = (cxt << 1) | y;
  cxt &= 0xff;
  _pr = (((unsigned long long)(ct[cxt][1] + 1) << 32) / (ct[cxt][0] + ct[cxt][1] + 2));
}

int rb() {
  unsigned long long m = l + ((h - l) >> 32) * _pr;
  int y = x <= m;
  if (y) h = m;
  else l = m + 1;
  up(y);
  while (((l ^ h) & 0xff00000000000000LL) == 0) {
    l = l << 8;
    h = h << 8 | 0xff;
    int c = getc(in);
    if (c == EOF) c = 0;
    x = x << 8 | c;
  }
  return y;
}

unsigned int eg() {
  unsigned int l2 = 0;
  while (rb()) l2++;
  unsigned int v = 0;
  while (l2--) v = (v << 1) | rb();
  return v;
}

O** fs;
unsigned int* fns, nfs;

E* pe() {
  char t = rb() * 2 + rb();
  switch (t) {
    case 0:
      return mc(pe(), pe());
    case 1:
      unsigned int len=eg();
      char* v = calloc(len + 1, 1);
      for (int i = 0; i < len; i++) v[i] = rb() ? 49 : 48;
      return mf(v);
    case 2:
      return mr(eg());
    case 3:
      unsigned int x = eg();
      return ma(x, pe());
  }
}

void pf() {
  fs = calloc(nfs = eg(), sizeof(O*));
  fns = calloc(nfs, sizeof(O));
  for (int i = 0; i < nfs; i++) {
    fs[i] = calloc(fns[i] = eg(), sizeof(O));
    for (int j = 0; j < fns[i]; j++) {
      O* op = &fs[i][j];
      unsigned int len;
      op -> s = calloc((len = eg()) + 1, 1);
      for (int x = 0; x < len; x++) op -> s[x] = rb() ? 49 : 48;
      op -> d = pe();
    }
  }
}

int pre(char* w, char* z) {
  while (*w) if (*w != *z) return 0; else {w++; z++;}
  return 1;
}

char* eval(int f, char* in);

char* de(E* e,char* in) {
  switch(e -> t) {
    case 2:
      return strdup(!e -> r ? in : e -> r >= strlen(in) ? "" : in + e -> r);
    case 1:
      return strdup(e -> v);
    case 0:
      char* l = de(e -> c.r, in);
      char* r = de(e -> c.l, in);
      char* o = malloc(strlen(l) + strlen(r) + 1);
      strcpy(o, l);
      strcat(o, r);
      free(l);
      free(r);
      return o;
    case 3:
      return eval(e -> ap.f, de(e -> ap.a, in));
  }
}

char* eval(int f, char* in) {
  O* ops = fs[f];
re:
  for (int j = 0; j < strlen(in); j++) {
    for (int i = 0; i < fns[f]; i++) {
      if(pre(ops[i].s, in + j)) {
        char* o = de(ops[i].d, in + j + strlen(ops[i].s));
        char* ni = malloc(strlen(o) + strlen(in) - strlen(ops[i].s) + 1 + j);
        strncpy(ni, in, j);
        ni[j] = 0;
        strcat(ni, o);
        strcat(ni, in + j + strlen(ops[i].s));
        free(in);
        free(o);
        in=ni;
        goto re;
      }
    }
  }
  return in;
}


int main(int ac, char* av[]) {
  in = fopen(av[1], "rb");
  for (int i = 0; i < 8; i++) {
    int c = getc(in);
    if (c == EOF) c = 0;
    x = x << 8 | c;
  }
  pf();
  char* ni = malloc(strlen(av[2]) + 5);
  strcpy(ni, "000");
  strcat(ni, av[2]);
  char* r = eval(0, ni);
  printf("%s\n", r);
}

