# Partial Results

## Notation

Let `a_x(t)` be the Rule 30 cell at spatial position `x in Z` and time `t in N`, with the standard single-seed initial condition

- `a_0(0) = 1`
- `a_x(0) = 0` for `x != 0`

Rule 30 evolves by

`a_x(t + 1) = a_{x - 1}(t) xor (a_x(t) or a_{x + 1}(t))`

for all `x, t`.

## Lemma 1: Left Reconstruction

For every `x, t`,

`a_{x - 1}(t) = a_x(t + 1) xor (a_x(t) or a_{x + 1}(t))`.

### Proof

This is just the Rule 30 update rule solved for the left input cell. Since XOR with a fixed bit is invertible, the left neighbor is uniquely determined by the triple

- `a_x(t)`
- `a_{x + 1}(t)`
- `a_x(t + 1)`

So Rule 30 is left-permutative.

## Proposition 2: Adjacent Eventual Periodicity Propagates Left

Assume that for some `x`, the two adjacent columns

- `u(t) = a_x(t)`
- `v(t) = a_{x + 1}(t)`

are both eventually periodic with common period `p >= 1` after time `i`, meaning

`u(t + p) = u(t)` and `v(t + p) = v(t)` for all `t > i`.

Then every column `a_y(t)` with `y <= x` is also eventually periodic with period `p` after time `i`.

### Proof

First reconstruct the column immediately to the left:

`a_{x - 1}(t) = a_x(t + 1) xor (a_x(t) or a_{x + 1}(t))`.

For every `t > i`,

`a_{x - 1}(t + p)`
`= a_x(t + p + 1) xor (a_x(t + p) or a_{x + 1}(t + p))`
`= a_x(t + 1) xor (a_x(t) or a_{x + 1}(t))`
`= a_{x - 1}(t)`.

So `a_{x - 1}` is eventually `p`-periodic after time `i`.

Now iterate the same argument inductively. If `a_y` and `a_{y + 1}` are eventually `p`-periodic after time `i`, then Lemma 1 shows that `a_{y - 1}` is too. Therefore all columns to the left of `x` inherit the same eventual period.

## Corollary 3: A Far-Left Column Would Become Eventually Zero

Under the assumptions of Proposition 2, there exists some column `a_y` with `y <= x` that is identically zero for all sufficiently large times.

### Proof

Choose `y` so far to the left that `|y| > i + p`. Because information in a nearest-neighbor cellular automaton cannot travel faster than one cell per step, the single seed at the origin cannot affect column `y` before time `|y|`. Therefore

`a_y(t) = 0` for `0 <= t < |y|`.

In particular,

`a_y(i + 1) = a_y(i + 2) = ... = a_y(i + p) = 0`.

But by Proposition 2, the column `a_y` is eventually `p`-periodic after time `i`. Hence these `p` consecutive zeros repeat forever, so `a_y(t) = 0` for all `t > i`.

## Corollary 4: An Eventually Zero Column Forces Mirror Equality Across It

If some column `a_y` satisfies `a_y(t) = 0` for all `t > i`, then for all `t > i`,

`a_{y - 1}(t) = a_{y + 1}(t)`.

### Proof

Apply Rule 30 at position `y`:

`a_y(t + 1) = a_{y - 1}(t) xor (a_y(t) or a_{y + 1}(t))`.

When `a_y(t) = a_y(t + 1) = 0`, this becomes

`0 = a_{y - 1}(t) xor a_{y + 1}(t)`.

So the two neighboring columns agree.

## Proposition 5: The Neighbor of an Eventually Zero Column Is Eventually Constant

Assume `a_y(t) = 0` for all `t > i`. Define

`b_t = a_{y - 1}(t) = a_{y + 1}(t)`

for `t > i`, where equality is from Corollary 4. Then the binary sequence `b_t` is monotone nondecreasing, hence eventually constant.

### Proof

Fix `t > i`. Because `a_y(t) = a_y(t + 1) = 0`, Corollary 4 gives

`a_{y - 1}(t) = a_{y + 1}(t) = b_t`.

Now compare the updates of the two neighboring columns:

`a_{y - 1}(t + 1) = a_{y - 2}(t) xor b_t`

because `a_y(t) = 0`, and

`a_{y + 1}(t + 1) = b_t or a_{y + 2}(t)`

because `a_y(t) = 0`.

But Corollary 4 applied at time `t + 1` gives

`a_{y - 1}(t + 1) = a_{y + 1}(t + 1)`.

Therefore

`a_{y - 2}(t) xor b_t = b_t or a_{y + 2}(t)`.

Now split into cases.

If `b_t = 0`, then

`a_{y - 2}(t) = a_{y + 2}(t)`

and also

`b_{t + 1} = a_{y - 1}(t + 1) = a_{y - 2}(t)`.

So `b_{t + 1}` may be `0` or `1`.

If `b_t = 1`, then the right-hand side is `1`, so

`a_{y - 2}(t) xor 1 = 1`,

hence `a_{y - 2}(t) = 0`. Therefore

`b_{t + 1} = a_{y - 1}(t + 1) = a_{y - 2}(t) xor 1 = 1`.

So once `b_t` becomes `1`, it stays `1` forever. Thus `b_t` is monotone nondecreasing as a binary sequence, and therefore eventually constant.

## Corollary 6: Left-Tail Classification Beyond an Eventually Zero Column

Assume `a_y(t) = 0` for all `t > i`. Then exactly one of the following two scenarios occurs.

### Case A

For every fixed `m >= 0`, the column `a_{y - m}` is eventually zero.

### Case B

For every fixed `m >= 0`:

- `a_{y - 2m}` is eventually zero,
- `a_{y - (2m + 1)}` is eventually one.

So every fixed column to the left of `y` eventually settles into the spatial pattern obtained by extending either all zeros or the alternating word `...1010` from the column `y`.

### Proof

By Proposition 5, the neighboring column `a_{y - 1}` is eventually constant. Let its eventual value be `beta in {0, 1}`.

If `beta = 0`, then `a_{y - 1}` is eventually zero. Applying Corollary 4 to the eventually zero column `y - 1` gives

