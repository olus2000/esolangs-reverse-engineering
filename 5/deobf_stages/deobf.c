#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <stdint.h>

#define TRAV(x, y) for (N1 *x = y->c; x; x = x->s)
#define Fi(n, a...) for (int i=0; i<n; i++){a;}

typedef struct N1 {
  int v, m;               // Value, mark (flag if the node is used)
  struct N1 *s, *c, *p;   // Sibling, child, parent
} N1;


N1 *r1, *r2, *np;
int npc;              // length of np array


// Mark the node and all children
void m(N1 *n) {       
  if (n->m) return;
  n->m = 1;
  TRAV(x, n) m(x);
}


// Make a new node with value v
N1* tmk(uint32_t v) {
  // Find an unmarked node in np
  N1 *O = 0;
  for (int i = 0; i < npc; i++) {
    if (!np[i].m) {
      O = &np[i];
      printf("tmk creates a node at %d (%d)\n", i, O);
      break;
    }
  }
  // If not found then double the np array and fill with zeros
  if (!O) {
    printf("Reallocating!!");
    np = realloc(np, sizeof(N1) * (npc <<= 1));
    memset(&np[npc >> 1], 0, sizeof(N1) * (npc >> 1));
    O = &np[npc >> 1];
  }
  // Set the value of that node to v, clear its children and siblings, and mark
  // it.
  O->v = v;
  O->s = O->c = 0;
  O->m = 1;
  return O;
}


// Sum values of a tree
int tsx(N1 *O) {
  int sum = 0;
  TRAV(x, O) sum += tsx(x);
  printf("sum: %d\n", sum);
  return O->v + sum;
}


// Negate values of a tree
void tnx(N1 *O) {
  O->v = -O->v;
  TRAV(x, O) tnx(x);
}


// Count children of a node
int tcnt(N1 *O) {
  int c = 0;
  TRAV(_, O) c++;
  return c;
}


// Move O's first child to be its first grandchild
// Breaks parentage
void tright(N1 *O) {
  N1 *C = O->c;
  O->c = C->s;
  C->s = O->c->c;
  O->c->c = C;
}


// Move O's first grandchild to be its first child
// Breaks parentage
void tleft(N1 *O) {
  N1 *C = O->c;
  O->c = C->c;
  C->c = O->c->s;
  O->c->s = C;
}


// Copy a tree. Copied trees are marked.
N1* tcopy(N1 * O) {
  // w : a new node with the value from O
  N1 *w = tmk(O->v), *C, *q, *s, *c;
  // Recursively copy children, in reverse order
  TRAV(C, O) {
    c = tcopy(C);
    c->p = w;
    c->s = w->c;
    w->c = c;
  }
  // Reverse the reverse order, bringing children back in order
  for(C = w->c, q = 0; C;) {
    s = C->s;
    C->s = q;
    q = C;
    C = s;
  }
  w->c = q;
  return w;
}


// Print a tree O at depth d
void tdi(N1 *O, int d){
  for (int i = 0; i < d; i++) printf("  ");
  printf("%d, %d, %d, %d\n", O->v, O, O->c, O->s);
  TRAV(C, O) tdi(C, d+1);
}


