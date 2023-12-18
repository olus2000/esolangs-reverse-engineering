#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define P(a,b) {uint32_t x=a;x^=x>>17;x*=0xed5ad4bbU;x^=x>>11;x*=0xac4c1b51U;x^=x>>15;x*=0x31848babU;x^=x>>14;b=x;}

uint32_t* mem, s;
uint16_t t[16640], ai; // 65 * 256, only 16639 used

// Reallocate vector
void gw(uint32_t a) {
    if (__builtin_expect(a >= s, 0)) {
        uint32_t i = s;
        s = a + 1;
        mem = realloc(mem, s * sizeof(uint32_t));
        while (i < s) {
            P(i, mem[i]);
            i++;
        }
    }
}

// memory get
uint32_t mg(uint32_t a) {
    gw(a);
    return mem[a];
}

// memory set
void ms(uint32_t a, uint32_t v) {
    gw(a);
    mem[a] = v;
}

// Pretty sure this is bait
// Sum squared error?????? That's entirely not true!
int sse(int p, int c, int b) {
    int g = (b << 16) + (b << 6) - b - b; // 0x1003E or 0, which should actually still behave like 0x10040
    t[ai] += (g - t[ai]) >> 6;          //
    t[ai + 1] += (g - t[ai + 1]) >> 6;  // brings those closer to g
    int w = p & 127;
    ai = (p >> 2) + (c << 6) + c;  // What the fuck?
    return(t[ai] * (128 - w) + t[ai + 1] * w) >> 15; // Lerp?
}
// t[k * 65] and t[k * 65 - 1] are always zero.
// I need to aim for those with ai I think.

// Fun fact: xor of all bits
uint32_t pc(uint32_t x) { // 01101001100101101001011001101001100101100110...
    x -= (x >> 1) & 0x55555555;
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
    x = (x + (x >> 4)) & 0x0f0f0f0f;
    return (x * 0x01010101) >> 24;
}

int main(int argc, char* argv[]) {
    
    // First row is multiples of 1024
    // The rest is also multiples of 1024
    for (int i = 0; i < 256; i++)
      for (int j = 0; j < 65; j++)
        t[i * 65 + j] = i == 0 ? j << 10 : t[j];  // just j << 10

 //   gw(256);
 //   for (int i = 0; i < 10; i++) {
 //       printf("%d ", mem[i]);
 //   }

    FILE* in = fopen(argv[1], "rb");  // Program read in binary mode
    printf("dupa\n");
    // Instruction bytes xored with memory
    uint32_t idx = 0;
    while (!feof(in)) {
//        printf("%d: ", idx);
        uint8_t instr = fgetc(in);
//        printf("read %x, ", instr);
        ms(idx, mg(idx) ^ instr);
//        printf("resulted in %x\n", mg(idx));
        idx++;
        if ((instr & 15) == 15) {  // Loads a 4 byte immediate if instr is xxxx1111
            uint32_t value = 0;
            for (int i = 0; i < 4; i++)
              value = (value << 8) | fgetc(in);  // Big endian
//            printf("read value %x, ", value);
            ms(idx, mg(idx) ^ value);
//            printf("resulted in %x\n", mg(idx));
            idx++;
        }
    }
    fclose(in);
    
    // For the whole program the contents of the last cell with the fucking sse
    for (uint32_t i = 1; i < idx; i++) {
      ms(idx, mg(idx) ^ sse(mg(i - 1) & 255, mg(i) & 255, pc(mg(i)) & 1)); }

 //   for (int i = 0; i < idx; i++) {
 //       printf("%x ", mem[i]);
 //   }
    printf("succ\n");
    
    uint32_t a = 0x66, b = 0xF0, c = 0x0F, ip = 0;
    for (;;) {
        if (mg(ip) < 256 && mg(ip) >= 0 && mg(ip) != 0x70)
            printf("%d@ %x: %d, %x, %d\n", ip, mg(ip), a, b, c);
        switch (mg(ip++)) {
            case 0x0F: printf("imm: %d\n", mg(ip)); a=mg(ip++); break;  // Load immediate
            case 0x1F: b=mg(ip++);                              break;
            case 0x2F: c=mg(ip++);                              break;
            case 0x3F: ip=mg(ip++);                             break;  // Jumps and conditionals
            case 0x4F: if(a<=b)ip=mg(ip++);                     break;
            case 0x5F: if(b>=c)ip=mg(ip++);                     break;
            case 0x6F: a=sse(b&0xFF, c&0xFF, pc(mg(ip++))&1);   break;
            case 0x00: ms(ip++,a);                              break;  // Store at next cell (useless)
            case 0x10: ms(ip++,b);                              break;
            case 0x20: ms(ip++,c);                              break;
            case 0x30: ms(a,b);                                 break;  // Store computed
            case 0x40: ms(a,c);                                 break;
            case 0x50: ms(a,mg(a));                             break;  // No-op
            case 0x60: b=a;                                     break;  // Register shuffling
            case 0x70: c=a;                                     break;
            case 0x80: a=b;                                     break;
            case 0x90: a=c;                                     break;
            case 0xA0: ip=a;                                    break;  // Computed jump
            case 0xB0: a=b+c;                                   break;  // Add
            case 0xC0: a=b-c;                                   break;  // Sub
            case 0xD0: putchar(a);                              break;  // Out
            case 0xE0: a=getchar();                             break;  // In
            case 0xF0: return 0;  // Halt
            default:
                P(a,a);
                P(b,b);  // Fucking random shit
                P(c,c);
        }
        //if (mg(ip - 1) < 256 && mg(ip - 1) >= 0 && mg(ip - 1) != 0x70)
          //  printf("%x: %d, %d, %d @ %d\n", mg(ip - 1), a, b, c, ip);
    }
}