`a_{y - 2}(t) = a_y(t) = 0`

for all sufficiently large `t`, so `a_{y - 2}` is eventually zero. Repeating the same argument inductively shows that every fixed column to the left is eventually zero.

If `beta = 1`, then from the proof of Proposition 5, whenever `a_{y - 1}(t) = 1`, we have `a_{y - 2}(t) = 0`. So `a_{y - 2}` is eventually zero. Applying Corollary 4 to the eventually zero column `y - 2` gives

`a_{y - 3}(t) = a_{y - 1}(t) = 1`

for all sufficiently large `t`, so `a_{y - 3}` is eventually one. Repeating this argument inductively gives eventual zeros on all even offsets to the left of `y` and eventual ones on all odd offsets.

## Proposition 7: Eventual Periodicity Survives Finite-State Observation

Let `c(t)` be any eventually periodic binary sequence. Suppose `s(t)` is a finite-state process driven by `c(t)`, meaning there is a finite state set `S`, an initial state `s(0) in S`, a transition map

`T : S x {0, 1} -> S`,

and an output map

`O : S x {0, 1} -> A`

to some finite alphabet `A`, such that

- `s(t + 1) = T(s(t), c(t))`,
- `d(t) = O(s(t), c(t))`.

Then the output sequence `d(t)` is eventually periodic.

### Proof

Because `c(t)` is eventually periodic, there exist integers `i, p` with `p >= 1` such that

`c(t + p) = c(t)`

for all `t > i`.

Look only at times after `i`. Group time into blocks of length `p`. Over each such block, the input word seen by the machine is the same fixed word

`w = c(i + 1)c(i + 2)...c(i + p)`.

Let `F_w : S -> S` be the state update obtained by feeding the whole word `w` to the machine. Since `S` is finite, repeated application of `F_w` to the state sequence

`s(i + 1), s(i + 1 + p), s(i + 1 + 2p), ...`

must eventually repeat. So there exist `m < n` such that

`s(i + 1 + mp) = s(i + 1 + np)`.

From that point on, because both the machine state and the future input blocks repeat, the entire future state sequence repeats with block period `(n - m)p`. Therefore the output sequence `d(t)` also repeats from that point onward, so it is eventually periodic.

## Corollary 8: Sliding-Window and Running-Parity Transforms Preserve Eventual Periodicity

Any transform of the center column obtained by either of the following constructions preserves eventual periodicity:

- fixed finite sliding windows,
- finite-state transducers such as running parity.

In particular, the transforms used in this workspace

- `xor-shift`,
- `window-parity`,
- `running-parity`

would all have to become eventually periodic if the Rule 30 center column were eventually periodic.

## Proposition 9: The Center Column Uniquely Determines the Entire Right Half-Plane

Fix the standard single-seed initial condition. Let

`c(t) = a_0(t)`

be the center column. Then the restriction of the full Rule 30 spacetime to positions `x >= 1` is uniquely determined by the sequence `c(t)`.

Equivalently, for each fixed `x >= 1` and `t >= 0`, the value `a_x(t)` is a deterministic function of the finite prefix

`c(0), c(1), ..., c(t - 1)`.

### Proof

At time `0`, all cells with `x >= 1` are zero.

Now evolve forward in time. For each `x >= 1`, the Rule 30 update is

`a_x(t + 1) = a_{x - 1}(t) xor (a_x(t) or a_{x + 1}(t))`.

For `x = 1`, the left input `a_0(t)` is exactly the known boundary value `c(t)`. For `x >= 2`, all required inputs lie in the right half-plane itself. Since the entire row on `x >= 1` is known at time `t`, the entire row on `x >= 1` is uniquely determined at time `t + 1`.

By induction on time, the whole right half-plane is uniquely determined by the boundary sequence `c(t)` together with the initial all-zero right half-line.

Because information propagates at speed at most one, the value of `a_x(t)` depends only on the finite prefix `c(0), ..., c(t - 1)`.

## Corollary 10: The Adjacent Right Column Is an Effective Functional of the Center Column

The adjacent right column

`r(t) = a_1(t)`

is completely determined by the center column `c(t)`.

So the one-column proof gap is not about uniqueness. It is about complexity: we do not currently know any bounded-memory or otherwise simple rule that recovers `r(t)` from `c(t)` alone.

## What This Does Not Yet Prove

These results show that if two adjacent columns were eventually periodic, then eventual periodicity would propagate indefinitely to the left, and some far-left column would even become eventually zero. Beyond that, the left tail of fixed columns would be forced into one of only two eventual behaviors: all zeros, or an alternating `...1010` pattern.

What is still missing is a contradiction that starts from only one eventually periodic column, such as the center column. The left-reconstruction formula fundamentally uses two adjacent columns, not one. Even the stronger left-tail classification above still does not by itself bridge that gap.

The transform experiments are relevant because Proposition 7 shows they are testing observables that really would inherit eventual periodicity from the center column. What they have not yet produced is an observable that also interacts strongly enough with Rule 30 structure to force a contradiction.

Proposition 9 sharpens this further: the adjacent right column is already uniquely encoded in the center column. The hard part is apparently not information content, but extracting that information with sufficiently controlled structure.

## Relevance to the Main Problem

This note isolates the precise reason the classical two-column argument stops short of solving Wolfram's Problem 1:

- two columns give enough information to reconstruct leftward,
- one column does not.

Any successful proof for the center column likely has to recover equivalent extra information from the center sequence alone, or show that a single eventually periodic column would force a second eventually periodic object.

## Theorem 11: Full Raw-State Reachability From All-Zeros (Proved for all h)

For each h ≥ 1, **every** width-h binary state (tuple of h bits) is reachable from the all-zeros
state `(0,...,0)` via a sequence of exactly h Rule 30 boundary steps:

```
s_{t+1} = rule30_next(s_t, b_t)[:h]
```

for appropriate boundary bits b_0, ..., b_{h-1} ∈ {0,1}.

### Computational Verification

BFS over all 2^h width-h states from the all-zeros initial state, extended to h=20
(via `experiments/quotient_connectivity.py`):