// Run program pr of length pl on a tree R
N1* run(N1 *R, char *pr, int pl) {
  // C points to R, r1 and r2 are initialised with value 0
  // R is the root of our tree
  // C is the current tree node we're working on
  // r1 and r2 are "register" trees
  N1 *C = R, *O;
  r1 = tmk(0);
  r2 = tmk(0);
  for (int i = 0; i < pl; i++) {
    tdi(R, 0);
    printf("%c, %d\n", pr[i], C);
    switch(pr[i]) {
      case'A':                        // Add new immediate node to C
        printf("Root: %d, %d, %d, %d\n", R->v, R, R->c, R->s);
        O = tmk(pr[++i]);
        printf("Root: %d, %d, %d, %d\n", R->v, R, R->c, R->s);
        printf("Created %d\n", O);
        O->p = C;
        printf("Root: %d, %d, %d, %d\n", R->v, R, R->c, R->s);
        printf("Sibling: %d\n", C->c);
        O->s = C->c;
        printf("Root: %d, %d, %d, %d\n", R->v, R, R->c, R->s);
        printf("...\n");
        C->c = O;
      break;
      case'B':                        // If C has a child remove it
        (O = C->c) && (C->c = O->s);
      break;
      case'C':                        // Set r2 to C's 2nd child
        O = C->c;
        // Fi(r1->v) // No-op?
        O = O->s;
        r2 = O;
      break;
      case'D':                        // Set C's 3rd children to r2           !!
        O = C->c;
        // Fi(r1->v - 1) // No-op?
        O = O->s;
        O->s = r2;
      break;
      case'E':                        // Set C's value to sum of C
        C->v = tsx(C);
      break;
      case'F':                        // Negate C
        tnx(C);
      break;
      case'G':                        // Set r1's value to child count of C
        r1->v = tcnt(C);
      break;
      case'H':                        // Swap r1 and r2
        O = r1;
        r1 = r2;
        r2 = O;
      break;
      case'I':                        // Move C's first child a level down    !!
        tright(C);
      break;
      case'J':                        // Move C's first grandhild a level up  !!
        tleft(C);
      break;
      case'K':                        // Deep copy C to r1
        r1 = tcopy(C);
      break;
      case'L':                        // Set r1 to C
        r1 = C;
      break;
      case'M':                        // Go up the tree
        C = C->p;
      break;
      case'N':                        // Go down the tree
        C = C->c;
      break;
      case'O':                        // Go right the tree
        C = C->s;
      break;
      case'P':                        // Set C to r1
        C = r1;
      break;
      case'Q':                        // Jump forward or backward by r1
        if (!C->v) i -= r1->v;
        else i += r1->v;
      break;
      case'R':                        // Output value of C
        putchar(C->v);
      break;
      case'S':                        // Get value into C
        C->v = getchar();
      break;
      case'T':                        // Set value of C to product of r1 and r2
        C->v = r1->v * r2->v;
      break;
      case'U':                        // Debug print C
        tdi(C, 0);
      break;
      case'V':                        // Get back to root
        C = R;
      break;
      case'W':                        // Jump by zero or forward by r1
        if (!C->v) i += r1->v;
      break;
    }
    printf("Success!\n");
    // GC XD
    if (rand() % 10 == 0) {
      printf("Collection time!!\n");
      for (int i = 0; i < npc; i++) np[i].m = 0;
      m(r1);
      m(r2);
      m(R);
      m(C);
    }
  }
  return C;
}


typedef struct N2 {
  struct N2 *p, *a, *b;
  unsigned short s;
  int v, o;             // o starts at 512 and decreases by 1 or 2
} N2;

N2 n2p[512];
int n2i = 0;


// Make a new node2 with a given parent and other parameters
N2* mn2(N2 *p, unsigned short s, int v, int o) {
  N2 *O = &n2p[n2i++];
  O->p = p;
  O->a = O->b = 0;
  O->s = s;
  O->v = v;
  O->o = o;
  return O;
}


// z points to a pointer to a parent of new nodes
// ss is an array of 256 pointers to N2, absolutely useless
N2* n2s(unsigned short s, N2 **z, N2 **ss) {
  N2 *l = mn2(*z, 0xFFFF, 0, (*z)->o - 2), *r = mn2(*z, s, 1, (*z)->o - 1), *q = *z;
  (*z)->s = 0xFFFE;
  (*z)->a = l;
  ss[s] = (*z)->b = r;
  *z = l;
  return q;
}


