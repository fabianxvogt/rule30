# Literature Notes

## Current Status of the Target Claim

The claim we were asked to prove, in its standard precise form, is still presented in current sources as an open problem.

### Stephen Wolfram, 2019, "Announcing the Rule 30 Prizes"

Key points extracted from the source:

- Problem 1 is explicitly stated as: "Does the center column always remain non-periodic?"
- The formal version is: there do not exist integers `p, i` such that for all `t > i`, `c[t + p] == c[t]`.
- The article says the sequence is known not to become periodic in the first billion steps, but that a proof is still needed to rule out eventual periodicity forever.
- The article also says: "Because while it’s not known if the center column in the rule 30 pattern ever becomes periodic, Erica Jen showed in 1986 that no two columns can both become periodic."
- It further says there is no known way to extend that argument from two columns to a single column.

Implication:

- As of that source, a full proof of center-column nonperiodicity is not available there; it is framed as a prize problem.

### Rule30Prize.org status check

The official prize site still lists all three prize questions, including Problem 1, under active submission material and does not indicate that Problem 1 has been solved or awarded.

Implication:

- There is no official resolution signal from the prize site as of this check.

### Informal corroboration

- A 2021 Math Stack Exchange question states: "It's still unproven whether or not the center column of Rule 30 ever becomes periodic."
- This is not a primary source, but it is consistent with the Wolfram prize statement.

## Consequence for This Workspace

We should distinguish three goals:

1. Verify the exact open status from reliable sources.
2. Prove partial theorems that are actually within reach.
3. Build strong experiments that may suggest or eliminate candidate proof strategies.

## Unverified Claims

- Search results turn up claimed solution papers and community posts, but nothing gathered so far indicates an official prize resolution or a broadly accepted proof.
- Treat such claims as unverified until they are peer reviewed, formally accepted, or explicitly recognized by the prize committee.

## Partial Results Worth Isolating

- No two columns can both become periodic.
- Rule 30 is left-permutative, which enables reconstruction to the left from two adjacent columns.
- That reconstruction argument is strong enough to rule out simultaneous periodicity of two columns, but not yet strong enough to rule out periodicity of only the center column.