| h  | raw states | all reachable? |
|----|------------|----------------|
|  1 |          2 |            yes |
|  8 |        256 |            yes |
| 12 |       4096 |            yes |
| 16 |      65536 |            yes |
| 18 |     262144 |            yes |
| 20 |    1048576 |            yes |

All 2^h states are reached in exactly h BFS steps for all h = 1..20.

### Proof for all h (by induction)

**Setup**: The Rule 30 truncated transition at width h with boundary bit b is:
- $s'_0 = b \oplus (s_0 \vee s_1)$  — depends on b
- $s'_j = s_{j-1} \oplus (s_j \vee s_{j+1})$  for  $1 \le j \le h-2$  — determined by s alone
- $s'_{h-1} = s_{h-2} \oplus s_{h-1}$  — determined by s alone (zero padding at right)

**Lemma** (Inner Bijectivity): For each k ≥ 1, starting from the all-zeros state and applying k
truncated steps with boundary bits $b_0, \ldots, b_{k-1}$:
1. Bits $s^{(k)}_j = 0$ for $j \ge k$ (the "light cone" is empty to the right of position k-1).
2. The map $\phi_k : (b_0, \ldots, b_{k-1}) \mapsto (s^{(k)}_0, \ldots, s^{(k)}_{k-1})$ is a bijection from $\{0,1\}^k$ to $\{0,1\}^k$.

**Proof of Lemma** (by induction on k):

*Base case k=1*: Starting from all-zeros, after one step with boundary bit $b_0$:
$s^{(1)}_0 = b_0 \oplus (0 \vee 0) = b_0$.
The map $b_0 \mapsto b_0$ is clearly a bijection from $\{0,1\}$ to $\{0,1\}$. ✓

*Inductive step*: Assume $\phi_k$ is a bijection. We show $\phi_{k+1}$ is also a bijection.

After k+1 steps, the state $s^{(k+1)}$ is obtained from $s^{(k)}$ (which has zeros at positions ≥ k) with boundary bit $b_k$:
- Bit at position 0: $s^{(k+1)}_0 = b_k \oplus (s^{(k)}_0 \vee s^{(k)}_1)$
- Bits at positions $j = 1, \ldots, k-1$: $s^{(k+1)}_j = s^{(k)}_{j-1} \oplus (s^{(k)}_j \vee s^{(k)}_{j+1})$
- Bit at position k: $s^{(k+1)}_k = s^{(k)}_{k-1} \oplus (s^{(k)}_k \vee 0) = s^{(k)}_{k-1} \oplus 0 = s^{(k)}_{k-1}$

Claim: The map $(s^{(k)}_0, \ldots, s^{(k)}_{k-1}) \mapsto (s^{(k+1)}_1, \ldots, s^{(k+1)}_k)$ is a bijection.

*Proof of claim by backward reconstruction*: Given $(s^{(k+1)}_1, \ldots, s^{(k+1)}_k)$, we recover $(s^{(k)}_0, \ldots, s^{(k)}_{k-1})$ uniquely by working right to left:
- $s^{(k)}_{k-1} = s^{(k+1)}_k$ (directly from the formula above)
- For $j = k-1$ down to 1: the Rule 30 update gives
  $s^{(k+1)}_j = s^{(k)}_{j-1} \oplus (s^{(k)}_j \vee s^{(k)}_{j+1})$.
  Since $s^{(k)}_j$ and $s^{(k)}_{j+1}$ are already known (recovered in previous steps),
  we get $s^{(k)}_{j-1} = s^{(k+1)}_j \oplus (s^{(k)}_j \vee s^{(k)}_{j+1})$ uniquely.
- At j=1: we recover $s^{(k)}_0 = s^{(k+1)}_1 \oplus (s^{(k)}_1 \vee s^{(k)}_2)$.

This backward reconstruction uniquely recovers all of $(s^{(k)}_0, \ldots, s^{(k)}_{k-1})$ from
$(s^{(k+1)}_1, \ldots, s^{(k+1)}_k)$. So the map IS a bijection. ✓

Now, $\phi_{k+1}$ maps $(b_0, \ldots, b_k) \mapsto (s^{(k+1)}_0, \ldots, s^{(k+1)}_k)$, which is:
1. $(b_0, \ldots, b_{k-1}) \mapsto (s^{(k)}_0, \ldots, s^{(k)}_{k-1})$  by $\phi_k$ (bijection by IH)
2. $(s^{(k)}_0, \ldots, s^{(k)}_{k-1}) \mapsto (s^{(k+1)}_1, \ldots, s^{(k+1)}_k)$ (bijection, proved above)
3. Then $s^{(k+1)}_0 = b_k \oplus (s^{(k)}_0 \vee s^{(k)}_1)$: given $(b_0, \ldots, b_{k-1})$, the value
   $s^{(k)}_0 \vee s^{(k)}_1$ is determined, and choosing $b_k$ freely sets $s^{(k+1)}_0$ to any value.

The map $\phi_{k+1} : (b_0, \ldots, b_k) \mapsto (s^{(k+1)}_0, \ldots, s^{(k+1)}_k)$ is therefore a
composition of bijections: $(b_0, \ldots, b_{k-1}) \mapsto (s^{(k)}_0, \ldots, s^{(k)}_{k-1})$ (bijection
by IH), then $(s^{(k)}, b_k) \mapsto (s^{(k+1)}_0, s^{(k+1)}_1, \ldots, s^{(k+1)}_k)$ where the inner bits
are a bijection in $s^{(k)}$ (just proved) and the first bit is xor'd with $b_k$ (freely setting it). ✓

**Main theorem**: Given any target state $\tau \in \{0,1\}^h$, the unique preimage of $\tau$ under $\phi_h$
gives boundary bits $b_0, \ldots, b_{h-1}$ such that starting from all-zeros and applying these bits,
we reach exactly $\tau$ after h steps. This proves full reachability. ∎

### Corollary 11a (All Predictive-State Classes Reachable)

All |S_h| predictive-state classes in S_h are reachable from the initial all-zeros class,
since the quotient map from raw states to classes is surjective (by definition) and Theorem 11
shows all raw states are reachable.