// Find in the tree a node with r.o < R.o and r.v == R.v
N2* fr(N2 *m, N2 *R) {
  N2 *r = m, *t;
  // If Root's value is greater than root's value and Root has both children
  if (R->v > r->v && R->a && R->b) {
    t = fr(r, R->a);
    if (t) r = t;
    t = fr(r, R->b);
    if (t) r = t;
  } else if (R->v == r->v && R->o > r->o) r = R;
  return r != m ? r : 0;
}


// Exchange two trees, keeping their o values at original place
// If they're siblings and n1 is the a child only exchange o values!
void swpn2(N2 *n1, N2 *n2) {
  int t = n1->o;
  n1->o = n2->o;
  n2->o = t;
  if (n1->p->a == n1) n1->p->a = n2;
  else n1->p->b = n2;
  if (n2->p->a == n2) n2->p->a = n1;
  else n2->p->b = n1;
  N2 *t2 = n1->p;
  n1->p = n2->p;
  n2->p = t2;
}


// Update a node2 under root R
void updn2(N2 *s, N2 *R) {
  // For all nodes from s to the Root (but not the Root) increasing their v
  for (N2 *r; s->p; s->v++, s = s->p) {
    r = fr(s, R);
    if(r && s->p != r) swpn2(s, r);
  }
  // Increase v of root
  s->v++;
}



void debug_print_tree(N2 *R, int d) {
  for (int i = 0; i < d; i++) printf("| ");
//  if (R->s == 0xFFFE) {
   printf("%d: %d\n", R->o, R->v);
//  } else if (R->s == 0xFFFF) {
//    printf("%d: %d -1\n", R->o, R->v);
//  } else printf("%d: %d %c\n", R->o, R->v, R->s);
  if (R->a) {
    debug_print_tree(R->a, d + 1);
    debug_print_tree(R->b, d + 1);
  }
}


void debug_print_command(char c) {
  if ('A' <= c && c <= 'Z') putchar(c);
  else printf("%d", c);
}


int main(int argc, char *argv[]) {
  // Of course it's bitwise input....
  #define RF if(!bc){bits=fgetc(in);bc=8;}
  srand(time(NULL));
  if (argc != 2) {
    fprintf(stderr, "Usage: %s <file>\n", argv[0]);
    return 1;
  }
  FILE* in = fopen(argv[1], "rb");
  if (!in) {
    perror("fopen");
    return 1;
  }
  int pr_cap = 1024, pl = 0;
  char* pr = malloc(pr_cap);
  int bits = 0, bc = 0, c;
  N2 *R = mn2(NULL, 0xFFFF, 0, 512), *z = R, *n, *ss[256];
  memset(ss, 0, sizeof(ss));
  for (;; updn2(n, R)) {
    //debug_print_tree(R, 0);
    // While n has a child go left or right based on the bit read
    for (n = R; n->a ||n->b;) {
      RF
      n = (bits >> --bc) & 1 ? n->b : n->a;
    }
    // If n was the spawning leaf
    if (n->s == 0xFFFF) {
      RF
      // If next bit is 1 stop reading the program
      c = (bits >> --bc) & 1;
      if (c) break;
      c = 0; // Redundant
      // Read an immediate byte from the program, little endian
      for (int i = 0; i < 8; i++) {
        RF
        c |= ((bits >> --bc) & 1) << i;
      }
      // Append the byte to the program
      pr[pl++] = c;
      debug_print_command(c);
      // Create a new branching based on that byte
      n = n2s(c, &z, ss);
    // Otherwise append its character to the program
    //} else pr[pl++] = n->s;
    } else { pr[pl++] = n->s; debug_print_command(n->s); }
    // Realloc if the program gets too long
    if (pl == pr_cap) pr = realloc(pr, pr_cap *= 2);
  }
  printf("\n");
  np = malloc(sizeof(N1) * (npc = 64));
  memset(np, 0, sizeof(N1) * npc);
  run(tmk(0), pr, pl);
  fclose(in);
  free(pr);
  free(np);
}
