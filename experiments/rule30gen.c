/*
 * Generate Rule 30 center column bits using GMP big integers.
 * Compile: gcc -O3 -o rule30gen rule30gen.c -lgmp
 * Usage: ./rule30gen <num_steps> > output.txt
 */

#include <stdio.h>
#include <stdlib.h>
#include <gmp.h>

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <num_steps>\n", argv[0]);
        return 1;
    }
    
    long n = atol(argv[1]);
    if (n <= 0) {
        fprintf(stderr, "num_steps must be positive\n");
        return 1;
    }
    
    mpz_t state, shifted1, shifted2, or_result;
    mpz_init(state);
    mpz_init(shifted1);
    mpz_init(shifted2);
    mpz_init(or_result);
    
    mpz_set_ui(state, 1);  // single seed at position 0
    
    // Output bit at t=0
    putchar('0' + mpz_tstbit(state, 0));
    
    for (long t = 1; t <= n; t++) {
        // state = state ^ ((state << 1) | (state << 2))
        mpz_mul_2exp(shifted1, state, 1);
        mpz_mul_2exp(shifted2, state, 2);
        mpz_ior(or_result, shifted1, shifted2);
        mpz_xor(state, state, or_result);
        
        // The center column is at position t (it shifts right by 1 each step)
        putchar('0' + mpz_tstbit(state, t));
        
        if (t % 1000000 == 0) {
            fprintf(stderr, "  Generated %ld M bits...\n", t / 1000000);
        }
    }
    
    putchar('\n');
    
    mpz_clear(state);
    mpz_clear(shifted1);
    mpz_clear(shifted2);
    mpz_clear(or_result);
    
    return 0;
}