### Corollary 11b (Implication for Proof of Aperiodicity)

Theorem 11 establishes that the driven right-half system is "fully controllable" — every state is
reachable by choosing appropriate input bits. This means the ONLY reason the actual trajectory might
fail to visit some class is if the center-column sequence doesn't happen to produce the right steering
pattern. The fact that ALL classes ARE visited for h ≤ 20 is a deep property of the center column.

**Note**: Theorem 11 does NOT directly prove that the actual center-column sequence covers all classes.
It shows that some sequence can cover all classes. The gap between "some sequence can" and "the actual
Rule 30 center column does" is the remaining open question (see Computational Observation 12 and
Proposition 13).

### Theorem 11+ (Front Propagation Lemma and Universal Bijectivity)

**Lemma (Front Propagation)**: In the truncated width-h system, consider two trajectories from the
same initial state $s_0$, driven by identical boundary bits except at step k: bits $b_0, \ldots,
b_{h-1}$ vs. the same but with $b_k$ flipped. Let $\Delta^{(t)}_j$ denote the XOR of the two
trajectories at position j, time t. Then:

1. $\Delta^{(t)}_j = 0$ for $j > t - k - 1$ (difference cannot outrun the light cone).
2. $\Delta^{(t)}_{t-k-1} = 1$ for $t = k+1, \ldots, k+h$ (the front is always lit).

**Proof**: By induction on the front position $j = t - k - 1$.

*Base* ($j = 0$, time $t = k+1$): Only position 0 depends on $b_k$ (via $s'_0 = b_k \oplus
(s_0 \vee s_1)$). Flipping $b_k$ toggles position 0; positions $j \geq 1$ are unchanged. ✓

*Step*: Suppose at time $k+j$: $\Delta_{j-1} = 1$ and $\Delta_m = 0$ for $m \geq j$. At time
$k+j+1$, for position $j$:

$$s'^{(k+j+1)}_j = s'^{(k+j)}_{j-1} \oplus (s'^{(k+j)}_j \vee s'^{(k+j)}_{j+1}).$$

Since $\Delta^{(k+j)}_j = 0$ and $\Delta^{(k+j)}_{j+1} = 0$, the OR-term is identical in both
trajectories. Left-permutativity gives:

$$\Delta^{(k+j+1)}_j = \Delta^{(k+j)}_{j-1} = 1. \quad \checkmark$$

For $m > j$: positions $m-1, m, m+1$ all have $\Delta = 0$ at time $k+j$, so
$\Delta^{(k+j+1)}_m = 0$. ✓   ∎

(Verified exhaustively for h ≤ 10 and by sampling for h ≤ 14;
see `experiments/front_propagation_proof.py`.)

**Theorem (Universal Bijectivity)**: For ANY starting state $s_0 \in \{0,1\}^h$, the map

$$\Phi_{s_0} : (b_0, \ldots, b_{h-1}) \mapsto s_h$$

(evolve h steps of truncated width-h Rule 30 with boundary bits $b_0, \ldots, b_{h-1}$) is a
bijection from $\{0,1\}^h$ to $\{0,1\}^h$.

**Proof**: Consider the GF(2) Jacobian $J_{ij} = \partial (s_h)_i / \partial b_j$. By the Front
Propagation Lemma:

- $J_{ij} = 0$ when $j > h-1-i$ (beyond the light cone), making $J$ lower-triangular (with rows
  indexed by position $i$ and columns by bit index $j$, where bit $b_j$ can affect at most
  positions $0, \ldots, h-1-j$ of $s_h$).
- $J_{i, h-1-i} = 1$ (the diagonal: bit $b_{h-1-i}$ always toggles position $i$ after $i$
  propagation steps).

A lower-triangular GF(2) matrix with all-1 diagonal has determinant 1, so $\Phi_{s_0}$ is
invertible over $GF(2)^h$. Since $\Phi_{s_0}$ maps a finite set to itself injectively, it is a
bijection. ∎

Note: The single-step map $s \mapsto f_b(s)$ is NOT bijective — it has image size approximately
$0.6 \cdot 2^h$ — so this is not a trivial corollary. The bijectivity emerges from the
accumulation of h steps with independently chosen boundary bits.

(Verified exhaustively for h ≤ 11 and by sampling for h ≤ 15; see `experiments/bijectivity_test.py`
and `experiments/jacobian_test.py`.)

**Remark (State Forgetting Is Eventual, Not Instantaneous)**: Universal Bijectivity does NOT
imply that the system forgets its initial state after h steps. Two trajectories from different
starting states $s_0 \ne s'_0$, driven by the SAME boundary bits, do NOT in general converge
after h steps. Empirically, convergence times range from O(h) to O(h²) depending on the pair
(see `experiments/state_forgetting2.py`). However, what IS true is that for any fixed starting
state, the h boundary bits uniquely determine the outcome — and this holds for ALL starting
states simultaneously.

### Proposition 11c (Recursive Characterization of Predictive Classes)

There is a well-defined deterministic map from predictive classes at horizon h to **pairs** of
predictive classes at horizon h-1:

$$
\Psi_h : S_h \to S_{h-1} \times S_{h-1}, \qquad
\Psi_h(c) = (\tau_0(c), \tau_1(c)),
$$

where $\tau_b(c)$ is defined by: take any raw state $s$ in class $c$, evolve one step with boundary
bit $b$, truncate the rightmost bit of the resulting h-bit state, and then project to $S_{h-1}$.

Also let $\ell(c) \in \{0,1\}$ denote the common leftmost bit of any state in class $c$.

Then the map

$$
c \mapsto (\ell(c), \tau_0(c), \tau_1(c))
$$

is injective. Consequently, every fiber of $\Psi_h$ has size at most 2, and any 2-element fiber must
consist of one class with $\ell(c)=0$ and one class with $\ell(c)=1$.

**Proof**: Let $s$ be an h-bit state and let $\beta = b\gamma$ be a boundary word of length h, where
$b \in \{0,1\}$ is the first boundary bit and $\gamma$ has length h-1. The predictive response of $s$
to $\beta$ has the recursive form

