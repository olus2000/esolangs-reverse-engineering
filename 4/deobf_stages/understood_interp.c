#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <math.h>
#include <stdlib.h>

typedef struct Expression {
  int type;
  union {
    struct {
      struct Expression* left;
      struct Expression* right;
    } cat;
    char* v;
    int r;
    struct {
      int function;
      struct Expression* argument;
    } application;
  };
} Expression;

typedef struct {
  char* s;
  Expression* d;
} Operator;

Expression* make_expression(int type) {
  Expression* e = malloc(sizeof(Expression));
  e -> type = type;
  return e;
}

Expression* make_cat(Expression* l, Expression* r) {
  Expression* e = make_expression(0);
  e -> cat.left = l;
  e -> cat.right = r;
  return e;
}

Expression* mf(char* v) {
  Expression* e = make_expression(1);
  e -> v = v;
  return e;
}

Expression* mr(int r) {
  Expression* e = make_expression(2);
  e -> r = r;
  return e;
}

Expression* make_application(int f, Expression* a) {
  Expression* e = make_expression(3);
  e -> application.function = f;
  e -> application.argument = a;
  return e;
}

FILE* in;
unsigned long long low, high = 0xffffffffffffffffLL, x;
unsigned int cxt, _pr = 0xFFFFFFFF; // cxt is always < 256
int ct[512][2]; // Only first 256 values used
Operator** fs;          // functions? Groups of operators? Both!
unsigned int* fns, nfs; // group sizes, number of functions/groups

void up(int y) {
  if (++ct[cxt][y] > 0xFFFFFFF) { // ct gets incremented. If it's over 0xFFFFFFF
    ct[cxt][1] >>= 1;             // then both get halved.
    ct[cxt][0] >>= 1;
  }
  cxt = (cxt << 1) | y;
  cxt &= 0xff;
  // A ratio of ones to all accesses at this cxt
  _pr = (((unsigned long long)(ct[cxt][1] + 1) << 32) /
         (ct[cxt][0] + ct[cxt][1] + 2));
  // This is a predictive model that looks at last 8 bits and makes the next
  // output likely to be the same as previously seen ones, making it converge
  // slower on repeated inputs and consume less input.
}


// Generates bits
int read_bit() {
  unsigned long long middle = low + ((high - low) >> 32) * _pr; // First time 0xfffffffe00000001
  int y = x <= middle;
  if (y) high = middle;
  else low = middle + 1;  // Binsearch?
  up(y);                  // Updates _pr
  // Loop as long as their top byte is the same
  while (((low ^ high) & 0xff00000000000000LL) == 0) {
    low = low << 8;             // Push a new 0x00 byte to low
    high = high << 8 | 0xff;    // Push a new 0xff byte to high
    int c = getc(in);     // Load a new byte into x
    if (c == EOF) c = 0;
    x = x << 8 | c;
  }
  printf("%d", y);
  return y; // 0 if x was greater than middle, else 1
}

unsigned int eg() {
  unsigned int l2 = 0;
  while (read_bit()) l2++;                // How many times was x <= m?
  unsigned int v = 0;
  while (l2--) v = (v << 1) | read_bit(); // Get that many bits from read_bit
  return v;
}

Expression* parse_expression() {
  char t = read_bit() * 2 + read_bit();
  switch (t) {
    case 0: // cat
      return make_cat(parse_expression(), parse_expression());
    case 1: // string of 1 and 0
      unsigned int len = eg();
      char* v = calloc(len + 1, 1);
      for (int i = 0; i < len; i++) v[i] = read_bit() ? 49 : 48;
      return mf(v);
    case 2: // int
      return mr(eg());
    case 3: // application of function number x
      unsigned int x = eg();
      return make_application(x, parse_expression());
  }
}


void parse_file() {
  fs = calloc(nfs = eg(), sizeof(Operator*));  // Get number of groups??
  fns = calloc(nfs, sizeof(Operator));
  for (int i = 0; i < nfs; i++) {             // For each group
    fs[i] = calloc(fns[i] = eg(), sizeof(Operator)); // Get number of functions
    for (int j = 0; j < fns[i]; j++) {        // For each function
      Operator* op = &fs[i][j];
      unsigned int len;
      op -> s = calloc((len = eg()) + 1, 1);  // Get its substitution pattern
      // Length then bits
      for (int x = 0; x < len; x++) op -> s[x] = read_bit() ? 49 : 48;
      op -> d = parse_expression();           // Get its expression
    }
  }
}

int is_prefix(char* w, char* z) {
  while (*w) if (*w != *z) return 0; else {w++; z++;}
  return 1;
}

char* eval(int f, char* in);

char* de(Expression* e, char* in) {
  switch(e -> type) {
    case 2: // int
      // Cut off first `r` characters from `in`.
      return strdup(e -> r >= strlen(in) ? "" : in + e -> r);
      //return strdup(!e -> r ? in : e -> r >= strlen(in) ? "" : in + e -> r);
    case 1: // 10101 string
      // Return v literally
      return strdup(e -> v);
    case 0: // cat
      // Call both left and right on `in` and return sum of results
      char* l = de(e -> cat.right, in);
      char* r = de(e -> cat.left, in);
      char* o = malloc(strlen(l) + strlen(r) + 1);
      strcpy(o, l);
      strcat(o, r);
      free(l);
      free(r);
      return o;
    case 3: // application
      // Evaluate argument and apply function
      return eval(e -> application.function, de(e -> application.argument, in));
  }
}

char* eval(int f, char* in) {
  Operator* ops = fs[f]; // Get the operator group
re:
  for (int j = 0; j < strlen(in); j++) {  // Go through the string
    for (int i = 0; i < fns[f]; i++) {    // For each operator
      if(is_prefix(ops[i].s, in + j)) {   // If it matches
        char* o = de(ops[i].d, in + j + strlen(ops[i].s));
        char* ni = malloc(strlen(o) + strlen(in) - strlen(ops[i].s) + 1 + j);
        strncpy(ni, in, j);
        ni[j] = 0;
        strcat(ni, o);
        strcat(ni, in + j + strlen(ops[i].s));
        free(in);
        free(o);
        // New input is what was before operator + result + what was after the operator
        in=ni;
        goto re;  // catidered harmful
      }
    }
  }
  return in;
}


int main(int argc, char* argv[]) {
  in = fopen(argv[1], "read_bit");    // SAVED GLOBALLY
  for (int i = 0; i < 8; i++) { // Read 8 bytes into unsigned long long x
    int c = getc(in);           // Big endian
    if (c == EOF) c = 0;
    x = x << 8 | c;
  }
  parse_file();
  printf("\n\n");
  char* ni = malloc(strlen(argv[2]) + 5); // Space for 000, string, zero, and
  strcpy(ni, "000");                      // one more
  strcat(ni, argv[2]);
  char* result = eval(0, ni);
  printf("%s\n", result);
}

