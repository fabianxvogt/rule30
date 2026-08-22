#!/usr/bin/env python3
"""
Fix the left-half dynamics. The issue is in the zero-padding boundary.

For the left half, position -(h+1) is beyond our truncation, so we zero-pad on 
the LEFT (far from center). In our reversed indexing l[j] = row[-(j+1)]:

l'[j] = l[j+1] XOR (l[j] OR l[j-1])    for 1 ≤ j ≤ h-2
l'[0] = l[1] XOR (l[0] OR b)
l'[h-1] = l[h] XOR (l[h-1] OR l[h-2])  where l[h] = 0 (zero padding)

So l'[h-1] = 0 ^ (l[h-1] | l[h-2]) = l[h-1] | l[h-2]

But the issue is that the truncation on the left side is DIFFERENT from the right.
On the right side: we zero-pad position h+1, and the update for position h-1 is:
  s'[h-1] = s[h-2] XOR (s[h-1] OR s[h])  where s[h] = 0
  = s[h-2] XOR s[h-1]

On the left side: we zero-pad position -(h+1), and the update for l[h-1] is:
  l'[h-1] = l[h] XOR (l[h-1] OR l[h-2])  where l[h] = 0
  = l[h-1] OR l[h-2]

Wait, but the ACTUAL Rule 30 update at position -(h+1) involves positions:
old[-(h+2)], old[-(h+1)], old[-h]

Which in our indexing is: l[h+1], l[h], l[h-1]
The update is: new[-(h+1)] = l[h+1] XOR (l[h] OR l[h-1])

And for position -h: new[-h] = l[h] XOR (l[h-1] OR l[h-2])

Let me re-derive more carefully.

Full Rule 30: new[i] = old[i-1] XOR (old[i] OR old[i+1])

For position i = -(j+1) where j = 0, 1, ..., h-1:
new[-(j+1)] = old[-(j+2)] XOR (old[-(j+1)] OR old[-j])

Mapping: old[-(j+2)] = l[j+1] for j < h-1, else 0 (padding)
         old[-(j+1)] = l[j]
         old[-j] = l[j-1] for j ≥ 1
         old[0] = b for j = 0

So:
j = 0: l'[0] = l[1] XOR (l[0] OR b)
j = 1, ..., h-2: l'[j] = l[j+1] XOR (l[j] OR l[j-1])
j = h-1: l'[h-1] = 0 XOR (l[h-1] OR l[h-2]) = l[h-1] | l[h-2]

Hmm, but the verification fails specifically at position h-1.
Let me check the actual positions more carefully.
"""
import os, sys

def full_rule30_step(row):
    """One step of full Rule 30."""
    width = len(row)
    new_row = [0] * width
    for i in range(1, width - 1):
        new_row[i] = row[i-1] ^ (row[i] | row[i+1])
    return new_row


def main():
    width = 40
    center = width // 2
    row = [0] * width
    row[center] = 1
    
    h = 5
    
    for t in range(15):
        new_row = full_rule30_step(row)
        
        b = row[center]
        
        # Right half: s[j] = row[center + 1 + j] for j = 0, ..., h-1
        s = tuple(row[center + 1 + j] for j in range(h))
        s_next_actual = tuple(new_row[center + 1 + j] for j in range(h))
        
        # Right-half formula:
        # s'[j] = s[j-1] XOR (s[j] OR s[j+1])   with s[-1] = b, s[h] = 0
        s_next_computed = [0] * h
        for j in range(h):
            left = b if j == 0 else s[j-1]
            right = 0 if j == h-1 else s[j+1]
            s_next_computed[j] = left ^ (s[j] | right)
        s_next_computed = tuple(s_next_computed)
        
        # Left half: l[j] = row[center - 1 - j] for j = 0, ..., h-1
        l = tuple(row[center - 1 - j] for j in range(h))
        l_next_actual = tuple(new_row[center - 1 - j] for j in range(h))
        
        # Left-half formula:
        # Position -(j+1): new[-(j+1)] = old[-(j+2)] XOR (old[-(j+1)] OR old[-j])
        # old[-(j+2)] = l[j+1] for j < h-1, else 0
        # old[-(j+1)] = l[j]
        # old[-j] = b for j=0, l[j-1] for j ≥ 1
        l_next_computed = [0] * h
        for j in range(h):
            far = l[j+1] if j < h-1 else 0  # position -(j+2)
            mid = l[j]                        # position -(j+1)
            near = b if j == 0 else l[j-1]    # position -j (closer to center)
            l_next_computed[j] = far ^ (mid | near)
        l_next_computed = tuple(l_next_computed)
        
        r_ok = s_next_computed == s_next_actual
        l_ok = l_next_computed == l_next_actual
        
        if not r_ok or not l_ok:
            print(f"t={t}: RIGHT {'✓' if r_ok else 'FAIL'}, LEFT {'✓' if l_ok else 'FAIL'}")
            if not l_ok:
                print(f"  l={l}, b={b}")
                print(f"  computed: {l_next_computed}")
                print(f"  actual:   {l_next_actual}")
                # Check each position
                for j in range(h):
                    far = l[j+1] if j < h-1 else 0
                    mid = l[j]
                    near = b if j == 0 else l[j-1]
                    comp = far ^ (mid | near)
                    act = l_next_actual[j]
                    if comp != act:
                        print(f"    j={j}: far={far}, mid={mid}, near={near}, "
                              f"computed={comp}, actual={act}")
                        # What are the actual cells?
                        actual_far = row[center - 2 - j]
                        actual_mid = row[center - 1 - j]
                        actual_near = row[center - j]
                        print(f"    actual cells: row[{center-2-j}]={actual_far}, "
                              f"row[{center-1-j}]={actual_mid}, row[{center-j}]={actual_near}")
        
        row = new_row
    
    print("\nDone checking.")


if __name__ == "__main__":
    main()