$$
R_h(s, b\gamma) = s_0 \;\Vert\; R_{h-1}(T_b(s), \gamma),
$$

where $T_b(s)$ is the truncated state obtained by evolving one step with boundary bit $b$ and then
discarding the rightmost site, and $\Vert$ denotes concatenation.

Therefore the full response signature of $s$ is completely determined by:

1. its leftmost bit $s_0$;
2. the predictive class of $T_0(s)$ in $S_{h-1}$;
3. the predictive class of $T_1(s)$ in $S_{h-1}$.

In particular, if two states $s,t \in \{0,1\}^h$ satisfy

$$
s_0 = t_0, \qquad [T_0(s)] = [T_0(t)], \qquad [T_1(s)] = [T_1(t)],
$$

then for every boundary word $b\gamma$ they have the same response
$R_h(s, b\gamma) = R_h(t, b\gamma)$, so they lie in the same predictive class. Thus the triple
$(\ell(c), \tau_0(c), \tau_1(c))$ uniquely determines the class $c$. ∎

This is valid even though the same-h class dynamics is NOT deterministic: different raw states in the
same class can evolve to different classes in $S_h$ under the same boundary bit. The deterministic
structure appears only after one-step evolution **and truncation to horizon h-1**.

Computationally, for h <= 21, the number of distinct pairs $\Psi_h(c)$ is:

| h  | \|S_h\| | distinct pairs $\Psi_h(c)$ | pair-fiber size-2 count |
|----|---------|-------------------------------|-------------------------|
| 16 |     517 |                           436 |                      81 |
| 17 |     733 |                           618 |                     115 |
| 18 |     971 |                           822 |                     149 |
| 19 |    1364 |                          1154 |                     210 |
| 20 |    1792 |                          1518 |                     274 |
| 21 |    2497 |                          2115 |                     382 |

This does not yet close the induction h -> h+1, but it is a genuine recursive structure on the
predictive quotients and appears to be the right replacement for the invalid same-h deterministic
graph picture.

### Proposition 11d (Right-Truncation Descends to Predictive Classes)

Define the right-truncation map on raw states by

$$
\rho_h(s_0,\dots,s_{h-1}) = (s_0,\dots,s_{h-2}).
$$

Then $\rho_h$ descends to a well-defined surjective map

$$
\rho_h : S_h \to S_{h-1}.
$$

**Proof**: Suppose two h-bit states $s,t$ lie in the same predictive class in $S_h$. Let $u$ be any
boundary word of length h-1, and append an arbitrary final bit $a \in \{0,1\}$ to form the h-bit
boundary word $ua$. Since $s$ and $t$ are predictively equivalent at horizon h, their full response
words to $ua$ are identical. In particular, their first h-1 output bits agree.

But those first h-1 output bits depend only on the first h-1 cells of the initial state: the dropped
rightmost cell is at distance h-1 from the observed site and cannot influence the leftmost output in
fewer than h steps. Therefore the response of $\rho_h(s)$ to u is exactly the first h-1 output bits
of s under ua, and likewise for t. Hence $\rho_h(s)$ and $\rho_h(t)$ have identical responses to all
boundary words u of length h-1, so they lie in the same class in $S_{h-1}$. Thus $\rho_h$ is well-
defined.

Surjectivity is immediate: given any (h-1)-bit raw state x, append either final bit 0 or 1 to obtain
an h-bit state whose class maps to the class of x. ∎

### Computational Observation 11e (Small Fibers for Right-Truncation)

For h <= 21, the map $\rho_h : S_h \to S_{h-1}$ has only 1-element and 2-element fibers:

| h  | \|S_h\| | fiber-size distribution for $\rho_h$ |
|----|---------|----------------------------------------|
| 16 |     517 | {1: 257, 2: 130}                       |
| 17 |     733 | {1: 301, 2: 216}                       |
| 18 |     971 | {1: 495, 2: 238}                       |
| 19 |    1364 | {1: 578, 2: 393}                       |
| 20 |    1792 | {1: 936, 2: 428}                       |
| 21 |    2497 | {1: 1087, 2: 705}                      |

So empirically, each predictive class at horizon h-1 has either one or two lifts to horizon h under
right-extension.

### Computational Observation 11f (Parity Pattern for $(\rho_h, \tau_b)$)

Define the combined invariants $(\rho_h(c), \tau_0(c))$ and $(\rho_h(c), \tau_1(c))$. Empirically:

- For even h <= 20, each of the maps $c \mapsto (\rho_h(c), \tau_0(c))$ and
  $c \mapsto (\rho_h(c), \tau_1(c))$ is injective.
- For odd h <= 21, both maps fail to be injective.

This even/odd alternation is striking and may reflect a genuine parity structure in the recursive
description of predictive classes, though no proof is known yet.

### Proposition 11g (Commuting Square for $\rho_h$ and $\tau_b$)

For each h >= 3 and each b in {0,1}, the following diagram commutes:

$$
\rho_{h-1} \circ \tau_b = \tau_b \circ \rho_h : S_h \to S_{h-2}.
$$

**Proof**: On raw states this is immediate from the definitions. Starting with an h-bit state s:

1. applying $\tau_b$ means evolve one step with boundary bit b and truncate the last site;
2. then applying $\rho_{h-1}$ drops the last remaining site.

So the left-hand side is obtained by evolving one step and then deleting the last two sites.
On the other hand:

1. applying $\rho_h$ first drops the last site of s;
2. then applying $\tau_b$ at horizon h-1 evolves one step and drops the last site again.

Because Rule 30 is local and the rightmost dropped site cannot affect cells two or more positions to
its left in a single update, both constructions produce the same (h-2)-bit raw state. Since both
$\rho$ and $\tau_b$ descend to well-defined maps on predictive classes, the induced class maps also
commute. ∎

### Proposition 11h (Opposite Leading Bits for the Two Children)

For every predictive class c in S_h, the two child classes $\tau_0(c)$ and $\tau_1(c)$ lie in opposite
leading-bit sectors of $S_{h-1}$.

Equivalently, if $\ell(c')$ denotes the common leftmost bit of a class c', then

$$
\ell(\tau_1(c)) = 1 - \ell(\tau_0(c)).
$$

**Proof**: Let s be any raw state in class c. The leftmost bit of the one-step successor under
boundary bit b is

$$
s'_0 = b \oplus (s_0 \vee s_1).
$$

So changing b from 0 to 1 flips the leftmost successor bit and changes nothing else in the formula.
After truncation to horizon h-1, this leftmost successor bit becomes the leading bit of the child
class. Therefore the two children have opposite leading bits. ∎

### Computational Observation 11i (Same Leading Bit and Same Rho-Children for 2-Fiber Siblings)

For $2 \le h \le 21$, every 2-element fiber of $\rho_h : S_h \to S_{h-1}$ consists of two classes with
the **same** leading bit $\ell$. Moreover, for any 2-fiber siblings $c, c'$ (i.e.,
$\rho_h(c) = \rho_h(c')$ with $c \ne c'$):

$$
\rho_{h-1}(\tau_b(c)) = \rho_{h-1}(\tau_b(c')) \quad \text{for each } b \in \{0,1\}.
$$

That is, the siblings' children always land in the same $\rho$-fiber of $S_{h-1}$.

The same-leading-bit property is verified computationally. The same-rho-children property follows
from the commuting square (Proposition 11g): $\rho_{h-1}(\tau_b(c)) = \tau_b(\rho_h(c)) =
\tau_b(\rho_h(c'))= \rho_{h-1}(\tau_b(c'))$.

At $h=1$, this statement is false in the degenerate finite partition: the two classes in the
single $\rho_1$-fiber have leading bits 0 and 1. See
`experiments/sibling_fiber_parity.py` and
`docs/agent-wave-2026-08-25-sibling-fiber-parity.md` for the exact bounded witness.

### Computational Observation 11j (Even/Odd Parity Pattern for 2-Fiber Children)

For 2-element $\rho$-fiber siblings $\{c, c'\}$ at horizon $h \ge 3$:

- **Even h** (verified h ≤ 20): siblings share **neither** child.
  $\tau_0(c) \ne \tau_0(c')$ AND $\tau_1(c) \ne \tau_1(c')$.

- **Odd h** (verified h ≤ 21): siblings share **exactly one** child.
  Either $\tau_0(c) = \tau_0(c')$ and $\tau_1(c) \ne \tau_1(c')$, or vice versa.
  The two cases occur in roughly equal proportions.

(Verified via `experiments/child_relationship.py`.)

The lower bound $h \ge 3$ is necessary for the unqualified parity wording. At $h=1$, both
children of the two sibling classes are the unique class in $S_0$, so that pair shares both
children. The even $h=2$ row already has the “share neither” behavior.

### Observation 11k (Growth Decomposition)

Let $n_1(h)$ denote the number of 1-element fibers and $n_2(h)$ the number of 2-element fibers
of $\rho_h : S_h \to S_{h-1}$. Then:

$$
|S_h| = n_1(h) + 2 n_2(h), \qquad |S_{h-1}| = n_1(h) + n_2(h),
$$

and therefore:

$$
|S_h| - |S_{h-1}| = n_2(h).
$$

This is verified exactly for h = 1 to 21. Furthermore, the $n_2$ growth shows a parity pattern:

| h  | $|S_h|$ | $n_1(h)$ | $n_2(h)$ | $n_2(h)/n_2(h-1)$ |
|----|---------|----------|----------|--------------------|
| 15 |     387 |      131 |      128 |                    |
| 16 |     517 |      257 |      130 |  1.02 (even)       |
| 17 |     733 |      301 |      216 |  1.66 (odd)        |
| 18 |     971 |      495 |      238 |  1.10 (even)       |
| 19 |    1364 |      578 |      393 |  1.65 (odd)        |
| 20 |    1792 |      936 |      428 |  1.09 (even)       |
| 21 |    2497 |     1087 |      705 |  1.65 (odd)        |

The ratio $n_2(h)/n_2(h-1)$ alternates: ≈ 1.1 at even h, ≈ 1.65 at odd h.

(Verified via `experiments/fiber_growth_table.py`.)

### Remark on True vs. Truncated Dynamics

The predictive-state classes $S_h$ and the response function $R_h(s, \beta)$ are defined using
the **truncated** (zero-padded) width-h dynamics. This is the system tracked by
`experiments/fast_class_coverage2.py`.

There is a distinct dynamical system: the **true infinite right-half** of Rule 30, where one
observes the first h positions $a(1,t), \ldots, a(h,t)$ of the actual spacetime. The h-tuples
from the true system diverge from the truncated system after ≈ h steps (48–88% mismatch rate;
see `experiments/verify_rho_trajectory.py`).

For the proof argument (Proposition 13), the **truncated system is correct**: it is a finite-
state machine driven by $c(t)$, so Proposition 7 applies. The true system's h-prefix is not a
finite-state function of $c(t)$ (it depends on the full infinite state, requiring unbounded
memory). Both systems empirically achieve full class coverage for h ≤ 18
(`experiments/coverage_comparison.py`).

## Computational Observation 12: All Predictive-State Classes Are Visited By the Actual Trajectory

(Computationally verified for h <= 22 via fast integer-lookup-table trajectory tracing against
precomputed center-column bits. See `experiments/fast_class_coverage2.py`.)

The actual Rule 30 center-column-driven trajectory visits **all** classes in S_h:

| h  | \|S_h\| | sat_step  | ratio  | rarest class example                   |
|----|---------|-----------|--------|----------------------------------------|
| 16 |     517 |   104,527 | 202.2x | `0000000000000001` (wt=1)              |
| 17 |     733 |   203,477 | 277.6x | `00100100100100010` (wt=5)             |
| 18 |     971 |   429,241 | 442.1x | `000000000000001101` (wt=3)            |
| 19 |    1364 |   658,581 | 482.8x | `0100100100100100010` (wt=6)           |
| 20 |   1792  |   877,606 | 489.7x | `00000000000000000001` (wt=1)          |
| 21 |   2497  | 1,666,406 | 667.4x | `000000000000000000100` (wt=1, cls 3)  |
| 22 |   3263  | 4,585,894 | 1405.4x| `0100100100100100100010` (wt=7, cls 1246)|

For h ≤ 15, all |S_h| classes were verified within 50,000 steps in earlier experiments.

**Key observations:**
- Saturation ratio (sat_step / |S_h|) grows from ~202x at h=16 to ~490x at h=20, suggesting
  that the ratio grows with h but remains polynomial — well within any fixed period p.
- The rarest class at each h is typically a very-low-weight or very-high-weight state (a right-
  half state with few or many 1-bits). Class 1 (the state with a single 1 at the rightmost bit)
  is consistently among the rarest, requiring a long run of 0s in the center column to reach.
- The 1M bit prefix comfortably covers all h <= 20, but h = 21 and h = 22 require substantially
  longer prefixes: about 1.67M and 4.59M bits respectively.

The visit distribution is highly non-uniform, with some classes visited very rarely. This is
consistent with the structure of the quotient: low-weight states have fewer predecessors and
require specific boundary-bit patterns to enter.

## Proposition 13 [RETRACTED]: Period Lower Bound From Class Coverage

**Status: RETRACTED.** The original argument contained a fundamental error in the period bound.
The corrected version is recorded below, followed by an explanation of why the corrected bound
is vacuous.

**Hypothesis (Coverage Hypothesis)**: For all h, the Rule 30 center-column-driven truncated
trajectory eventually visits every class in S_h. (Verified computationally for h <= 22; believed
to hold for all h.)

**Original (incorrect) claim**: The machine state has period dividing p, so within one period
the trajectory visits at most p distinct classes, giving p >= |S_h|.

**Error**: By Proposition 7, the driven system has eventual period L·p, where L is the cycle
length of the p-step macro-map F_w on the state space. L can be much larger than 1. The machine
state does NOT generally have period p; it has period L·p.

**Concrete counterexamples**: The smallest witness is at h=1 with constant period-1 boundary
word "1" and initial state 0. The width-1 update is `s(t+1) = 1 xor s(t)`, so the state
alternates `0, 1, 0, ...`: the input period is 1, but the phase-lifted machine period is 2
and both finite classes are visited, not the ≤1 claimed by the original argument. A useful
nonconstant witness is h=6 with period-2 boundary word "10", where the machine period is
8 = 4×2 (macro-cycle length L=4) and one machine cycle visits 7 distinct classes, not the
≤2 claimed by the original argument.

Systematic verification (experiments/verify_period_bug.py):
- h=4, p=2: max L=5 (micro-period 10)
- h=6, p=2: max L=4 (micro-period 8)
- h=8, p=3: max L=12 (micro-period 36)
- h=10, p=3: max L=17 (micro-period 51)

**Corrected bound**: If T is the number of pre-cycle microsteps after the periodic input has
started, the trajectory visits at most T + L·p distinct classes, where L is the macro-cycle
length. Equivalently, if T_macro counts complete input periods, use T_macro·p + L·p (up to a
fixed phase-alignment offset). Using only L ≤ 2^h gives the worst-case envelope
T + 2^h·p, which dominates |S_h| for p ≥ 1 (since |S_h| ≤ 2^h). The exact T + L·p can be
informative for a fixed finite machine, but without an independent upper bound on T or L it
gives no lower bound on p. The coverage-based argument is therefore **vacuous** in general.

**Conclusion**: The Coverage Hypothesis approach, combined with this counting argument, CANNOT
prove aperiodicity. A fundamentally different argument is needed.

### Remark: Coverage is a Dynamical Property, Not a Subword Property

A natural conjecture might be that coverage holds because all length-h binary words appear as
subwords of the center column. This is FALSE for h ≥ 19:

| h  | \|S_h\| | classes from subwords | trajectory-only classes | subword fraction |
|----|---------|-----------------------|--------------------------|-----------------|
| 18 |     971 |                   971 |                        0 |           31.9% |
| 19 |    1364 |                  1363 |                        1 |           17.2% |
| 20 |    1792 |                  1786 |                        6 |            9.1% |

At h=20, the truncated trajectory visits **6 classes** whose member h-tuples NEVER appear as
subwords of the center column within 1M bits. Moreover, only ~9% of trajectory states at each
step are actual subwords. The truncated dynamics reaches states through indirect evolutionary
paths that have no direct representation in the center column's subword structure.

This means:
- Coverage CANNOT be proved via subword complexity arguments alone.
- The proof must engage with the dynamical structure of the truncated system.
- The relevant property is something like "ergodicity" or "transitivity" of the truncated system
  driven by the specific center-column input, not a property of the center column as a string.

(Verified via `experiments/coverage_vs_subwords.py`.)

### What Remains to Prove

The missing step is to prove the Coverage Hypothesis: that the truncated trajectory visits all
classes in S_h for every h.

**What does NOT work**: A subword-complexity argument. The coverage mechanism is dynamical, not
string-theoretic. At h=20, only ~9% of trajectory states correspond to actual subwords of the
center column, and 6 classes visited by the trajectory have NO member tuples appearing as subwords.

**Possible approaches to proving coverage**:

1. **Contradiction argument**: Assume some class c ∈ S_h is never visited. The truncated system
   is driven by (a periodic) c(t). Since the trajectory is confined to a strict subset V ⊊ S_h,
   and V is closed under the truncated transition driven by c(t), one might derive structural
   constraints on c(t) that conflict with it being a Rule 30 center column.

2. **Inductive/recursive approach**: Use the cross-horizon maps τ_b and ρ_h. If coverage at
   horizon h-1 is known, can the fiber structure (Observations 11i-11k) force coverage at h?
   The parity-alternating pattern in how 2-fibers split across horizons may be key.

3. **Density/mixing argument**: The truncated system at horizon h has 2^h raw states but only
   |S_h| ≈ exp(h^{2/3}) classes. The enormous redundancy (each class contains 2^h/|S_h| states
   on average) means the system has many paths to reach each class. Perhaps a counting argument
   can show that the center column's input sequence, regardless of its specific pattern (as long
   as it's a valid Rule 30 center column), must steer through enough of the state space.

4. **Exploit left-permutativity**: Theorem 11 shows that the system is fully controllable — any
   state can be reached by SOME boundary sequence in exactly h steps. If the center column has
   period p, then it cycles through at most p distinct length-h input windows. These p windows
   can reach at most p · (something) states. But the full class coverage requires visiting |S_h|
   classes, so if |S_h| > p, we get a contradiction directly. This IS the content of Prop. 13.
   The gap is: why does the periodic trajectory ACTUALLY visit all classes, not just some?

5. **Use the specific structure of Rule 30**: The center column is not an arbitrary sequence; it
   is generated by the Rule 30 CA itself. Perhaps the self-referential nature of the dynamics
   (the center column drives the right half, which in turn constrains the center column) can be
   exploited to show that missing a class leads to a contradiction with Rule 30 evolution.

**Note**: Given the retraction of Proposition 13, even if the Coverage Hypothesis is proved, it
would NOT yield a proof of aperiodicity via the counting argument. The Coverage Hypothesis
remains interesting in its own right, but a different proof strategy is needed.

## The Fundamental Gap: From One Column to Two Columns

### The Known Result (Erica Jen, 1986)

It is known that no two adjacent columns of Rule 30 from a single cell can both be eventually
periodic. Our Proposition 2 + Corollary 3 give a self-contained proof:

1. Assume columns x and x+1 are both eventually periodic with common period Q after time i.
2. By Proposition 2, all columns y ≤ x inherit period Q after time i.
3. By Corollary 3, choose y with |y| > i + Q; then column y is permanently zero for t > i.
4. The left-edge property a_{-t}(t) = 1 for all t ≥ 1 provides a contradiction:
   for t = |y| > i, column y should be zero, but a_y(|y|) = a_{-|y|}(|y|) = 1.

Note: Step 4 uses the left-edge property, which follows from the Rule 30 update and induction:
a_{-(t+1)}(t+1) = a_{-t}(t) ⊕ (a_{-(t+1)}(t) ∨ a_{-(t+2)}(t)) = 1 ⊕ (0 ∨ 0) = 1,
since a_{-(t+1)}(t) = a_{-(t+2)}(t) = 0 (outside the light cone).

### The Gap

To prove that a SINGLE column (e.g., the center column a_0) is not eventually periodic, we
would need to show: "if a_0 has period p, then some adjacent column (a_1 or a_{-1}) is also
eventually periodic." Then the two-column result gives a contradiction.

For the LEFT neighbor: a_{-1}(t) = a_0(t+1) ⊕ (a_0(t) ∨ a_1(t)). When a_0(t) = 1, this
gives a_{-1}(t) = a_0(t+1) ⊕ 1, fully determined by the periodic center column. When a_0(t) = 0,
we get a_{-1}(t) = a_0(t+1) ⊕ a_1(t), which depends on a_1.

For the RIGHT neighbor: a_1(t) is the first column of the right half, driven by a_0 as a
periodic boundary. The right half is a semi-infinite system, NOT a finite-state machine. It
starts from all zeros and its "width" grows at each time step (light cone expansion).

### Why the Right Half Doesn't Help Directly

The width-K truncated right half (cells 1 through K with zero padding at K+1) IS a finite-state
machine with 2^K states, and by Proposition 7, its column 1 is eventually periodic when driven
by periodic a_0. However:

1. The truncated column 1 agrees with the true column 1 only up to time ≈ 2K.
2. The period of the truncated system grows rapidly with K:
   - K=20, p=2: period 138
   - K=30, p=2: period 510
   - K=39, p=2: period 6258
   - K=40, p=2: period 2722
   (data from experiments/truncation_period_stability.py)
3. The periods do NOT stabilize as K → ∞, strongly suggesting the true column 1 is NOT
   eventually periodic for generic periodic boundaries.

### What Would Bridge the Gap

Any of the following would suffice:

1. **Direct proof that a_1 is eventually periodic when a_0 is**: This seems unlikely given the
   truncation experiments, unless the specific Rule 30 structure forces it.

2. **Show that some OTHER finite-state observable of the spacetime is eventually periodic AND
   provides enough information to reconstruct leftward**: The observable would need to be
   (a) a finite-state function of the center column (so Prop 7 applies), and
   (b) equivalent to "two adjacent periodic columns" for left-reconstruction purposes.

3. **Find a contradiction that doesn't require two adjacent columns**: A proof that uses only
   the periodicity of a_0, without needing a_1 or a_{-1} to be periodic.

4. **Show that the difference sequence d_x(t) = a_x(t+p) ⊕ a_x(t) has structural properties
   incompatible with d_0 = 0**: For example, if d can be shown to propagate in a way that
   forces d_x ≠ 0 for all x near the light cone, contradicting d_0 = 0.

### Approaches Tried and Their Outcomes

- **Left-permutativity reconstruction (Proposition 2 route)**: Works for TWO columns; stuck at
  one column because a_{-1} reconstruction requires a_1.

- **Truncated right-half convergence**: Periods grow too fast; no evidence of convergence.

- **Coverage + counting (Proposition 13)**: Retracted — corrected bound is vacuous.

- **Diagonal analysis (edge structure)**: Right-edge diagonals have periodic structure (periods
  doubling: 1, 2, 2, 4, 8, 8, 16, 32, ...), but these are diagonal, not fixed-column properties.

- **Difference propagation (d_x analysis)**: The system for d_x is nonlinear (due to the OR in
  Rule 30), making it hard to analyze. When a_0(t) = 1, the OR blocks d-propagation through the
  center, giving d_{-1}(t+1) = d_{-2}(t). When a_0(t) = 0, d propagates more freely.

### Current Assessment

The gap between one-column and two-column periodicity is the EXACT known barrier for this
problem. As noted in Wolfram's 2019 prize announcement: "there is no known way to extend [the
two-column result] from two columns to a single column."

The predictive-state framework (|S_h| → ∞, full reachability, coverage) provides deep structural
information about the right half, but has not yet yielded a way to bridge this specific gap.
The most promising unexplored direction is finding a finite-state observable of the center column
that acts as an effective "second column" for the left-reconstruction argument.
